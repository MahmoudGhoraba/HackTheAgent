#!/usr/bin/env python3
"""
Find the correct Watson Orchestrate API endpoint for agents
"""

import os
import requests
import json

def get_iam_token(api_key):
    """Get IAM token from API key"""
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
        "response_type": "cloud_iam"
    }
    
    response = requests.post(url, headers=headers, data=data, timeout=10)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_endpoints():
    """Test different possible endpoint paths"""
    
    api_key = os.environ.get("WATSON_ORCHESTRATE_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        return
    
    print("\n" + "="*60)
    print("🔍 Finding Correct Watson Orchestrate Endpoint")
    print("="*60 + "\n")
    
    iam_token = get_iam_token(api_key)
    if not iam_token:
        print("❌ Failed to get IAM token")
        return
    
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }
    
    base_url = "https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4"
    
    # Test different endpoint variations
    endpoints = [
        ("With /v1/agents", f"{base_url}/v1/agents"),
        ("Without /v1", f"{base_url}/agents"),
        ("With /api/v1/agents", f"{base_url}/api/v1/agents"),
        ("With /workflows/email_analysis/agents", f"{base_url}/workflows/email_analysis/agents"),
        ("Base URL check", f"{base_url}"),
        ("Base URL with /v1", f"{base_url}/v1"),
        ("Root endpoint", "https://api.jp-tok.watson-orchestrate.cloud.ibm.com"),
    ]
    
    print("Testing endpoints...\n")
    
    for name, url in endpoints:
        try:
            print(f"Testing: {name}")
            print(f"  URL: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"  ✅ SUCCESS!")
                if response.text:
                    try:
                        data = response.json()
                        print(f"  Response: {json.dumps(data, indent=2)[:200]}")
                    except:
                        print(f"  Response: {response.text[:200]}")
            elif response.status_code == 404:
                print(f"  ❌ Not Found (404)")
            else:
                print(f"  Response: {response.text[:100]}")
            
            print()
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")

if __name__ == "__main__":
    test_endpoints()