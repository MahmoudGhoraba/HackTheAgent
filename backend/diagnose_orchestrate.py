#!/usr/bin/env python3
"""
Diagnose IBM Orchestrate connection issues
"""
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

print("=" * 60)
print("IBM ORCHESTRATE CONNECTION DIAGNOSTIC")
print("=" * 60)

api_key = os.getenv("ORCHESTRATOR_API_KEY", "").strip()
base_url = os.getenv("ORCHESTRATOR_BASE_URL", "").strip()

print("\n📋 CONFIGURATION CHECK:")
print("-" * 60)

if not api_key:
    print("❌ ORCHESTRATOR_API_KEY is MISSING or EMPTY")
else:
    print(f"✓ ORCHESTRATOR_API_KEY is set")
    print(f"  Length: {len(api_key)} characters")
    print(f"  Preview: {api_key[:20]}...{api_key[-10:]}")

if not base_url:
    print("❌ ORCHESTRATOR_BASE_URL is MISSING or EMPTY")
else:
    print(f"✓ ORCHESTRATOR_BASE_URL is set")
    print(f"  Value: {base_url}")

print("\n🔌 CONNECTION TEST:")
print("-" * 60)

if not api_key or not base_url:
    print("❌ Cannot test connection - credentials missing!")
    print("\n💡 FIX: Update backend/.env with valid Orchestrate credentials")
    print("   Get them from IBM Cloud Dashboard:")
    print("   1. Go to https://cloud.ibm.com/")
    print("   2. Select Watson Orchestrate instance")
    print("   3. Access Management → Users → API Keys")
    print("   4. Create or regenerate API key")
    print("   5. Update backend/.env:")
    print("      ORCHESTRATOR_API_KEY=<new_key>")
    print("      ORCHESTRATOR_BASE_URL=https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/<instance-id>")
else:
    try:
        # Test basic connectivity
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Try to get instance info (simple endpoint)
        test_url = f"{base_url}/v1/agents/list"
        
        print(f"Testing: {test_url}")
        print(f"Auth: Bearer {api_key[:20]}...")
        
        with httpx.Client() as client:
            response = client.get(test_url, headers=headers, timeout=10.0)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ CONNECTION SUCCESSFUL!")
                print(f"Response: {response.json()}")
            elif response.status_code == 401:
                print("❌ AUTHENTICATION FAILED (401 Unauthorized)")
                print("\n💡 SOLUTIONS:")
                print("   1. API Key is INVALID or EXPIRED")
                print("   2. API Key is for wrong service (not Orchestrate)")
                print("   3. API Key format is incorrect")
                print("\n🔧 ACTION REQUIRED:")
                print("   Get new Orchestrate API Key from IBM Cloud:")
                print("   https://cloud.ibm.com/ → Watson Orchestrate → Access Management → API Keys")
                print("\n   Then update backend/.env:")
                print("   ORCHESTRATOR_API_KEY=<your_new_key_here>")
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("\n💡 Possible issues:")
        print("   - Network connectivity problem")
        print("   - Invalid base URL")
        print("   - IBM Orchestrate service is down")

print("\n" + "=" * 60)
print("END DIAGNOSTIC")
print("=" * 60)
