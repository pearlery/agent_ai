#!/usr/bin/env python3
"""
Quick test for Control Agent functionality without full server.
"""
import sys
import asyncio
from pathlib import Path

# Add agntics_ai to Python path
sys.path.append(str(Path(__file__).parent / "agntics_ai"))

from agntics_ai.control.control_agent import ControlAgent


async def test_control_agent():
    """Test control agent directly without API server."""
    print("Testing Control Agent directly...")
    
    try:
        # Create control agent without NATS
        control_agent = ControlAgent(None, "test_output.json")
        print("PASS: Control Agent created successfully")
        
        # Test start flow
        test_alert = {
            "alert_id": "test_001", 
            "timestamp": "2025-08-07T23:20:00Z",
            "severity": "high",
            "message": "Test alert for control agent"
        }
        
        result = await control_agent.start_flow(test_alert, "test_session_001")
        print(f"PASS: Start flow result: {result}")
        
        # Test type finished
        type_data = {
            "technique_name": "T1055 Process Injection",
            "confidence": 0.85,
            "analysis": "Test analysis data"
        }
        
        result = await control_agent.finished_type(type_data, "test_session_001")
        print(f"PASS: Finished type result: {result}")
        
        # Test flow finished
        final_data = {
            "status": "completed",
            "report": "Test incident analysis completed successfully",
            "recommendations": "Implement security measures"
        }
        
        result = await control_agent.finished_flow(final_data, "test_session_001")
        print(f"PASS: Finished flow result: {result}")
        
        print("\nSUCCESS: All Control Agent tests passed!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Direct Control Agent Test")
    print("=" * 30)
    asyncio.run(test_control_agent())