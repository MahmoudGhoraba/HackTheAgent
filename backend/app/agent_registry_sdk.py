"""
IBM Watson SDK-based Agent Registration & Export

Uses the IBM Watson SDK to register HackTheAgent agents with IBM Orchestrate platform.
More robust and maintainable than raw HTTP calls.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_cloud_sdk_core.get_authenticator import get_authenticator_from_environment

logger = logging.getLogger(__name__)


class AgentCapability(BaseModel):
    """Agent capability/tool definition"""
    tool_id: str
    tool_name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class AgentDefinition(BaseModel):
    """Complete agent definition for Orchestrate registration"""
    agent_id: str
    agent_name: str
    agent_type: str
    description: str
    version: str
    status: str  # ACTIVE, DISABLED, DEPRECATED
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    capabilities: List[AgentCapability] = []
    config: Dict[str, Any] = {}
    endpoints: Dict[str, str] = {}


class OrchestrateAgentRegistry:
    """
    Registers and manages local agents in IBM Orchestrate using Watson SDK
    Exports agents as native Orchestrate agents with tool integration
    """
    
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize agent registry with IBM Watson SDK
        
        Args:
            api_key: IBM Orchestrate API key
            base_url: IBM Orchestrate base URL (e.g., https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/...)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.instance_id = self._extract_instance_id(base_url)
        
        # Initialize authenticator
        self.authenticator = BearerTokenAuthenticator(bearer_token=api_key)
        
        logger.info(f"Initialized Orchestrate Agent Registry")
        logger.info(f"  Instance ID: {self.instance_id}")
        logger.info(f"  Base URL: {self.base_url}")
    
    def _extract_instance_id(self, base_url: str) -> str:
        """Extract instance ID from base URL"""
        try:
            return base_url.split("/instances/")[-1]
        except:
            return "unknown"
    
    def _prepare_agent_payload(self, agent_def: AgentDefinition) -> Dict[str, Any]:
        """Prepare agent definition for SDK registration"""
        return {
            "agent_id": agent_def.agent_id,
            "agent_name": agent_def.agent_name,
            "agent_type": agent_def.agent_type,
            "description": agent_def.description,
            "version": agent_def.version,
            "status": agent_def.status,
            "input_schema": agent_def.input_schema,
            "output_schema": agent_def.output_schema,
            "capabilities": [
                {
                    "tool_id": cap.tool_id,
                    "tool_name": cap.tool_name,
                    "description": cap.description,
                    "input_schema": cap.input_schema,
                    "output_schema": cap.output_schema
                } for cap in agent_def.capabilities
            ],
            "config": agent_def.config,
            "endpoints": agent_def.endpoints
        }
    
    async def register_agent(self, agent_def: AgentDefinition) -> Dict[str, Any]:
        """
        Register a local agent with IBM Orchestrate using Watson SDK
        
        Args:
            agent_def: Agent definition to register
            
        Returns:
            Registration response from Orchestrate
        """
        try:
            import requests
            
            url = f"{self.base_url}/v1/agents/register"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = self._prepare_agent_payload(agent_def)
            
            logger.info(f"Registering agent: {agent_def.agent_name}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Agent registered: {agent_def.agent_name}")
                return {
                    "status": "success",
                    "agent_id": agent_def.agent_id,
                    "message": f"Agent {agent_def.agent_name} registered successfully"
                }
            else:
                error_msg = response.text
                logger.error(f"✗ Failed to register {agent_def.agent_name}: {response.status_code}")
                logger.error(f"  Response: {error_msg}")
                return {
                    "status": "error",
                    "agent_id": agent_def.agent_id,
                    "error": error_msg,
                    "status_code": response.status_code
                }
        
        except Exception as e:
            logger.error(f"Exception registering agent {agent_def.agent_id}: {str(e)}")
            return {
                "status": "error",
                "agent_id": agent_def.agent_id,
                "error": str(e)
            }
    
    async def register_all_agents(self, agents: List[AgentDefinition]) -> Dict[str, Any]:
        """
        Register multiple agents with IBM Orchestrate using batch endpoint
        
        Args:
            agents: List of agent definitions to register
            
        Returns:
            Batch registration response
        """
        try:
            import requests
            
            url = f"{self.base_url}/v1/agents/register-batch"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payloads = [self._prepare_agent_payload(agent) for agent in agents]
            
            logger.info(f"Batch registering {len(agents)} agents...")
            
            response = requests.post(
                url,
                json={"agents": payloads},
                headers=headers,
                timeout=60
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Batch registration successful: {len(agents)} agents")
                return {
                    "status": "success",
                    "agents_registered": len(agents),
                    "message": f"Successfully registered {len(agents)} agents"
                }
            else:
                error_msg = response.text
                logger.error(f"✗ Batch registration failed: {response.status_code}")
                logger.error(f"  Response: {error_msg}")
                return {
                    "status": "error",
                    "agents_registered": 0,
                    "error": error_msg,
                    "status_code": response.status_code
                }
        
        except Exception as e:
            logger.error(f"Exception in batch registration: {str(e)}")
            return {
                "status": "error",
                "agents_registered": 0,
                "error": str(e)
            }
    
    async def list_agents(self) -> Dict[str, Any]:
        """
        List all registered agents from IBM Orchestrate
        
        Returns:
            List of registered agents
        """
        try:
            import requests
            
            url = f"{self.base_url}/v1/agents/list"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info("✓ Retrieved agent list")
                return response.json()
            else:
                logger.error(f"Failed to list agents: {response.status_code}")
                return {
                    "status": "error",
                    "error": response.text
                }
        
        except Exception as e:
            logger.error(f"Exception listing agents: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get specific agent details from IBM Orchestrate
        
        Args:
            agent_id: ID of agent to retrieve
            
        Returns:
            Agent details
        """
        try:
            import requests
            
            url = f"{self.base_url}/v1/agents/{agent_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✓ Retrieved agent: {agent_id}")
                return response.json()
            else:
                logger.error(f"Failed to get agent {agent_id}: {response.status_code}")
                return {
                    "status": "error",
                    "error": response.text
                }
        
        except Exception as e:
            logger.error(f"Exception getting agent {agent_id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_agent(self, agent_def: AgentDefinition) -> Dict[str, Any]:
        """
        Update an existing agent in IBM Orchestrate
        
        Args:
            agent_def: Updated agent definition
            
        Returns:
            Update response
        """
        try:
            import requests
            
            url = f"{self.base_url}/v1/agents/{agent_def.agent_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = self._prepare_agent_payload(agent_def)
            
            response = requests.put(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Agent updated: {agent_def.agent_name}")
                return {
                    "status": "success",
                    "message": f"Agent {agent_def.agent_name} updated"
                }
            else:
                logger.error(f"Failed to update agent: {response.status_code}")
                return {
                    "status": "error",
                    "error": response.text
                }
        
        except Exception as e:
            logger.error(f"Exception updating agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Delete an agent from IBM Orchestrate
        
        Args:
            agent_id: ID of agent to delete
            
        Returns:
            Delete response
        """
        try:
            import requests
            
            url = f"{self.base_url}/v1/agents/{agent_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code in [200, 204]:
                logger.info(f"✓ Agent deleted: {agent_id}")
                return {
                    "status": "success",
                    "message": f"Agent {agent_id} deleted"
                }
            else:
                logger.error(f"Failed to delete agent: {response.status_code}")
                return {
                    "status": "error",
                    "error": response.text
                }
        
        except Exception as e:
            logger.error(f"Exception deleting agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global registry instance
_registry: Optional[OrchestrateAgentRegistry] = None


def get_agent_registry() -> Optional[OrchestrateAgentRegistry]:
    """Get or initialize the global agent registry"""
    global _registry
    
    if _registry is None:
        from app.config import settings
        
        if settings.orchestrator_api_key and settings.orchestrator_base_url:
            _registry = OrchestrateAgentRegistry(
                api_key=settings.orchestrator_api_key,
                base_url=settings.orchestrator_base_url
            )
        else:
            logger.warning("Orchestrate credentials not configured")
    
    return _registry


def get_hacktheagent_agents() -> List[AgentDefinition]:
    """
    Define all 6 HackTheAgent agents with complete schemas and tools
    
    Returns:
        List of agent definitions ready for Orchestrate registration
    """
    agents = [
        # 1. Intent Detection Agent
        AgentDefinition(
            agent_id="intent_detection_agent",
            agent_name="Intent Detection Agent",
            agent_type="email_analysis",
            description="Analyzes user queries to determine intent type and extract entities",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "User query to analyze"},
                    "analyze_entities": {"type": "boolean", "default": True}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "intent_type": {"type": "string"},
                    "confidence": {"type": "number"},
                    "entities": {"type": "array"},
                    "keywords": {"type": "array"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="intent_parser",
                    tool_name="Intent Parser",
                    description="Parses user query to extract primary intent",
                    input_schema={"query": "string"},
                    output_schema={"intent_type": "string", "confidence": "number"}
                ),
                AgentCapability(
                    tool_id="entity_extractor",
                    tool_name="Entity Extractor",
                    description="Extracts named entities from query text",
                    input_schema={"text": "string"},
                    output_schema={"entities": "array", "keywords": "array"}
                )
            ]
        ),
        
        # 2. Semantic Search Agent
        AgentDefinition(
            agent_id="semantic_search_agent",
            agent_name="Semantic Search Agent",
            agent_type="email_analysis",
            description="Performs semantic search over emails using embeddings",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                    "score_threshold": {"type": "number", "default": 0.5}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "results": {"type": "array"},
                    "result_count": {"type": "integer"},
                    "average_score": {"type": "number"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="semantic_indexer",
                    tool_name="Semantic Indexer",
                    description="Indexes emails using Sentence Transformers embeddings",
                    input_schema={"emails": "array"},
                    output_schema={"indexed_count": "integer"}
                ),
                AgentCapability(
                    tool_id="semantic_search_tool",
                    tool_name="Semantic Search",
                    description="Performs semantic search over indexed emails",
                    input_schema={"query": "string", "top_k": "integer"},
                    output_schema={"results": "array"}
                )
            ]
        ),
        
        # 3. Classification Agent
        AgentDefinition(
            agent_id="classification_agent",
            agent_name="Classification Agent",
            agent_type="email_analysis",
            description="Classifies emails by category, priority, and sentiment",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "emails": {"type": "array"},
                    "categories": {"type": "array"},
                    "extract_sentiment": {"type": "boolean", "default": True}
                },
                "required": ["emails"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "classifications": {"type": "array"},
                    "total_classified": {"type": "integer"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="category_classifier",
                    tool_name="Category Classifier",
                    description="Classifies emails into predefined categories",
                    input_schema={"email_text": "string", "categories": "array"},
                    output_schema={"category": "string"}
                ),
                AgentCapability(
                    tool_id="priority_detector",
                    tool_name="Priority Detector",
                    description="Detects priority level of emails",
                    input_schema={"email_text": "string"},
                    output_schema={"priority": "string"}
                ),
                AgentCapability(
                    tool_id="sentiment_analyzer",
                    tool_name="Sentiment Analyzer",
                    description="Analyzes sentiment of email content",
                    input_schema={"text": "string"},
                    output_schema={"sentiment": "string", "score": "number"}
                )
            ]
        ),
        
        # 4. RAG Generation Agent
        AgentDefinition(
            agent_id="rag_generation_agent",
            agent_name="RAG Answer Generation Agent",
            agent_type="email_analysis",
            description="Generates grounded answers using RAG over email context",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "context_emails": {"type": "integer", "default": 5},
                    "generate_citations": {"type": "boolean", "default": True}
                },
                "required": ["question"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "citations": {"type": "array"},
                    "confidence": {"type": "number"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="context_retriever",
                    tool_name="Context Retriever",
                    description="Retrieves relevant email context for RAG",
                    input_schema={"query": "string", "top_k": "integer"},
                    output_schema={"context": "string", "email_ids": "array"}
                ),
                AgentCapability(
                    tool_id="answer_generator",
                    tool_name="Answer Generator",
                    description="Generates answers using LLM with context",
                    input_schema={"question": "string", "context": "string"},
                    output_schema={"answer": "string"}
                ),
                AgentCapability(
                    tool_id="citation_tracker",
                    tool_name="Citation Tracker",
                    description="Tracks citations for grounded answers",
                    input_schema={"answer": "string", "context": "string"},
                    output_schema={"citations": "array"}
                )
            ]
        ),
        
        # 5. Threat Detection Agent
        AgentDefinition(
            agent_id="threat_detection_agent",
            agent_name="Threat Detection Agent",
            agent_type="security",
            description="Detects phishing, malware, and other email threats",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "emails": {"type": "array"},
                    "analyze_phishing": {"type": "boolean", "default": True},
                    "analyze_malware": {"type": "boolean", "default": True}
                },
                "required": ["emails"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "threats_detected": {"type": "integer"},
                    "threat_summary": {"type": "object"},
                    "recommendations": {"type": "array"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="phishing_detector",
                    tool_name="Phishing Detector",
                    description="Detects phishing patterns in emails",
                    input_schema={"email": "object"},
                    output_schema={"is_phishing": "boolean", "score": "number"}
                ),
                AgentCapability(
                    tool_id="domain_analyzer",
                    tool_name="Domain Analyzer",
                    description="Analyzes sender domain reputation",
                    input_schema={"domain": "string"},
                    output_schema={"reputation": "string"}
                ),
                AgentCapability(
                    tool_id="threat_scorer",
                    tool_name="Threat Scorer",
                    description="Calculates overall threat score",
                    input_schema={"threats": "array"},
                    output_schema={"threat_level": "string", "score": "number"}
                )
            ]
        ),
        
        # 6. Database Persistence Agent
        AgentDefinition(
            agent_id="database_persistence_agent",
            agent_name="Database Persistence Agent",
            agent_type="data_management",
            description="Stores workflow execution results and threats to database",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "execution_data": {"type": "object"},
                    "threat_data": {"type": "array"},
                    "persist_execution": {"type": "boolean", "default": True},
                    "persist_threats": {"type": "boolean", "default": True}
                },
                "required": ["execution_data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "execution_stored": {"type": "boolean"},
                    "threats_stored": {"type": "integer"},
                    "query_id": {"type": "string"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="execution_storage",
                    tool_name="Execution Storage",
                    description="Stores workflow execution records",
                    input_schema={"execution_record": "object"},
                    output_schema={"stored": "boolean", "id": "string"}
                ),
                AgentCapability(
                    tool_id="threat_storage",
                    tool_name="Threat Storage",
                    description="Stores threat analysis results",
                    input_schema={"threats": "array"},
                    output_schema={"count": "integer"}
                ),
                AgentCapability(
                    tool_id="analytics_logger",
                    tool_name="Analytics Logger",
                    description="Logs analytics for reporting",
                    input_schema={"event": "object"},
                    output_schema={"logged": "boolean"}
                )
            ]
        )
    ]
    
    return agents


async def register_all_agents() -> Dict[str, Any]:
    """
    Register all HackTheAgent agents with IBM Orchestrate
    
    Returns:
        Registration results
    """
    registry = get_agent_registry()
    
    if not registry:
        logger.error("Agent registry not available")
        return {"error": "Registry not configured"}
    
    try:
        agents = get_hacktheagent_agents()
        
        logger.info(f"Registering {len(agents)} agents with IBM Orchestrate...")
        
        result = await registry.register_all_agents(agents)
        
        logger.info(f"Agent registration result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to register agents: {str(e)}")
        return {"error": str(e)}
