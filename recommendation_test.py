#!/usr/bin/env python3
"""
Test recommendation generation with tool integration
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "agntics_ai"))

from agntics_ai.config.config import get_config
from agntics_ai.utils.tool_loader import get_tool_loader
from agntics_ai.utils.llm_handler_ollama import create_recommendation_prompt, get_llm_completion

async def test_recommendation():
    """Test recommendation generation with your test.json data"""
    
    # Load test data
    with open('test.json', 'r') as f:
        test_data = json.load(f)
    
    # Simulate analysis results (normally comes from Analysis Agent)
    analysis_data = {
        "alert_id": test_data.get('alert_id'),
        "timestamp": test_data.get('detected_time'),
        "hostname": test_data.get('contexts', {}).get('user', 'yb-lt2338$'),
        "technique_id": "T1548.002",  # From your test data MITRE
        "technique_name": "Bypass User Account Control", 
        "tactic": "Defense Evasion",
        "confidence_score": 0.95,
        "reasoning": "UAC bypass technique detected via sdclt.exe",
        "raw_log_data": test_data,
        "mitre_analysis": {
            "technique_id": "T1548.002",
            "technique_name": "Bypass User Account Control",
            "tactic": "Defense Evasion",
            "confidence_score": 0.95
        }
    }
    
    # Load relevant tools
    tool_loader = get_tool_loader()
    available_customers = tool_loader.get_available_customers()
    print(f"Available customers: {available_customers}")
    
    if available_customers:
        customer = available_customers[0]  # Use first customer
        relevant_tools = tool_loader.find_relevant_tools("T1548.002", customer)
        print(f"Found {len(relevant_tools)} relevant tools for {customer}")
        for tool in relevant_tools:
            print(f"- {tool.get('product')} ({tool.get('technology')})")
    else:
        relevant_tools = []
    
    # Generate recommendation
    messages = create_recommendation_prompt(analysis_data, relevant_tools)
    
    print("\n=== Testing LLM Recommendation Generation ===")
    try:
        cfg = get_config()
        llm_config = cfg.get_llm_config()
        
        recommendation = await get_llm_completion(messages, llm_config)
        
        print("\n=== Generated Recommendation ===")
        print(recommendation)
        
        # Save result
        with open('test_recommendation_output.md', 'w') as f:
            f.write(recommendation)
        print(f"\nRecommendation saved to: test_recommendation_output.md")
        
    except Exception as e:
        print(f"LLM generation failed: {e}")
        print("\nWould generate recommendation with these tools:")
        for tool in relevant_tools:
            print(f"- Use {tool.get('product')} to detect {tool.get('purpose', 'this attack')}")

if __name__ == "__main__":
    asyncio.run(test_recommendation())