"""
Analysis Agent - Consumes alerts, maps them to MITRE ATT&CK framework using LLM.
"""
import asyncio
import json
import logging
from typing import Dict, Any
from utils.nats_handler import NATSHandler
from utils.llm_handler import get_llm_completion, create_analysis_prompt

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """
    Analysis Agent that processes security alerts and maps them to MITRE ATT&CK framework.
    """
    
    def __init__(self, nats_handler: NATSHandler, llm_config: Dict[str, Any]):
        """
        Initialize the Analysis Agent.
        
        Args:
            nats_handler: Connected NATS handler instance
            llm_config: LLM configuration dictionary
        """
        self.nats_handler = nats_handler
        self.llm_config = llm_config
        self.running = False
    
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
                            logger.info(f"Processing alert: {payload.get('alert_id', 'unknown')}")
                            
                            # Extract log data
                            raw_log_data = payload.get('raw_log_data', {})
                            
                            # Perform MITRE ATT&CK analysis
                            analysis_result = await self._analyze_alert(raw_log_data)
                            
                            # Create enriched payload
                            enriched_payload = {
                                "alert_id": payload.get('alert_id'),
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
                            
                            # Acknowledge the message
                            await msg.ack()
                            logger.info(f"Successfully processed and published analysis for: {payload.get('alert_id')}")
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode message JSON: {e}")
                            await msg.ack()  # Acknowledge to prevent redelivery
                        except Exception as e:
                            logger.error(f"Failed to process message: {e}")
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
            
            # Get LLM completion
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
        
        # Create and run analysis agent
        agent = AnalysisAgent(nats_handler, config['llm'])
        await agent.run()
        
    except KeyboardInterrupt:
        logger.info("Analysis Agent interrupted by user")
    except Exception as e:
        logger.error(f"Analysis Agent execution failed: {e}")
    finally:
        await nats_handler.close()


if __name__ == "__main__":
    asyncio.run(main())