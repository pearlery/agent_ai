"""
Control Agent - Orchestrates the entire Agent AI pipeline and manages workflow state.
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

from ..utils.nats_handler import NATSHandler
from ..utils.output_handler import get_output_handler
from ..utils.timeline_tracker import get_timeline_tracker, TimelineStage, TimelineStatus
from ..utils.persistence import get_default_persistence
from ..utils.tools_monitor import get_tools_monitor

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Workflow stages for the Control Agent."""
    RECEIVED_ALERT = 1
    TYPE_AGENT = 2
    ANALYZE_ROOT_CAUSE = 3
    TRIAGE_STATUS = 4
    ACTION_TAKEN = 5
    TOOL_STATUS = 6
    RECOMMENDATION = 7


class ControlAgent:
    """
    Control Agent that orchestrates the entire Agent AI workflow.
    """
    
    def __init__(self, nats_handler: Optional[NATSHandler], output_file: str = "output.json"):
        """
        Initialize the Control Agent.
        
        Args:
            nats_handler: Connected NATS handler instance (can be None for test mode)
            output_file: Path to output JSON file
        """
        self.nats_handler = nats_handler
        self.output_file = output_file
        self.output_handler = get_output_handler(output_file)
        self.persistence = get_default_persistence()
        self.tools_monitor = get_tools_monitor()
        self.running = False
        
        # Create database directory
        self.db_dir = Path("database")
        self.db_dir.mkdir(exist_ok=True)
    
    async def start_flow(self, alert_data: Dict[str, Any], session_id: Optional[str] = None) -> str:
        """
        Start the processing flow for a new alert.
        
        Args:
            alert_data: Alert data to process
            session_id: Optional session ID, will generate one if not provided
            
        Returns:
            Status message
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = self.output_handler.generate_session_id()
            
            # Initialize timeline
            timeline = get_timeline_tracker(session_id, self.output_file)
            timeline.mark_stage_success(TimelineStage.RECEIVED_ALERT)
            
            # Save alert data
            alert_id = alert_data.get('alert_id', f"alert_{session_id}")
            self.persistence.save_alert(alert_id, alert_data)
            
            # Record start log
            start_log_entry = {
                "session_id": session_id,
                "alert_id": alert_id,
                "timestamp": datetime.now().isoformat(),
                "alert_data": alert_data
            }
            await self._append_to_log("start_log.json", start_log_entry)
            
            # Initialize output sections
            self.output_handler.update_overview(session_id, "Alert received and processing started")
            
            # Update tools status
            await self.tools_monitor.update_output(session_id, self.output_file)
            
            # Publish timeline update
            await self._publish_timeline_update(session_id, WorkflowStage.RECEIVED_ALERT)
            
            logger.info(f"Started flow for session {session_id}")
            return "success"
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON provided to start_flow")
            return "error: invalid JSON"
        except Exception as e:
            logger.error(f"Error starting flow: {e}")
            return f"error: {str(e)}"
    
    async def finished_type(self, data: Dict[str, Any], session_id: str) -> str:
        """
        Handle completion of type classification stage.
        
        Args:
            data: Type classification results
            session_id: Session identifier
            
        Returns:
            Status message
        """
        try:
            # Update timeline
            timeline = get_timeline_tracker(session_id, self.output_file)
            timeline.mark_stage_success(TimelineStage.TYPE_AGENT)
            
            # Record type log
            type_log_entry = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "type_data": data
            }
            await self._append_to_log("type_log.json", type_log_entry)
            
            # Update output with analysis results
            if 'technique_name' in data:
                overview_desc = f"Analysis completed: {data['technique_name']} technique identified"
                self.output_handler.update_overview(session_id, overview_desc)
                self.output_handler.save_to_file()
            
            # Publish timeline update (jump to stage 5 as per original logic)
            await self._publish_timeline_update(session_id, WorkflowStage.ACTION_TAKEN)
            
            logger.info(f"Finished type stage for session {session_id}")
            return "success"
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON - {str(e)}"
            await self._handle_error(session_id, WorkflowStage.TYPE_AGENT, error_msg)
            return f"error: {error_msg}"
        except Exception as e:
            error_msg = str(e)
            await self._handle_error(session_id, WorkflowStage.TYPE_AGENT, error_msg)
            return f"error: {error_msg}"
    
    async def finished_flow(self, data: Dict[str, Any], session_id: str) -> str:
        """
        Handle completion of the entire workflow.
        
        Args:
            data: Final workflow results
            session_id: Session identifier
            
        Returns:
            Status message
        """
        try:
            # Check for upstream errors
            if data.get("status") == "error":
                error_msg = str(data.get("message", "Unknown error from agent"))
                await self._handle_error(session_id, WorkflowStage.RECOMMENDATION, error_msg)
                return f"error: {error_msg}"
            
            # Update timeline for successful completion
            timeline = get_timeline_tracker(session_id, self.output_file)
            timeline.mark_stage_success(TimelineStage.RECOMMENDATION)
            timeline.complete_processing(True, "Workflow completed successfully")
            
            # Record final results
            context_log_entry = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "final_data": data
            }
            await self._append_to_log("context_log.json", context_log_entry)
            
            # Save complete session data
            session_data = {
                "session_id": session_id,
                "completed_at": datetime.now().isoformat(),
                "final_results": data,
                "status": "completed"
            }
            self.persistence.save_session_data(session_id, session_data)
            
            # Update final output sections
            await self._finalize_output(session_id, data)
            
            # Publish final timeline update
            await self._publish_timeline_update(session_id, WorkflowStage.RECOMMENDATION)
            
            logger.info(f"Successfully finished flow for session {session_id}")
            return "success"
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON - {str(e)}"
            await self._handle_error(session_id, WorkflowStage.RECOMMENDATION, error_msg)
            return f"error: {error_msg}"
        except Exception as e:
            error_msg = str(e)
            await self._handle_error(session_id, WorkflowStage.RECOMMENDATION, error_msg)
            return f"error: {error_msg}"
    
    async def _handle_error(self, session_id: str, stage: WorkflowStage, error_msg: str) -> None:
        """
        Handle errors during workflow processing.
        
        Args:
            session_id: Session identifier
            stage: Stage where error occurred
            error_msg: Error message
        """
        try:
            # Update timeline with error
            timeline = get_timeline_tracker(session_id, self.output_file)
            
            # Convert WorkflowStage to TimelineStage
            timeline_stage_map = {
                WorkflowStage.RECEIVED_ALERT: TimelineStage.RECEIVED_ALERT,
                WorkflowStage.TYPE_AGENT: TimelineStage.TYPE_AGENT,
                WorkflowStage.ANALYZE_ROOT_CAUSE: TimelineStage.ANALYZE_ROOT_CAUSE,
                WorkflowStage.TRIAGE_STATUS: TimelineStage.TRIAGE_STATUS,
                WorkflowStage.ACTION_TAKEN: TimelineStage.ACTION_TAKEN,
                WorkflowStage.TOOL_STATUS: TimelineStage.TOOL_STATUS,
                WorkflowStage.RECOMMENDATION: TimelineStage.RECOMMENDATION
            }
            
            timeline_stage = timeline_stage_map.get(stage, TimelineStage.RECOMMENDATION)
            timeline.mark_stage_error(timeline_stage, error_msg)
            timeline.complete_processing(False, f"Processing failed at {stage.name}: {error_msg}")
            
            # Update output with error information
            executive_title = f"Processing Error - {stage.name}"
            executive_content = f"An error occurred during {stage.name}: {error_msg}"
            self.output_handler.update_executive_summary(session_id, executive_title, executive_content)
            self.output_handler.save_to_file()
            
            # Publish error timeline
            await self._publish_timeline_update(session_id, stage, error_msg)
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    async def _publish_timeline_update(self, session_id: str, stage: WorkflowStage, error: str = "") -> None:
        """
        Publish timeline update to NATS.
        
        Args:
            session_id: Session identifier
            stage: Current workflow stage
            error: Error message if any
        """
        try:
            if self.nats_handler is None:
                logger.debug(f"NATS not available, skipping timeline update for session {session_id}")
                return
                
            timeline_payload = self._build_timeline_payload(stage.value, session_id, error)
            
            # Publish to websocket subject for real-time updates
            websoc_subject = "agentAI.websoc"
            await self.nats_handler.publish(websoc_subject, timeline_payload)
            
            logger.debug(f"Published timeline update for session {session_id}, stage {stage.name}")
            
        except Exception as e:
            logger.error(f"Failed to publish timeline update: {e}")
    
    def _build_timeline_payload(self, case: int, session_id: str, error: str = "") -> Dict[str, Any]:
        """
        Build timeline payload similar to original Control Agent.
        
        Args:
            case: Stage number (1-7)
            session_id: Session identifier
            error: Error message if any
            
        Returns:
            Timeline payload dictionary
        """
        if case == 0:
            return {
                "alert_id": session_id,
                "agent.timeline.updated": {
                    "data": []
                }
            }
        
        stage_names = {
            1: 'Received Alert',
            2: 'Type Agent', 
            3: 'Analyze Root Cause',
            4: 'Triage Status',
            5: 'Action Taken',
            6: 'Tool Status',
            7: 'Recommendation'
        }
        
        timeline_data = []
        
        for i in range(1, case + 1):
            stage = stage_names.get(i)
            if not stage:
                continue
            
            if i == case and error:
                timeline_data.append({
                    "stage": stage,
                    "status": "error",
                    "errorMessage": error
                })
            else:
                timeline_data.append({
                    "stage": stage,
                    "status": "success",
                    "errorMessage": ""
                })
        
        return {
            "agent.timeline.updated": {
                "alert_id": session_id,
                "data": timeline_data
            }
        }
    
    async def _append_to_log(self, filename: str, entry: Dict[str, Any]) -> None:
        """
        Append entry to log file.
        
        Args:
            filename: Log filename
            entry: Entry to append
        """
        try:
            log_file = self.db_dir / filename
            
            # Load existing data or create empty list
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Append new entry
            data.append(entry)
            
            # Save back to file
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to append to log {filename}: {e}")
    
    async def _finalize_output(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Finalize all output sections with completed workflow data.
        
        Args:
            session_id: Session identifier
            data: Final workflow data
        """
        try:
            # Update executive summary
            executive_title = "Incident Analysis Complete"
            executive_content = "All processing stages completed successfully. Review recommendations and take appropriate action."
            self.output_handler.update_executive_summary(session_id, executive_title, executive_content)
            
            # Update final recommendation if available
            if 'report' in data or 'recommendation' in data:
                report_content = data.get('report', data.get('recommendation', 'Analysis completed'))
                self.output_handler.update_recommendation(
                    session_id,
                    "Final incident response recommendations",
                    report_content
                )
            
            # Save all updates
            self.output_handler.save_to_file()
            
        except Exception as e:
            logger.error(f"Failed to finalize output: {e}")
    
    def stop(self) -> None:
        """Stop the control agent."""
        self.running = False
        logger.info("Control Agent stop requested")