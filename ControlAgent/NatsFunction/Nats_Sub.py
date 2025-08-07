from config.Config import cfg
from NatsFunction.Nats_Client import nc  
from nats.js.api import DeliverPolicy
from control.nats_action import startFlow,finishedType,finishedFlow
from config.Config import cfg
subscriptions = {}  # Track subscriptions by subject

topic_handlers = {
    cfg.INPUT_SUBJECT1: startFlow,
    cfg.INPUT_SUBJECT2: finishedType,
    cfg.INPUT_SUBJECT3: finishedFlow
}

async def message_handler(msg):
    subject = msg.subject
    data_str = msg.data.decode("utf-8", errors="replace")
    #print(data_str)
    handler = topic_handlers.get(subject)
    if handler:
        result = await handler(data_str)
        print(f"[✓] Handled message on '{subject}' → {result}")
    else:
        print(f"[] No handler for subject: {subject}")


async def start_nats_subscriber(subject: str):  
    global subscriptions
    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)
    sub = await nc.subscribe(subject, cb=message_handler)
    subscriptions[subject] = sub
    print(f"Subscribed to '{subject}'")
    
    
async def start_nats_subscriber_with_js(subject: str, durable_name: str = "default_durable", queue_name: str = None):
    global subscriptions

    if not nc.is_connected:
        await nc.connect(cfg.NAT_SERVER_URL)

    js = nc.jetstream()

    # 🧠 Add `queue=...` if queue_name is provided
    if queue_name:
        sub = await js.subscribe(
            subject,
            cb=message_handler,
            durable=durable_name
            #,queue=queue_name
            ,deliver_policy=DeliverPolicy.NEW
        )
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