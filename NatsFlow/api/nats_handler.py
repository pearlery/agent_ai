# api/nats_handler.py
from fastapi import Body
from pydantic import BaseModel
import asyncio
from NatsFunction.Nats_Sub import start_nats_subscriber, stop_nats_subscriber,start_nats_subscriber_with_js
from NatsFunction.Nats_Pub import publish_message as pub_msg
from NatsFunction.Nats_Pub import publish_Js_message as pub_Js_msg
from NatsFunction.Nats_JS_Create import create_js_stream as create_stream  
from NatsFunction.Nats_Fetch_Messages import fetch_last_messages
from NatsFunction.Nats_Close_Stream import close_jetstream_stream
from config.Config import cfg
from fastapi import HTTPException, Query

subscriber_task = None

class SubscribeRequest(BaseModel):
    subject: str

async def start_subscriber(req: SubscribeRequest):
    global subscriber_task
    if subscriber_task is None or subscriber_task.done():
        loop = asyncio.get_running_loop()
        subscriber_task = loop.create_task(start_nats_subscriber(req.subject))
        return {"status": f"Subscribed to '{req.subject}'"}
    return {"status": "Subscriber already running"}
 
async def stop_subscriber():
    global subscriber_task
    await stop_nats_subscriber()
    if subscriber_task:
        subscriber_task.cancel()
        subscriber_task = None
    return {"status": "Subscriber stopped"}


class PublishRequest(BaseModel):
    subject: str
    message: dict

async def publish_message(req: PublishRequest):
    await pub_msg(req.subject, req.message)
    return {"status": f"Message published to '{req.subject}'"}

async def publish_Js_message(req: PublishRequest):
    await pub_Js_msg(req.subject, req.message)
    return {"status": f"MessageJs published to '{req.subject}'"}


class JsSubscribeRequest(BaseModel):
    subject: str
    durable_name: str = Query("default_durable", description="Durable name for JetStream subscription, defaults to 'default_durable'")

async def start_Js_subscriber(req: JsSubscribeRequest):
    global subscriber_task

    if subscriber_task is None or subscriber_task.done():
        loop = asyncio.get_running_loop()
        subscriber_task = loop.create_task(
            start_nats_subscriber_with_js(
                subject=req.subject,
                durable_name=req.durable_name
            )
        )
        return {"status": f"Subscribed to JetStream subject '{req.subject}' with durable '{req.durable_name}'"}
    return {"status": "Subscriber already running with JetStream"}

async def get_last_js_messages(req: JsSubscribeRequest,count: int = Query(3, description="Number of latest messages to fetch")):
    try:
        subject = req.subject
        durable_name = req.durable_name
        result = await fetch_last_messages(subject, durable_name, count)
        return {"status": "success", "messages": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
class CreateStreamRequest(BaseModel):
    stream_name: str = cfg.STREAM_NAME
    subject_prefix: str = cfg.STREAM_PREFIX
    
async def create_jetstream_stream(req: CreateStreamRequest):
    await create_stream(req.stream_name, req.subject_prefix)
    return {
        "status": "success",
        "message": f"Stream '{req.stream_name}' created for subject prefix '{req.subject_prefix}'"
    }

    
class DeleteStreamRequest(BaseModel):
    stream_name: str = cfg.STREAM_NAME
    
async def delete_jetstream_stream(req: DeleteStreamRequest):
    result = await close_jetstream_stream(cfg.NAT_SERVER_URL, req.stream_name)
    if result["status"] == "success":
        return result
    elif result["status"] == "not_found":
        raise HTTPException(status_code=404, detail=result["message"])
    else:
        raise HTTPException(status_code=500, detail=result["message"])
