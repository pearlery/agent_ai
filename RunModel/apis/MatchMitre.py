from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field
from typing import Dict
from model.MatchMitre import optimized_match
from apis.Example_Log_Keeper import example_prediction_body as example_log
match_mitre_router = APIRouter()

CSV_PATH = "./model/MitreMatch.csv"

class PredictionRequest(BaseModel):
    prediction: Dict[str, list] = Field(
    #default=example_log["prediction"],  # This is the default value
    example = example_log["prediction"]  # This is the example shown in Swagger UI
    )

@match_mitre_router.post("/match-mitre")
async def match_mitre(request: PredictionRequest):
    try:
        result = optimized_match(CSV_PATH, request.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
