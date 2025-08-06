#!/usr/bin/env python3
"""
Startup script for the Control Agent API server.
"""
import sys
from pathlib import Path

# Add agntics_ai to Python path
sys.path.append(str(Path(__file__).parent / "agntics_ai"))

from agntics_ai.control.control_app import start_api


if __name__ == "__main__":
    print("🎯 Agent AI Control Agent")
    print("=" * 30)
    print("🚀 Starting Control Agent API server...")
    
    # Default to port 9002 like original ControlAgent
    start_api(host="0.0.0.0", port=9002)