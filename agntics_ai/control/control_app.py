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
            print("🚀 AUTO_OPEN_CONNECTION enabled. Initializing Control Agent...")
            # Initialize control agent on startup
            control_agent = await get_control_agent()
            print("✅ Control Agent initialized successfully")
        else:
            print("⏸️  AUTO_OPEN_CONNECTION disabled. Control Agent will initialize on first request.")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        print(f"❌ Startup error: {e}")
    
    yield
    
    # Shutdown
    try:
        print("🔻 Shutting down Control Agent...")
        # Clean shutdown logic here if needed
        print("✅ Control Agent shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        print(f"❌ Shutdown error: {e}")


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
                "POST /control/start - Start processing flow",
                "POST /control/type/finished - Complete type stage",
                "POST /control/flow/finished - Complete entire flow",
                "GET /control/status/{session_id} - Get session status",
                "GET /control/sessions - List all sessions",
                "DELETE /control/session/{session_id} - Delete session",
                "GET /control/health - Health check"
            ]
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
    print("🎯 Starting Agent AI Control API server...")
    print(f"📡 Server will be available at http://{host}:{port}")
    print("📚 API documentation at http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    print("Agent AI Control Agent")
    print("=" * 30)
    start_api()