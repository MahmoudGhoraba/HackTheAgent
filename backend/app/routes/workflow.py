"""
Workflow Execution Routes
Orchestrates multiple agents to execute complex email workflows
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json

from app.local_agent_engine import get_agent_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow", tags=["workflow"])

# Request/Response Models
class WorkflowExecuteRequest(BaseModel):
    question: str
    top_k: int = 100

class WorkflowStep(BaseModel):
    description: str
    agent: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

class WorkflowExecuteResponse(BaseModel):
    status: str
    steps: List[WorkflowStep]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(request: WorkflowExecuteRequest):
    """
    Execute multi-agent workflow for email processing
    
    Flow:
    1. Intent Detection: Parse user intent from query
    2. Route by Intent: 
       - "search" → Semantic Search → RAG Generation
       - "classify" → Email Classification
       - "threat" → Threat Detection
       - "general" → Direct RAG Generation
    3. Persist Results: Store execution results
    """
    try:
        engine = get_agent_engine()
        steps: List[WorkflowStep] = []
        
        logger.info(f"🚀 Starting workflow: {request.question}")
        
        # ============================================================================
        # STEP 1: INTENT DETECTION
        # ============================================================================
        logger.info("📊 Step 1/3: Intent Detection Agent")
        
        intent_result = engine.parse_intent(request.question)
        
        steps.append(WorkflowStep(
            description="Parsing user intent and extracting entities",
            agent="intent_detection_agent",
            status="completed" if intent_result.get("success") else "error",
            result=intent_result.get("output"),
            error=intent_result.get("error")
        ))
        
        if not intent_result.get("success"):
            raise Exception(f"Intent detection failed: {intent_result.get('error')}")
        
        # Get detected intent
        intent_data = intent_result.get("output", {})
        detected_intent = intent_data.get("intent", "general").lower()
        entities = intent_data.get("entities", [])
        
        logger.info(f"✅ Detected intent: {detected_intent}")
        
        # ============================================================================
        # STEP 2: ROUTE BY INTENT
        # ============================================================================
        final_result = None
        
        if detected_intent == "search":
            # ====== SEARCH WORKFLOW ======
            logger.info("📧 Step 2/3: Semantic Search Agent")
            
            search_result = engine.semantic_search(request.question, None)
            
            steps.append(WorkflowStep(
                description="Searching emails semantically",
                agent="semantic_search_agent",
                status="completed" if search_result.get("success") else "error",
                result=search_result.get("output"),
                error=search_result.get("error")
            ))
            
            if not search_result.get("success"):
                raise Exception(f"Semantic search failed: {search_result.get('error')}")
            
            # Extract context from search results
            search_output = search_result.get("output", {})
            search_results = search_output.get("results", [])
            context = [r.get("snippet", "") for r in search_results[:5] if r.get("snippet")]
            
            logger.info(f"✅ Found {len(search_results)} matching emails")
            
            # ====== GENERATE ANSWER WITH RAG ======
            logger.info("💡 Step 3/3: RAG Generation Agent")
            
            rag_result = engine.generate_answer(request.question, context)
            
            steps.append(WorkflowStep(
                description="Generating grounded answer with citations",
                agent="rag_generation_agent",
                status="completed" if rag_result.get("success") else "error",
                result=rag_result.get("output"),
                error=rag_result.get("error")
            ))
            
            if not rag_result.get("success"):
                raise Exception(f"Answer generation failed: {rag_result.get('error')}")
            
            rag_output = rag_result.get("output", {})
            
            final_result = {
                "answer": rag_output.get("answer", ""),
                "citations": rag_output.get("citations", []),
                "search_results": search_results,
                "confidence": rag_output.get("confidence", 0),
                "entities": entities
            }
        
        elif detected_intent == "classify":
            # ====== CLASSIFICATION WORKFLOW ======
            logger.info("📋 Step 2/3: Email Classification Agent")
            
            # Mock email data for classification
            mock_emails = [
                {"id": "email_001", "subject": "Project Update", "body": "Here's the latest progress on the project"},
                {"id": "email_002", "subject": "Meeting Reminder", "body": "Reminder: we have a meeting tomorrow at 2pm"},
                {"id": "email_003", "subject": "Invoice", "body": "Your monthly invoice is ready"},
                {"id": "email_004", "subject": "URGENT ALERT", "body": "Click here immediately to verify account"},
            ]
            
            classify_result = engine.classify_emails(mock_emails)
            
            steps.append(WorkflowStep(
                description="Classifying emails by category, priority, and sentiment",
                agent="classification_agent",
                status="completed" if classify_result.get("success") else "error",
                result=classify_result.get("output"),
                error=classify_result.get("error")
            ))
            
            if not classify_result.get("success"):
                raise Exception(f"Classification failed: {classify_result.get('error')}")
            
            logger.info("✅ Emails classified successfully")
            
            final_result = {
                "classifications": classify_result.get("output", {}),
                "entities": entities
            }
        
        elif detected_intent == "threat":
            # ====== THREAT DETECTION WORKFLOW ======
            logger.info("🛡️  Step 2/3: Threat Detection Agent")
            
            mock_emails = [
                {"id": "email_001", "subject": "Verify your account", "body": "Click here to verify your account immediately"},
                {"id": "email_002", "subject": "Urgent action needed", "body": "Confirm your password immediately"},
                {"id": "email_003", "subject": "System maintenance", "body": "Scheduled maintenance tomorrow"},
            ]
            
            threat_result = engine.detect_threats(mock_emails)
            
            steps.append(WorkflowStep(
                description="Detecting security threats (phishing, malware, etc)",
                agent="threat_detection_agent",
                status="completed" if threat_result.get("success") else "error",
                result=threat_result.get("output"),
                error=threat_result.get("error")
            ))
            
            if not threat_result.get("success"):
                raise Exception(f"Threat detection failed: {threat_result.get('error')}")
            
            logger.info("✅ Threat detection completed")
            
            final_result = {
                "threats": threat_result.get("output", {}),
                "entities": entities
            }
        
        else:
            # ====== GENERAL/QA WORKFLOW ======
            logger.info("💡 Step 2/3: RAG Generation Agent")
            
            rag_result = engine.generate_answer(request.question, [])
            
            steps.append(WorkflowStep(
                description="Generating answer to your question",
                agent="rag_generation_agent",
                status="completed" if rag_result.get("success") else "error",
                result=rag_result.get("output"),
                error=rag_result.get("error")
            ))
            
            if not rag_result.get("success"):
                raise Exception(f"Answer generation failed: {rag_result.get('error')}")
            
            logger.info("✅ Answer generated")
            
            rag_output = rag_result.get("output", {})
            
            final_result = {
                "answer": rag_output.get("answer", ""),
                "citations": rag_output.get("citations", []),
                "confidence": rag_output.get("confidence", 0),
                "entities": entities
            }
        
        # ============================================================================
        # STEP 3: PERSIST RESULTS
        # ============================================================================
        logger.info("💾 Persisting workflow execution results")
        
        persist_result = engine.persist_data("workflow_execution", {
            "question": request.question,
            "intent": detected_intent,
            "result": final_result,
            "status": "success"
        })
        
        steps.append(WorkflowStep(
            description="Storing execution results to database",
            agent="database_persistence_agent",
            status="completed" if persist_result.get("success") else "warning",
            result=persist_result.get("output"),
            error=persist_result.get("error")
        ))
        
        logger.info("✅ Workflow completed successfully")
        
        return WorkflowExecuteResponse(
            status="completed",
            steps=steps,
            result=final_result
        )
    
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}", exc_info=True)
        
        steps.append(WorkflowStep(
            description="Error occurred during workflow execution",
            agent="orchestrator",
            status="error",
            error=str(e)
        ))
        
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "steps": [s.dict() for s in steps],
                "error": str(e)
            }
        )

@router.get("/agents")
async def list_workflow_agents():
    """List all available agents in the workflow system"""
    try:
        engine = get_agent_engine()
        agents = engine.list_agents()
        
        return {
            "status": "success",
            "agents": agents,
            "count": len(agents)
        }
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def workflow_status():
    """Check workflow system status"""
    try:
        engine = get_agent_engine()
        agents = engine.list_agents()
        
        return {
            "status": "operational",
            "agents_available": len(agents),
            "agents": agents,
            "capabilities": [
                "intent_detection",
                "semantic_search",
                "email_classification",
                "rag_generation",
                "threat_detection",
                "data_persistence"
            ]
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))
