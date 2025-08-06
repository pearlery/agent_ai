import asyncio
import json
from utils.nats_handler import NATSHandler
from config.settings import INPUT_SUBJECT, TYPE_SUBJECT

# Simple rule-based classifier
def classify_attack(alert):
    name = alert.get("alert_name", "").lower()
    incident_type = alert.get("incident_type", "").lower()

    # Rule-based matching
    if "phish" in name or "phishing" in incident_type:
        return "Phishing"
    elif "bypass" in name or "uac" in name:
        return "UAC Bypass"
    elif "port scan" in name or "scan" in incident_type:
        return "Reconnaissance"
    elif "powershell" in name or "script" in incident_type:
        return "Execution"
    elif "ransom" in name:
        return "Ransomware"
    elif "teams" in name:
        return "Suspicious Communication"
    else:
        return "Uncategorized"

async def main():
    nats_handler = NATSHandler()
    await nats_handler.connect()

    async def handle_message(msg):
        data = json.loads(msg.data.decode())
        log = data.get("raw_log", {})

        attack_type = classify_attack(log)
        output = {
            "event_id": data.get("event_id"),
            "attack_type": attack_type,
            "source": "attack_type_agent",
            "raw_log": log
        }

        print(f"🧠 [attack_type_agent] {output['event_id']} classified as: {attack_type}")
        await nats_handler.publish(TYPE_SUBJECT, output)

    await nats_handler.js.subscribe(
        INPUT_SUBJECT,
        durable="attack_type_agent",
        cb=handle_message
    )

    print("✅ attack_type_agent subscribed and running...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
