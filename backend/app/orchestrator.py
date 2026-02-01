"""
IBM Orchestrate-inspired Multi-Agent Workflow Orchestration
Coordinates semantic search, classification, and RAG agents
"""
import logging
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from app.load import load_emails
from app.semantic import get_search_engine
from app.classify import classifier
from app.rag import get_rag_engine
from app.config import settings
from app.threat_detection import get_threat_detector, EmailThreatAnalysis
from app.database import get_database

# Try to import IBM Orchestrate client (optional)
try:
    from app.ibm_orchestrate import IBMOrchestrateClient, OrchestrateWorkflowInput, OrchestrateWorkflowOutput
    IBM_ORCHESTRATE_AVAILABLE = True
except ImportError:
    IBM_ORCHESTRATE_AVAILABLE = False

logger = logging.getLogger(__name__)

if not IBM_ORCHESTRATE_AVAILABLE:
    logger.info("IBM Orchestrate optional module not available - using local orchestrator")


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
        
        Try IBM Orchestrate first if configured, fallback to local orchestration
        
        Args:
            query: User's question or intent
            top_k: Number of top results to return
            enable_rag: Whether to generate RAG answer
            
        Returns:
            WorkflowExecution: Complete workflow execution record with all steps
        """
        # Try IBM Orchestrate if available and properly configured (Fix #1)
        # Skip if it's a placeholder value or not a valid API key
        is_valid_orchestrator_key = (
            IBM_ORCHESTRATE_AVAILABLE 
            and settings.orchestrator_api_key 
            and not settings.orchestrator_api_key.startswith("your-")
            and len(settings.orchestrator_api_key) > 10
        )
        
        if is_valid_orchestrator_key:
            try:
                logger.info(f"Attempting IBM Orchestrate execution with URL: {settings.orchestrator_base_url}")
                result = await self._execute_ibm_orchestrate(query, top_k, enable_rag)
                if result:
                    logger.info("IBM Orchestrate execution successful")
                    return result
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"IBM Orchestrate failed: {error_msg}")
                
                # Log helpful diagnostic info
                if "401" in error_msg or "Unauthorized" in error_msg:
                    logger.error("IBM Orchestrate returned 401 Unauthorized")
                    logger.error(f"  API Key: {settings.orchestrator_api_key[:20]}..." if settings.orchestrator_api_key else "  API Key: Not set")
                    logger.error(f"  Base URL: {settings.orchestrator_base_url}")
                    logger.error("  Check: 1) API key is correct and not expired")
                    logger.error("         2) Base URL matches your IBM instance")
                    logger.error("         3) Credentials have required permissions")
                
                logger.warning("Falling back to local orchestrator")
        else:
            if IBM_ORCHESTRATE_AVAILABLE and settings.orchestrator_api_key:
                logger.debug("IBM Orchestrate API key is placeholder, using local orchestrator")
        
        # Fallback to local multi-agent orchestration
        return await self._execute_local_workflow(query, top_k, enable_rag)
    
    async def _execute_ibm_orchestrate(
        self,
        query: str,
        top_k: int,
        enable_rag: bool
    ) -> Optional[WorkflowExecution]:
        """
        Execute using IBM Orchestrate (if configured)
        """
        try:
            from app.ibm_orchestrate import get_orchestrate_client
            
            client = get_orchestrate_client()
            input_data = OrchestrateWorkflowInput(
                user_query=query,
                email_ids=[],  # Will be populated by workflow
                num_results=top_k
            )
            
            # Call IBM Orchestrate workflow
            result = await client.execute_workflow(
                workflow_id="email_analysis",
                input_data=input_data
            )
            
            # Convert to our WorkflowExecution format
            self.execution_counter += 1
            execution = WorkflowExecution(
                execution_id=f"ibm_{result.execution_id}",
                intent=query,
                status=WorkflowStatus.COMPLETED if result.status == "COMPLETED" else WorkflowStatus.ERROR,
                result=result.result,
                end_time=datetime.utcnow().isoformat(),
                duration_ms=1000  # IBM Orchestrate timing not available
            )
            
            logger.info(f"IBM Orchestrate execution completed: {result.execution_id}")
            self.executions[execution.execution_id] = execution
            return execution
            
        except Exception as e:
            logger.error(f"IBM Orchestrate error: {str(e)}")
            return None
    
    async def _execute_local_workflow(
        self,
        query: str,
        top_k: int = 5,
        enable_rag: bool = True
    ) -> WorkflowExecution:
        """
        Local multi-agent orchestration (fallback if IBM Orchestrate not available)
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
            # Step 4: RAG Agent (if enabled)
            # Run in parallel for better performance (Fix #5)
            logger.info(f"[{execution_id}] Running classification and RAG agents in parallel")
            
            classify_coro = self._step_classification(execution)
            rag_coro = self._step_rag_generation(execution, query, top_k) if enable_rag else None
            
            # Run both concurrently
            if rag_coro:
                classify_step, rag_step = await asyncio.gather(
                    classify_coro,
                    rag_coro,
                    return_exceptions=True
                )
            else:
                classify_step = await classify_coro
                rag_step = None
            
            execution.steps.append(classify_step)
            if rag_step:
                execution.steps.append(rag_step)
            
            # Build result from parallel steps
            if enable_rag and rag_step and rag_step.status == WorkflowStatus.COMPLETED:
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
            
            # Step 5: Threat Detection Agent (NEW - #2 Fix)
            logger.info(f"[{execution_id}] Running threat detection agent")
            threat_step = await self._step_threat_detection(execution, search_step)
            execution.steps.append(threat_step)
            
            # Step 6: Database Persistence Agent (NEW - #3 Fix)
            logger.info(f"[{execution_id}] Persisting workflow results to database")
            persist_step = await self._step_database_persistence(execution)
            execution.steps.append(persist_step)
            
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
    
    async def _step_threat_detection(
        self,
        execution: WorkflowExecution,
        search_step: WorkflowStep
    ) -> WorkflowStep:
        """
        Threat Detection Agent (NEW)
        Analyzes retrieved emails for security threats
        """
        step = WorkflowStep(
            step_id="step_5_threat",
            agent="Threat Detection Agent",
            description="Scanning emails for phishing, spoofing, and security threats"
        )
        
        try:
            step.status = WorkflowStatus.RUNNING
            threat_detector = get_threat_detector()
            
            search_results = search_step.metadata.get('results', [])
            threats_found = []
            threat_counts = {"SAFE": 0, "CAUTION": 0, "WARNING": 0, "CRITICAL": 0}
            
            # Analyze each search result for threats
            for email in search_results[:5]:  # Analyze top 5 results
                threat_analysis = threat_detector.analyze({
                    'id': email.get('id'),
                    'subject': email.get('subject', ''),
                    'body': email.get('snippet', ''),
                    'from': email.get('from', '')
                })
                
                threat_counts[threat_analysis.threat_level] += 1
                
                if threat_analysis.threat_level in ["WARNING", "CRITICAL"]:
                    threats_found.append({
                        'email_id': threat_analysis.email_id,
                        'threat_level': threat_analysis.threat_level,
                        'threat_score': threat_analysis.threat_score,
                        'recommendation': threat_analysis.recommendation
                    })
            
            step.metadata = {
                'threats_detected': len(threats_found),
                'threat_summary': threat_counts,
                'critical_threats': threats_found
            }
            step.result = f"Analyzed {len(search_results[:5])} emails - {threat_counts['CRITICAL']} critical, {threat_counts['WARNING']} warnings"
            step.status = WorkflowStatus.COMPLETED
            
            logger.info(f"Threat detection: {threat_counts['CRITICAL']} critical, {threat_counts['WARNING']} warnings found")
            
        except Exception as e:
            logger.error(f"Threat detection error: {str(e)}")
            step.status = WorkflowStatus.ERROR
            step.error = str(e)
        
        return step
    
    async def _step_database_persistence(
        self,
        execution: WorkflowExecution
    ) -> WorkflowStep:
        """
        Database Persistence Agent (NEW)
        Stores workflow results and threat analysis in SQLite
        """
        step = WorkflowStep(
            step_id="step_6_persist",
            agent="Database Persistence Agent",
            description="Storing workflow execution and threat analysis in database"
        )
        
        try:
            step.status = WorkflowStatus.RUNNING
            db = get_database()
            
            # Store workflow execution
            db.store_workflow_execution({
                'workflow_id': execution.execution_id,
                'status': execution.status.value,
                'intent': execution.intent,
                'steps': len(execution.steps),
                'result': str(execution.result),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Store threat analysis from threat detection step
            threat_step = next((s for s in execution.steps if s.step_id == "step_5_threat"), None)
            if threat_step and threat_step.metadata.get('critical_threats'):
                for threat in threat_step.metadata['critical_threats']:
                    db.store_threat_analysis({
                        'email_id': threat['email_id'],
                        'threat_level': threat['threat_level'],
                        'threat_score': threat['threat_score'],
                        'recommendation': threat['recommendation'],
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            step.metadata = {
                'execution_stored': True,
                'threats_stored': len(threat_step.metadata.get('critical_threats', []) if threat_step else [])
            }
            step.result = "Workflow and threat analysis persisted to database"
            step.status = WorkflowStatus.COMPLETED
            
            logger.info(f"Workflow {execution.execution_id} persisted to database")
            
        except Exception as e:
            logger.error(f"Database persistence error: {str(e)}")
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
