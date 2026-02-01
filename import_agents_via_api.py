#!/usr/bin/env python3
"""
Native Agent Import Script for IBM Watson Orchestrate
This script imports all 6 native agents from YAML files into Orchestrate
"""

import os
import sys
import json
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration - Load from environment
ORCHESTRATE_API_URL = os.getenv(
    "ORCHESTRATE_API_URL",
    "https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/default/v1"
)
AGENTS_DIR = Path(__file__).parent / "backend" / "agents"
IAM_URL = os.getenv("IBM_IAM_URL", "https://iam.cloud.ibm.com/identity/token")

class OrchestrateAgentImporter:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.iam_token = None
        self.imported_agents = []
        self.failed_agents = []
        
        # Get IAM token
        self.iam_token = self._get_iam_token()
        if not self.iam_token:
            raise Exception("Failed to get IAM token")
        
        self.headers = {
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json"
        }

    def _get_iam_token(self) -> str:
        """Get IAM token from API key"""
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key,
            "response_type": "cloud_iam"
        }
        
        try:
            print("🔑 Getting IAM token...")
            response = requests.post(IAM_URL, headers=headers, data=data, timeout=10)
            
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

    def load_agent_yaml(self, yaml_file: Path) -> Dict:
        """Load and parse a native agent YAML file"""
        try:
            with open(yaml_file, 'r') as f:
                agent_data = yaml.safe_load(f)
            print(f"✅ Loaded: {yaml_file.name}")
            return agent_data
        except Exception as e:
            print(f"❌ Failed to load {yaml_file.name}: {e}")
            return None

    def validate_agent(self, agent: Dict) -> Tuple[bool, str]:
        """Validate agent has required fields"""
        required_fields = ['spec_version', 'kind', 'name', 'display_name', 'description', 'instructions', 'llm', 'tools']
        
        for field in required_fields:
            if field not in agent:
                return False, f"Missing required field: {field}"
        
        if agent.get('spec_version') != 'v1':
            return False, f"Invalid spec_version: {agent.get('spec_version')}"
        
        if agent.get('kind') != 'native':
            return False, f"Invalid kind: {agent.get('kind')}"
        
        return True, "Valid"

    def import_agent(self, agent: Dict) -> Tuple[bool, str]:
        """Import a single agent via Orchestrate API"""
        agent_name = agent.get('name')
        
        # Prepare payload
        payload = {
            "spec_version": agent.get('spec_version'),
            "kind": agent.get('kind'),
            "name": agent_name,
            "display_name": agent.get('display_name'),
            "description": agent.get('description'),
            "instructions": agent.get('instructions'),
            "style": agent.get('style', 'default'),
            "llm": agent.get('llm'),
            "tools": agent.get('tools', []),
            "collaborators": agent.get('collaborators', []),
            "hide_reasoning": agent.get('hide_reasoning', False),
            "restrictions": agent.get('restrictions', 'editable'),
        }
        
        if 'icon' in agent:
            payload['icon'] = agent['icon']
        
        try:
            # First check if agent exists
            check_url = f"{ORCHESTRATE_API_URL}/agents/{agent_name}"
            check_response = requests.get(check_url, headers=self.headers, timeout=10)
            
            if check_response.status_code == 200:
                # Agent exists, update it
                print(f"  🔄 Agent exists, updating: {agent_name}")
                response = requests.put(
                    check_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10
                )
            else:
                # Create new agent
                create_url = f"{ORCHESTRATE_API_URL}/agents"
                response = requests.post(
                    create_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10
                )
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Imported: {agent_name}")
                return True, response.json()
            elif response.status_code == 401:
                return False, "❌ Authentication failed (401). Check API key."
            elif response.status_code == 403:
                return False, "❌ Permission denied (403). Check IAM roles."
            elif response.status_code == 409:
                return False, f"❌ Agent already exists: {agent_name}"
            else:
                error_msg = response.text[:200] if response.text else "Unknown error"
                return False, f"❌ API error {response.status_code}: {error_msg}"
        
        except requests.exceptions.ConnectionError:
            return False, f"❌ Connection error. Check API endpoint: {ORCHESTRATE_API_URL}"
        except requests.exceptions.Timeout:
            return False, "❌ Request timeout. Try again."
        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    def import_all_agents(self) -> Dict:
        """Import all agent YAML files from agents directory"""
        print("\n" + "="*60)
        print("🚀 Watson Orchestrate Native Agent Importer")
        print("="*60 + "\n")

        # Find all YAML files
        if not AGENTS_DIR.exists():
            print(f"❌ Agents directory not found: {AGENTS_DIR}")
            return {"success": False, "agents": []}

        yaml_files = sorted(AGENTS_DIR.glob("*.yaml"))
        
        if not yaml_files:
            print(f"❌ No YAML files found in: {AGENTS_DIR}")
            return {"success": False, "agents": []}

        print(f"📁 Found {len(yaml_files)} agent files:\n")
        for f in yaml_files:
            print(f"   • {f.name}")
        
        print("\n" + "-"*60 + "\n")

        # Load and validate all agents
        agents_to_import = []
        for yaml_file in yaml_files:
            agent_data = self.load_agent_yaml(yaml_file)
            if agent_data:
                is_valid, msg = self.validate_agent(agent_data)
                if is_valid:
                    agents_to_import.append(agent_data)
                else:
                    print(f"  ⚠️  Invalid agent {yaml_file.name}: {msg}\n")
        
        if not agents_to_import:
            print("❌ No valid agents to import")
            return {"success": False, "agents": []}

        print(f"\n✅ Validated {len(agents_to_import)} agents\n")
        print("-"*60 + "\n")

        # Import each agent
        print("📤 Importing agents...\n")
        
        for agent in agents_to_import:
            agent_name = agent.get('name')
            success, result = self.import_agent(agent)
            
            if success:
                self.imported_agents.append({
                    "name": agent_name,
                    "status": "imported",
                    "display_name": agent.get('display_name')
                })
            else:
                self.failed_agents.append({
                    "name": agent_name,
                    "error": result
                })
                print(f"  {result}")

        return self.get_summary()

    def get_summary(self) -> Dict:
        """Return import summary"""
        print("\n" + "="*60)
        print("📊 Import Summary")
        print("="*60 + "\n")

        print(f"✅ Imported: {len(self.imported_agents)}")
        for agent in self.imported_agents:
            print(f"   • {agent['display_name']} ({agent['name']})")

        if self.failed_agents:
            print(f"\n❌ Failed: {len(self.failed_agents)}")
            for agent in self.failed_agents:
                print(f"   • {agent['name']}: {agent['error']}")

        print("\n" + "="*60 + "\n")

        return {
            "success": len(self.failed_agents) == 0,
            "imported": len(self.imported_agents),
            "failed": len(self.failed_agents),
            "agents": self.imported_agents,
            "errors": self.failed_agents
        }

    def verify_imports(self) -> None:
        """Verify imported agents exist"""
        print("🔍 Verifying imports...\n")
        
        for agent_info in self.imported_agents:
            agent_name = agent_info['name']
            try:
                url = f"{ORCHESTRATE_API_URL}/agents/{agent_name}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    agent_data = response.json()
                    print(f"✅ Verified: {agent_info['display_name']}")
                    print(f"   Status: {agent_data.get('status', 'Unknown')}")
                else:
                    print(f"⚠️  Not found: {agent_name}")
            except Exception as e:
                print(f"⚠️  Error verifying {agent_name}: {e}")

def main():
    """Main entry point"""
    
    # Get API key from environment
    api_key = os.environ.get("WATSON_ORCHESTRATE_API_KEY")
    
    if not api_key:
        print("\n" + "="*60)
        print("❌ Error: No API Key Provided")
        print("="*60 + "\n")
        print("To use this script, set your API key in .env or environment:\n")
        print("  export WATSON_ORCHESTRATE_API_KEY='<your-api-key-from-ibm-cloud>'\n")
        print("Then run:")
        print("  python3 import_agents_via_api.py\n")
        print("="*60 + "\n")
        sys.exit(1)

    try:
        # Import agents
        importer = OrchestrateAgentImporter(api_key)
        result = importer.import_all_agents()

        # Verify imports if successful
        if result["success"] and result["imported"] > 0:
            time.sleep(2)  # Wait for agents to be registered
            importer.verify_imports()

        print("\n📋 Next Steps:")
        print("  1. Go to: https://orchestrate.cloud.ibm.com/")
        print("  2. Navigate to: Manage Agents")
        print("  3. Verify all agents are listed")
        print("  4. Deploy agents to make them live")
        print("\n")

        sys.exit(0 if result["success"] else 1)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()