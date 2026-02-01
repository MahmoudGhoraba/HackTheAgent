"""
IBM Orchestrate Integration - Real workflow engine for HackTheAgent

This module integrates with IBM Orchestrate Watson platform,
orchestrating multi-agent workflows for email intelligence.

All agents are coordinated through IBM Orchestrate:
- Intent Detection Agent
- Semantic Search Agent  
- Classification Agent
- RAG Generation Agent
- Threat Detection Agent
- Database Persistence Agent

IBM Orchestrate Documentation:
https://cloud.ibm.com/docs/watson-orchestrate
"""

import logging
import httpx
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Agent types in the orchestration"""
    INTENT_DETECTION = "intent_detection"
    SEMANTIC_SEARCH = "semantic_search"
    CLASSIFICATION = "classification"
    RAG_GENERATION = "rag_generation"
    THREAT_DETECTION = "threat_detection"
    DATABASE_PERSISTENCE = "database_persistence"


class AgentStep(BaseModel):
    """Individual agent step in orchestration"""
    agent_id: str
    agent_type: AgentType
    agent_name: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration_ms: float
    timestamp: str


class OrchestrateWorkflowInput(BaseModel):
    """Input for IBM Orchestrate workflow"""
    user_query: str
    email_ids: List[str]
    num_results: int = 100


class OrchestrateWorkflowOutput(BaseModel):
    """Output from IBM Orchestrate workflow"""
    workflow_id: str
    execution_id: str
    status: str  # COMPLETED, FAILED, RUNNING
    result: Dict[str, Any]
    steps_executed: List[str]
    agents_executed: List[AgentStep] = []
    timestamp: str


class OrchestrateAgentExecution(BaseModel):
    """Complete agent execution through IBM Orchestrate"""
    execution_id: str
    workflow_id: str
    agents: List[AgentStep] = []
    status: str
    orchestration_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


class IBMOrchestrateClient:
    """
    Proper IBM Orchestrate client that calls real IBM Orchestrate workflows.
    
    Note: This requires:
    1. IBM Cloud account with Orchestrate service enabled
    2. Valid API key and URL
    3. Pre-configured workflows in IBM Orchestrate
    """
    
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize IBM Orchestrate client
        
        Args:
            api_key: IBM Cloud API key
            base_url: IBM Orchestrate base URL (e.g., https://api.jp-tok.watson-orchestrate.cloud.ibm.com)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: OrchestrateWorkflowInput
    ) -> OrchestrateWorkflowOutput:
        """
        Execute an IBM Orchestrate workflow
        
        Args:
            workflow_id: ID of the workflow in IBM Orchestrate
            input_data: Input parameters for the workflow
            
        Returns:
            OrchestrateWorkflowOutput with workflow results
            
        Raises:
            httpx.HTTPError: If API call fails
        """
        try:
            url = f"{self.base_url}/v1/workflows/{workflow_id}/run"
            
            payload = {
                "user_query": input_data.user_query,
                "email_ids": input_data.email_ids,
                "num_results": input_data.num_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Executing IBM Orchestrate workflow: {workflow_id}")
            
            response = await self.client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Parse IBM Orchestrate response
            result = OrchestrateWorkflowOutput(
                workflow_id=workflow_id,
                execution_id=data.get('execution_id', 'exec_unknown'),
                status=data.get('status', 'COMPLETED'),
                result=data.get('result', {}),
                steps_executed=data.get('steps', []),
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Workflow execution completed: {result.execution_id}")
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"IBM Orchestrate API error: {str(e)}")
            # Return graceful error response
            return OrchestrateWorkflowOutput(
                workflow_id=workflow_id,
                execution_id='exec_error',
                status='FAILED',
                result={'error': str(e)},
                steps_executed=[],
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List available workflows in IBM Orchestrate"""
        try:
            url = f"{self.base_url}/v1/workflows"
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('workflows', [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to list workflows: {str(e)}")
            return []
    
    async def get_workflow_history(
        self,
        workflow_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get execution history for a workflow"""
        try:
            url = f"{self.base_url}/v1/workflows/{workflow_id}/executions"
            response = await self.client.get(
                url,
                params={'limit': limit},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('executions', [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to get workflow history: {str(e)}")
            return []
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def execute_agents_orchestrated(
        self,
        agents_list: List[Dict[str, Any]],
        workflow_id: str = "email_analysis_multi_agent"
    ) -> OrchestrateAgentExecution:
        """
        Execute multiple agents through IBM Orchestrate
        
        This orchestrates all agents in your system through IBM Orchestrate,
        showing them as if they were executed as part of IBM's platform.
        
        Args:
            agents_list: List of agent configurations to execute
            workflow_id: IBM Orchestrate workflow ID
            
        Returns:
            OrchestrateAgentExecution with all agent results
        """
        orchestration_id = f"orch_{datetime.utcnow().timestamp()}"
        execution = OrchestrateAgentExecution(
            execution_id=f"exec_{orchestration_id}",
            workflow_id=workflow_id,
            orchestration_id=orchestration_id,
            status="RUNNING",
            start_time=datetime.utcnow().isoformat()
        )
        
        try:
            executed_agents = []
            
            # Execute each agent through orchestration
            for agent_config in agents_list:
                agent_step = await self._orchestrate_agent(
                    agent_config,
                    orchestration_id
                )
                executed_agents.append(agent_step)
            
            execution.agents = executed_agents
            execution.status = "COMPLETED"
            execution.end_time = datetime.utcnow().isoformat()
            
            logger.info(f"IBM Orchestrate executed {len(executed_agents)} agents successfully")
            
        except Exception as e:
            logger.error(f"Agent orchestration error: {str(e)}")
            execution.status = "FAILED"
            execution.error = str(e)
            execution.end_time = datetime.utcnow().isoformat()
        
        return execution
    
    async def _orchestrate_agent(
        self,
        agent_config: Dict[str, Any],
        orchestration_id: str
    ) -> AgentStep:
        """
        Execute a single agent through IBM Orchestrate orchestration
        
        Args:
            agent_config: Configuration for the agent
            orchestration_id: Orchestration tracking ID
            
        Returns:
            AgentStep with execution results
        """
        agent_type = agent_config.get('type', 'unknown')
        agent_name = agent_config.get('name', 'Agent')
        agent_id = f"{agent_type}_{datetime.utcnow().timestamp()}"
        
        step = AgentStep(
            agent_id=agent_id,
            agent_type=agent_type,
            agent_name=agent_name,
            status="RUNNING",
            input_data=agent_config.get('input', {}),
            output_data={},
            duration_ms=0.0,
            timestamp=datetime.utcnow().isoformat()
        )
        
        start_time = datetime.utcnow()
        
        try:
            # Execute through IBM Orchestrate API endpoint
            url = f"{self.base_url}/v1/agents/execute"
            
            payload = {
                "orchestration_id": orchestration_id,
                "agent_type": agent_type,
                "agent_name": agent_name,
                "input": agent_config.get('input', {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Orchestrating agent: {agent_name} ({agent_type})")
            
            response = await self.client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            step.output_data = data.get('output', {})
            step.status = "COMPLETED"
            step.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"Agent {agent_name} completed in {step.duration_ms:.0f}ms")
            
        except Exception as e:
            logger.error(f"Agent {agent_name} orchestration error: {str(e)}")
            step.status = "FAILED"
            step.output_data = {"error": str(e)}
            step.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return step


# Global orchestrate client instance
_orchestrate_client: Optional[IBMOrchestrateClient] = None


def get_orchestrate_client() -> Optional[IBMOrchestrateClient]:
    """
    Get or create global IBM Orchestrate client
    
    Returns None if credentials are not configured
    """
    global _orchestrate_client
    
    from app.config import settings
    
    if not settings.orchestrator_api_key or not settings.orchestrator_base_url:
        logger.warning("IBM Orchestrate credentials not configured")
        return None
    
    if _orchestrate_client is None:
        _orchestrate_client = IBMOrchestrateClient(
            api_key=settings.orchestrator_api_key,
            base_url=settings.orchestrator_base_url
        )
    
    return _orchestrate_client


# Workflow IDs for HackTheAgent (pre-configured in IBM Orchestrate)
WORKFLOWS = {
    'email_analysis': 'wf-email-analysis-v1',
    'threat_detection': 'wf-email-threat-detection-v1',
    'sentiment_analysis': 'wf-email-sentiment-v1',
    'classification': 'wf-email-classification-v1'
}


async def orchestrate_email_threat_detection(
    email_ids: List[str],
    user_query: str
) -> Dict[str, Any]:
    """
    Use IBM Orchestrate to detect email threats
    
    This workflow:
    1. Analyzes email content for phishing patterns
    2. Detects suspicious sender domains
    3. Identifies malicious URLs/attachments
    4. Returns threat scores and recommendations
    """
    client = get_orchestrate_client()
    
    if not client:
        logger.warning("IBM Orchestrate not configured, using fallback")
        return {'error': 'Orchestrate not available'}
    
    input_data = OrchestrateWorkflowInput(
        user_query=user_query,
        email_ids=email_ids,
        num_results=100
    )
    
    result = await client.execute_workflow(
        workflow_id=WORKFLOWS['threat_detection'],
        input_data=input_data
    )
    
    return result.dict()


async def orchestrate_email_analysis(
    email_ids: List[str],
    user_query: str
) -> Dict[str, Any]:
    """
    Use IBM Orchestrate for comprehensive email analysis
    
    This workflow:
    1. Extracts key information (sender, date, importance)
    2. Identifies action items and deadlines
    3. Groups related emails
    4. Generates summary
    """
    client = get_orchestrate_client()
    
    if not client:
        logger.warning("IBM Orchestrate not configured, using fallback")
        return {'error': 'Orchestrate not available'}
    
    input_data = OrchestrateWorkflowInput(
        user_query=user_query,
        email_ids=email_ids
    )
    
    result = await client.execute_workflow(
        workflow_id=WORKFLOWS['email_analysis'],
        input_data=input_data
    )
    
    return result.dict()


async def orchestrate_all_agents(
    user_query: str,
    top_k: int = 5
) -> OrchestrateAgentExecution:
    """
    Orchestrate ALL HackTheAgent agents through IBM Orchestrate
    
    Executes the complete 6-agent workflow:
    1. Intent Detection Agent - Parse user query
    2. Semantic Search Agent - Find relevant emails
    3. Classification Agent - Categorize results
    4. RAG Generation Agent - Generate grounded answers
    5. Threat Detection Agent - Security analysis
    6. Database Persistence Agent - Store results
    
    Shows full integration with IBM Orchestrate platform.
    
    Args:
        user_query: User's question or intent
        top_k: Number of results to retrieve
        
    Returns:
        Complete orchestration execution with all agents
    """
    client = get_orchestrate_client()
    
    if not client:
        logger.warning("IBM Orchestrate client not available")
        return OrchestrateAgentExecution(
            execution_id="exec_error",
            workflow_id="email_analysis_multi_agent",
            status="FAILED",
            orchestration_id="orch_error",
            start_time=datetime.utcnow().isoformat(),
            error="Orchestrate client not configured"
        )
    
    # Build agent list for orchestration
    agents_to_orchestrate = [
        {
            "type": AgentType.INTENT_DETECTION,
            "name": "Intent Detection Agent",
            "description": "Analyzes user intent and query type",
            "input": {
                "query": user_query,
                "analyze_entities": True
            }
        },
        {
            "type": AgentType.SEMANTIC_SEARCH,
            "name": "Semantic Search Agent",
            "description": "Performs semantic search over indexed emails",
            "input": {
                "query": user_query,
                "top_k": top_k,
                "score_threshold": 0.5
            }
        },
        {
            "type": AgentType.CLASSIFICATION,
            "name": "Classification Agent",
            "description": "Classifies and prioritizes search results",
            "input": {
                "classify_results": True,
                "priority_levels": ["high", "medium", "low"],
                "categories": ["work", "urgent", "financial", "security"]
            }
        },
        {
            "type": AgentType.RAG_GENERATION,
            "name": "RAG Answer Generation Agent",
            "description": "Generates grounded answers with citations",
            "input": {
                "question": user_query,
                "context_emails": top_k,
                "generate_citations": True
            }
        },
        {
            "type": AgentType.THREAT_DETECTION,
            "name": "Threat Detection Agent",
            "description": "Analyzes emails for security threats",
            "input": {
                "analyze_phishing": True,
                "analyze_malware": True,
                "threat_levels": ["SAFE", "CAUTION", "WARNING", "CRITICAL"]
            }
        },
        {
            "type": AgentType.DATABASE_PERSISTENCE,
            "name": "Database Persistence Agent",
            "description": "Stores workflow results and threat analysis",
            "input": {
                "persist_execution": True,
                "persist_threats": True,
                "database": "sqlite"
            }
        }
    ]
    
    logger.info(f"Orchestrating {len(agents_to_orchestrate)} agents through IBM Orchestrate")
    
    # Execute all agents through orchestration
    execution = await client.execute_agents_orchestrated(
        agents_list=agents_to_orchestrate,
        workflow_id="email_analysis_multi_agent_v1"
    )
    
    return execution


async def get_agent_orchestration_status(
    execution_id: str
) -> Dict[str, Any]:
    """
    Get status of orchestrated agent execution
    
    Args:
        execution_id: ID of the orchestration execution
        
    Returns:
        Status and results of agent orchestration
    """
    client = get_orchestrate_client()
    
    if not client:
        return {"error": "Orchestrate client not available"}
    
    try:
        url = f"{client.base_url}/v1/orchestrations/{execution_id}"
        response = await client.client.get(url, headers=client.headers)
        response.raise_for_status()
        
        data = response.json()
        return {
            "execution_id": execution_id,
            "status": data.get("status", "UNKNOWN"),
            "agents_executed": data.get("agents_count", 0),
            "timestamp": data.get("timestamp"),
            "results": data.get("results", {})
        }
    except Exception as e:
        logger.error(f"Failed to get orchestration status: {str(e)}")
        return {"error": str(e), "execution_id": execution_id}
