#!/usr/bin/env python3
"""
Simple test script for Control Agent API.
"""
import requests
import json
import time

def test_control_api():
    base_url = "http://127.0.0.1:9004"
    
    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test status endpoint
        print("Testing status endpoint...")
        response = requests.get(f"{base_url}/status", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test start endpoint with test data
        print("Testing start endpoint...")
        test_data = {
            "input_file": "test.json"
        }
        response = requests.post(f"{base_url}/start", json=test_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Control Agent API - is it running on port 9004?")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Control Agent API Test")
    print("=" * 30)
    test_control_api()