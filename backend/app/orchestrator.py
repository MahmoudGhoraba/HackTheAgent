"""
IBM Orchestrate-inspired Multi-Agent Workflow Orchestration
Coordinates semantic search, classification, and RAG agents
"""
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from app.load import load_emails
from app.semantic import get_search_engine
from app.classify import classifier
from app.rag import get_rag_engine
from app.config import settings

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class WorkflowStep:
    """Individual step in the workflow"""
    step_id: str
    agent: str
    description: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class WorkflowExecution:
    """Complete workflow execution record"""
    execution_id: str
    intent: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'execution_id': self.execution_id,
            'intent': self.intent,
            'steps': [step.to_dict() for step in self.steps],
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_ms': self.duration_ms
        }


class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent workflow for email processing.
    Mimics IBM Orchestrate workflow engine with agents:
    - Semantic Agent: Searches emails by meaning
    - Classification Agent: Classifies and prioritizes
    - RAG Agent: Generates answers using RAG
    - Intent Agent: Determines user intent
    """
    
    def __init__(self):
        self.executions: Dict[str, WorkflowExecution] = {}
        self.execution_counter = 0
    
    async def execute_workflow(
        self,
        query: str,
        top_k: int = 5,
        enable_rag: bool = True
    ) -> WorkflowExecution:
        """
        Execute the full multi-agent workflow
        
        Args:
            query: User's question or intent
            top_k: Number of top results to return
            enable_rag: Whether to generate RAG answer
            
        Returns:
            WorkflowExecution: Complete workflow execution record with all steps
        """
        self.execution_counter += 1
        execution_id = f"exec_{self.execution_counter}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            intent=query
        )
        
        try:
            execution.status = WorkflowStatus.RUNNING
            start_time = datetime.utcnow()
            
            # Step 1: Intent Detection Agent
            logger.info(f"[{execution_id}] Starting workflow for query: '{query}'")
            intent_step = await self._step_intent_detection(execution, query)
            execution.steps.append(intent_step)
            
            # Step 2: Semantic Search Agent
            # Enhance query for better search results
            enhanced_query = self._enhance_search_query(query, intent_step.metadata.get("intent_type"))
            logger.info(f"[{execution_id}] Running semantic search agent with enhanced query")
            search_step = await self._step_semantic_search(execution, enhanced_query, top_k)
            execution.steps.append(search_step)
            
            # Check if search found results
            if search_step.status == WorkflowStatus.ERROR:
                execution.status = WorkflowStatus.ERROR
                execution.error = search_step.error
                execution.end_time = datetime.utcnow().isoformat()
                execution.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                return execution
            
            # Step 3: Classification Agent (for priority/categorization)
            logger.info(f"[{execution_id}] Running classification agent")
            classify_step = await self._step_classification(execution)
            execution.steps.append(classify_step)
            
            # Step 4: RAG Agent (if enabled)
            if enable_rag:
                logger.info(f"[{execution_id}] Running RAG answer generation agent")
                rag_step = await self._step_rag_generation(execution, query, top_k)
                execution.steps.append(rag_step)
                
                # Extract answer from RAG step
                if rag_step.status == WorkflowStatus.COMPLETED:
                    rag_result = rag_step.metadata.get('answer')
                    citations = rag_step.metadata.get('citations', [])
                    execution.result = {
                        'answer': rag_result,
                        'citations': citations,
                        'search_results': search_step.metadata.get('results', [])
                    }
            else:
                # Just return search results
                execution.result = {
                    'search_results': search_step.metadata.get('results', [])
                }
            
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.utcnow().isoformat()
            execution.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"[{execution_id}] Workflow completed successfully in {execution.duration_ms:.0f}ms")
            
        except Exception as e:
            logger.error(f"[{execution_id}] Workflow error: {str(e)}", exc_info=True)
            execution.status = WorkflowStatus.ERROR
            execution.error = str(e)
            execution.end_time = datetime.utcnow().isoformat()
            execution.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        self.executions[execution_id] = execution
        return execution
    
    async def _step_intent_detection(self, execution: WorkflowExecution, query: str) -> WorkflowStep:
        """
        Intent Detection Agent
        Analyzes user query to determine intent (search, analysis, summarization, etc.)
        """
        step = WorkflowStep(
            step_id="step_1_intent",
            agent="Intent Detection Agent",
            description="Analyzing user intent and query type"
        )
        
        try:
            step.status = WorkflowStatus.RUNNING
            
            # Simple intent detection
            query_lower = query.lower()
            intent_type = "search"
            
            if any(word in query_lower for word in ["summarize", "summary", "overview", "what are"]):
                intent_type = "summarization"
            elif any(word in query_lower for word in ["count", "how many", "statistics", "analyze"]):
                intent_type = "analysis"
            elif any(word in query_lower for word in ["who", "from", "sender"]):
                intent_type = "sender_analysis"
            elif any(word in query_lower for word in ["when", "date", "time"]):
                intent_type = "temporal_search"
            
            step.metadata = {
                "intent_type": intent_type,
                "confidence": 0.95
            }
            step.result = f"Detected intent type: {intent_type}"
            step.status = WorkflowStatus.COMPLETED
            
            logger.info(f"Intent detected: {intent_type}")
            
        except Exception as e:
            logger.error(f"Intent detection error: {str(e)}")
            step.status = WorkflowStatus.ERROR
            step.error = str(e)
        
        return step
    
    def _enhance_search_query(self, query: str, intent_type: str) -> str:
        """
        Enhance search query based on intent to improve results
        
        Args:
            query: Original user query
            intent_type: Detected intent type
            
        Returns:
            Enhanced search query
        """
        query_lower = query.lower()
        
        # If looking for critical/urgent emails, search for urgent-related keywords
        if "critical" in query_lower or "urgent" in query_lower or "important" in query_lower:
            return f"{query} urgent asap important priority"
        
        # If looking for security vulnerabilities, enhance with security keywords
        if "security" in query_lower or "vulnerability" in query_lower or "vulnerable" in query_lower:
            return f"{query} CVE critical vulnerability patch security alert threat"
        
        # If looking for bugs/issues, enhance with related keywords
        if "bug" in query_lower or "issue" in query_lower or "error" in query_lower:
            return f"{query} fix bug error authentication failure"
        
        # If analyzing emails, keep original query
        if intent_type == "analysis" or intent_type == "summarization":
            return query
        
        # If looking for emails from specific person
        if intent_type == "sender_analysis":
            return query
        
        # Default: use original query
        return query
    
    async def _step_semantic_search(
        self,
        execution: WorkflowExecution,
        query: str,
        top_k: int = 5
    ) -> WorkflowStep:
        """
        Semantic Search Agent
        Performs semantic search over indexed emails
        """
        step = WorkflowStep(
            step_id="step_2_search",
            agent="Semantic Search Agent",
            description=f"Searching for emails matching: '{query}'"
        )
        
        try:
            step.status = WorkflowStatus.RUNNING
            
            search_engine = get_search_engine()
            results = search_engine.search(query=query, top_k=top_k)
            
            # Convert SearchResult objects to dicts for JSON serialization
            results_list = [
                {
                    "id": r.id,
                    "subject": r.subject,
                    "date": r.date,
                    "score": r.score,
                    "snippet": r.snippet
                } for r in results
            ]
            
            step.metadata = {
                "results": results_list,
                "result_count": len(results_list),
                "query": query
            }
            step.result = f"Found {len(results_list)} matching emails"
            step.status = WorkflowStatus.COMPLETED
            
            logger.info(f"Search returned {len(results)} results")
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            step.status = WorkflowStatus.ERROR
            step.error = str(e)
        
        return step
    
    async def _step_classification(self, execution: WorkflowExecution) -> WorkflowStep:
        """
        Classification Agent
        Classifies and prioritizes search results
        """
        step = WorkflowStep(
            step_id="step_3_classify",
            agent="Classification Agent",
            description="Classifying and prioritizing results"
        )
        
        try:
            step.status = WorkflowStatus.RUNNING
            
            # Get search results from previous step
            search_step = next((s for s in execution.steps if s.step_id == "step_2_search"), None)
            if not search_step or search_step.status != WorkflowStatus.COMPLETED:
                step.result = "Skipped (no search results)"
                step.status = WorkflowStatus.COMPLETED
                return step
            
            results = search_step.metadata.get("results", [])
            
            # Classify each result
            classifications = []
            for result in results:
                # Results are now dicts from the search step
                # Create a mock email dict for classification
                email_dict = {
                    "id": result.get("id"),
                    "subject": result.get("subject", ""),
                    "body": result.get("snippet", "")
                }
                
                # Classify the email
                classification = classifier.classify_email(email_dict)
                
                classifications.append({
                    "email_id": result.get("id"),
                    "subject": result.get("subject"),
                    "category": classification.get("categories", ["general"])[0],
                    "priority": classification.get("priority", "medium"),
                    "score": result.get("score", 0)
                })
            
            # Sort by priority and relevance
            classifications.sort(
                key=lambda x: (-1 if x.get("priority") == "high" else 0, -x.get("score", 0))
            )
            
            step.metadata = {
                "classifications": classifications,
                "total_classified": len(classifications)
            }
            step.result = f"Classified {len(classifications)} emails"
            step.status = WorkflowStatus.COMPLETED
            
            logger.info(f"Classified {len(classifications)} emails")
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            step.status = WorkflowStatus.ERROR
            step.error = str(e)
        
        return step
    
    async def _step_rag_generation(
        self,
        execution: WorkflowExecution,
        query: str,
        top_k: int = 5
    ) -> WorkflowStep:
        """
        RAG Generation Agent
        Uses Retrieval-Augmented Generation to answer user question
        """
        step = WorkflowStep(
            step_id="step_4_rag",
            agent="RAG Answer Generation Agent",
            description="Generating grounded answer using retrieved context"
        )
        
        try:
            step.status = WorkflowStatus.RUNNING
            
            rag_engine = get_rag_engine()
            response = rag_engine.answer_question(question=query, top_k=top_k)
            
            step.metadata = {
                "answer": response.answer,
                "citations": response.citations,
                "model": settings.llm_model
            }
            step.result = "Answer generated successfully"
            step.status = WorkflowStatus.COMPLETED
            
            logger.info(f"RAG answer generated with {len(response.citations)} citations")
            
        except Exception as e:
            logger.error(f"RAG generation error: {str(e)}")
            step.status = WorkflowStatus.ERROR
            step.error = str(e)
        
        return step
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution by ID"""
        return self.executions.get(execution_id)
    
    def list_recent_executions(self, limit: int = 10) -> List[WorkflowExecution]:
        """List recent executions"""
        return sorted(
            list(self.executions.values()),
            key=lambda x: x.start_time,
            reverse=True
        )[:limit]


# Global orchestrator instance
_orchestrator: Optional[MultiAgentOrchestrator] = None


def get_orchestrator() -> MultiAgentOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
        logger.info("Initialized MultiAgentOrchestrator")
    return _orchestrator
