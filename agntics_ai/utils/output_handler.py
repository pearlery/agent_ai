"""
Output handler for generating JSON output in the required format.
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

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
        
    def _initialize_output_structure(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize the output data structure."""
        return {
            "agent.overview.updated": [],
            "agent.tools.updated": [],
            "agent.recommendation.updated": [],
            "agent.checklist.updated": [],
            "agent.executive.updated": [],
            "agent.attack.updated": [],
            "agent.timeline.updated": []
        }
    
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
        overview_data = {
            "id": session_id,
            "data": {
                "description": description
            }
        }
        
        # Remove existing entry with same ID
        self.output_data["agent.overview.updated"] = [
            item for item in self.output_data["agent.overview.updated"] 
            if item["id"] != session_id
        ]
        
        # Add new entry
        self.output_data["agent.overview.updated"].append(overview_data)
        logger.info(f"Updated overview for session {session_id}")
    
    def update_tools_status(self, session_id: str, tools: List[Dict[str, str]]) -> None:
        """
        Update the tools status section.
        
        Args:
            session_id: Unique session identifier
            tools: List of tool status dictionaries with 'name' and 'status'
        """
        tools_data = {
            "id": session_id,
            "data": tools
        }
        
        # Remove existing entry with same ID
        self.output_data["agent.tools.updated"] = [
            item for item in self.output_data["agent.tools.updated"] 
            if item["id"] != session_id
        ]
        
        # Add new entry
        self.output_data["agent.tools.updated"].append(tools_data)
        logger.info(f"Updated tools status for session {session_id}")
    
    def update_recommendation(self, session_id: str, description: str, content: str) -> None:
        """
        Update the recommendation section.
        
        Args:
            session_id: Unique session identifier
            description: Recommendation description
            content: Full recommendation content
        """
        recommendation_data = {
            "id": session_id,
            "data": {
                "description": description,
                "content": content
            }
        }
        
        # Remove existing entry with same ID
        self.output_data["agent.recommendation.updated"] = [
            item for item in self.output_data["agent.recommendation.updated"] 
            if item["id"] != session_id
        ]
        
        # Add new entry
        self.output_data["agent.recommendation.updated"].append(recommendation_data)
        logger.info(f"Updated recommendation for session {session_id}")
    
    def update_checklist(self, session_id: str, title: str, content: str) -> None:
        """
        Update the checklist section.
        
        Args:
            session_id: Unique session identifier
            title: Checklist title
            content: Checklist content
        """
        checklist_data = {
            "id": session_id,
            "data": {
                "title": title,
                "content": content
            }
        }
        
        # Remove existing entry with same ID
        self.output_data["agent.checklist.updated"] = [
            item for item in self.output_data["agent.checklist.updated"] 
            if item["id"] != session_id
        ]
        
        # Add new entry
        self.output_data["agent.checklist.updated"].append(checklist_data)
        logger.info(f"Updated checklist for session {session_id}")
    
    def update_executive_summary(self, session_id: str, title: str, content: str) -> None:
        """
        Update the executive summary section.
        
        Args:
            session_id: Unique session identifier
            title: Executive summary title
            content: Executive summary content
        """
        executive_data = {
            "id": session_id,
            "data": {
                "title": title,
                "content": content
            }
        }
        
        # Remove existing entry with same ID
        self.output_data["agent.executive.updated"] = [
            item for item in self.output_data["agent.executive.updated"] 
            if item["id"] != session_id
        ]
        
        # Add new entry
        self.output_data["agent.executive.updated"].append(executive_data)
        logger.info(f"Updated executive summary for session {session_id}")
    
    def update_attack_mapping(self, session_id: str, tactics: List[Dict[str, Any]]) -> None:
        """
        Update the MITRE ATT&CK mapping section.
        
        Args:
            session_id: Unique session identifier
            tactics: List of tactic dictionaries with tacticID, tacticName, confidence
        """
        attack_data = {
            "id": session_id,
            "data": tactics
        }
        
        # Remove existing entry with same ID
        self.output_data["agent.attack.updated"] = [
            item for item in self.output_data["agent.attack.updated"] 
            if item["id"] != session_id
        ]
        
        # Add new entry
        self.output_data["agent.attack.updated"].append(attack_data)
        logger.info(f"Updated attack mapping for session {session_id}")
    
    def update_timeline(self, session_id: str, timeline_entries: List[Dict[str, str]]) -> None:
        """
        Update the timeline section.
        
        Args:
            session_id: Unique session identifier
            timeline_entries: List of timeline dictionaries with stage, status, errorMessage
        """
        timeline_data = {
            "id": session_id,
            "data": timeline_entries
        }
        
        # Remove existing entry with same ID
        self.output_data["agent.timeline.updated"] = [
            item for item in self.output_data["agent.timeline.updated"] 
            if item["id"] != session_id
        ]
        
        # Add new entry
        self.output_data["agent.timeline.updated"].append(timeline_data)
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
        # Find existing timeline for this session
        existing_timeline = None
        for item in self.output_data["agent.timeline.updated"]:
            if item["id"] == session_id:
                existing_timeline = item
                break
        
        # Create new timeline entry
        new_entry = {
            "stage": stage,
            "status": status,
            "errorMessage": error_message
        }
        
        if existing_timeline:
            # Update existing timeline
            existing_timeline["data"].append(new_entry)
        else:
            # Create new timeline
            timeline_data = {
                "id": session_id,
                "data": [new_entry]
            }
            self.output_data["agent.timeline.updated"].append(timeline_data)
        
        logger.info(f"Added timeline entry for session {session_id}: {stage} - {status}")
    
    def save_to_file(self) -> None:
        """Save the current output data to the JSON file."""
        try:
            with open(self.output_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Output saved to {self.output_file_path}")
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
    
    def get_output_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the current output data."""
        return self.output_data.copy()
    
    def clear_session_data(self, session_id: str) -> None:
        """
        Clear all data for a specific session.
        
        Args:
            session_id: Session ID to clear
        """
        for key in self.output_data:
            self.output_data[key] = [
                item for item in self.output_data[key] 
                if item.get("id") != session_id
            ]
        logger.info(f"Cleared data for session {session_id}")


# Global output handler instance
_output_handler = None

def get_output_handler(output_file_path: str = "output.json") -> OutputHandler:
    """Get the global output handler instance."""
    global _output_handler
    if _output_handler is None:
        _output_handler = OutputHandler(output_file_path)
        _output_handler.load_from_file()
    return _output_handler