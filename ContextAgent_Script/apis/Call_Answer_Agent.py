from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from agents.agent_factory import AgentFactory
from tools.Example_Log_Keeper import example_log_body2 as example_log
import json

agent_router = APIRouter()

class Input(BaseModel):
    question: str
    
class NodeWrapper(BaseModel):
    node: Dict[str, Any] = Field(
        default=example_log["node"], # This is the default value
        #example=example_log["node"]  # This is the example shown in Swagger UI
    )

@agent_router.post("/cybersecurity-answer/")
async def cybersecurity_answer(input_data: Input,input_log:Optional[NodeWrapper] = None):
    try:
        agent_factory = AgentFactory()
        agent = agent_factory.create_cybersecurity_answer_agent()
        node_data = input_log.node if input_log else example_log["node"]
        
        combined_input = {
            "question": f"{input_data.question}\n\nHere is the log context:\n{json.dumps(node_data, indent=2)}"
        }

        response = await agent.ainvoke(combined_input)
        result_text = response.get("text", "The returned response does not contain text.")
        #result_text = response["text"].replace("\n", "<br>")
        return {"status": "success", "result": result_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))