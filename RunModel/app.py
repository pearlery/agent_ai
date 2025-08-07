# app.py
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apis.root import root_router
from apis.PredictOne import predict_router
from apis.ConvertOne import convert_router
from apis.Manage_Service import manage_service_router
from apis.MatchMitre import match_mitre_router
from apis.PredictIfEmptyOne import predict_if_empty_router
from apis.CheckFlow import check_flow_router
from NatsFunction.Connection_to_Nats import OpenService,CloseService
from config.Config import cfg

@asynccontextmanager
async def lifespan(app: FastAPI):
    if cfg.AUTO_OPEN_CONNECTION:
        print("AUTO_OPEN_CONNECTION is enabled. Connecting...")
        await OpenService()
    else:
        print("AUTO_OPEN_CONNECTION is disabled. Skipping startup connection.")

    yield

    print("🔻 Shutting down — cleaning up NATS connection...")
    await CloseService()

app = FastAPI(title="Type Agent Model API", lifespan=lifespan)
# Route registration
app.include_router(root_router)  # Handles "/"
app.include_router(predict_router, prefix="/api")
app.include_router(convert_router, prefix="/api")
app.include_router(manage_service_router, prefix="/api")
app.include_router(match_mitre_router, prefix="/api")
app.include_router(predict_if_empty_router, prefix="/api")
app.include_router(check_flow_router, prefix="/api")

