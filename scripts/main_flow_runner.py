
import asyncio
import json
from nats.aio.client import Client as NATS

async def run_flow():
    # Connect to NATS
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])  # Adjust if your NATS server is elsewhere

    # Load the message from the JSON file
    with open('../tests/message.json', 'r') as f:
        data = json.load(f)

    subject = data.get("subject")
    message = json.dumps(data.get("message")).encode('utf-8')

    if not subject:
        print("Error: 'subject' not found in message.json")
        await nc.close()
        return

    # Publish the message
    await nc.publish(subject, message)
    print(f"Published to subject '{subject}': {message.decode()}")

    # Close the connection
    await nc.close()

if __name__ == '__main__':
    asyncio.run(run_flow())

