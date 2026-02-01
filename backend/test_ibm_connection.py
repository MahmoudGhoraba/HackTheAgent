#!/usr/bin/env python3
"""
Test IBM Orchestrate API connection directly
"""

import asyncio
import httpx
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_ibm_orchestrate():
    """Test connection to IBM Orchestrate"""
    # Load .env - find it correctly
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    api_key = os.getenv("ORCHESTRATOR_API_KEY")
    base_url = os.getenv("ORCHESTRATOR_BASE_URL")
    
    print("=" * 70)
    print("TESTING IBM ORCHESTRATE CONNECTION")
    print("=" * 70)
    print()
    
    print("Configuration:")
    if api_key:
        print(f"  API Key: {api_key[:30]}...")
    else:
        print("  API Key: NOT SET")
    print(f"  Base URL: {base_url}")
    print()
    
    if not api_key or not base_url:
        print("❌ IBM Orchestrate credentials not fully configured")
        return
    
    # Test 1: Check if URL is valid
    print("Test 1: URL Format")
    print("-" * 70)
    url = base_url
    if url.endswith("/"):
        print("  ⚠️  WARNING: Base URL ends with / - this might cause issues")
    
    # Try to construct workflow run URL
    workflow_url = f"{base_url}/workflows/email_analysis/run"
    print(f"  Workflow URL: {workflow_url}")
    print()
    
    # Test 2: Test HTTP connection
    print("Test 2: HTTP Connection")
    print("-" * 70)
    try:
        async with httpx.AsyncClient() as client:
            # Try a simple test without authentication
            print("  Attempting connection to IBM Orchestrate...")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Try to make a request
            try:
                response = await client.post(
                    workflow_url,
                    headers=headers,
                    json={"user_query": "test", "email_ids": [], "num_results": 5},
                    timeout=10.0
                )
                
                print(f"  Status Code: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
                if response.status_code == 401:
                    print()
                    print("  🔴 401 UNAUTHORIZED")
                    print("  Possible causes:")
                    print("    1. API key is invalid or expired")
                    print("    2. API key doesn't have permission for this instance")
                    print("    3. Base URL is incorrect")
                    print("    4. Authentication header format is wrong")
                elif response.status_code == 404:
                    print()
                    print("  🟡 404 NOT FOUND")
                    print("  Possible causes:")
                    print("    1. Workflow 'email_analysis' doesn't exist")
                    print("    2. Base URL is incorrect")
                elif response.status_code == 200:
                    print()
                    print("  ✅ SUCCESS")
                else:
                    print()
                    print(f"  🟠 Status {response.status_code}")
                    
            except httpx.ConnectError as e:
                print(f"  ❌ Connection Error: {e}")
                print("  → Check that Base URL is correct")
            except httpx.TimeoutException:
                print("  ❌ Timeout connecting to IBM Orchestrate")
                print("  → Service might be down or URL is unreachable")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    print("=" * 70)
    print()
    print("RECOMMENDATION:")
    print("-" * 70)
    print("If you're getting 401 errors:")
    print()
    print("Option 1: Switch to LOCAL ORCHESTRATOR (RECOMMENDED)")
    print("  → In .env, change:")
    print("     ORCHESTRATOR_API_KEY=your-orchestrate-api-key")
    print("  → This will use the built-in local implementation")
    print()
    print("Option 2: Verify IBM Orchestrate Credentials")
    print("  → Check credentials at: https://cloud.ibm.com/")
    print("  → Verify API key hasn't expired")
    print("  → Ensure key has 'Orchestrate' service permissions")
    print()
    print("Option 3: Get new IBM Orchestrate credentials")
    print("  → Visit: https://cloud.ibm.com/iam/apikeys")
    print("  → Create new API key")
    print("  → Visit: https://cloud.ibm.com/orchestrate/")
    print("  → Get your instance URL")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_ibm_orchestrate())
