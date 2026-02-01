#!/usr/bin/env python3
"""
Test Watson Orchestrate Integration
Verifies that the backend is properly connected to Watson Orchestrate agents
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.watson_orchestrate import get_orchestrate_client

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_client_connection():
    """Test Watson Orchestrate client connection"""
    print_header("1️⃣  Testing Watson Orchestrate Client Connection")
    
    try:
        client = get_orchestrate_client()
        print(f"✅ Client initialized successfully")
        print(f"   Region: {client.region}")
        print(f"   Instance ID: {client.instance_id}")
        print(f"   Base URL: {client.base_url}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False

def test_list_agents():
    """Test listing agents"""
    print_header("2️⃣  Listing Available Agents")
    
    try:
        client = get_orchestrate_client()
        agents = client.list_agents()
        
        if agents.get("agents"):
            print(f"✅ Found {len(agents['agents'])} agents:\n")
            for agent in agents["agents"]:
                name = agent.get("name", "Unknown")
                status = agent.get("status", "Unknown")
                print(f"   • {name} (Status: {status})")
            return True
        else:
            print("⚠️  No agents found")
            return False
    except Exception as e:
        print(f"❌ Failed to list agents: {e}")
        return False

def test_parse_intent():
    """Test Intent Detection Agent"""
    print_header("3️⃣  Testing Intent Detection Agent")
    
    try:
        client = get_orchestrate_client()
        test_query = "Find all emails from John about the project deadline"
        
        print(f"Query: '{test_query}'")
        print(f"\n⏳ Invoking intent_detection_agent...")
        
        result = client.parse_intent(test_query)
        
        if result.get("success"):
            print(f"✅ Agent invoked successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("result"), indent=2))
            return True
        else:
            print(f"❌ Agent invocation failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing intent detection: {e}")
        return False

def test_semantic_search():
    """Test Semantic Search Agent"""
    print_header("4️⃣  Testing Semantic Search Agent")
    
    try:
        client = get_orchestrate_client()
        test_query = "emails about budget planning and financial forecasts"
        
        print(f"Query: '{test_query}'")
        print(f"\n⏳ Invoking semantic_search_agent...")
        
        result = client.semantic_search(test_query)
        
        if result.get("success"):
            print(f"✅ Agent invoked successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("result"), indent=2))
            return True
        else:
            print(f"❌ Agent invocation failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing semantic search: {e}")
        return False

def test_all_agents_status():
    """Check status of all agents"""
    print_header("5️⃣  Checking All Agents Status")
    
    try:
        client = get_orchestrate_client()
        statuses = client.get_all_agent_statuses()
        
        print("Agent Status Report:\n")
        for agent_name, status_info in statuses.items():
            if status_info.get("error"):
                print(f"❌ {agent_name}: {status_info.get('error')}")
            else:
                print(f"✅ {agent_name}: {json.dumps(status_info, indent=2)}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking agent statuses: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print_header("6️⃣  Testing API Endpoints")
    
    try:
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        print("Testing /orchestrate/health...")
        response = requests.get(f"{base_url}/orchestrate/health")
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test list agents endpoint
        print("\nTesting /orchestrate/agents...")
        response = requests.get(f"{base_url}/orchestrate/agents")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listed {data.get('count', 0)} agents")
        else:
            print(f"❌ Failed to list agents: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not test API endpoints (server might not be running): {e}")
        return False

def main():
    """Run all tests"""
    print_header("🤖 Watson Orchestrate Integration Test Suite")
    print(f"Started: {datetime.now().isoformat()}\n")
    
    results = {
        "Client Connection": test_client_connection(),
        "List Agents": test_list_agents(),
        "Parse Intent": test_parse_intent(),
        "Semantic Search": test_semantic_search(),
        "Agent Status": test_all_agents_status(),
        "API Endpoints": test_api_endpoints(),
    }
    
    # Summary
    print_header("📊 Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Watson Orchestrate integration is working!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
