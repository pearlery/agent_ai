"""
Analysis Agent - Consumes alerts, maps them to MITRE ATT&CK framework using LLM.
"""
import asyncio
import json
import logging
from typing import Dict, Any
from ..config.config import get_config
from ..utils.nats_handler import NATSHandler
from ..utils.llm_handler_ollama import get_llm_completion, create_analysis_prompt
from ..utils.output_handler import get_output_handler
from ..utils.timeline_tracker import get_timeline_tracker, TimelineStage, TimelineStatus
from ..utils.persistence import get_default_persistence

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """
    Analysis Agent that processes security alerts and maps them to MITRE ATT&CK framework.
    """
    
    def __init__(self, nats_handler: NATSHandler, llm_config: Dict[str, Any], output_file: str = "output.json"):
        """
        Initialize the Analysis Agent.
        
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
        self.persistence = get_default_persistence()
    
    async def run(self) -> None:
        """
        Main loop for the Analysis Agent.
        Subscribes to input subject, processes alerts, and publishes analysis results.
        """
        logger.info("Starting Analysis Agent...")
        
        try:
            # Create pull subscription to input subject
            psub = await self.nats_handler.subscribe_pull(
                subject=self.nats_handler.subjects['input'],
                durable_name='analysis_agent'
            )
            
            self.running = True
            logger.info("Analysis Agent subscribed and running...")
            
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
                            logger.info(f"Processing alert: {alert_id}")
                            
                            # Create session ID from alert ID
                            session_id = payload.get('session_id', alert_id)
                            
                            # Initialize timeline tracker
                            timeline = get_timeline_tracker(session_id, self.output_file)
                            timeline.mark_stage_in_progress(TimelineStage.ANALYSIS_AGENT)
                            
                            # Extract log data
                            raw_log_data = payload.get('raw_log_data', {})
                            
                            # Save alert data to persistence
                            self.persistence.save_alert(alert_id, raw_log_data)
                            
                            # Perform MITRE ATT&CK analysis
                            analysis_result = await self._analyze_alert(raw_log_data)
                            
                            # Save analysis results
                            self.persistence.save_analysis(session_id, analysis_result)
                            
                            # Update output with attack mapping
                            await self._update_attack_output(session_id, analysis_result)
                            
                            # Update overview with analysis summary
                            overview_desc = f"MITRE ATT&CK analysis completed. Identified technique: {analysis_result.get('technique_name', 'Unknown')}"
                            self.output_handler.update_overview(session_id, overview_desc)
                            self.output_handler.save_to_file()
                            
                            # Create enriched payload
                            enriched_payload = {
                                "alert_id": alert_id,
                                "session_id": session_id,
                                "original_payload": payload,
                                "raw_log_data": raw_log_data,
                                "mitre_analysis": analysis_result,
                                "source": "analysis_agent",
                                "processing_timestamp": asyncio.get_event_loop().time()
                            }
                            
                            # Publish to analysis subject
                            await self.nats_handler.publish(
                                subject=self.nats_handler.subjects['analysis'],
                                payload=enriched_payload
                            )
                            
                            # Mark timeline as successful
                            timeline.mark_stage_success(TimelineStage.ANALYSIS_AGENT)
                            
                            # Acknowledge the message
                            await msg.ack()
                            logger.info(f"Successfully processed and published analysis for: {alert_id}")
                            
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
                                timeline.mark_stage_error(TimelineStage.ANALYSIS_AGENT, str(e))
                            except:
                                pass
                            
                            # Don't acknowledge - message will be redelivered
                
                except asyncio.TimeoutError:
                    # No messages available, continue polling
                    continue
                except Exception as e:
                    logger.error(f"Error in Analysis Agent main loop: {e}")
                    await asyncio.sleep(1)  # Brief pause before retrying
        
        except Exception as e:
            logger.error(f"Analysis Agent failed to start: {e}")
            raise
    
    async def _analyze_alert(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze alert using LLM to map to MITRE ATT&CK framework.
        
        Args:
            log_data: Raw log data from the alert
            
        Returns:
            Dict containing MITRE analysis results
        """
        try:
            # TODO: Implement more sophisticated context extraction
            external_context = self._extract_context(log_data)
            
            # Create analysis prompt
            messages = create_analysis_prompt(log_data, external_context)
            
            # Get LLM completion using Ollama
            llm_response = await get_llm_completion(messages, self.llm_config)
            
            # TODO: Parse and validate the LLM's JSON response
            try:
                analysis_result = json.loads(llm_response.strip())
                
                # Validate required fields
                required_fields = ['technique_id', 'technique_name', 'tactic', 'confidence_score', 'reasoning']
                for field in required_fields:
                    if field not in analysis_result:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate confidence score
                confidence = analysis_result.get('confidence_score', 0.0)
                if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                    analysis_result['confidence_score'] = 0.5  # Default value
                
                logger.info(f"Analysis complete: {analysis_result.get('technique_id')} - {analysis_result.get('technique_name')}")
                return analysis_result
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Return fallback analysis
                return {
                    "technique_id": "T1000",
                    "technique_name": "Unknown",
                    "tactic": "Unknown",
                    "confidence_score": 0.1,
                    "reasoning": f"Failed to parse LLM response: {e}",
                    "error": "LLM response parsing failed"
                }
        
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return error analysis
            return {
                "technique_id": "T1000",
                "technique_name": "Unknown",
                "tactic": "Unknown",
                "confidence_score": 0.0,
                "reasoning": f"Analysis failed due to error: {e}",
                "error": str(e)
            }
    
    async def _update_attack_output(self, session_id: str, analysis_result: Dict[str, Any]) -> None:
        """
        Update the attack mapping section in output.
        
        Args:
            session_id: Session identifier
            analysis_result: Analysis results from LLM
        """
        try:
            # Convert analysis result to attack mapping format
            tactic_mapping = {
                "Defense Evasion": "TA0005",
                "Privilege Escalation": "TA0004", 
                "Execution": "TA0002",
                "Initial Access": "TA0001",
                "Persistence": "TA0003",
                "Discovery": "TA0007",
                "Collection": "TA0009",
                "Command and Control": "TA0011",
                "Exfiltration": "TA0010",
                "Impact": "TA0040"
            }
            
            tactic_name = analysis_result.get('tactic', 'Unknown')
            tactic_id = tactic_mapping.get(tactic_name, "TA0000")
            confidence = analysis_result.get('confidence_score', 0.0)
            
            attack_data = [{
                "tacticID": tactic_id,
                "tacticName": tactic_name,
                "confidence": confidence
            }]
            
            self.output_handler.update_attack_mapping(session_id, attack_data)
            logger.info(f"Updated attack mapping for session {session_id}: {tactic_name}")
            
        except Exception as e:
            logger.error(f"Failed to update attack mapping: {e}")
    
    def _extract_context(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract additional context from log data for analysis.
        
        Args:
            log_data: Raw log data
            
        Returns:
            Dict containing extracted context information
        """
        # TODO: Implement sophisticated context extraction logic
        context = {}
        
        # Extract command line decoding if base64 encoded
        command_line = log_data.get('command_line', '')
        if 'EncodedCommand' in command_line or '-enc' in command_line.lower():
            context['encoded_command_detected'] = True
            # TODO: Add base64 decoding logic here if needed
        
        # Extract process relationships
        if log_data.get('parent_process'):
            context['parent_process'] = log_data['parent_process']
        
        # Extract network indicators
        if log_data.get('destination_ip'):
            context['network_communication'] = True
            context['destination_ip'] = log_data['destination_ip']
        
        return context
    
    def stop(self) -> None:
        """Stop the agent gracefully."""
        self.running = False
        logger.info("Analysis Agent stop requested")


async def main():
    """
    Main entry point for standalone analysis agent execution.
    """
    import yaml
    from pathlib import Path
    
    # Load configuration using enhanced config system
    config = get_config()
    
    # Convert to dict format for compatibility
    config_dict = {
        'nats': config.get_nats_config(),
        'llm': config.get_llm_config(),
        'logging': {
            'level': config.LOG_LEVEL,
            'format': config.LOG_FORMAT
        }
    }
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config_dict.get('logging', {}).get('level', 'INFO')),
        format=config_dict.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Initialize NATS handler
    nats_handler = NATSHandler(config_dict['nats'])
    
    try:
        # Connect to NATS
        await nats_handler.connect()
        
        # Create and run analysis agent
        agent = AnalysisAgent(nats_handler, config_dict['llm'])
        await agent.run()
        
    except KeyboardInterrupt:
        logger.info("Analysis Agent interrupted by user")
    except Exception as e:
        logger.error(f"Analysis Agent execution failed: {e}")
    finally:
        await nats_handler.close()


if __name__ == "__main__":
    asyncio.run(main())