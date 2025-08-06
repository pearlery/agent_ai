#!/usr/bin/env python3
"""
Demo script to test the updated Agent AI system with new output format.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the agntics_ai package to path
sys.path.append(str(Path(__file__).parent / "agntics_ai"))

from agntics_ai.config.config import get_config
from agntics_ai.utils.nats_handler import NATSHandler
from agntics_ai.agents.input_agent import run_input_agent
from agntics_ai.agents.analysis_agent import AnalysisAgent
from agntics_ai.agents.recommendation_agent import RecommendationAgent
from agntics_ai.utils.output_handler import get_output_handler


async def run_demo():
    """Run a demonstration of the Agent AI system."""
    print("🚀 Starting Agent AI Demo with New Output Format...")
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = get_config()
        
        # Initialize NATS handler
        nats_config = config.get_nats_config()
        nats_handler = NATSHandler(nats_config)
        
        print("📡 Connecting to NATS...")
        await nats_handler.connect()
        
        # Initialize output handler
        output_file = Path(__file__).parent / "output.json"
        output_handler = get_output_handler(str(output_file))
        print(f"📄 Output will be saved to: {output_file}")
        
        # Phase 1: Input Agent
        print("\n📥 Phase 1: Publishing test alerts...")
        test_file = Path(__file__).parent / "test.json"
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return
        
        await run_input_agent(nats_handler, str(test_file), str(output_file))
        print("✅ Input phase completed")
        
        # Brief delay to ensure messages are queued
        await asyncio.sleep(2)
        
        # Phase 2: Processing Agents
        print("\n🧠 Phase 2: Starting analysis and recommendation agents...")
        
        llm_config = config.get_llm_config()
        analysis_agent = AnalysisAgent(nats_handler, llm_config, str(output_file))
        recommendation_agent = RecommendationAgent(nats_handler, llm_config, str(output_file))
        
        # Run agents with timeout
        print("⏳ Processing alerts (max 60 seconds)...")
        
        try:
            await asyncio.wait_for(
                asyncio.gather(
                    analysis_agent.run(),
                    recommendation_agent.run(),
                    return_exceptions=True
                ),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            print("⏰ Demo timeout reached (60 seconds)")
            analysis_agent.stop()
            recommendation_agent.stop()
        
        # Phase 3: Display Results
        print("\n📊 Phase 3: Displaying results...")
        
        if output_file.exists():
            print(f"✅ Output file generated: {output_file}")
            
            # Load and display summary
            with open(output_file, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            
            print("\n📋 Summary:")
            for section_name, entries in output_data.items():
                if entries:
                    print(f"  • {section_name}: {len(entries)} entries")
                    
                    # Show first entry details for key sections
                    if section_name in ["agent.attack.updated", "agent.executive.updated", "agent.timeline.updated"]:
                        if entries:
                            first_entry = entries[0]
                            session_id = first_entry.get('id', 'unknown')
                            print(f"    Session ID: {session_id}")
                            
                            if section_name == "agent.timeline.updated":
                                timeline_data = first_entry.get('data', [])
                                if timeline_data:
                                    last_stage = timeline_data[-1]
                                    print(f"    Last Stage: {last_stage.get('stage', 'Unknown')} - {last_stage.get('status', 'Unknown')}")
            
            print(f"\n📁 Full output saved to: {output_file}")
            print("🎯 You can now compare this with your expected output.json format!")
            
        else:
            print("❌ No output file was generated")
    
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
    
    finally:
        # Cleanup
        if 'nats_handler' in locals():
            await nats_handler.close()
        print("\n🏁 Demo completed!")


if __name__ == "__main__":
    print("Agent AI Demo - Updated Output Format")
    print("=" * 40)
    asyncio.run(run_demo())