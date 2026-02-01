"""
IBM Orchestrate Integration - Real workflow engine for HackTheAgent

This module properly integrates with IBM Orchestrate Watson platform,
using actual orchestration workflows instead of custom Python orchestrator.

IBM Orchestrate Documentation:
https://cloud.ibm.com/docs/watson-orchestrate
"""

import logging
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


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
    timestamp: str


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
