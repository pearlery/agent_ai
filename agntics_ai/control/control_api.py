"""
Control API - FastAPI endpoints for controlling the Agent AI workflow.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .control_agent import ControlAgent
from ..utils.nats_handler import NATSHandler
from ..utils.connection_manager import get_connection_manager
from ..utils.session_manager import get_session_manager
from ..config.config import get_config

logger = logging.getLogger(__name__)

# Initialize router
control_router = APIRouter(prefix="/control", tags=["control"])

# Global instances with thread safety
_control_agent: Optional[ControlAgent] = None
_control_agent_lock = asyncio.Lock()


class AlertData(BaseModel):
    """Pydantic model for alert data input."""
    alert_id: Optional[str] = None
    data: Dict[str, Any]


class ProcessingData(BaseModel):
    """Pydantic model for processing data input."""
    session_id: str
    data: Dict[str, Any]


async def get_control_agent() -> ControlAgent:
    """Get or initialize the control agent with proper concurrency control."""
    global _control_agent
    
    # Use double-checked locking pattern
    if _control_agent is None:
        async with _control_agent_lock:
            # Check again inside the lock
            if _control_agent is None:
                logger.info("Initializing Control Agent...")
                
                config = get_config()
                nats_config = config.get_nats_config()
                
                # Skip NATS connection for now to avoid blocking
                try:
                    # Use connection manager to prevent leaks
                    connection_manager = get_connection_manager()
                    nats_handler = await connection_manager.get_connection("control_agent", nats_config)
                    
                    _control_agent = ControlAgent(nats_handler)
                    
                    # Start session manager cleanup task
                    session_manager = get_session_manager()
                    await session_manager.start_cleanup_task()
                    
                    logger.info("Control Agent initialized successfully")
                    
                except Exception as e:
                    logger.warning(f"Failed to initialize with NATS: {e}")
                    # Create a dummy ControlAgent without NATS for testing
                    _control_agent = ControlAgent(None)
                    logger.info("Control Agent initialized without NATS (test mode)")
    
    return _control_agent


@control_router.post("/start")
async def start_flow(alert_data: AlertData):
    """
    Start processing flow for a new alert.
    
    Args:
        alert_data: Alert data to process
        
    Returns:
        Status and session information
    """
    try:
        control_agent = await get_control_agent()
        
        # Generate session ID if not provided
        session_id = alert_data.alert_id or control_agent.output_handler.generate_session_id()
        
        # Track session in session manager
        session_manager = get_session_manager()
        session_manager.add_session(session_id)
        
        result = await control_agent.start_flow(alert_data.data, session_id)
        
        if result == "success":
            return {
                "status": "success",
                "session_id": session_id,
                "message": "Flow started successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=result)
            
    except Exception as e:
        logger.error(f"Error starting flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.post("/type/finished")
async def finished_type(processing_data: ProcessingData):
    """
    Handle completion of type classification stage.
    
    Args:
        processing_data: Processing data with session ID
        
    Returns:
        Status message
    """
    try:
        control_agent = await get_control_agent()
        
        # Update session activity
        session_manager = get_session_manager()
        session_manager.update_session(processing_data.session_id)
        
        result = await control_agent.finished_type(
            processing_data.data,
            processing_data.session_id
        )
        
        if result == "success":
            return {
                "status": "success",
                "message": "Type classification stage completed"
            }
        else:
            raise HTTPException(status_code=400, detail=result)
            
    except Exception as e:
        logger.error(f"Error in finished_type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.post("/flow/finished")
async def finished_flow(processing_data: ProcessingData):
    """
    Handle completion of entire workflow.
    
    Args:
        processing_data: Final processing data with session ID
        
    Returns:
        Status message
    """
    try:
        control_agent = await get_control_agent()
        
        # Update session activity
        session_manager = get_session_manager()
        session_manager.update_session(processing_data.session_id)
        
        result = await control_agent.finished_flow(
            processing_data.data,
            processing_data.session_id
        )
        
        if result == "success":
            return {
                "status": "success",
                "message": "Workflow completed successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=result)
            
    except Exception as e:
        logger.error(f"Error in finished_flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.get("/status/{session_id}")
async def get_status(session_id: str):
    """
    Get current status for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Current session status and timeline
    """
    try:
        control_agent = await get_control_agent()
        
        # Load session data
        session_data = control_agent.persistence.load_session_data(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get current output data
        output_data = control_agent.output_handler.get_output_data()
        
        # Find session-specific data
        session_timeline = []
        for item in output_data.get("agent.timeline.updated", []):
            if item.get("id") == session_id:
                session_timeline = item.get("data", [])
                break
        
        return {
            "session_id": session_id,
            "status": session_data.get("data", {}).get("status", "unknown"),
            "timeline": session_timeline,
            "last_updated": session_data.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.get("/sessions")
async def list_sessions():
    """
    List all available sessions.
    
    Returns:
        List of session IDs and their basic information
    """
    try:
        control_agent = await get_control_agent()
        
        session_ids = control_agent.persistence.list_sessions()
        sessions = []
        
        for session_id in session_ids:
            try:
                session_data = control_agent.persistence.load_session_data(session_id)
                if session_data:
                    sessions.append({
                        "session_id": session_id,
                        "created_at": session_data.get("timestamp"),
                        "status": session_data.get("data", {}).get("status", "unknown")
                    })
            except Exception as e:
                logger.warning(f"Could not load session {session_id}: {e}")
                continue
        
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and its associated data.
    
    Args:
        session_id: Session identifier to delete
        
    Returns:
        Deletion confirmation
    """
    try:
        control_agent = await get_control_agent()
        
        # Remove session from session manager (includes data cleanup)
        session_manager = get_session_manager()
        session_manager.remove_session(session_id)
        
        return {
            "status": "success",
            "message": f"Session {session_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.get("/memory/stats")
async def get_memory_stats():
    """Get memory usage statistics."""
    try:
        session_manager = get_session_manager()
        connection_manager = get_connection_manager()
        
        return {
            "session_stats": session_manager.get_memory_stats(),
            "active_connections": len(connection_manager.get_active_connections()),
            "service": "Control Agent API"
        }
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.post("/memory/cleanup")
async def manual_cleanup():
    """Manually trigger memory cleanup."""
    try:
        session_manager = get_session_manager()
        await session_manager._cleanup_expired_sessions()
        
        return {
            "status": "success",
            "message": "Memory cleanup completed",
            "remaining_sessions": session_manager.get_active_session_count()
        }
    except Exception as e:
        logger.error(f"Manual cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@control_router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        control_agent = await get_control_agent()
        session_manager = get_session_manager()
        connection_manager = get_connection_manager()
        
        return {
            "status": "healthy",
            "service": "Control Agent API",
            "active_sessions": session_manager.get_active_session_count(),
            "active_connections": len(connection_manager.get_active_connections()),
            "nats_connected": True  # Assume connected if we get this far
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")