from NatsFunction.Nats_Sub import start_nats_subscriber_with_js
from NatsFunction.Nats_Sub import stop_nats_subscriber
from config.Config import cfg
from NatsFunction.Nats_Client import nc

async def CloseService():
    """
    Gracefully close the NATS subscription and connection.
    """
    try:
        await stop_nats_subscriber(cfg.INPUT_SUBJECT)
        if nc.is_connected:
            await nc.drain()
            print("Drained NATS connection")
            await nc.close()
            print("NATS connection closed")
    except Exception as e:
        print(f"Error during shutdown: {e}")


async def OpenService():
    """
    Open the model server:
    - Force-drain old connections if needed
    - Start a new subscriber
    """
    try:
        # Force-close old connection if still alive
        if nc.is_connected:
            print("Previous NATS connection still alive — draining it before reconnecting.")
            await nc.drain()
            await nc.close()
            
        await start_nats_subscriber_with_js(
            subject=cfg.INPUT_SUBJECT,
            durable_name=cfg.DURABLE_NAME,
            queue_name=cfg.QUEUE_NAME,
        )
    except Exception as e:
        if "consumer name already in use" in str(e).lower() or "already bound" in str(e).lower():
            print(f"Subscriber already exists on subject '{cfg.INPUT_SUBJECT}' with durable '{cfg.DURABLE_NAME}' — continuing.")
        else:
            print(f"Error starting NATS subscriber: {e}")
            raise

    print("Model server is running and ready to receive messages.")
