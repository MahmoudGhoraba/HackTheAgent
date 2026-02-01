#!/usr/bin/env python3
"""
Test FastAPI Routes
Verifies that the FastAPI routes work with the local agent engine
"""

import os
import sys
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/orchestrate/health")
    print(f"Health: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agents_available"] == 6
    print(f"✅ Health check passed")

def test_list_agents():
    """Test list agents endpoint"""
    response = client.get("/orchestrate/agents")
    print(f"List agents: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 6
    print(f"✅ Listed {data['count']} agents")

def test_parse_intent():
    """Test parse intent endpoint"""
    response = client.post("/orchestrate/intent/parse", json={"query": "Find emails from John"})
    print(f"Parse intent: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✅ Parsed intent: {data['output']['intent']}")

def test_semantic_search():
    """Test semantic search endpoint"""
    response = client.post("/orchestrate/search/semantic", json={"query": "budget planning"})
    print(f"Semantic search: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✅ Semantic search returned {data['output']['total_matches']} results")

def test_classify():
    """Test classify endpoint"""
    response = client.post("/orchestrate/classify", json={
        "emails": [
            {"id": "1", "sender": "boss@company.com", "subject": "URGENT!", "body": "Help"}
        ]
    })
    print(f"Classify: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✅ Classified {len(data['output']['classified_emails'])} email(s)")

def test_generate_answer():
    """Test generate answer endpoint"""
    response = client.post("/orchestrate/generate-answer", json={
        "query": "What is the deadline?",
        "context": ["The deadline is tomorrow"]
    })
    print(f"Generate answer: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✅ Generated answer with {len(data['output']['citations'])} citations")

def test_detect_threats():
    """Test detect threats endpoint"""
    response = client.post("/orchestrate/threats/detect", json={
        "emails": [
            {"id": "1", "sender": "unknown@phishing.com", "subject": "Verify now!", "body": "Click here"}
        ]
    })
    print(f"Detect threats: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✅ Threat detection completed")

def test_persist_data():
    """Test persist data endpoint"""
    response = client.post("/orchestrate/persist", json={
        "data_type": "email_analysis",
        "data": {"email_id": "123", "result": "safe"}
    })
    print(f"Persist data: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✅ Persisted {data['output']['records']} record(s)")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🚀 Testing FastAPI Routes")
    print("="*70 + "\n")
    
    try:
        test_health()
        test_list_agents()
        test_parse_intent()
        test_semantic_search()
        test_classify()
        test_generate_answer()
        test_detect_threats()
        test_persist_data()
        
        print("\n" + "="*70)
        print("  ✅ ALL ROUTE TESTS PASSED!")
        print("="*70 + "\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
