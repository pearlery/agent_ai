
import asyncio
import json
from utils.nats_handler import NATSHandler
from config.settings import TYPE_SUBJECT, CONTEXT_SUBJECT

# 🔍 Extract useful context fields
def extract_context(log):
    context = {
        "host": log.get("hostname") or log.get("host"),
        "src_ip": log.get("contexts", {}).get("src_ip", [None])[0],
        "dst_ip": None,
        "domain": None,
        "alert_name": log.get("alert_name"),
        "log_source": log.get("log_source"),
        "detected_time": log.get("detected_time")
    }

    # Extract from events array
    events = log.get("events", [])
    if events and isinstance(events, list):
        event = events[0]
        context["dst_ip"] = event.get("dst_ip", [None])[0] if isinstance(event.get("dst_ip"), list) else event.get("dst_ip")
        context["domain"] = event.get("domain")

    return context

async def main():
    nats_handler = NATSHandler()
    await nats_handler.connect()

    async def handle_message(msg):
        data = json.loads(msg.data.decode())
        log = data.get("raw_log", {})
        event_id = data.get("event_id")

        context = extract_context(log)
        output = {
            "event_id": event_id,
            "attack_type": data.get("attack_type"),
            "context": context,
            "source": "context_agent",
            "raw_log": log
        }

        print(f"🔎 [context_agent] Extracted context for {event_id}")
        await nats_handler.publish(CONTEXT_SUBJECT, output)

    await nats_handler.js.subscribe(
        TYPE_SUBJECT,
        durable="context_agent",
        cb=handle_message
    )

    print("✅ context_agent subscribed and running...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
