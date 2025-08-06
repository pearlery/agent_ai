"""
Connection manager for NATS to prevent connection leaks.
"""
import logging
import asyncio
from typing import Dict, Optional
from .nats_handler import NATSHandler

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Singleton connection manager for NATS connections."""
    
    _instance: Optional['ConnectionManager'] = None
    _connections: Dict[str, NATSHandler] = {}
    _lock = asyncio.Lock()
    
    def __new__(cls) -> 'ConnectionManager':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_connection(self, connection_id: str, nats_config: Dict) -> NATSHandler:
        """
        Get or create a NATS connection.
        
        Args:
            connection_id: Unique identifier for the connection
            nats_config: NATS configuration dictionary
            
        Returns:
            NATSHandler instance
        """
        async with self._lock:
            if connection_id not in self._connections:
                logger.info(f"Creating new NATS connection: {connection_id}")
                handler = NATSHandler(nats_config)
                await handler.connect()
                self._connections[connection_id] = handler
            else:
                logger.debug(f"Reusing existing NATS connection: {connection_id}")
            
            return self._connections[connection_id]
    
    async def close_connection(self, connection_id: str) -> None:
        """
        Close a specific connection.
        
        Args:
            connection_id: Connection identifier to close
        """
        async with self._lock:
            if connection_id in self._connections:
                logger.info(f"Closing NATS connection: {connection_id}")
                await self._connections[connection_id].close()
                del self._connections[connection_id]
    
    async def close_all_connections(self) -> None:
        """Close all active connections."""
        async with self._lock:
            logger.info("Closing all NATS connections")
            for connection_id, handler in self._connections.items():
                try:
                    await handler.close()
                    logger.debug(f"Closed connection: {connection_id}")
                except Exception as e:
                    logger.error(f"Error closing connection {connection_id}: {e}")
            
            self._connections.clear()
    
    def get_active_connections(self) -> Dict[str, NATSHandler]:
        """Get all active connections."""
        return self._connections.copy()
    
    def is_connected(self, connection_id: str) -> bool:
        """Check if a specific connection is active."""
        return connection_id in self._connections


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None

def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager