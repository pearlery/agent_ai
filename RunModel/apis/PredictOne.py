# apis/predictone.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from model.runModel import clean_run_prediction
from apis.Example_Log_Keeper import example_log_body as example_log
predict_router = APIRouter()

class NodeWrapper(BaseModel):
    node: Dict[str, Any] = Field(
        #default=example_log["node"], # This is the default value
        example=example_log["node"]  # This is the example shown in Swagger UI
    )

@predict_router.post(
    "/predict"
)
async def predict(alert: NodeWrapper):
    try:
        result = clean_run_prediction(alert.model_dump())

        # Optional logging
        with open("log.txt", "a") as f:
            f.write(f"Received alert to predict: {alert.model_dump()}\n")

        return result  # this returns a JSON object   

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
