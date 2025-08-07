import asyncio
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig
from config.Config import cfg

async def create_js_stream(input_stream: str, input_filter: str):
    nc = NATS()
    await nc.connect(cfg.NAT_SERVER_URL)
    js = nc.jetstream()

    subject_filter = [f"{input_filter}.>"]  # e.g., alert.>

    try:
        await js.add_stream(
            config=StreamConfig(
                name=input_stream,
                subjects=[f"{input_filter}.>"],
                storage="memory"
            )
        )
        print(f" Stream '{input_stream}' created.")
    except Exception as e:
        if "stream name already in use" in str(e).lower():
            print(f" Stream '{input_stream}' already exists.")
        else:
            print(f"Error creating stream: {e}")


    await nc.drain()