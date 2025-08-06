"""
Session manager for cleaning up old sessions and managing memory.
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
from pathlib import Path

from .output_handler import get_output_handler
from .persistence import get_default_persistence

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session lifecycle and memory cleanup."""
    
    def __init__(self, max_sessions: int = 1000, cleanup_interval: int = 3600, session_ttl: int = 86400):
        """
        Initialize session manager.
        
        Args:
            max_sessions: Maximum number of sessions to keep in memory
            cleanup_interval: Cleanup interval in seconds (default: 1 hour)
            session_ttl: Session time-to-live in seconds (default: 24 hours)
        """
        self.max_sessions = max_sessions
        self.cleanup_interval = cleanup_interval
        self.session_ttl = session_ttl
        self.active_sessions: Set[str] = set()
        self.session_timestamps: Dict[str, float] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Get handlers
        self.output_handler = get_output_handler()
        self.persistence = get_default_persistence()
    
    def add_session(self, session_id: str) -> None:
        """
        Add a new session to tracking.
        
        Args:
            session_id: Session identifier to track
        """
        self.active_sessions.add(session_id)
        self.session_timestamps[session_id] = time.time()
        logger.debug(f"Added session to tracking: {session_id}")
        
        # Check if we need immediate cleanup
        if len(self.active_sessions) > self.max_sessions:
            asyncio.create_task(self._cleanup_oldest_sessions(immediate=True))
    
    def update_session(self, session_id: str) -> None:
        """
        Update session timestamp to indicate activity.
        
        Args:
            session_id: Session identifier to update
        """
        if session_id in self.active_sessions:
            self.session_timestamps[session_id] = time.time()
            logger.debug(f"Updated session timestamp: {session_id}")
    
    def remove_session(self, session_id: str) -> None:
        """
        Remove session from tracking and cleanup its data.
        
        Args:
            session_id: Session identifier to remove
        """
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
            
        if session_id in self.session_timestamps:
            del self.session_timestamps[session_id]
        
        # Cleanup session data
        self._cleanup_session_data(session_id)
        logger.info(f"Removed session: {session_id}")
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self.active_sessions)
    
    def get_session_age(self, session_id: str) -> Optional[float]:
        """
        Get session age in seconds.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session age in seconds or None if not found
        """
        if session_id in self.session_timestamps:
            return time.time() - self.session_timestamps[session_id]
        return None
    
    async def start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if not self.running:
            self.running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info(f"Started session cleanup task (interval: {self.cleanup_interval}s, TTL: {self.session_ttl}s)")
    
    async def stop_cleanup_task(self) -> None:
        """Stop the background cleanup task."""
        self.running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped session cleanup task")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                if self.running:
                    await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions based on TTL."""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, timestamp in self.session_timestamps.items():
            if current_time - timestamp > self.session_ttl:
                expired_sessions.append(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaning up {len(expired_sessions)} expired sessions")
            for session_id in expired_sessions:
                self.remove_session(session_id)
    
    async def _cleanup_oldest_sessions(self, immediate: bool = False) -> None:
        """Clean up oldest sessions when memory limit is reached."""
        if len(self.active_sessions) <= self.max_sessions and not immediate:
            return
        
        # Sort sessions by timestamp (oldest first)
        sorted_sessions = sorted(
            self.session_timestamps.items(),
            key=lambda x: x[1]
        )
        
        # Remove oldest sessions until we're under the limit
        sessions_to_remove = len(self.active_sessions) - self.max_sessions + 10  # Remove extra buffer
        sessions_removed = 0
        
        for session_id, _ in sorted_sessions:
            if sessions_removed >= sessions_to_remove:
                break
            
            self.remove_session(session_id)
            sessions_removed += 1
        
        if sessions_removed > 0:
            logger.info(f"Cleaned up {sessions_removed} oldest sessions to free memory")
    
    def _cleanup_session_data(self, session_id: str) -> None:
        """
        Clean up all data associated with a session.
        
        Args:
            session_id: Session identifier to cleanup
        """
        try:
            # Clear from output handler
            self.output_handler.clear_session_data(session_id)
            
            # Note: We don't delete persistent data files as they might be needed for audit
            # Only clear from memory structures
            
        except Exception as e:
            logger.error(f"Error cleaning up session data for {session_id}: {e}")
    
    async def cleanup_old_files(self, days_to_keep: int = 30) -> None:
        """
        Clean up old persistent files.
        
        Args:
            days_to_keep: Number of days to keep files
        """
        try:
            logger.info(f"Starting cleanup of files older than {days_to_keep} days")
            self.persistence.cleanup_old_data(days_to_keep)
            logger.info("File cleanup completed")
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get memory usage statistics."""
        return {
            "active_sessions": len(self.active_sessions),
            "max_sessions": self.max_sessions,
            "memory_usage_percent": int((len(self.active_sessions) / self.max_sessions) * 100),
            "tracked_timestamps": len(self.session_timestamps)
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None

def get_session_manager(**kwargs) -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(**kwargs)
    return _session_manager