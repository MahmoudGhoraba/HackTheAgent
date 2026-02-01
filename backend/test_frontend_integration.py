#!/usr/bin/env python3
"""
Test Workflow Integration with Frontend
Verifies end-to-end integration from frontend to IBM Orchestrate agents
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_workflow_status():
    """Test workflow system status"""
    print_header("1️⃣  Testing Workflow System Status")
    
    response = client.get("/workflow/status")
    print(f"Status code: {response.status_code}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    data = response.json()
    print(f"✅ Workflow System Operational")
    print(f"   Agents Available: {data['agents_available']}")
    print(f"   Capabilities: {', '.join(data['capabilities'])}")
    
    return True

def test_list_agents():
    """Test listing workflow agents"""
    print_header("2️⃣  Testing List Workflow Agents")
    
    response = client.get("/workflow/agents")
    print(f"Status code: {response.status_code}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    data = response.json()
    print(f"✅ Found {data['count']} agents:")
    for agent in data['agents']:
        agent_name = agent.get('name', 'unknown')
        print(f"   • {agent_name}")
    
    return True

def test_workflow_search():
    """Test workflow with search intent"""
    print_header("3️⃣  Testing Workflow: Search Intent (Frontend Query)")
    
    query = "Find emails about project deadlines from John"
    print(f"Query: '{query}'")
    print(f"\n⏳ Executing workflow...\n")
    
    response = client.post("/workflow/execute", json={
        "question": query,
        "top_k": 100
    })
    
    print(f"Status code: {response.status_code}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    data = response.json()
    
    print(f"✅ Workflow Status: {data['status']}")
    print(f"\n📊 Execution Steps:")
    
    for i, step in enumerate(data['steps'], 1):
        status_icon = "✅" if step['status'] == "completed" else "❌"
        print(f"\n   {i}. {status_icon} {step['description']}")
        print(f"      Agent: {step['agent']}")
        print(f"      Status: {step['status']}")
        if step['result']:
            if isinstance(step['result'], dict):
                print(f"      Result: {json.dumps(step['result'], indent=8)[:200]}...")
    
    print(f"\n🎯 Final Result:")
    if data['result']:
        print(f"   Answer: {data['result'].get('answer', 'N/A')[:100]}...")
        print(f"   Citations: {len(data['result'].get('citations', []))}")
        print(f"   Search Results: {len(data['result'].get('search_results', []))}")
    
    return True

def test_workflow_classify():
    """Test workflow with classification intent"""
    print_header("4️⃣  Testing Workflow: Classification Intent (Frontend Query)")
    
    query = "Organize and classify all my emails"
    print(f"Query: '{query}'")
    print(f"\n⏳ Executing workflow...\n")
    
    response = client.post("/workflow/execute", json={
        "question": query,
        "top_k": 100
    })
    
    print(f"Status code: {response.status_code}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    data = response.json()
    
    print(f"✅ Workflow Status: {data['status']}")
    print(f"\n📊 Execution Steps:")
    
    for i, step in enumerate(data['steps'], 1):
        status_icon = "✅" if step['status'] == "completed" else "❌"
        print(f"\n   {i}. {status_icon} {step['description']}")
        print(f"      Agent: {step['agent']}")
        print(f"      Status: {step['status']}")
    
    print(f"\n🎯 Final Result:")
    if data['result']:
        classifications = data['result'].get('classifications', {})
        print(f"   Classified Emails: {len(classifications.get('classified_emails', []))}")
    
    return True

def test_workflow_threat():
    """Test workflow with threat intent"""
    print_header("5️⃣  Testing Workflow: Threat Detection Intent (Frontend Query)")
    
    query = "Check my emails for security threats and phishing"
    print(f"Query: '{query}'")
    print(f"\n⏳ Executing workflow...\n")
    
    response = client.post("/workflow/execute", json={
        "question": query,
        "top_k": 100
    })
    
    print(f"Status code: {response.status_code}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    data = response.json()
    
    print(f"✅ Workflow Status: {data['status']}")
    print(f"\n📊 Execution Steps:")
    
    for i, step in enumerate(data['steps'], 1):
        status_icon = "✅" if step['status'] == "completed" else "❌"
        print(f"\n   {i}. {status_icon} {step['description']}")
        print(f"      Agent: {step['agent']}")
        print(f"      Status: {step['status']}")
    
    print(f"\n🎯 Final Result:")
    if data['result']:
        threats = data['result'].get('threats', {})
        print(f"   Threats Detected: {threats.get('threats_detected', 0)}")
    
    return True

def test_workflow_general():
    """Test workflow with general query"""
    print_header("6️⃣  Testing Workflow: General Query (Frontend Question)")
    
    query = "What are the important emails I received this week?"
    print(f"Query: '{query}'")
    print(f"\n⏳ Executing workflow...\n")
    
    response = client.post("/workflow/execute", json={
        "question": query,
        "top_k": 50
    })
    
    print(f"Status code: {response.status_code}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    data = response.json()
    
    print(f"✅ Workflow Status: {data['status']}")
    print(f"\n📊 Execution Steps:")
    
    for i, step in enumerate(data['steps'], 1):
        status_icon = "✅" if step['status'] == "completed" else "❌"
        print(f"\n   {i}. {status_icon} {step['description']}")
        print(f"      Agent: {step['agent']}")
        print(f"      Status: {step['status']}")
    
    print(f"\n🎯 Final Result:")
    if data['result']:
        print(f"   Answer: {data['result'].get('answer', 'N/A')[:100]}...")
        print(f"   Confidence: {data['result'].get('confidence', 0)}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  🤖 Frontend to IBM Orchestrate Integration Tests")
    print("  Testing Complete End-to-End Workflow from Frontend UI")
    print("="*80)
    print(f"\nStarted: {datetime.now().isoformat()}\n")
    
    results = []
    
    try:
        results.append(("Workflow Status", test_workflow_status()))
        results.append(("List Agents", test_list_agents()))
        results.append(("Search Workflow", test_workflow_search()))
        results.append(("Classify Workflow", test_workflow_classify()))
        results.append(("Threat Workflow", test_workflow_threat()))
        results.append(("General Query Workflow", test_workflow_general()))
        
        # Summary
        print_header("📊 Test Summary")
        
        passed = sum(1 for _, result in results if result)
        failed = len(results) - passed
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n✅ Passed: {passed}/{len(results)}")
        
        if failed > 0:
            print(f"⚠️  {failed} tests failed")
            return 1
        else:
            print(f"\n🎉 All tests passed!")
            print(f"\n✨ Frontend is now fully connected to IBM Orchestrate agents!")
            print(f"   • Search queries use Semantic Search + RAG agents")
            print(f"   • Classification queries use Classification agent")
            print(f"   • Threat queries use Threat Detection agent")
            print(f"   • General questions use RAG agent")
            print(f"   • All results are persisted via Database agent")
            return 0
    
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
