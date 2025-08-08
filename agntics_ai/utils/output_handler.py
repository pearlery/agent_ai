"""
Output handler for generating JSON output in the required format.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from .graphql_publisher import get_graphql_publisher

logger = logging.getLogger(__name__)


class OutputHandler:
    """Handles the generation and management of JSON output in the required format."""
    
    def __init__(self, output_file_path: str = "output.json"):
        """
        Initialize the output handler.
        
        Args:
            output_file_path: Path to the output JSON file
        """
        self.output_file_path = Path(output_file_path)
        self.output_data = self._initialize_output_structure()
        
    def _initialize_output_structure(self) -> Dict[str, Any]:
        """Initialize the output data structure."""
        return {}
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID for tracking."""
        return str(uuid.uuid4())
    
    def update_overview(self, session_id: str, description: str) -> None:
        """
        Update the overview section.
        
        Args:
            session_id: Unique session identifier
            description: Overview description
        """
        self.output_data["agentAI.overview.updated"] = {
            "id": session_id,
            "data": {
                "description": description
            }
        }
        logger.info(f"Updated overview for session {session_id}")
        
        # ส่งไป GraphQL ผ่าน NATS
        self._publish_to_graphql("overview", session_id, description)
    
    def update_tools_status(self, session_id: str, tools: List[Dict[str, str]]) -> None:
        """
        Update the tools status section.
        
        Args:
            session_id: Unique session identifier
            tools: List of tool status dictionaries with 'name' and 'status'
        """
        self.output_data["agentAI.tools.updated"] = {
            "id": session_id,
            "data": tools
        }
        logger.info(f"Updated tools status for session {session_id}")
    
    def update_recommendation(self, session_id: str, description: str, content: str) -> None:
        """
        Update the recommendation section.
        
        Args:
            session_id: Unique session identifier
            description: Recommendation description
            content: Full recommendation content
        """
        recommendation_data = [{
            "description": description,
            "content": content
        }]
        self.output_data["agentAI.recommendation.updated"] = {
            "id": session_id,
            "data": recommendation_data
        }
        logger.info(f"Updated recommendation for session {session_id}")
        
        # ส่งไป GraphQL ผ่าน NATS
        self._publish_to_graphql("recommendation", session_id, recommendation_data)
    
    def update_checklist(self, session_id: str, title: str, content: str) -> None:
        """
        Update the checklist section.
        
        Args:
            session_id: Unique session identifier
            title: Checklist title
            content: Checklist content
        """
        self.output_data["agentAI.checklist.updated"] = {
            "id": session_id,
            "data": [
                {
                    "title": title,
                    "content": content
                }
            ]
        }
        logger.info(f"Updated checklist for session {session_id}")
    
    def update_executive_summary(self, session_id: str, title: str, content: str) -> None:
        """
        Update the executive summary section.
        
        Args:
            session_id: Unique session identifier
            title: Executive summary title
            content: Executive summary content
        """
        self.output_data["agentAI.executive.updated"] = {
            "id": session_id,
            "data": [
                {
                    "title": title,
                    "content": content
                }
            ]
        }
        logger.info(f"Updated executive summary for session {session_id}")
        
        # ส่งไป GraphQL ผ่าน NATS
        self._publish_to_graphql("executive", session_id, {"title": title, "content": content})
    
    def update_attack_mapping(self, session_id: str, tactics: List[Dict[str, Any]]) -> None:
        """
        Update the MITRE ATT&CK mapping section.
        
        Args:
            session_id: Unique session identifier
            tactics: List of tactic dictionaries with tacticID, tacticName, confidence
        """
        self.output_data["agentAI.attack.updated"] = {
            "id": session_id,
            "data": tactics
        }
        logger.info(f"Updated attack mapping for session {session_id}")
        
        # ส่งไป GraphQL ผ่าน NATS
        self._publish_to_graphql("attack", session_id, tactics)
    
    def update_timeline(self, session_id: str, timeline_entries: List[Dict[str, str]]) -> None:
        """
        Update the timeline section.
        
        Args:
            session_id: Unique session identifier
            timeline_entries: List of timeline dictionaries with stage, status, errorMessage
        """
        self.output_data["agentAI.timeline.updated"] = {
            "id": session_id,
            "data": timeline_entries
        }
        logger.info(f"Updated timeline for session {session_id}")
    
    def add_timeline_entry(self, session_id: str, stage: str, status: str, error_message: str = "") -> None:
        """
        Add a single entry to the timeline.
        
        Args:
            session_id: Unique session identifier
            stage: Timeline stage name
            status: Status (success, error, in_progress)
            error_message: Error message if status is error
        """
        # Create new timeline entry
        new_entry = {
            "stage": stage,
            "status": status,
            "errorMessage": error_message
        }
        
        # Get existing timeline or create new one
        if "agentAI.timeline.updated" not in self.output_data:
            self.output_data["agentAI.timeline.updated"] = {
                "id": session_id,
                "data": []
            }
        
        # Add new entry to timeline
        self.output_data["agentAI.timeline.updated"]["data"].append(new_entry)
        
        logger.info(f"Added timeline entry for session {session_id}: {stage} - {status}")
        
        # ส่งไป GraphQL ผ่าน NATS
        self._publish_to_graphql("timeline", session_id, self.output_data["agentAI.timeline.updated"]["data"])
    
    def save_to_file(self) -> None:
        """Save the current output data to the JSON file."""
        try:
            with open(self.output_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Output saved to {self.output_file_path}")
            
            # ส่ง full output ไป GraphQL ผ่าน NATS
            self._publish_to_graphql("full_output", "", self.output_data)
            
        except Exception as e:
            logger.error(f"Failed to save output to file: {e}")
            raise
    
    def load_from_file(self) -> None:
        """Load existing output data from the JSON file if it exists."""
        try:
            if self.output_file_path.exists():
                with open(self.output_file_path, 'r', encoding='utf-8') as f:
                    self.output_data = json.load(f)
                logger.info(f"Output loaded from {self.output_file_path}")
            else:
                logger.info("No existing output file found, using empty structure")
        except Exception as e:
            logger.error(f"Failed to load output from file: {e}")
            # Continue with empty structure if loading fails
            self.output_data = self._initialize_output_structure()
    
    def get_output_data(self) -> Dict[str, Any]:
        """Get the current output data."""
        return self.output_data.copy()
    
    def clear_session_data(self, session_id: str) -> None:
        """
        Clear all data for a specific session.
        
        Args:
            session_id: Session ID to clear
        """
        # Clear all sections that match the session_id
        keys_to_remove = []
        for key in self.output_data:
            if isinstance(self.output_data[key], dict) and self.output_data[key].get("id") == session_id:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.output_data[key]
        
        logger.info(f"Cleared data for session {session_id}")
    
    def _publish_to_graphql(self, update_type: str, session_id: str, data: Any) -> None:
        """
        ส่ง update ไป GraphQL ผ่าน NATS
        
        Args:
            update_type: ประเภทของการอัพเดท (overview, attack, recommendation, etc.)
            session_id: Session ID
            data: ข้อมูลที่จะส่ง
        """
        try:
            publisher = get_graphql_publisher()
            if publisher is None:
                logger.debug("GraphQL publisher not initialized, skipping publish")
                return
            
            # Run async publish in background
            if update_type == "overview":
                asyncio.create_task(publisher.publish_overview_update(session_id, data))
            elif update_type == "attack":
                asyncio.create_task(publisher.publish_attack_update(session_id, data))
            elif update_type == "recommendation":
                asyncio.create_task(publisher.publish_recommendation_update(session_id, data))
            elif update_type == "timeline":
                asyncio.create_task(publisher.publish_timeline_update(session_id, data))
            elif update_type == "executive":
                title = data.get("title", "")
                content = data.get("content", "")
                asyncio.create_task(publisher.publish_executive_summary_update(session_id, title, content))
            elif update_type == "full_output":
                asyncio.create_task(publisher.publish_full_output(self.output_data))
                
            logger.debug(f"Queued GraphQL publish for {update_type}")
            
        except Exception as e:
            logger.error(f"Failed to publish to GraphQL: {e}")


# Global output handler instance
_output_handler = None

def get_output_handler(output_file_path: str = "output.json") -> OutputHandler:
    """Get the global output handler instance."""
    global _output_handler
    if _output_handler is None:
        _output_handler = OutputHandler(output_file_path)
        _output_handler.load_from_file()
    return _output_handler