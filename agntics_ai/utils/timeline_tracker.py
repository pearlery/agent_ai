"""
Timeline tracking system for monitoring agent processing stages.
"""
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from .output_handler import get_output_handler

logger = logging.getLogger(__name__)


class TimelineStatus(Enum):
    """Timeline entry status options."""
    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


class TimelineStage(Enum):
    """Standard timeline stages for the agent pipeline."""
    RECEIVED_ALERT = "Received Alert"
    INPUT_AGENT = "Input Agent"
    ANALYSIS_AGENT = "Analysis Agent"
    RECOMMENDATION_AGENT = "Recommendation Agent"
    OUTPUT_GENERATED = "Output Generated"
    PROCESS_COMPLETE = "Process Complete"


class TimelineTracker:
    """Tracks the timeline of processing stages for each session."""
    
    def __init__(self, session_id: str, output_file_path: str = "output.json"):
        """
        Initialize the timeline tracker.
        
        Args:
            session_id: Unique session identifier
            output_file_path: Path to the output JSON file
        """
        self.session_id = session_id
        self.output_handler = get_output_handler(output_file_path)
        self.start_time = datetime.now()
        
        # Initialize timeline with first entry
        self.add_entry(TimelineStage.RECEIVED_ALERT, TimelineStatus.SUCCESS)
    
    def add_entry(self, stage: TimelineStage, status: TimelineStatus, error_message: str = "") -> None:
        """
        Add a new entry to the timeline.
        
        Args:
            stage: The processing stage
            status: Status of the stage
            error_message: Error message if status is error
        """
        try:
            stage_name = stage.value if isinstance(stage, TimelineStage) else str(stage)
            status_value = status.value if isinstance(status, TimelineStatus) else str(status)
            
            self.output_handler.add_timeline_entry(
                session_id=self.session_id,
                stage=stage_name,
                status=status_value,
                error_message=error_message
            )
            
            # Save to file immediately
            self.output_handler.save_to_file()
            
            logger.info(f"Timeline updated: {stage_name} - {status_value}")
            
        except Exception as e:
            logger.error(f"Failed to add timeline entry: {e}")
    
    def mark_stage_in_progress(self, stage: TimelineStage) -> None:
        """Mark a stage as in progress."""
        self.add_entry(stage, TimelineStatus.IN_PROGRESS)
    
    def mark_stage_success(self, stage: TimelineStage) -> None:
        """Mark a stage as successfully completed."""
        self.add_entry(stage, TimelineStatus.SUCCESS)
    
    def mark_stage_error(self, stage: TimelineStage, error_message: str) -> None:
        """Mark a stage as failed with error message."""
        self.add_entry(stage, TimelineStatus.ERROR, error_message)
    
    def get_current_timeline(self) -> List[Dict[str, str]]:
        """Get the current timeline for this session."""
        output_data = self.output_handler.get_output_data()
        
        for item in output_data.get("agent.timeline.updated", []):
            if item.get("id") == self.session_id:
                return item.get("data", [])
        
        return []
    
    def get_processing_duration(self) -> float:
        """Get the total processing duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def is_stage_completed(self, stage: TimelineStage) -> bool:
        """Check if a specific stage has been completed successfully."""
        timeline = self.get_current_timeline()
        stage_name = stage.value if isinstance(stage, TimelineStage) else str(stage)
        
        for entry in timeline:
            if entry.get("stage") == stage_name and entry.get("status") == TimelineStatus.SUCCESS.value:
                return True
        
        return False
    
    def has_errors(self) -> bool:
        """Check if there are any error entries in the timeline."""
        timeline = self.get_current_timeline()
        
        for entry in timeline:
            if entry.get("status") == TimelineStatus.ERROR.value:
                return True
        
        return False
    
    def get_error_stages(self) -> List[str]:
        """Get list of stages that have errors."""
        timeline = self.get_current_timeline()
        error_stages = []
        
        for entry in timeline:
            if entry.get("status") == TimelineStatus.ERROR.value:
                error_stages.append(entry.get("stage", "Unknown"))
        
        return error_stages
    
    def complete_processing(self, success: bool = True, final_message: str = "") -> None:
        """
        Mark the entire processing as complete.
        
        Args:
            success: Whether processing completed successfully
            final_message: Final message or error description
        """
        if success:
            self.add_entry(TimelineStage.PROCESS_COMPLETE, TimelineStatus.SUCCESS, final_message)
        else:
            self.add_entry(TimelineStage.PROCESS_COMPLETE, TimelineStatus.ERROR, final_message)
        
        duration = self.get_processing_duration()
        logger.info(f"Processing completed for session {self.session_id} in {duration:.2f} seconds")


class TimelineManager:
    """Global manager for timeline trackers."""
    
    def __init__(self):
        self._trackers: Dict[str, TimelineTracker] = {}
    
    def get_tracker(self, session_id: str, output_file_path: str = "output.json") -> TimelineTracker:
        """
        Get or create a timeline tracker for a session.
        
        Args:
            session_id: Unique session identifier
            output_file_path: Path to the output JSON file
            
        Returns:
            TimelineTracker instance
        """
        if session_id not in self._trackers:
            self._trackers[session_id] = TimelineTracker(session_id, output_file_path)
        
        return self._trackers[session_id]
    
    def remove_tracker(self, session_id: str) -> None:
        """Remove a timeline tracker."""
        if session_id in self._trackers:
            del self._trackers[session_id]
    
    def get_all_active_sessions(self) -> List[str]:
        """Get list of all active session IDs."""
        return list(self._trackers.keys())


# Global timeline manager instance
_timeline_manager = TimelineManager()

def get_timeline_tracker(session_id: str, output_file_path: str = "output.json") -> TimelineTracker:
    """Get a timeline tracker for the given session."""
    return _timeline_manager.get_tracker(session_id, output_file_path)