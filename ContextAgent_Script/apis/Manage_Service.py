from NatsFunction.Connection_to_Nats import OpenService,CloseService
from NatsFunction.Nats_Sub import show_subscriptions
from fastapi import APIRouter, HTTPException

manage_service_router = APIRouter()

@manage_service_router.post("/service/start")
async def start_nats_service():
    #Start the NATS connection and subscriber
    try:
        await OpenService()
        return {"message": "TypeAgent is running and ready to receive messages."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@manage_service_router.post("/service/stop")
async def stop_nats_service():
    #Gracefully stop the NATS connection and clean up
    try:
        await CloseService()
        return {"message": "TypeAgent NATS connection has been closed cleanly."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@manage_service_router.get("/service/checkSub")
async def check_nats_subscriber():
    #Show current Subscription for debugging
    try:
        subs = show_subscriptions()
        return {"subscriptions": subs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))