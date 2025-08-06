"""
Recommendation Agent - Consumes analysis results and generates actionable incident reports.
"""
import asyncio
import json
import logging
from typing import Dict, Any
from ..utils.nats_handler import NATSHandler
from ..utils.llm_handler_ollama import get_llm_completion, create_recommendation_prompt
from ..utils.output_handler import get_output_handler
from ..utils.timeline_tracker import get_timeline_tracker, TimelineStage, TimelineStatus
from ..utils.tools_monitor import get_tools_monitor
from ..utils.persistence import get_default_persistence

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """
    Recommendation Agent that processes MITRE analysis results and generates incident reports.
    """
    
    def __init__(self, nats_handler: NATSHandler, llm_config: Dict[str, Any], output_file: str = "output.json"):
        """
        Initialize the Recommendation Agent.
        
        Args:
            nats_handler: Connected NATS handler instance
            llm_config: LLM configuration dictionary
            output_file: Path to output JSON file
        """
        self.nats_handler = nats_handler
        self.llm_config = llm_config
        self.running = False
        self.output_file = output_file
        self.output_handler = get_output_handler(output_file)
        self.tools_monitor = get_tools_monitor()
        self.persistence = get_default_persistence()
    
    async def run(self) -> None:
        """
        Main loop for the Recommendation Agent.
        Subscribes to analysis subject, generates reports, and publishes final output.
        """
        logger.info("Starting Recommendation Agent...")
        
        try:
            # Create pull subscription to analysis subject
            psub = await self.nats_handler.subscribe_pull(
                subject=self.nats_handler.subjects['analysis'],
                durable_name='recommendation_agent'
            )
            
            self.running = True
            logger.info("Recommendation Agent subscribed and running...")
            
            # Main processing loop
            while self.running:
                try:
                    # Fetch messages from the subscription
                    msgs = await psub.fetch(batch=1, timeout=5.0)
                    
                    for msg in msgs:
                        try:
                            # Decode the message payload
                            payload = json.loads(msg.data.decode('utf-8'))
                            alert_id = payload.get('alert_id', 'unknown')
                            session_id = payload.get('session_id', alert_id)
                            logger.info(f"Generating recommendation for: {alert_id}")
                            
                            # Initialize timeline tracker
                            timeline = get_timeline_tracker(session_id, self.output_file)
                            timeline.mark_stage_in_progress(TimelineStage.RECOMMENDATION_AGENT)
                            
                            # Update tools status
                            await self.tools_monitor.update_output(session_id, self.output_file)
                            
                            # Generate incident report
                            report = await self._generate_report(payload)
                            
                            # Save report data
                            self.persistence.save_report(session_id, {
                                'markdown_report': report,
                                'analysis_data': payload.get('mitre_analysis', {}),
                                'alert_id': alert_id
                            })
                            
                            # Update output with recommendations and other sections
                            await self._update_output_sections(session_id, payload, report)
                            
                            # Create final output payload
                            final_payload = {
                                "alert_id": alert_id,
                                "session_id": session_id,
                                "original_alert": payload.get('original_payload', {}),
                                "raw_log_data": payload.get('raw_log_data', {}),
                                "mitre_analysis": payload.get('mitre_analysis', {}),
                                "incident_report": report,
                                "source": "recommendation_agent",
                                "processing_timestamp": asyncio.get_event_loop().time()
                            }
                            
                            # Publish to output subject
                            await self.nats_handler.publish(
                                subject=self.nats_handler.subjects['output'],
                                payload=final_payload
                            )
                            
                            # Mark timeline as successful and complete
                            timeline.mark_stage_success(TimelineStage.RECOMMENDATION_AGENT)
                            timeline.mark_stage_success(TimelineStage.OUTPUT_GENERATED)
                            timeline.complete_processing(True, "All processing stages completed successfully")
                            
                            # Acknowledge the message
                            await msg.ack()
                            logger.info(f"Successfully generated and published report for: {alert_id}")
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode message JSON: {e}")
                            await msg.ack()  # Acknowledge to prevent redelivery
                        except Exception as e:
                            logger.error(f"Failed to process message: {e}")
                            
                            # Mark timeline as error if we have session info
                            try:
                                payload = json.loads(msg.data.decode('utf-8'))
                                session_id = payload.get('session_id', payload.get('alert_id', 'unknown'))
                                timeline = get_timeline_tracker(session_id, self.output_file)
                                timeline.mark_stage_error(TimelineStage.RECOMMENDATION_AGENT, str(e))
                                timeline.complete_processing(False, f"Processing failed: {str(e)}")
                            except:
                                pass
                            
                            # Don't acknowledge - message will be redelivered
                
                except asyncio.TimeoutError:
                    # No messages available, continue polling
                    continue
                except Exception as e:
                    logger.error(f"Error in Recommendation Agent main loop: {e}")
                    await asyncio.sleep(1)  # Brief pause before retrying
        
        except Exception as e:
            logger.error(f"Recommendation Agent failed to start: {e}")
            raise
    
    async def _generate_report(self, analysis_payload: Dict[str, Any]) -> str:
        """
        Generate incident report using LLM based on analysis results.
        
        Args:
            analysis_payload: Complete analysis payload from analysis agent
            
        Returns:
            str: Generated Markdown incident report
        """
        try:
            # Extract components for report generation
            raw_log = analysis_payload.get('raw_log_data', {})
            mitre_analysis = analysis_payload.get('mitre_analysis', {})
            
            # Prepare structured data for report generation
            report_data = {
                "alert_id": analysis_payload.get('alert_id'),
                "timestamp": raw_log.get('timestamp'),
                "hostname": raw_log.get('hostname'),
                "source_ip": raw_log.get('source_ip'),
                "destination_ip": raw_log.get('destination_ip'),
                "process_name": raw_log.get('process_name'),
                "command_line": raw_log.get('command_line'),
                "user": raw_log.get('user'),
                "severity": raw_log.get('severity'),
                "log_source": raw_log.get('log_source'),
                "technique_id": mitre_analysis.get('technique_id'),
                "technique_name": mitre_analysis.get('technique_name'),
                "tactic": mitre_analysis.get('tactic'),
                "confidence_score": mitre_analysis.get('confidence_score'),
                "reasoning": mitre_analysis.get('reasoning'),
                "raw_log_data": raw_log,
                "mitre_analysis": mitre_analysis
            }
            
            # TODO: Construct the prompt for the Recommendation Agent
            messages = create_recommendation_prompt(report_data)
            
            # Generate report using LLM
            markdown_report = await get_llm_completion(messages, self.llm_config)
            
            if not markdown_report or len(markdown_report.strip()) < 100:
                # Fallback report if LLM fails
                logger.warning("LLM generated insufficient report, using fallback")
                markdown_report = self._generate_fallback_report(report_data)
            
            logger.info(f"Generated report of length: {len(markdown_report)}")
            return markdown_report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            # Return error report
            return self._generate_error_report(analysis_payload, str(e))
    
    def _generate_fallback_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate a basic fallback report when LLM fails.
        
        Args:
            report_data: Structured report data
            
        Returns:
            str: Basic Markdown report
        """
        technique_id = report_data.get('technique_id', 'Unknown')
        technique_name = report_data.get('technique_name', 'Unknown')
        tactic = report_data.get('tactic', 'Unknown')
        hostname = report_data.get('hostname', 'Unknown')
        timestamp = report_data.get('timestamp', 'Unknown')
        
        return f"""# Security Alert Report (Fallback)

## Executive Summary
A security event was detected on host **{hostname}** at **{timestamp}**. The activity has been classified as **{tactic}** tactic using technique **{technique_id} - {technique_name}**.

## Alert Details
- **Timestamp**: {timestamp}
- **Hostname**: {hostname}
- **Technique**: {technique_id} - {technique_name}
- **Tactic**: {tactic}
- **Source IP**: {report_data.get('source_ip', 'N/A')}
- **Process**: {report_data.get('process_name', 'N/A')}

## Recommended Actions
1. **Immediate**: Isolate the affected host using CrowdStrike Falcon
2. **Investigation**: Search for similar activities in Splunk SIEM
3. **Monitoring**: Continue monitoring for related indicators

## Technical Details
```json
{json.dumps(report_data.get('raw_log_data', {}), indent=2)}
```
"""
    
    def _generate_error_report(self, payload: Dict[str, Any], error: str) -> str:
        """
        Generate an error report when report generation fails.
        
        Args:
            payload: Original payload
            error: Error message
            
        Returns:
            str: Error report in Markdown format
        """
        alert_id = payload.get('alert_id', 'Unknown')
        
        return f"""# Error Report - Alert {alert_id}

## Summary
An error occurred while generating the incident report for this alert.

## Error Details
**Error**: {error}

## Raw Data
```json
{json.dumps(payload, indent=2)}
```

## Manual Review Required
This alert requires manual analysis by a security analyst.
"""
    
    async def _update_output_sections(self, session_id: str, payload: Dict[str, Any], report: str) -> None:
        """
        Update all output sections with the final analysis results.
        
        Args:
            session_id: Session identifier
            payload: Complete payload with analysis data
            report: Generated markdown report
        """
        try:
            analysis_data = payload.get('mitre_analysis', {})
            
            # Extract key information
            technique_name = analysis_data.get('technique_name', 'Unknown')
            tactic = analysis_data.get('tactic', 'Unknown')
            confidence = analysis_data.get('confidence_score', 0.0)
            
            # Update recommendation section
            recommendation_desc = f"Generated incident response recommendations for {technique_name} technique"
            self.output_handler.update_recommendation(
                session_id, 
                recommendation_desc, 
                report
            )
            
            # Update executive summary
            executive_title = f"Security Incident Analysis - {tactic}"
            executive_content = f"Detected {technique_name} technique with {confidence:.2f} confidence score. Immediate containment and investigation recommended."
            self.output_handler.update_executive_summary(
                session_id,
                executive_title,
                executive_content
            )
            
            # Update checklist
            checklist_title = "Incident Response Checklist"
            checklist_content = self._generate_checklist(analysis_data)
            self.output_handler.update_checklist(
                session_id,
                checklist_title,
                checklist_content
            )
            
            # Save all updates
            self.output_handler.save_to_file()
            logger.info(f"Updated all output sections for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update output sections: {e}")
    
    def _generate_checklist(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate a checklist based on analysis data.
        
        Args:
            analysis_data: Analysis results
            
        Returns:
            Formatted checklist string
        """
        technique_name = analysis_data.get('technique_name', 'Unknown')
        tactic = analysis_data.get('tactic', 'Unknown')
        
        checklist_items = [
            "[ ] Isolate affected host from network",
            "[ ] Collect forensic evidence",
            "[ ] Check for lateral movement",
            "[ ] Review security logs for similar activity",
            f"[ ] Implement {tactic} detection rules",
            f"[ ] Update security controls for {technique_name}",
            "[ ] Document incident timeline",
            "[ ] Notify stakeholders",
            "[ ] Begin remediation activities"
        ]
        
        return "\n".join(checklist_items)

    def stop(self) -> None:
        """Stop the agent gracefully."""
        self.running = False
        logger.info("Recommendation Agent stop requested")


async def main():
    """
    Main entry point for standalone recommendation agent execution.
    """
    import yaml
    from pathlib import Path
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.get('logging', {}).get('level', 'INFO')),
        format=config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Initialize NATS handler
    nats_handler = NATSHandler(config['nats'])
    
    try:
        # Connect to NATS
        await nats_handler.connect()
        
        # Create and run recommendation agent
        agent = RecommendationAgent(nats_handler, config['llm'])
        await agent.run()
        
    except KeyboardInterrupt:
        logger.info("Recommendation Agent interrupted by user")
    except Exception as e:
        logger.error(f"Recommendation Agent execution failed: {e}")
    finally:
        await nats_handler.close()


if __name__ == "__main__":
    asyncio.run(main())