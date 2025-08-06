"""
NATS JetStream handler for agent communication.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig, ConsumerConfig
from nats.js.errors import NotFoundError

logger = logging.getLogger(__name__)


class NATSHandler:
    """
    Handler for NATS JetStream operations including publishing and subscribing.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the NATS handler with configuration.
        
        Args:
            config: NATS configuration dictionary containing server_url, stream_name, and subjects
        """
        self.config = config
        self.nc = NATS()
        self.js = None
        self.stream_name = config.get('stream_name', 'AGENT_AI_PIPELINE')
        self.subjects = config.get('subjects', {})
        
    async def connect(self) -> None:
        """
        Connect to NATS server, get JetStream context, and ensure stream exists.
        """
        try:
            await self.nc.connect(servers=[self.config['server_url']])
            self.js = self.nc.jetstream()
            
            # Ensure stream exists
            await self._ensure_stream_exists()
            logger.info(f"Connected to NATS at {self.config['server_url']}")
            
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise
    
    async def _ensure_stream_exists(self) -> None:
        """
        Create the stream if it doesn't exist.
        """
        try:
            await self.js.stream_info(self.stream_name)
            logger.info(f"Stream '{self.stream_name}' already exists")
        except NotFoundError:
            # Stream doesn't exist, create it
            subjects = list(self.subjects.values())
            stream_config = StreamConfig(
                name=self.stream_name,
                subjects=subjects,
                retention="workqueue"
            )
            await self.js.add_stream(config=stream_config)
            logger.info(f"Created stream '{self.stream_name}' with subjects: {subjects}")
    
    async def publish(self, subject: str, payload: Dict[str, Any]) -> None:
        """
        Publish a JSON payload to a given subject.
        
        Args:
            subject: The subject to publish to
            payload: Dictionary payload to be JSON-encoded and published
        """
        if not self.js:
            raise RuntimeError("NATS not connected. Call connect() first.")
        
        try:
            message_data = json.dumps(payload).encode('utf-8')
            await self.js.publish(subject, message_data)
            logger.info(f"Published message to subject '{subject}'")
        except Exception as e:
            logger.error(f"Failed to publish to subject '{subject}': {e}")
            raise
    
    async def subscribe_pull(self, subject: str, durable_name: str):
        """
        Create and return a durable, pull-based subscription.
        
        Args:
            subject: The subject to subscribe to
            durable_name: Name for the durable consumer
            
        Returns:
            Pull subscription object
        """
        if not self.js:
            raise RuntimeError("NATS not connected. Call connect() first.")
        
        try:
            # Create or get existing consumer
            consumer_config = ConsumerConfig(
                durable_name=durable_name,
                ack_policy="explicit"
            )
            
            # Create pull subscription
            psub = await self.js.pull_subscribe(
                subject=subject,
                durable=durable_name,
                config=consumer_config
            )
            
            logger.info(f"Created pull subscription for subject '{subject}' with durable '{durable_name}'")
            return psub
            
        except Exception as e:
            logger.error(f"Failed to create subscription for subject '{subject}': {e}")
            raise
    
    async def close(self) -> None:
        """
        Close the NATS connection gracefully.
        """
        if self.nc:
            try:
                await self.nc.drain()
                logger.info("NATS connection closed")
            except Exception as e:
                logger.error(f"Error closing NATS connection: {e}")