
import asyncio
import json
import aiohttp
import os

from utils.nats_handler import NATSHandler
from config.settings import CONTEXT_SUBJECT, OUTPUT_SUBJECT, LOCAL_LLM_URL, LLM_MODEL, LLM_TEMPERATURE

# Load customer technology stack (tool awareness)
TOOLS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Output_N-Health_EndPoint.json"))

with open(TOOLS_FILE, "r", encoding="utf-8") as f:
    customer_data = json.load(f)
    TOOL_MAP = {tech["technology"]: tech["product"] for tech in customer_data[0]["data"]["onBoarding"]["currentTechnologies"]}

def build_recommendation_prompt(attack_type, context):
    relevant_tools = []

    # Heuristic: choose tools based on attack type
    if "phish" in attack_type.lower():
        relevant_tools = ["EMAILGATEWAY", "IAM", "SANDBOX"]
    elif "execution" in attack_type.lower() or "uac" in attack_type.lower():
        relevant_tools = ["EDR", "ANTIVIRUS", "PAM"]
    elif "recon" in attack_type.lower():
        relevant_tools = ["NDR", "NIDS_NIPS", "FIREWALL"]
    elif "ransom" in attack_type.lower():
        relevant_tools = ["EDR", "BACKUP", "SANDBOX"]
    elif "communication" in attack_type.lower():
        relevant_tools = ["WAF", "NDR", "NIDS_NIPS"]
    else:
        relevant_tools = ["EDR", "NDR", "IAM"]

    customer_tools = [TOOL_MAP[t] for t in relevant_tools if t in TOOL_MAP]

    tool_lines = "\n".join([f"- {tool}" for tool in customer_tools]) or "None"

    return f"""
You are a cybersecurity expert AI.

### Attack Type:
{attack_type}

### Context:
- Host: {context.get('host')}
- Source IP: {context.get('src_ip')}
- Destination IP: {context.get('dst_ip')}
- Domain: {context.get('domain')}
- Detected Time: {context.get('detected_time')}
- Alert Name: {context.get('alert_name')}
- Log Source: {context.get('log_source')}

### Available Tools in Customer Environment:
{tool_lines}

### Task:
Generate a markdown-formatted recommendation that includes:
1. Summary of what this alert could indicate
2. Step-by-step investigation actions using customer’s tools
3. Suggested commands, logs to check, or integrations
4. MITRE ATT&CK mapping if applicable
"""

async def query_llm(prompt):
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": LLM_MODEL,
            "temperature": LLM_TEMPERATURE,
            "prompt": prompt,
            "stream": False
        }
        async with session.post(f"{LOCAL_LLM_URL}api/generate", json=payload) as resp:
            res = await resp.json()
            return res.get("response", "").strip()

async def main():
    nats_handler = NATSHandler()
    await nats_handler.connect()

    async def handle_message(msg):
        data = json.loads(msg.data.decode())
        event_id = data.get("event_id")
        attack_type = data.get("attack_type")
        context = data.get("context", {})

        print(f"🧠 [recommendation_agent] Generating recommendation for: {event_id}")
        prompt = build_recommendation_prompt(attack_type, context)
        recommendation = await query_llm(prompt)

        output = {
            "event_id": event_id,
            "attack_type": attack_type,
            "context": context,
            "recommendation_markdown": recommendation,
            "source": "recommendation_agent"
        }

        await nats_handler.publish(OUTPUT_SUBJECT, output)
        print(f"✅ Recommendation published for: {event_id}")

    await nats_handler.js.subscribe(
        CONTEXT_SUBJECT,
        durable="recommendation_agent",
        cb=handle_message
    )

    print("🚀 recommendation_agent subscribed and running...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
