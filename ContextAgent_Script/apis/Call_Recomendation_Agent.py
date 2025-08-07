from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any
from agents.agent_factory import AgentFactory
from tools.Example_Log_Keeper import example_log_body as example_log
from tools.Example_Log_Keeper import example_type_body as example_type
from contexts.compose_tools_data import compose_full_tools_data_from_log 

# Set up router
recommendation_agent_router = APIRouter()

# --- Pydantic Models ---

class NodeWrapper(BaseModel):
    node: Dict[str, Any] 
    
class Prediction(BaseModel):
    tactic: List[Tuple[str, float]]
    technique: List[Tuple[str, float]]
    subtechnique: List[Tuple[str, float]]

class MitreMatch(BaseModel):
    tactic: str
    technique: str
    subtechnique: Optional[str]
    Detection: str

class ExampleTypeBody(BaseModel):
    prediction: Prediction
    Mitre_Match: List[MitreMatch]
    
class RecommendationInput(BaseModel):
    log: Optional[NodeWrapper] = Field(
        default=None,
        example=example_log
    )
    type: Optional[ExampleTypeBody] = Field(
        default=None,
        example=example_type
    )

# --- API Endpoint ---
@recommendation_agent_router.post("/call-recommendation-agent/")
async def call_recommendation_agent(input_data: RecommendationInput):
    try:
        log_data = input_data.log.node if input_data.log and input_data.log.node else example_log["node"]
        type_data = input_data.type.model_dump() if input_data.type else example_type
        tools_data = await compose_full_tools_data_from_log(input_data.log.model_dump())

        # Create and run the recommendation agent
        agent_factory = AgentFactory()
        agent = agent_factory.create_recommending_agent()

        response = agent(
            log=log_data,
            mitre_attack_type=type_data,
            client_tools_json=tools_data
        )
        return {"status": "success", "result": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
