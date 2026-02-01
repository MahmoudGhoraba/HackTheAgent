#!/usr/bin/env python3
"""
Test Local Agent Engine Integration
Verifies that the local agent engine works properly
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.local_agent_engine import get_agent_engine

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_engine_initialization():
    """Test local agent engine initialization"""
    print_header("1️⃣  Testing Local Agent Engine Initialization")
    
    try:
        engine = get_agent_engine()
        print(f"✅ Engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        return False

def test_list_agents():
    """Test listing agents"""
    print_header("2️⃣  Listing Available Agents")
    
    try:
        engine = get_agent_engine()
        agents = engine.list_agents()
        
        if agents:
            print(f"✅ Found {len(agents)} agents:\n")
            for agent in agents:
                print(f"   • {agent}")
            return True
        else:
            print(f"❌ No agents found")
            return False
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        return False

def test_parse_intent():
    """Test Intent Detection Agent"""
    print_header("3️⃣  Testing Intent Detection Agent")
    
    try:
        engine = get_agent_engine()
        test_query = "Find all emails from John about the project deadline"
        
        print(f"Query: '{test_query}'")
        print(f"\n⏳ Invoking parse_intent...")
        
        result = engine.parse_intent(test_query)
        
        if result.get("success"):
            print(f"✅ Agent executed successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("output"), indent=2))
            return True
        else:
            print(f"❌ Agent execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing intent detection: {e}")
        return False

def test_semantic_search():
    """Test Semantic Search Agent"""
    print_header("4️⃣  Testing Semantic Search Agent")
    
    try:
        engine = get_agent_engine()
        test_query = "emails about budget planning and financial forecasts"
        
        print(f"Query: '{test_query}'")
        print(f"\n⏳ Invoking semantic_search...")
        
        result = engine.semantic_search(test_query, None)
        
        if result.get("success"):
            print(f"✅ Agent executed successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("output"), indent=2))
            return True
        else:
            print(f"❌ Agent execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing semantic search: {e}")
        return False

def test_classify_emails():
    """Test Classification Agent"""
    print_header("5️⃣  Testing Classification Agent")
    
    try:
        engine = get_agent_engine()
        
        test_emails = [
            {
                "id": "email_1",
                "sender": "boss@company.com",
                "subject": "URGENT: Project deadline tomorrow!",
                "body": "We need to deliver the project by EOD tomorrow"
            },
            {
                "id": "email_2",
                "sender": "support@vendor.com",
                "subject": "Your invoice is ready",
                "body": "Your monthly invoice is available for download"
            }
        ]
        
        print(f"⏳ Classifying {len(test_emails)} emails...")
        
        result = engine.classify_emails(test_emails)
        
        if result.get("success"):
            print(f"✅ Agent executed successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("output"), indent=2))
            return True
        else:
            print(f"❌ Agent execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing classification: {e}")
        return False

def test_generate_answer():
    """Test RAG Generation Agent"""
    print_header("6️⃣  Testing RAG Generation Agent")
    
    try:
        engine = get_agent_engine()
        
        test_query = "What is the project deadline?"
        test_context = [
            "The project deadline is tomorrow at 5 PM",
            "We need to submit all deliverables by EOD",
            "Team members should sync on final items"
        ]
        
        print(f"Query: '{test_query}'")
        print(f"\n⏳ Generating answer...")
        
        result = engine.generate_answer(test_query, test_context)
        
        if result.get("success"):
            print(f"✅ Agent executed successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("output"), indent=2))
            return True
        else:
            print(f"❌ Agent execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing RAG generation: {e}")
        return False

def test_detect_threats():
    """Test Threat Detection Agent"""
    print_header("7️⃣  Testing Threat Detection Agent")
    
    try:
        engine = get_agent_engine()
        
        test_emails = [
            {
                "id": "email_1",
                "sender": "unknown@suspicious.com",
                "subject": "Click here to verify your account",
                "body": "Your account will be closed unless you verify immediately"
            },
            {
                "id": "email_2",
                "sender": "it-support@company.com",
                "subject": "System maintenance scheduled",
                "body": "Scheduled maintenance on Friday from 10-12 PM"
            }
        ]
        
        print(f"⏳ Analyzing {len(test_emails)} emails for threats...")
        
        result = engine.detect_threats(test_emails)
        
        if result.get("success"):
            print(f"✅ Agent executed successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("output"), indent=2))
            return True
        else:
            print(f"❌ Agent execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing threat detection: {e}")
        return False

def test_persist_data():
    """Test Data Persistence Agent"""
    print_header("8️⃣  Testing Data Persistence Agent")
    
    try:
        engine = get_agent_engine()
        
        test_data = {
            "email_id": "email_123",
            "classification": "important",
            "threat_score": 0.2,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"⏳ Persisting data...")
        
        result = engine.persist_data("email_analysis", test_data)
        
        if result.get("success"):
            print(f"✅ Agent executed successfully!")
            print(f"\nResult:")
            print(json.dumps(result.get("output"), indent=2))
            return True
        else:
            print(f"❌ Agent execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing data persistence: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  🤖 Local Agent Engine Integration Test Suite")
    print("="*70)
    print(f"\nStarted: {datetime.now().isoformat()}\n")
    
    results = []
    
    # Run tests
    results.append(("Engine Initialization", test_engine_initialization()))
    results.append(("List Agents", test_list_agents()))
    results.append(("Parse Intent", test_parse_intent()))
    results.append(("Semantic Search", test_semantic_search()))
    results.append(("Classify Emails", test_classify_emails()))
    results.append(("Generate Answer", test_generate_answer()))
    results.append(("Detect Threats", test_detect_threats()))
    results.append(("Persist Data", test_persist_data()))
    
    # Summary
    print_header("📊 Test Summary")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n✅ Passed: {passed}/{len(results)}")
    if failed > 0:
        print(f"⚠️  {failed} tests failed. Check the errors above.")
        return 1
    else:
        print(f"🎉 All tests passed!")
        return 0

if __name__ == "__main__":
    exit(main())
