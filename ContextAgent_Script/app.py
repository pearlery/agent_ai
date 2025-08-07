from fastapi import FastAPI
import uvicorn
from apis.root_api import root_router
from apis.Call_Answer_Agent import agent_router
from apis.Call_Recomendation_Agent import recommendation_agent_router
from apis.Manage_Service import manage_service_router  
from NatsFunction.Connection_to_Nats import OpenService,CloseService

from contextlib import asynccontextmanager
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

app = FastAPI(title="Context Agent Model API", lifespan=lifespan)
app.include_router(root_router)
app.include_router(agent_router, prefix="/api")
app.include_router(recommendation_agent_router, prefix="/api")
app.include_router(manage_service_router, prefix="/api") 

def start_api():
    """
    Start the FastAPI server without opening any UI.
    This will allow users to interact with the agent through API endpoints.
    """
    uvicorn.run(app, host="0.0.0.0", port=9002)
    #Use 8000 for default. I'm using 9002 for docker
    
if __name__ == "__main__":
    print("Starting the agent API server...")
    start_api()
