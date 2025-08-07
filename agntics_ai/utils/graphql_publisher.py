"""
GraphQL Output Publisher - ส่ง output ไป GraphQL mutation ผ่าน NATS
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .nats_handler import NATSHandler

logger = logging.getLogger(__name__)


class GraphQLPublisher:
    """Publisher สำหรับส่ง output data ไป GraphQL mutation ผ่าน NATS"""
    
    def __init__(self, nats_handler: Optional[NATSHandler], graphql_topic: str = "agentAI.graphql.mutation"):
        """
        Initialize GraphQL Publisher
        
        Args:
            nats_handler: NATS handler instance
            graphql_topic: NATS topic สำหรับส่งไป GraphQL
        """
        self.nats_handler = nats_handler
        self.graphql_topic = graphql_topic
        
    async def publish_overview_update(self, session_id: str, description: str) -> None:
        """ส่ง overview update ไป GraphQL"""
        mutation_data = {
            "mutation_type": "updateOverview",
            "variables": {
                "sessionId": session_id,
                "description": description,
                "timestamp": datetime.now().isoformat()
            },
            "data": {
                "id": session_id,
                "description": description
            }
        }
        await self._publish_mutation(mutation_data)
    
    async def publish_attack_update(self, session_id: str, attack_data: list) -> None:
        """ส่ง attack analysis update ไป GraphQL"""
        mutation_data = {
            "mutation_type": "updateAttackAnalysis", 
            "variables": {
                "sessionId": session_id,
                "attackData": attack_data,
                "timestamp": datetime.now().isoformat()
            },
            "data": {
                "id": session_id,
                "attack_techniques": attack_data
            }
        }
        await self._publish_mutation(mutation_data)
    
    async def publish_recommendation_update(self, session_id: str, recommendations: list) -> None:
        """ส่ง recommendation update ไป GraphQL"""
        mutation_data = {
            "mutation_type": "updateRecommendations",
            "variables": {
                "sessionId": session_id,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            },
            "data": {
                "id": session_id,
                "recommendations": recommendations
            }
        }
        await self._publish_mutation(mutation_data)
    
    async def publish_timeline_update(self, session_id: str, timeline_data: list) -> None:
        """ส่ง timeline update ไป GraphQL"""
        mutation_data = {
            "mutation_type": "updateTimeline",
            "variables": {
                "sessionId": session_id,
                "timelineData": timeline_data,
                "timestamp": datetime.now().isoformat()
            },
            "data": {
                "alert_id": session_id,
                "timeline": timeline_data
            }
        }
        await self._publish_mutation(mutation_data)
    
    async def publish_executive_summary_update(self, session_id: str, title: str, content: str) -> None:
        """ส่ง executive summary update ไป GraphQL"""
        mutation_data = {
            "mutation_type": "updateExecutiveSummary",
            "variables": {
                "sessionId": session_id,
                "title": title,
                "content": content,
                "timestamp": datetime.now().isoformat()
            },
            "data": {
                "id": session_id,
                "title": title,
                "content": content
            }
        }
        await self._publish_mutation(mutation_data)
    
    async def publish_full_output(self, output_data: Dict[str, Any]) -> None:
        """ส่ง output ทั้งหมดไป GraphQL"""
        mutation_data = {
            "mutation_type": "updateFullOutput",
            "variables": {
                "outputData": output_data,
                "timestamp": datetime.now().isoformat()
            },
            "data": output_data
        }
        await self._publish_mutation(mutation_data)
    
    async def _publish_mutation(self, mutation_data: Dict[str, Any]) -> None:
        """
        ส่ง mutation data ไป NATS
        
        Args:
            mutation_data: Data สำหรับ GraphQL mutation
        """
        try:
            if self.nats_handler is None:
                logger.debug("NATS not available, skipping GraphQL publish")
                return
            
            # เพิ่ม metadata
            message = {
                "timestamp": datetime.now().isoformat(),
                "source": "agent_ai_system",
                "version": "2.0",
                **mutation_data
            }
            
            # Publish ไป NATS
            await self.nats_handler.publish(
                subject=self.graphql_topic,
                payload=message
            )
            
            logger.info(f"Published GraphQL mutation: {mutation_data['mutation_type']}")
            
        except Exception as e:
            logger.error(f"Failed to publish GraphQL mutation: {e}")
    
    async def publish_session_created(self, session_id: str, alert_data: Dict[str, Any]) -> None:
        """ส่งข้อมูลการสร้าง session ใหม่"""
        mutation_data = {
            "mutation_type": "createSession",
            "variables": {
                "sessionId": session_id,
                "alertData": alert_data,
                "timestamp": datetime.now().isoformat(),
                "status": "started"
            },
            "data": {
                "id": session_id,
                "alert_data": alert_data,
                "created_at": datetime.now().isoformat(),
                "status": "processing"
            }
        }
        await self._publish_mutation(mutation_data)
    
    async def publish_session_completed(self, session_id: str, final_status: str = "completed") -> None:
        """ส่งข้อมูลการเสร็จสิ้น session"""
        mutation_data = {
            "mutation_type": "completeSession",
            "variables": {
                "sessionId": session_id,
                "status": final_status,
                "timestamp": datetime.now().isoformat()
            },
            "data": {
                "id": session_id,
                "status": final_status,
                "completed_at": datetime.now().isoformat()
            }
        }
        await self._publish_mutation(mutation_data)


# Global instance
_graphql_publisher: Optional[GraphQLPublisher] = None

def init_graphql_publisher(nats_handler: Optional[NATSHandler], graphql_topic: str = "agentAI.graphql.mutation") -> GraphQLPublisher:
    """Initialize global GraphQL publisher"""
    global _graphql_publisher
    _graphql_publisher = GraphQLPublisher(nats_handler, graphql_topic)
    return _graphql_publisher

def get_graphql_publisher() -> Optional[GraphQLPublisher]:
    """Get global GraphQL publisher instance"""
    return _graphql_publisher