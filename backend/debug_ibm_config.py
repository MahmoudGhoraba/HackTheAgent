#!/usr/bin/env python3
"""
IBM Orchestrate Configuration Debugger
Helps diagnose why IBM Orchestrate is returning 401
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_configuration():
    """Check IBM Orchestrate configuration"""
    from app.config import settings
    
    print("=" * 70)
    print("IBM ORCHESTRATE CONFIGURATION DEBUG")
    print("=" * 70)
    print()
    
    print("1. API KEY CHECK")
    print("-" * 70)
    if settings.orchestrator_api_key:
        print(f"   ✅ API Key is set")
        print(f"   Key preview: {settings.orchestrator_api_key[:20]}...")
        print(f"   Key length: {len(settings.orchestrator_api_key)} characters")
        
        # Check if it looks valid
        if settings.orchestrator_api_key.startswith("your-"):
            print("   ⚠️  WARNING: This looks like a placeholder key!")
        elif len(settings.orchestrator_api_key) < 20:
            print("   ⚠️  WARNING: Key seems too short to be valid")
        else:
            print("   ✅ Key format looks valid")
    else:
        print("   ❌ API Key is NOT set")
        print("   → System will use local orchestrator")
    
    print()
    print("2. BASE URL CHECK")
    print("-" * 70)
    if settings.orchestrator_base_url:
        print(f"   ✅ Base URL is set")
        print(f"   URL: {settings.orchestrator_base_url}")
        
        # Check URL format
        if "watson-orchestrate" in settings.orchestrator_base_url:
            print("   ✅ URL format looks correct (watson-orchestrate)")
        
        if "/instances/" in settings.orchestrator_base_url:
            print("   ✅ URL includes instance ID")
            # Extract instance ID
            instance_part = settings.orchestrator_base_url.split("/instances/")[1] if "/instances/" in settings.orchestrator_base_url else "unknown"
            print(f"   Instance ID: {instance_part}")
        else:
            print("   ⚠️  WARNING: URL doesn't include /instances/ path")
            print("   → This might cause 401 errors")
    else:
        print("   ❌ Base URL is NOT set")
    
    print()
    print("3. IMPORT CHECK")
    print("-" * 70)
    try:
        from app.ibm_orchestrate import IBMOrchestrateClient
        print("   ✅ IBMOrchestrateClient imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import IBMOrchestrateClient: {e}")
    
    try:
        from app.orchestrator import IBM_ORCHESTRATE_AVAILABLE
        print(f"   ✅ IBM_ORCHESTRATE_AVAILABLE = {IBM_ORCHESTRATE_AVAILABLE}")
    except Exception as e:
        print(f"   ❌ Failed to check IBM availability: {e}")
    
    print()
    print("4. RECOMMENDATIONS")
    print("-" * 70)
    
    if settings.orchestrator_api_key and "your-" not in settings.orchestrator_api_key:
        print("   Your credentials appear to be set. If you're getting 401 errors:")
        print()
        print("   Option A: Use Local Orchestrator (RECOMMENDED)")
        print("   → Replace in .env:")
        print("      ORCHESTRATOR_API_KEY=your-orchestrate-api-key")
        print("   → This will use the built-in local orchestrator (fully working)")
        print()
        print("   Option B: Fix IBM Orchestrate Credentials")
        print("   → Verify credentials at: https://cloud.ibm.com/")
        print("   → Check API key is not expired")
        print("   → Verify instance URL matches your account")
        print("   → Ensure key has required permissions")
        print()
        print("   Option C: Create New IBM Orchestrate Credentials")
        print("   → Go to: https://cloud.ibm.com/iam/apikeys")
        print("   → Create new API key")
        print("   → Go to: https://cloud.ibm.com/orchestrate/")
        print("   → Get your instance URL")
        print("   → Update .env with new credentials")
    else:
        print("   ✅ System will use LOCAL ORCHESTRATOR (no IBM credentials needed)")
        print("   → All features working with built-in implementation")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    try:
        check_configuration()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
