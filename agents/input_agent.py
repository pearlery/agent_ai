import asyncio
import json
import os
from utils.nats_handler import NATSHandler
from config.settings import INPUT_SUBJECT

ALERT_FILE = os.path.join(os.path.dirname(__file__), '../data/test.json')
async def main():
    # Load alert data
    with open(ALERT_FILE, 'r', encoding='utf-8') as f:
        alert_data = json.load(f)

    # Connect to NATS
    nats_handler = NATSHandler()
    await nats_handler.connect()

    # Publish each alert in the list
    for idx, record in enumerate(alert_data):
        node = record.get('node', {})
        message = {
            "event_id": node.get("alert_id"),
            "raw_log": node,
            "source": "input_agent"
        }
        print(f"🚀 Publishing alert {idx + 1}: {message['event_id']}")
        await nats_handler.publish(INPUT_SUBJECT, message)

    # Close connection
    await nats_handler.close()

if __name__ == "__main__":
    asyncio.run(main())
