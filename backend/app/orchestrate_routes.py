"""
Watson Orchestrate API Routes
Routes for interacting with Watson Orchestrate agents
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.local_agent_engine import get_agent_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestrate", tags=["orchestrate"])

# Request/Response Models
class IntentParseRequest(BaseModel):
    query: str

class SemanticSearchRequest(BaseModel):
    query: str
    email_ids: Optional[List[str]] = None

class ClassifyEmailsRequest(BaseModel):
    emails: List[Dict[str, Any]]

class GenerateAnswerRequest(BaseModel):
    query: str
    context: List[str] = []

class DetectThreatsRequest(BaseModel):
    emails: List[Dict[str, Any]]

class PersistDataRequest(BaseModel):
    data_type: str
    data: Any

# Health check endpoint
@router.get("/health")
async def health_check():
    """Check Watson Orchestrate connection status"""
    try:
        engine = get_agent_engine()
        agents = engine.list_agents()
        return {
            "status": "healthy",
            "orchestrate": "connected",
            "agents_available": len(agents)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))

# Agent listing
@router.get("/agents")
async def list_agents():
    """List all available Watson Orchestrate agents"""
    try:
        engine = get_agent_engine()
        agents_data = engine.list_agents()
        return {
            "count": len(agents_data),
            "agents": agents_data
        }
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific agent"""
    try:
        engine = get_agent_engine()
        agent = engine.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        return {
            "agent": agent_name,
            "status": "imported",
            "available": True
        }
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Intent Detection
@router.post("/intent/parse")
async def parse_intent(request: IntentParseRequest):
    """Parse user intent from query"""
    try:
        engine = get_agent_engine()
        result = engine.parse_intent(request.query)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Agent invocation failed"))
    except Exception as e:
        logger.error(f"Error parsing intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Semantic Search
@router.post("/search/semantic")
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search on emails"""
    try:
        engine = get_agent_engine()
        result = engine.semantic_search(request.query, request.email_ids)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Agent invocation failed"))
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Email Classification
@router.post("/classify")
async def classify_emails(request: ClassifyEmailsRequest):
    """Classify emails by category, priority, sentiment"""
    try:
        engine = get_agent_engine()
        result = engine.classify_emails(request.emails)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Agent invocation failed"))
    except Exception as e:
        logger.error(f"Error classifying emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# RAG Generation
@router.post("/generate-answer")
async def generate_answer(request: GenerateAnswerRequest):
    """Generate grounded answer with citations"""
    try:
        engine = get_agent_engine()
        result = engine.generate_answer(request.query, request.context)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Agent invocation failed"))
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Threat Detection
@router.post("/threats/detect")
async def detect_threats(request: DetectThreatsRequest):
    """Detect security threats in emails"""
    try:
        engine = get_agent_engine()
        result = engine.detect_threats(request.emails)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Agent invocation failed"))
    except Exception as e:
        logger.error(f"Error detecting threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Data Persistence
@router.post("/persist")
async def persist_data(request: PersistDataRequest):
    """Persist data to storage"""
    try:
        engine = get_agent_engine()
        result = engine.persist_data(request.data_type, request.data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Agent invocation failed"))
    except Exception as e:
        logger.error(f"Error persisting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))