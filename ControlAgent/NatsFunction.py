import asyncio
import nats
import os
import time
from dotenv import load_dotenv

load_dotenv()
NATS_URL = os.getenv("NATS_URL", "nats://nats-server:4222")

async def connect_nats_with_retry(url, retries=10, delay=3):
    for attempt in range(retries):
        try:
            nc = await nats.connect(url)
            print(f"✅ Connected to NATS: {url}")
            return nc
        except Exception as e:
            print(f"⏳ NATS connection failed (attempt {attempt+1}/{retries}): {e}")
            await asyncio.sleep(delay)
    raise RuntimeError("❌ Could not connect to NATS after retries")

async def main():
    nc = await connect_nats_with_retry(NATS_URL)

    async def message_handler(msg):
        data = msg.data.decode()
        print(f"📩 Received a message on '{msg.subject}': {data}")

    await nc.subscribe("agentAI.Input", cb=message_handler)
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
