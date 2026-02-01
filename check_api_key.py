#!/usr/bin/env python3
"""
Check if Watson Orchestrate API Key is Valid - Using IAM Authentication
"""

import os
import sys
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
    
    try:
        print("🔑 Getting IAM token...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ Got IAM token: {token[:20]}...{token[-10:]}\n")
            return token
        else:
            print(f"❌ Failed to get IAM token: {response.status_code}")
            print(f"   Response: {response.text[:200]}\n")
            return None
    
    except Exception as e:
        print(f"❌ Error getting IAM token: {str(e)}\n")
        return None

def check_api_key():
    """Check if the API key is valid"""
    
    api_key = os.environ.get("WATSON_ORCHESTRATE_API_KEY")
    
    print("\n" + "="*60)
    print("🔐 Watson Orchestrate API Key Checker (IAM Auth)")
    print("="*60 + "\n")
    
    if not api_key:
        print("❌ No API key found!")
        print("\nTo set your API key, run:")
        print("  export WATSON_ORCHESTRATE_API_KEY='OppiS4ojVge4xPtJF8G6fulSF-VqgPM6R9vilzCPazCo'\n")
        print("Then verify it:")
        print("  python3 check_api_key_fixed.py\n")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...{api_key[-4:]}\n")
    
    # Get IAM token first
    iam_token = get_iam_token(api_key)
    if not iam_token:
        return False
    
    # Now test the endpoints with the IAM token
    print("🧪 Testing Watson Orchestrate endpoints...\n")
    
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }
    
    # Use the correct instance URL from your credentials
    base_url = "https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4/v1"
    
    endpoints = [
        ("Agents", f"{base_url}/agents"),
        ("Tools", f"{base_url}/tools"),
    ]
    
    valid = False
    
    for name, url in endpoints:
        try:
            print(f"Testing {name} endpoint...")
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ {name}: Valid (200 OK)")
                valid = True
                break
            elif response.status_code == 401:
                print(f"  ❌ {name}: Unauthorized (401) - Token issue")
            elif response.status_code == 403:
                print(f"  ❌ {name}: Forbidden (403) - No permission")
            elif response.status_code == 404:
                print(f"  ⚠️  {name}: Not found (404)")
                # If one endpoint 404s, doesn't mean key is bad
                if name == "Tools":
                    valid = True  # Key works, endpoint might be different
            else:
                print(f"  ⚠️  {name}: Error {response.status_code}")
                if response.text:
                    print(f"     Response: {response.text[:150]}")
        
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ {name}: Connection error - {str(e)[:100]}")
        except requests.exceptions.Timeout:
            print(f"  ⏱️  {name}: Timeout")
        except Exception as e:
            print(f"  ❌ {name}: Error - {str(e)[:100]}")
    
    print("\n" + "="*60 + "\n")
    
    if valid:
        print("✅ API Key is VALID!")
        print("\nYou can now import agents:")
        print("  export WATSON_ORCHESTRATE_API_KEY='OppiS4ojVge4xPtJF8G6fulSF-VqgPM6R9vilzCPazCo'")
        print("  python3 import_agents_via_api.py\n")
        return True
    else:
        print("❌ API Key appears to be INVALID or NOT ACCESSIBLE")
        print("\nTroubleshooting steps:")
        print("  1. Verify API key is correct:")
        print("     echo $WATSON_ORCHESTRATE_API_KEY")
        print("  2. Check it's the full key (80+ characters)")
        print("  3. Ensure it's not expired (check IBM Cloud)")
        print("  4. Check internet connection")
        print("  5. Try getting a new API key from IBM Cloud\n")
        return False

if __name__ == "__main__":
    success = check_api_key()
    sys.exit(0 if success else 1)