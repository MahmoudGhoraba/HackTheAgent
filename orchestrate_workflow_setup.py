#!/usr/bin/env python3
"""
Set up Watson Orchestrate workflow that orchestrates your local agents
This creates a workflow that Orchestrate can see and manage
"""

import os
import requests
import json
import yaml
from pathlib import Path

IAM_URL = "https://iam.cloud.ibm.com/identity/token"
ORCHESTRATE_API_URL = "https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4/v1"

def get_iam_token(api_key):
    """Get IAM token from API key"""
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
        "response_type": "cloud_iam"
    }
    
    response = requests.post(IAM_URL, headers=headers, data=data, timeout=10)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_workflow_endpoints():
    """Test available workflow endpoints"""
    
    api_key = os.environ.get("WATSON_ORCHESTRATE_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        return
    
    print("\n" + "="*60)
    print("🔍 Testing Watson Orchestrate Workflow Endpoints")
    print("="*60 + "\n")
    
    iam_token = get_iam_token(api_key)
    if not iam_token:
        print("❌ Failed to get IAM token")
        return
    
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }
    
    # Test workflow endpoints
    endpoints = [
        ("List Workflows", f"{ORCHESTRATE_API_URL}/workflows"),
        ("List Agents", f"{ORCHESTRATE_API_URL}/agents"),
        ("List Tools", f"{ORCHESTRATE_API_URL}/tools"),
        ("List Runtimes", f"{ORCHESTRATE_API_URL}/runtimes"),
        ("Status", f"{ORCHESTRATE_API_URL}/status"),
    ]
    
    print("Testing endpoints...\n")
    
    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"{name}:")
            print(f"  URL: {url}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"  ✅ SUCCESS!")
                if response.text and response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  Response: {json.dumps(data, indent=2)[:300]}")
                    except:
                        pass
            elif response.status_code == 404:
                print(f"  ❌ Not Found")
            else:
                print(f"  Status: {response.status_code}")
            
            print()
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")

if __name__ == "__main__":
    test_workflow_endpoints()