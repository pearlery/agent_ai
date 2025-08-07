# apis/predictone.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from model.predict_if_mitre_empty import predict_check_package
from apis.Example_Log_Keeper import example_log_body as example_log
check_flow_router = APIRouter()

class NodeWrapper(BaseModel):
    node: Dict[str, Any] = Field(
        #default=example_log["node"], # This is the default value
        example=example_log["node"]  # This is the example shown in Swagger UI
    )

@check_flow_router.post(
    "/Check_Flow"
)
async def Check_Flow(alert: NodeWrapper):
    try:
        result = predict_check_package(alert.model_dump())

        # Optional logging
        with open("log.txt", "a") as f:
            f.write(f"Received alert to predict: {alert.model_dump()}\n")

        return result  # this returns a JSON object   

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
