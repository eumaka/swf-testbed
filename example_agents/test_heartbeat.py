#!/usr/bin/env python3
"""
Test script to verify REST API heartbeat functionality without ActiveMQ.
"""

import os
import sys
import requests
import json

# Add the parent directory to Python path to import base_agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_heartbeat():
    """Test the REST API heartbeat independently."""
    
    # Configuration
    monitor_url = os.getenv('SWF_MONITOR_URL', 'http://localhost:8002').rstrip('/')
    api_token = os.getenv('SWF_API_TOKEN')
    
    print(f"Testing heartbeat to: {monitor_url}")
    print(f"Using token: {api_token[:10]}..." if api_token else "No token provided")
    
    # Set up session
    session = requests.Session()
    if api_token:
        session.headers.update({'Authorization': f'Token {api_token}'})
    
    # Test payload
    payload = {
        "instance_name": "test-heartbeat-agent",
        "agent_type": "TEST",
        "status": "OK",
        "description": "Test heartbeat without ActiveMQ",
        "mq_connected": False  # Since we're not connecting to MQ
    }
    
    try:
        print("\n--- Testing API connectivity ---")
        # First test basic API access
        url = f"{monitor_url}/api/v1/systemagents/"
        response = session.get(url, timeout=10)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text[:200]}")
        else:
            data = response.json()
            print(f"Current agents: {len(data)} agents found")
        
        print("\n--- Testing heartbeat POST ---")
        # Test heartbeat endpoint
        heartbeat_url = f"{monitor_url}/api/v1/systemagents/heartbeat/"
        response = session.post(heartbeat_url, json=payload, timeout=10)
        print(f"POST {heartbeat_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Heartbeat successful!")
            return True
        else:
            print("❌ Heartbeat failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    import subprocess
    result = subprocess.run(['bash', '-c', 'set -a && source ~/.env && env'], 
                          capture_output=True, text=True)
    
    for line in result.stdout.split('\n'):
        if '=' in line and not line.startswith('_'):
            key, value = line.split('=', 1)
            os.environ[key] = value
    
    success = test_heartbeat()
    sys.exit(0 if success else 1)