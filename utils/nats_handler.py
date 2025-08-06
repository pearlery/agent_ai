
import asyncio
import json
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

from config.settings import NATS_URL

class NATSHandler:
    def __init__(self):
        self.nc = NATS()
        self.js = None

    async def connect(self):
        await self.nc.connect(servers=[NATS_URL])
        self.js = self.nc.jetstream()

    async def publish(self, subject: str, message: dict):
        if not self.js:
            raise Exception("NATS not connected.")
        await self.js.publish(subject, json.dumps(message).encode())

    async def close(self):
        await self.nc.drain()
