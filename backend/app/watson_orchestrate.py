"""
IBM Watson Orchestrate Client Integration
Connects backend to Watson Orchestrate agents via API
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
import logging
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WatsonOrchestrateClient:
    """Client for interacting with Watson Orchestrate agents"""
    
    # Agent names that are imported
    AVAILABLE_AGENTS = [
        "intent_detection_agent",
        "semantic_search_agent",
        "classification_agent",
        "rag_generation_agent",
        "threat_detection_agent",
        "database_persistence_agent"
    ]
    
    def __init__(self):
        self.api_key = os.getenv("WATSON_ORCHESTRATE_API_KEY")
        self.instance_id = os.getenv("WATSON_INSTANCE_ID", "")
        self.region = os.getenv("WATSON_REGION", "us-south")
        self.base_url = os.getenv(
            "WATSON_ORCHESTRATE_BASE_URL",
            f"https://api.{self.region}.watson-orchestrate.cloud.ibm.com/instances/{self.instance_id}"
        )
        self.iam_url = os.getenv("IBM_IAM_URL", "https://iam.cloud.ibm.com/identity/token")
        self.iam_token = None
        
        if not self.api_key:
            raise ValueError("WATSON_ORCHESTRATE_API_KEY not set in environment")
        
        if not self.instance_id and "instances/" not in self.base_url:
            raise ValueError("WATSON_INSTANCE_ID or WATSON_ORCHESTRATE_BASE_URL must be set in environment")
        
        self._get_iam_token()
        logger.info("✅ Watson Orchestrate Client Initialized")
    
    def _get_iam_token(self) -> str:
        """Get IAM authentication token"""
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
            response = requests.post(self.iam_url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                self.iam_token = response.json().get("access_token")
                logger.info("🔑 Got IAM token for Orchestrate")
                return self.iam_token
            else:
                logger.error(f"❌ Failed to get IAM token: {response.status_code}")
                raise Exception(f"IAM token error: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error getting IAM token: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization"""
        return {
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json"
        }
    
    def invoke_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a Watson Orchestrate agent
        
        Args:
            agent_name: Name of the agent to invoke
            input_data: Input data for the agent
        
        Returns:
            Agent response
        """
        if agent_name not in self.AVAILABLE_AGENTS:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found. Available: {self.AVAILABLE_AGENTS}"
            }
        
        # Try different endpoint patterns
        endpoints = [
            f"{self.base_url}/v1/agents/{agent_name}/invoke",
            f"{self.base_url}/agents/{agent_name}/invoke",
            f"{self.base_url}/v1/agents/{agent_name}",
            f"{self.base_url}/agents/{agent_name}",
        ]
        
        for url in endpoints:
            try:
                logger.info(f"🤖 Invoking agent: {agent_name} at {url}")
                
                response = requests.post(
                    url,
                    json=input_data,
                    headers=self._get_headers(),
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"✅ Agent {agent_name} completed successfully")
                    return {
                        "success": True,
                        "agent": agent_name,
                        "result": result
                    }
                elif response.status_code == 404:
                    # Try next endpoint
                    continue
                else:
                    logger.error(f"❌ Agent invocation failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return {
                        "success": False,
                        "agent": agent_name,
                        "error": response.text,
                        "status_code": response.status_code
                    }
            
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️  Timeout on {url}")
                continue
            except Exception as e:
                logger.warning(f"⚠️  Error on {url}: {e}")
                continue
        
        # If all endpoints fail
        return {
            "success": False,
            "agent": agent_name,
            "error": f"All endpoint attempts failed",
            "attempted_urls": endpoints
        }
    
    def parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse user intent using Intent Detection Agent"""
        input_data = {
            "query": query
        }
        return self.invoke_agent("intent_detection_agent", input_data)
    
    def semantic_search(self, query: str, email_ids: Optional[List] = None) -> Dict[str, Any]:
        """Search emails using Semantic Search Agent"""
        input_data = {
            "query": query,
            "email_ids": email_ids or []
        }
        return self.invoke_agent("semantic_search_agent", input_data)
    
    def classify_emails(self, emails: List[Dict]) -> Dict[str, Any]:
        """Classify emails using Classification Agent"""
        input_data = {
            "emails": emails
        }
        return self.invoke_agent("classification_agent", input_data)
    
    def generate_answer(self, query: str, context: List) -> Dict[str, Any]:
        """Generate grounded answer using RAG Generation Agent"""
        input_data = {
            "query": query,
            "context": context
        }
        return self.invoke_agent("rag_generation_agent", input_data)
    
    def detect_threats(self, emails: List[Dict]) -> Dict[str, Any]:
        """Detect security threats using Threat Detection Agent"""
        input_data = {
            "emails": emails
        }
        return self.invoke_agent("threat_detection_agent", input_data)
    
    def persist_data(self, data_type: str, data: Any) -> Dict[str, Any]:
        """Store data using Database Persistence Agent"""
        input_data = {
            "data_type": data_type,
            "data": data
        }
        return self.invoke_agent("database_persistence_agent", input_data)
    
    def list_agents(self) -> Dict[str, Any]:
        """List all available agents"""
        return {
            "agents": [
                {
                    "name": name,
                    "status": "imported",
                    "available": True
                }
                for name in self.AVAILABLE_AGENTS
            ],
            "count": len(self.AVAILABLE_AGENTS)
        }
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        if agent_name in self.AVAILABLE_AGENTS:
            return {
                "name": agent_name,
                "status": "imported",
                "available": True
            }
        else:
            return {
                "name": agent_name,
                "status": "not_found",
                "available": False,
                "error": f"Agent '{agent_name}' not found"
            }
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        return {
            agent: self.get_agent_status(agent)
            for agent in self.AVAILABLE_AGENTS
        }


# Singleton instance
_orchestrate_client = None

def get_orchestrate_client() -> WatsonOrchestrateClient:
    """Get or create Orchestrate client"""
    global _orchestrate_client
    if _orchestrate_client is None:
        try:
            _orchestrate_client = WatsonOrchestrateClient()
        except Exception as e:
            logger.error(f"Failed to initialize Watson Orchestrate client: {e}")
            raise
    return _orchestrate_client