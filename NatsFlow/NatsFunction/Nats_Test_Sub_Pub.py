import asyncio
#from contextlib import asynccontextmanager
from fastapi import FastAPI
from NatsFunction.Nats_Sub import start_nats_subscriber, stop_nats_subscriber
from NatsFunction.Nats_Pub import publish_message

nats_task = None  # Declare global to keep reference

#@asynccontextmanager
async def lifespan(app: FastAPI):
    global nats_task
    loop = asyncio.get_event_loop()

    # STARTUP
    print("Starting NATS subscriber...")
    nats_task = loop.create_task(start_nats_subscriber())
    await asyncio.sleep(2)  # Ensure subscriber starts

    for i in range(3):
        print(f"Publishing message {i+1}/3...")
        await publish_message()

    yield  # <-- App runs here

    # SHUTDOWN
    print("Shutting down NATS subscriber...")
    await stop_nats_subscriber()

app = FastAPI(lifespan=lifespan)
