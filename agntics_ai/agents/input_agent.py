"""
Input Agent - Reads JSON alerts and publishes them to the pipeline.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any
from ..utils.nats_handler import NATSHandler
from ..utils.output_handler import get_output_handler
from ..utils.timeline_tracker import get_timeline_tracker, TimelineStage

logger = logging.getLogger(__name__)


async def run_input_agent(nats_handler: NATSHandler, alert_file_path: str, output_file: str = "output.json") -> None:
    """
    Run the input agent to process alerts from JSON file and publish to NATS.
    
    Args:
        nats_handler: Connected NATS handler instance
        alert_file_path: Path to the JSON file containing alerts
        output_file: Path to output JSON file
    """
    try:
        # Read the alert file
        alert_path = Path(alert_file_path)
        if not alert_path.exists():
            raise FileNotFoundError(f"Alert file not found: {alert_file_path}")
        
        with open(alert_path, 'r', encoding='utf-8') as f:
            alerts = json.load(f)
        
        if not isinstance(alerts, list):
            alerts = [alerts]  # Handle single alert case
        
        logger.info(f"Loaded {len(alerts)} alerts from {alert_file_path}")
        
        # Get output handler for session management
        output_handler = get_output_handler(output_file)
        
        # Process and publish each alert
        for idx, alert in enumerate(alerts):
            try:
                # Generate session ID
                session_id = output_handler.generate_session_id()
                alert_id = f"input_{idx}_{alert.get('id', alert.get('alert_id', session_id))}"
                
                # Initialize timeline tracker
                timeline = get_timeline_tracker(session_id, output_file)
                timeline.mark_stage_in_progress(TimelineStage.INPUT_AGENT)
                
                # Create message payload
                message_payload = {
                    "alert_id": alert_id,
                    "session_id": session_id,
                    "raw_log_data": alert,
                    "source": "input_agent",
                    "processing_timestamp": asyncio.get_event_loop().time()
                }
                
                # Publish to input subject
                await nats_handler.publish(
                    subject=nats_handler.subjects['input'],
                    payload=message_payload
                )
                
                # Mark input stage as successful
                timeline.mark_stage_success(TimelineStage.INPUT_AGENT)
                
                logger.info(f"Published alert {idx + 1}/{len(alerts)}: {alert_id}")
                
                # Small delay between messages
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to publish alert {idx}: {e}")
                continue
        
        logger.info(f"Input agent completed processing {len(alerts)} alerts")
        
    except Exception as e:
        logger.error(f"Input agent failed: {e}")
        raise


async def main():
    """
    Main entry point for standalone input agent execution.
    """
    from ..config.config import get_config
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
        
        # Run input agent
        alert_file_path = Path(__file__).parent.parent / "data" / "test.json"
        output_file_path = Path(__file__).parent.parent.parent / "output.json"
        await run_input_agent(nats_handler, str(alert_file_path), str(output_file_path))
        
    except Exception as e:
        logger.error(f"Input agent execution failed: {e}")
    finally:
        await nats_handler.close()


if __name__ == "__main__":
    asyncio.run(main())