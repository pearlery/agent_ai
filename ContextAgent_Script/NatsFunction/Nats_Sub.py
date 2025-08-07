from config.Config import cfg
from NatsFunction.Nats_Send_Function import send_to_next_agent_json
from NatsFunction.Nats_Client import nc  
from nats.js.api import DeliverPolicy
from nats.js.api import ConsumerConfig
subscriptions = {}  # Track subscriptions by subject

async def message_handler(msg):
    
    subject = msg.subject
    data_str = msg.data.decode("utf-8", errors="replace")

    print(f"New NATS message received from Subject: {subject}")

    if not data_str.strip():
        print(" Empty message — skipping.")
        return None

    try:
        await send_to_next_agent_json(data_str)
        await msg.ack()
        print(" ACK sent")
    except Exception as e:
        print("Error during agent processing:", e)
        await msg.ack()
        print(" ACK sent despite agent caught error")

async def start_nats_subscriber_with_js(subject: str, durable_name: str = "default_durable", queue_name: str = None):
    global subscriptions
    
    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)

    js = nc.jetstream()
    
    #due to LLM runing long this value needs to be more than LLM run time else the NATS will resent thus huge bug occurs
    consumer_config1 = ConsumerConfig(ack_wait=250)
    
    if queue_name:
        sub = await js.subscribe(
            subject,
            cb=message_handler
            ,durable=durable_name
            #,queue=queue_name
            ,deliver_policy=DeliverPolicy.NEW
            ,config = consumer_config1
        )
        #print("Subscribed with queue")
        #print(f"Subscribed with queue group: '{queue_name}'")
    else:
        sub = await js.subscribe(
            subject,
            cb=message_handler,
            durable=durable_name
        )
        print("Subscribed without queue group")

    subscriptions[subject] = sub
    print(f" Subscribed to JetStream subject: '{subject}', durable: '{durable_name}'")

async def stop_nats_subscriber(subject: str):
    global subscriptions
    if subject in subscriptions:
        sub = subscriptions[subject]
        await sub.unsubscribe()
        del subscriptions[subject]
        print(f"Unsubscribed from subject '{subject}'")
    else:
        print(f"No active subscription found for subject '{subject}'")

def show_subscriptions() -> list[str]:
    if not subscriptions:
        return []
    return list(subscriptions.keys())

#Unused
"""
async def start_nats_subscriber(subject: str):
    global subscriptions
    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)
    sub = await nc.subscribe(subject, cb=message_handler)
    subscriptions[subject] = sub
    print(f"Subscribed to '{subject}'")
"""
"""
#Code for without queue
async def start_nats_subscriber_with_js(subject: str, durable_name: str = "default_durable"):
    global subscriptions
    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)
    js = nc.jetstream()
    sub = await js.subscribe(subject, cb=message_handler, durable=durable_name)
    subscriptions[subject] = sub
    print(f"Subscribed to JetStream subject: '{subject}', durable: '{durable_name}'")
"""