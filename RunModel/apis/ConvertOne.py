# apis/convertone.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field
from typing import Dict, Any
from model.convert_input_format import convert_input_format
from apis.Example_Log_Keeper import example_log_body as example_log

convert_router = APIRouter()

class NodeWrapper(BaseModel):
    node: Dict[str, Any] = Field(
        #default=example_log["node"], # This is the default value
        example=example_log["node"]  # This is the example shown in Swagger UI
    )

@convert_router.post("/convert")
async def convert(alert: NodeWrapper):
    try:
        cleaned = convert_input_format(alert.dict())
        return {"converted_input": cleaned}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
