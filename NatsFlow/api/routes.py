# api/routes.py
from fastapi import APIRouter
from api import nats_handler
from api.nats_handler import PublishRequest, SubscribeRequest, JsSubscribeRequest,CreateStreamRequest,DeleteStreamRequest

router = APIRouter()

@router.post("/start-subscriber")
async def start_subscriber(req: SubscribeRequest):
    return await nats_handler.start_subscriber(req)

@router.post("/start-Js-subscriber")
async def start_Js_subscriber(req: JsSubscribeRequest):
    return await nats_handler.start_Js_subscriber(req)

@router.post("/stop-subscriber")
async def stop_subscriber():
    return await nats_handler.stop_subscriber()

@router.post("/publish")
async def publish(req: PublishRequest):
    return await nats_handler.publish_message(req)

@router.post("/publish-js")
async def publish_Js(req: PublishRequest):
    return await nats_handler.publish_Js_message(req)

@router.post("/create-stream")
async def create_stream(req: CreateStreamRequest):
    return await nats_handler.create_jetstream_stream(req)  

@router.post("/get-latest-messages/")
async def get_lastest_Js_messages(req: JsSubscribeRequest,count: int = 3):
    return await nats_handler.get_last_js_messages(req, count)

@router.post("/stream/delete")
async def delete_stream_api(req: DeleteStreamRequest):
    return await nats_handler.delete_jetstream_stream(req)