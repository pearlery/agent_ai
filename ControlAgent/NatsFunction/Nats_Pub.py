import json
from NatsFunction.Nats_Client import nc  
from config.Config import cfg

async def publish_Js_message(subject: str, message: dict):
    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)

    js = nc.jetstream()
    await js.publish(subject, json.dumps(message).encode())
    print(f"Published JS message to subject '{subject}'")

"""
async def publish_message(subject: str, message: dict):
    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)
    
    await nc.publish(subject, json.dumps(message).encode())
    print(f"Published message to subject '{subject}'")
"""
