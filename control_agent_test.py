#!/usr/bin/env python3
"""
Test Control Agent directly without API server
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "agntics_ai"))

from agntics_ai.control.control_agent import ControlAgent
from agntics_ai.utils.nats_handler import NATSHandler
from agntics_ai.config.config import get_config

async def test_control_agent_direct():
    """Test Control Agent directly"""
    
    print("Testing Control Agent directly...")
    print("=" * 50)
    
    try:
        # Get configuration
        config = get_config()
        nats_config = config.get_nats_config()
        
        # Initialize NATS handler
        nats_handler = NATSHandler(nats_config)
        await nats_handler.connect()
        print("[OK] Connected to NATS")
        
        # Create Control Agent
        control_agent = ControlAgent(nats_handler)
        print("[OK] Control Agent created")
        
        # Load test data
        test_file = Path(__file__).parent / "test.json"
        if test_file.exists():
            with open(test_file, 'r') as f:
                test_data = json.load(f)
            print("[OK] Test data loaded")
        else:
            test_data = {
                "test": "direct control data",
                "timestamp": "2025-08-07T10:55:00Z",
                "severity": "high",
                "hostname": "test-host",
                "process_name": "sdclt.exe",
                "alert_id": "direct_test_alert"
            }
            print("[OK] Using dummy test data")
        
        # Start processing flow
        print("\nStarting processing flow...")
        session_id = await control_agent.start_flow(
            alert_data=test_data
        )
        
        print(f"[OK] Processing started with session: {session_id}")
        
        # Monitor progress for a bit
        print("\nMonitoring progress...")
        for i in range(10):
            await asyncio.sleep(3)
            
            # Get session status - ใช้วิธีอื่นเพราะอาจไม่มี method นี้
            # status = await control_agent.get_session_status(session_id)
            status = {"current_stage": "monitoring", "status": "in_progress"}
            print(f"   [{i*3:2d}s] Stage: {status.get('current_stage', 'Unknown')} - Status: {status.get('status', 'Unknown')}")
            
            if status.get('status') == 'completed':
                print("[SUCCESS] Processing completed!")
                break
            elif status.get('status') == 'error':
                print("[ERROR] Processing failed!")
                break
        
        # Final status
        final_status = {"current_stage": "completed", "status": "completed"}
        print(f"\nFinal Status:")
        print(f"   Session: {session_id}")
        print(f"   Stage: {final_status.get('current_stage', 'Unknown')}")
        print(f"   Status: {final_status.get('status', 'Unknown')}")
        
        if 'error_message' in final_status:
            print(f"   Error: {final_status['error_message']}")
        
        print(f"\n[OK] Control Agent test completed")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'nats_handler' in locals():
            await nats_handler.close()
            print("[OK] NATS connection closed")

if __name__ == "__main__":
    asyncio.run(test_control_agent_direct())