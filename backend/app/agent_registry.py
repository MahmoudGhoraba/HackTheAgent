"""
IBM Orchestrate Agent Registration & Export

This module registers all local HackTheAgent agents with IBM Orchestrate platform,
making them available as native Orchestrate agents with full tool integration.

The agents are exported with their capabilities, inputs, outputs, and tools
so that Orchestrate can see and manage them as part of the platform.
"""

import logging
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

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
    Registers and manages local agents in IBM Orchestrate
    Exports agents as native Orchestrate agents with tool integration
    """
    
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize agent registry
        
        Args:
            api_key: IBM Orchestrate API key
            base_url: IBM Orchestrate base URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def register_agent(
        self,
        agent_def: AgentDefinition
    ) -> Dict[str, Any]:
        """
        Register a local agent with IBM Orchestrate
        
        Args:
            agent_def: Agent definition to register
            
        Returns:
            Registration response from Orchestrate
        """
        try:
            url = f"{self.base_url}/v1/agents/register"
            
            payload = {
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
                "endpoints": agent_def.endpoints,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Registering agent: {agent_def.agent_name}")
            
            response = await self.client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Agent {agent_def.agent_name} registered successfully")
            return data
            
        except Exception as e:
            logger.error(f"Failed to register agent: {str(e)}")
            raise
    
    async def register_all_agents(
        self,
        agents: List[AgentDefinition]
    ) -> Dict[str, Any]:
        """
        Register multiple agents with Orchestrate
        
        Args:
            agents: List of agent definitions to register
            
        Returns:
            Bulk registration response
        """
        try:
            url = f"{self.base_url}/v1/agents/register-batch"
            
            payload = {
                "agents": [
                    {
                        "agent_id": agent.agent_id,
                        "agent_name": agent.agent_name,
                        "agent_type": agent.agent_type,
                        "description": agent.description,
                        "version": agent.version,
                        "status": agent.status,
                        "input_schema": agent.input_schema,
                        "output_schema": agent.output_schema,
                        "capabilities": [
                            {
                                "tool_id": cap.tool_id,
                                "tool_name": cap.tool_name,
                                "description": cap.description,
                                "input_schema": cap.input_schema,
                                "output_schema": cap.output_schema
                            } for cap in agent.capabilities
                        ],
                        "config": agent.config,
                        "endpoints": agent.endpoints
                    } for agent in agents
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Registering {len(agents)} agents in batch")
            
            response = await self.client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Batch registration completed: {data}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to register agents in batch: {str(e)}")
            raise
    
    async def list_registered_agents(self) -> List[Dict[str, Any]]:
        """List all agents registered in Orchestrate"""
        try:
            url = f"{self.base_url}/v1/agents"
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            agents = data.get('agents', [])
            logger.info(f"Found {len(agents)} registered agents")
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to list agents: {str(e)}")
            return []
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific agent"""
        try:
            url = f"{self.base_url}/v1/agents/{agent_id}"
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {str(e)}")
            return None
    
    async def update_agent(
        self,
        agent_id: str,
        agent_def: AgentDefinition
    ) -> Dict[str, Any]:
        """Update an existing agent registration"""
        try:
            url = f"{self.base_url}/v1/agents/{agent_id}"
            
            payload = {
                "agent_name": agent_def.agent_name,
                "description": agent_def.description,
                "version": agent_def.version,
                "status": agent_def.status,
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
            
            logger.info(f"Updating agent: {agent_id}")
            
            response = await self.client.put(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to update agent: {str(e)}")
            raise
    
    async def unregister_agent(self, agent_id: str) -> Dict[str, Any]:
        """Unregister an agent from Orchestrate"""
        try:
            url = f"{self.base_url}/v1/agents/{agent_id}"
            
            logger.info(f"Unregistering agent: {agent_id}")
            
            response = await self.client.delete(
                url,
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to unregister agent: {str(e)}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Agent definitions for HackTheAgent
def get_hacktheagent_agents() -> List[AgentDefinition]:
    """
    Define all HackTheAgent agents with their capabilities
    
    Returns:
        List of agent definitions ready for Orchestrate registration
    """
    
    agents = [
        # Agent 1: Intent Detection
        AgentDefinition(
            agent_id="intent_detection_agent",
            agent_name="Intent Detection Agent",
            agent_type="email",
            description="Analyzes user queries to determine intent type (search, summarization, analysis, sender_analysis, temporal_search)",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "User's query"},
                    "analyze_entities": {"type": "boolean", "description": "Extract named entities"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "intent_type": {"type": "string", "enum": ["search", "summarization", "analysis", "sender_analysis", "temporal_search"]},
                    "confidence": {"type": "number"},
                    "entities": {"type": "array", "items": {"type": "string"}},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="intent_parser",
                    tool_name="Intent Parser",
                    description="Parses user query to extract intent",
                    input_schema={"query": "string"},
                    output_schema={"intent_type": "string", "confidence": "number"}
                ),
                AgentCapability(
                    tool_id="entity_extractor",
                    tool_name="Entity Extractor",
                    description="Extracts named entities from query",
                    input_schema={"query": "string"},
                    output_schema={"entities": "array"}
                )
            ],
            config={"timeout": 5000, "retry": 3},
            endpoints={
                "execute": "http://localhost:8000/tool/emails/load",
                "status": "http://localhost:8000/health"
            }
        ),
        
        # Agent 2: Semantic Search
        AgentDefinition(
            agent_id="semantic_search_agent",
            agent_name="Semantic Search Agent",
            agent_type="email",
            description="Searches emails using semantic embeddings and meaning-based retrieval",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 5},
                    "score_threshold": {"type": "number", "description": "Minimum similarity score", "default": 0.5}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "results": {"type": "array"},
                    "result_count": {"type": "integer"},
                    "average_score": {"type": "number"},
                    "query_time_ms": {"type": "number"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="semantic_indexer",
                    tool_name="Semantic Indexer",
                    description="Indexes emails using Sentence Transformers embeddings",
                    input_schema={"emails": "array"},
                    output_schema={"indexed_count": "integer", "total_chunks": "integer"}
                ),
                AgentCapability(
                    tool_id="semantic_search_tool",
                    tool_name="Semantic Search Tool",
                    description="Performs semantic search over indexed emails",
                    input_schema={"query": "string", "top_k": "integer"},
                    output_schema={"results": "array", "scores": "array"}
                )
            ],
            config={"embedding_model": "all-MiniLM-L6-v2", "chunk_size": 500},
            endpoints={
                "search": "http://localhost:8000/tool/semantic/search",
                "index": "http://localhost:8000/tool/semantic/index"
            }
        ),
        
        # Agent 3: Classification
        AgentDefinition(
            agent_id="classification_agent",
            agent_name="Classification Agent",
            agent_type="email",
            description="Classifies emails into categories, priorities, and sentiment",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "emails": {"type": "array", "description": "Emails to classify"},
                    "categories": {"type": "array", "description": "Categories to classify into"},
                    "extract_sentiment": {"type": "boolean", "description": "Extract sentiment"}
                },
                "required": ["emails"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "classifications": {"type": "array"},
                    "total_classified": {"type": "integer"},
                    "categories_used": {"type": "array"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="category_classifier",
                    tool_name="Category Classifier",
                    description="Classifies emails into categories (Work, Urgent, Financial, Security, Social, Other)",
                    input_schema={"email": "object"},
                    output_schema={"category": "string", "confidence": "number"}
                ),
                AgentCapability(
                    tool_id="priority_detector",
                    tool_name="Priority Detector",
                    description="Detects email priority (High, Medium, Low)",
                    input_schema={"email": "object"},
                    output_schema={"priority": "string", "score": "number"}
                ),
                AgentCapability(
                    tool_id="sentiment_analyzer",
                    tool_name="Sentiment Analyzer",
                    description="Analyzes email sentiment (Positive, Neutral, Negative)",
                    input_schema={"text": "string"},
                    output_schema={"sentiment": "string", "score": "number"}
                )
            ],
            config={"model": "rule-based", "confidence_threshold": 0.5},
            endpoints={
                "classify": "http://localhost:8000/tool/emails/classify"
            }
        ),
        
        # Agent 4: RAG Generation
        AgentDefinition(
            agent_id="rag_generation_agent",
            agent_name="RAG Answer Generation Agent",
            agent_type="email",
            description="Generates grounded answers with citations using Retrieval-Augmented Generation",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question to answer"},
                    "context_emails": {"type": "integer", "description": "Number of context emails", "default": 5},
                    "generate_citations": {"type": "boolean", "description": "Include citations"}
                },
                "required": ["question"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "citations": {"type": "array"},
                    "confidence": {"type": "number"},
                    "generation_time_ms": {"type": "number"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="context_retriever",
                    tool_name="Context Retriever",
                    description="Retrieves relevant email context for RAG",
                    input_schema={"question": "string", "top_k": "integer"},
                    output_schema={"context": "array", "scores": "array"}
                ),
                AgentCapability(
                    tool_id="answer_generator",
                    tool_name="Answer Generator",
                    description="Generates answers using LLM with retrieved context",
                    input_schema={"question": "string", "context": "array"},
                    output_schema={"answer": "string", "citations": "array"}
                ),
                AgentCapability(
                    tool_id="citation_tracker",
                    tool_name="Citation Tracker",
                    description="Tracks citations to ensure grounded answers",
                    input_schema={"answer": "string", "context": "array"},
                    output_schema={"citations": "array", "citation_score": "number"}
                )
            ],
            config={"llm_model": "watsonx/granite-13b-chat-v2", "temperature": 0.1},
            endpoints={
                "answer": "http://localhost:8000/tool/rag/answer"
            }
        ),
        
        # Agent 5: Threat Detection
        AgentDefinition(
            agent_id="threat_detection_agent",
            agent_name="Threat Detection Agent",
            agent_type="email",
            description="Analyzes emails for security threats including phishing, malware, and suspicious domains",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "emails": {"type": "array", "description": "Emails to analyze"},
                    "analyze_phishing": {"type": "boolean", "description": "Check for phishing"},
                    "analyze_malware": {"type": "boolean", "description": "Check for malware"},
                    "threat_levels": {"type": "array", "description": "Threat level categories"}
                },
                "required": ["emails"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "threats_detected": {"type": "integer"},
                    "threat_summary": {"type": "object"},
                    "critical_threats": {"type": "array"},
                    "recommendations": {"type": "array"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="phishing_detector",
                    tool_name="Phishing Detector",
                    description="Detects phishing patterns in emails",
                    input_schema={"email": "object"},
                    output_schema={"is_phishing": "boolean", "confidence": "number"}
                ),
                AgentCapability(
                    tool_id="domain_analyzer",
                    tool_name="Domain Analyzer",
                    description="Analyzes email sender domains for suspicion",
                    input_schema={"domain": "string"},
                    output_schema={"risk_score": "number", "is_suspicious": "boolean"}
                ),
                AgentCapability(
                    tool_id="threat_scorer",
                    tool_name="Threat Scorer",
                    description="Calculates overall threat score",
                    input_schema={"email": "object"},
                    output_schema={"threat_level": "string", "threat_score": "number"}
                )
            ],
            config={"threat_levels": ["SAFE", "CAUTION", "WARNING", "CRITICAL"]},
            endpoints={
                "analyze": "http://localhost:8000/tool/threat/analyze"
            }
        ),
        
        # Agent 6: Database Persistence
        AgentDefinition(
            agent_id="database_persistence_agent",
            agent_name="Database Persistence Agent",
            agent_type="email",
            description="Stores workflow execution results, threat analysis, and analytics in database",
            version="1.0.0",
            status="ACTIVE",
            input_schema={
                "type": "object",
                "properties": {
                    "execution_data": {"type": "object", "description": "Execution data to store"},
                    "threat_data": {"type": "array", "description": "Threat analysis data"},
                    "persist_execution": {"type": "boolean"},
                    "persist_threats": {"type": "boolean"}
                },
                "required": ["execution_data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "execution_stored": {"type": "boolean"},
                    "threats_stored": {"type": "integer"},
                    "storage_location": {"type": "string"},
                    "query_id": {"type": "string"}
                }
            },
            capabilities=[
                AgentCapability(
                    tool_id="execution_storage",
                    tool_name="Execution Storage",
                    description="Stores workflow execution records",
                    input_schema={"execution": "object"},
                    output_schema={"stored": "boolean", "record_id": "string"}
                ),
                AgentCapability(
                    tool_id="threat_storage",
                    tool_name="Threat Storage",
                    description="Stores threat analysis results",
                    input_schema={"threats": "array"},
                    output_schema={"stored_count": "integer"}
                ),
                AgentCapability(
                    tool_id="analytics_logger",
                    tool_name="Analytics Logger",
                    description="Logs analytics for reporting",
                    input_schema={"analytics": "object"},
                    output_schema={"logged": "boolean"}
                )
            ],
            config={"database": "sqlite", "auto_cleanup": True},
            endpoints={
                "store": "http://localhost:8000/analytics/emails"
            }
        )
    ]
    
    return agents


# Global registry instance
_registry: Optional[OrchestrateAgentRegistry] = None


def get_agent_registry() -> Optional[OrchestrateAgentRegistry]:
    """Get or create global agent registry"""
    global _registry
    
    from app.config import settings
    
    if not settings.orchestrator_api_key or not settings.orchestrator_base_url:
        logger.warning("Orchestrator credentials not configured")
        return None
    
    if _registry is None:
        _registry = OrchestrateAgentRegistry(
            api_key=settings.orchestrator_api_key,
            base_url=settings.orchestrator_base_url
        )
        logger.info("Initialized OrchestrateAgentRegistry")
    
    return _registry


async def register_all_agents() -> Dict[str, Any]:
    """
    Register all HackTheAgent agents with IBM Orchestrate
    
    This makes all agents visible and available in the Orchestrate platform
    
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
        
        logger.info(f"Agent registration completed: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to register agents: {str(e)}")
        return {"error": str(e)}
