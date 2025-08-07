import asyncio
from nats.aio.client import Client as NATS
from config.Config import cfg

async def fetch_last_messages(subject: str, durable_name: str = "not_default_durable", count: int = 3):
    nc = NATS()
    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)

    js = nc.jetstream()
    
    # Create a pull subscription
    sub = await js.pull_subscribe(subject=subject, durable=durable_name)
    
    # Fetch messages (max=count)
    try:
        msgs = await sub.fetch(count, timeout=2)
        results = []
        for msg in msgs:
            try:
                print(f"Received message on '{msg.subject}': {msg.data.decode('utf-8')}")
                data_str = msg.data.decode("utf-8", errors="replace")
            except Exception as e:
                data_str = f"<decode-error: {e}>"
            results.append({"subject": msg.subject, "data": data_str})
            await msg.ack()
    except Exception as e:
        results = [{"error": str(e)}]

    await nc.close()
    return results