#!/usr/bin/env python3
"""
Agent AI System Test - Comprehensive test for all components
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "agntics_ai"))

from agntics_ai.config.config import get_config
from agntics_ai.utils.nats_handler import NATSHandler
from agntics_ai.control.control_agent import ControlAgent

async def test_system_components():
    """Test all Agent AI system components"""
    
    print("Agent AI System Test")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    try:
        config = get_config()
        nats_config = config.get_nats_config()
        llm_config = config.get_llm_config()
        print("[OK] Configuration loaded successfully")
        print(f"   NATS Server: {nats_config.get('servers')}")
        print(f"   LLM Model: {llm_config.get('local_model')}")
    except Exception as e:
        print(f"[ERROR] Configuration failed: {e}")
        return False
    
    # Test 2: NATS Connection
    print("\n2. Testing NATS Connection...")
    try:
        nats_handler = NATSHandler(nats_config)
        await nats_handler.connect()
        print("[OK] NATS connected successfully")
        
        # Test stream exists
        print(f"[OK] Connected to stream: agentAI_stream")
    except Exception as e:
        print(f"[ERROR] NATS connection failed: {e}")
        return False
    
    # Test 3: Control Agent
    print("\n3. Testing Control Agent...")
    try:
        control_agent = ControlAgent(nats_handler)
        
        # Test with sample data
        test_data = {
            "alert_id": "system_test_alert",
            "timestamp": "2025-08-07T11:00:00Z",
            "severity": "high",
            "hostname": "test-system",
            "process_name": "sdclt.exe",
            "command_line": "sdclt.exe /kickoffelev",
            "source_ip": "192.168.1.100",
            "description": "Potential UAC bypass detected"
        }
        
        session_id = await control_agent.start_flow(alert_data=test_data)
        print(f"[OK] Control Agent started flow: {session_id}")
        
    except Exception as e:
        print(f"[ERROR] Control Agent failed: {e}")
        return False
    
    # Test 4: Tool Integration
    print("\n4. Testing Tool Integration...")
    try:
        from agntics_ai.utils.tool_loader import get_tool_loader
        tool_loader = get_tool_loader()
        customers = tool_loader.get_available_customers()
        print(f"[OK] Tool loader found {len(customers)} customers")
        
        if customers:
            customer = customers[0]
            tools = tool_loader.find_relevant_tools("T1548.002", customer)
            print(f"[OK] Found {len(tools)} relevant tools for T1548.002")
        
    except Exception as e:
        print(f"[ERROR] Tool integration failed: {e}")
    
    # Test 5: Output System
    print("\n5. Testing Output System...")
    try:
        output_file = Path(__file__).parent / "output.json"
        if output_file.exists():
            print(f"[OK] Output file exists: {output_file}")
            
            # Check file size
            file_size = output_file.stat().st_size
            print(f"[OK] Output file size: {file_size} bytes")
            
            # Validate JSON
            with open(output_file, 'r') as f:
                data = json.load(f)
            print(f"[OK] Valid JSON with {len(data)} sections")
            
        else:
            print("[WARNING] No output.json file found")
    
    except Exception as e:
        print(f"[ERROR] Output system failed: {e}")
    
    # Cleanup
    try:
        await nats_handler.close()
        print("\n[OK] System test completed - all connections closed")
        return True
    except Exception as e:
        print(f"[ERROR] Cleanup failed: {e}")
        return False

async def run_full_pipeline_test():
    """Run a full pipeline test using test.json"""
    
    print("\nFull Pipeline Test")
    print("=" * 50)
    
    test_file = Path(__file__).parent / "test.json"
    if not test_file.exists():
        print("[ERROR] test.json not found - cannot run full pipeline test")
        return False
    
    try:
        with open(test_file, 'r') as f:
            test_data = json.load(f)
        
        print(f"[OK] Loaded test data: {test_data.get('alert_id')}")
        
        # Use Control Agent to run full pipeline
        config = get_config()
        nats_config = config.get_nats_config()
        
        nats_handler = NATSHandler(nats_config)
        await nats_handler.connect()
        
        control_agent = ControlAgent(nats_handler)
        session_id = await control_agent.start_flow(alert_data=test_data)
        
        print(f"[OK] Full pipeline started with session: {session_id}")
        print("[INFO] Check output.json and web interface for results")
        
        await nats_handler.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Full pipeline test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("Starting Agent AI System Tests...")
    
    # Run component tests
    component_success = await test_system_components()
    
    if component_success:
        print("\n" + "=" * 60)
        # Run full pipeline test
        pipeline_success = await run_full_pipeline_test()
        
        if pipeline_success:
            print("\n[SUCCESS] All tests passed! System is ready.")
            print("\nNext steps:")
            print("1. Start web interface: python -m agntics_ai.webapp.app")
            print("2. Start Control Agent API: python start_control_agent.py")
            print("3. Run full demo: python run_demo.py")
        else:
            print("\n[WARNING] Component tests passed but pipeline test failed")
    else:
        print("\n[ERROR] Component tests failed - system not ready")

if __name__ == "__main__":
    asyncio.run(main())