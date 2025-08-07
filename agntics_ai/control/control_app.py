"""
Control Agent FastAPI Application
"""
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from .control_api import control_router, get_control_agent
from ..config.config import get_config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown events.
    """
    # Startup
    try:
        config = get_config()
        
        if hasattr(config, 'AUTO_OPEN_CONNECTION') and config.AUTO_OPEN_CONNECTION:
            print("AUTO_OPEN_CONNECTION enabled. Initializing Control Agent...")
            # Initialize control agent on startup
            control_agent = await get_control_agent()
            print("Control Agent initialized successfully")
        else:
            print("AUTO_OPEN_CONNECTION disabled. Control Agent will initialize on first request.")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        print(f"Startup error: {e}")
    
    yield
    
    # Shutdown
    try:
        print("Shutting down Control Agent...")
        # Clean shutdown logic here if needed
        print("Control Agent shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        print(f"Shutdown error: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create FastAPI app
    app = FastAPI(
        title="Agent AI Control API",
        description="Control Agent API for orchestrating the Agent AI workflow",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Include routers
    app.include_router(control_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "service": "Agent AI Control API",
            "status": "running",
            "version": "1.0.0",
            "endpoints": [
                "POST /start - Start processing (compatibility)",
                "POST /control/start - Start processing flow",
                "GET /status - Get system status",
                "GET /health - Health check",
                "POST /control/type/finished - Complete type stage",
                "POST /control/flow/finished - Complete entire flow",
                "GET /control/status/{session_id} - Get session status",
                "GET /control/sessions - List all sessions",
                "DELETE /control/session/{session_id} - Delete session"
            ]
        }
    
    # Add compatibility endpoints for Web App
    from pydantic import BaseModel
    from typing import Optional, Dict, Any
    
    class StartRequest(BaseModel):
        input_file: Optional[str] = "test.json"
    
    @app.post("/start")
    async def start_processing_compat(request: StartRequest):
        """Compatibility endpoint for starting processing."""
        from .control_api import get_control_agent
        try:
            control_agent = await get_control_agent()
            
            # Load data from input file
            from pathlib import Path
            import json
            
            input_file = request.input_file or "test.json"
            file_path = Path(__file__).parent.parent.parent / input_file
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Use first item if it's a list
                if isinstance(data, list) and data:
                    alert_data = data[0]
                else:
                    alert_data = data
                
                session_id = control_agent.output_handler.generate_session_id()
                result = await control_agent.start_flow(alert_data, session_id)
                
                return {
                    "status": "success" if result == "success" else "error",
                    "session_id": session_id,
                    "message": f"Processing started with {input_file}",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": f"Input file {input_file} not found"
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e)
            }
    
    @app.get("/status")
    async def get_system_status():
        """Get system status endpoint."""
        from .control_api import get_control_agent
        try:
            control_agent = await get_control_agent()
            from ..utils.session_manager import get_session_manager
            session_manager = get_session_manager()
            
            return {
                "status": "running",
                "active_sessions": session_manager.get_active_session_count(),
                "system_status": "healthy"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    @app.get("/health")
    async def health_check_compat():
        """Health check compatibility endpoint."""
        from .control_api import get_control_agent
        try:
            control_agent = await get_control_agent()
            return {
                "status": "healthy",
                "nats_connected": True,
                "llm_available": True,
                "uptime": 3600
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    return app


# Create app instance
app = create_app()


def start_api(host: str = "0.0.0.0", port: int = 9002):
    """
    Start the FastAPI server.
    
    Args:
        host: Host address to bind to
        port: Port number to use
    """
    print("Starting Agent AI Control API server...")
    print(f"Server will be available at http://{host}:{port}")
    print("API documentation at http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    print("Agent AI Control Agent")
    print("=" * 30)
    start_api()