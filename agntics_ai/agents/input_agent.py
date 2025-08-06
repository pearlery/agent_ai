"""
Input Agent - Reads JSON alerts and publishes them to the pipeline.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any
from utils.nats_handler import NATSHandler

logger = logging.getLogger(__name__)


async def run_input_agent(nats_handler: NATSHandler, alert_file_path: str) -> None:
    """
    Run the input agent to process alerts from JSON file and publish to NATS.
    
    Args:
        nats_handler: Connected NATS handler instance
        alert_file_path: Path to the JSON file containing alerts
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
        
        # Process and publish each alert
        for idx, alert in enumerate(alerts):
            try:
                # Create message payload
                message_payload = {
                    "alert_id": f"input_{idx}_{alert.get('timestamp', 'unknown')}",
                    "raw_log_data": alert,
                    "source": "input_agent",
                    "processing_timestamp": asyncio.get_event_loop().time()
                }
                
                # Publish to input subject
                await nats_handler.publish(
                    subject=nats_handler.subjects['input'],
                    payload=message_payload
                )
                
                logger.info(f"Published alert {idx + 1}/{len(alerts)}: {message_payload['alert_id']}")
                
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
        
        # Run input agent
        alert_file_path = Path(__file__).parent.parent / "data" / "test.json"
        await run_input_agent(nats_handler, str(alert_file_path))
        
    except Exception as e:
        logger.error(f"Input agent execution failed: {e}")
    finally:
        await nats_handler.close()


if __name__ == "__main__":
    asyncio.run(main())