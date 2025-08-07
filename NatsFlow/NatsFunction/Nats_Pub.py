import asyncio
import json
from nats.aio.client import Client as NATS
from config.Config import cfg


async def publish_message(subject: str, message: dict):
    nc = NATS()
    await nc.connect(cfg.NAT_SERVER_URL)
    
    #JetStream support
    #js = nc.jetstream()
    # await js.publish(subject, json.dumps(message).encode())
    
    #Non-JetStream support
    await nc.publish(subject, json.dumps(message).encode())
    
    print(f"Published message to subject '{subject}'")
    await nc.drain()
    
async def publish_Js_message(subject: str, message: dict):
    nc = NATS()
    await nc.connect(cfg.NAT_SERVER_URL)
    
    try:
        #JetStream support
        js = nc.jetstream()
        await js.publish(subject, json.dumps(message).encode())
        
        print(f"Published message to subject '{subject}'")
        await nc.drain()
        
    except Exception as e:
        print(f"Error publishing message to subject '{subject}': {e}")
        await nc.drain()
        raise e


