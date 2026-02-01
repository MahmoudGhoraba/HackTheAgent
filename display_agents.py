#!/usr/bin/env python3
"""
Display all agent YAML files for easy copying to Orchestrate UI
"""

from pathlib import Path
import yaml

def display_agents():
    agents_dir = Path(__file__).parent / "backend" / "agents"
    
    print("\n" + "="*80)
    print("📋 AGENT YAML FILES - READY FOR MANUAL IMPORT")
    print("="*80 + "\n")
    
    yaml_files = sorted(agents_dir.glob("*.yaml"))
    
    if not yaml_files:
        print(f"❌ No YAML files found in {agents_dir}")
        return
    
    for i, yaml_file in enumerate(yaml_files, 1):
        print(f"\n{'='*80}")
        print(f"Agent {i}/{len(yaml_files)}: {yaml_file.name}")
        print(f"{'='*80}\n")
        
        try:
            with open(yaml_file, 'r') as f:
                content = f.read()
            
            # Display content
            print(content)
            
            # Parse to show summary
            data = yaml.safe_load(content)
            print(f"\n{'─'*80}")
            print(f"Name: {data.get('display_name')}")
            print(f"ID: {data.get('name')}")
            print(f"Description: {data.get('description', 'N/A')[:100]}...")
            print(f"Tools: {', '.join(data.get('tools', []))}")
            
        except Exception as e:
            print(f"❌ Error reading {yaml_file.name}: {e}")
    
    print(f"\n{'='*80}")
    print("✅ All agents ready for import!")
    print(f"{'='*80}\n")
    
    print("\n📝 HOW TO IMPORT:")
    print("1. Go to: https://orchestrate.cloud.ibm.com/")
    print("2. Click: Manage Agents")
    print("3. Click: Import Agent or Create Agent")
    print("4. Paste the YAML content above")
    print("5. Click: Import/Create")
    print("6. Repeat for all 6 agents\n")

if __name__ == "__main__":
    display_agents()
