from fastapi import FastAPI
from api.routes import router as api_router
from api.log_generator import loggen_router
from api.root import root_router  
app = FastAPI(title="Nats Endpoint Connection")

# Register all routes under /api
app.include_router(root_router)         # This handles "/"
app.include_router(api_router, prefix="/api")
app.include_router(loggen_router, prefix="/api/logs")