#!/usr/bin/env python3
"""
Quick test of the workflow - should now fallback gracefully
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_workflow():
    from app.orchestrator import MultiAgentOrchestrator
    from app.config import settings
    
    print("=" * 60)
    print("Testing Workflow Execution")
    print("=" * 60)
    print()
    
    print(f"Orchestrator API Key: {settings.orchestrator_api_key}")
    print(f"  - Is placeholder? {settings.orchestrator_api_key.startswith('your-') if settings.orchestrator_api_key else 'N/A'}")
    print()
    
    orchestrator = MultiAgentOrchestrator()
    
    print("Testing query: 'hi'")
    print()
    
    try:
        result = await orchestrator.execute_workflow("hi", top_k=5, enable_rag=False)
        
        print(f"✅ Workflow executed successfully!")
        print(f"  Execution ID: {result.execution_id}")
        print(f"  Intent: {result.intent}")
        print(f"  Status: {result.status.value if hasattr(result.status, 'value') else result.status}")
        print(f"  Steps executed: {len(result.steps)}")
        print()
        
        if result.steps:
            print("  Steps:")
            for i, step in enumerate(result.steps, 1):
                if hasattr(step, 'name'):
                    print(f"    {i}. {step.name}")
                else:
                    print(f"    {i}. {step}")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow())
