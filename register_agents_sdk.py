#!/usr/bin/env python3
"""
One-command agent registration using SDK
Run this after starting the backend!
"""

import asyncio
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def main():
    print("\n" + "="*60)
    print("🚀 HackTheAgent SDK Agent Registration")
    print("="*60 + "\n")
    
    # Import after path is set
    from app.agent_registry_sdk import (
        get_agent_registry, 
        get_hacktheagent_agents,
        register_all_agents
    )
    from app.config import settings
    
    print("📋 Configuration Check")
    print("-" * 60)
    
    if not settings.orchestrator_api_key:
        print("❌ ORCHESTRATOR_API_KEY not set in .env")
        print("   Update backend/.env with valid Orchestrate API key")
        return False
    
    if not settings.orchestrator_base_url:
        print("❌ ORCHESTRATOR_BASE_URL not set in .env")
        return False
    
    print("✓ API Key configured")
    print(f"  Length: {len(settings.orchestrator_api_key)} chars")
    print(f"✓ Base URL configured")
    print(f"  Instance: {settings.orchestrator_base_url.split('/instances/')[-1]}")
    print()
    
    print("🔍 Loading Agent Definitions")
    print("-" * 60)
    
    agents = get_hacktheagent_agents()
    print(f"✓ Loaded {len(agents)} agents")
    
    for i, agent in enumerate(agents, 1):
        tool_count = len(agent.capabilities)
        print(f"  {i}. {agent.agent_name}")
        print(f"     └─ {tool_count} tools")
    print()
    
    print("🔌 Testing Connection")
    print("-" * 60)
    
    registry = get_agent_registry()
    if not registry:
        print("❌ Could not initialize registry")
        return False
    
    print("✓ Registry initialized")
    print(f"  API Key: {settings.orchestrator_api_key[:20]}...{settings.orchestrator_api_key[-10:]}")
    print(f"  Base URL: {settings.orchestrator_base_url}")
    print()
    
    print("📤 Registering Agents with IBM Orchestrate")
    print("-" * 60)
    print()
    
    result = await register_all_agents()
    
    if result.get("status") == "success":
        print("✅ REGISTRATION SUCCESSFUL!")
        print()
        print(f"   Agents Registered: {result.get('agents_registered', 0)}")
        print(f"   Message: {result.get('message', 'Success')}")
        print()
        print("Agents:")
        if result.get('agents'):
            for agent in result['agents']:
                print(f"  ✓ {agent}")
        print()
        return True
    else:
        print("❌ REGISTRATION FAILED")
        print()
        if "error" in result:
            error = result['error']
            if "401" in str(error):
                print("   Error: 401 Unauthorized")
                print("   Cause: Invalid or expired API key")
                print()
                print("   Fix:")
                print("   1. Go to https://cloud.ibm.com/")
                print("   2. Watson Orchestrate → Access Management → API Keys")
                print("   3. Create or regenerate API key")
                print("   4. Update backend/.env with new key")
                print("   5. Restart backend and try again")
            else:
                print(f"   Error: {error}")
        print()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        
        print("=" * 60)
        if success:
            print("✅ Next Steps:")
            print("   1. Check IBM Orchestrate dashboard")
            print("   2. See all 6 agents in Agents section")
            print("   3. Build workflows using these agents")
        else:
            print("❌ Fix errors above and try again")
        print("=" * 60 + "\n")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
