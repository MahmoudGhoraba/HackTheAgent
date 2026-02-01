"""
FastAPI main application - HackTheAgent Email Brain Tool Server
"""
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Optional

from app.config import settings
from app.schemas import (
    EmailsResponse, NormalizeRequest, NormalizeResponse,
    IndexRequest, IndexResponse, SearchRequest, SearchResponse,
    RAGRequest, RAGResponse, ErrorResponse,
    ClassifyRequest, ClassifyResponse, ThreadsResponse,
    AnalyticsResponse, SearchStatsResponse, EmailThread,
    OAuthUrlResponse, OAuthCallbackRequest, OAuthTokenResponse,
    GmailProfileResponse, GmailFetchRequest, GmailFetchResponse,
    GmailAuthStatusResponse, GmailEmailResponse
)
from app.load import load_emails
from app.normalize import normalize_emails
from app.semantic import get_search_engine
from app.rag import get_rag_engine
from app.classify import classifier, thread_detector
from app.analytics import email_analytics, search_analytics
from app.cache import cache
from app.gmail_oauth import gmail_service
from app.orchestrator import get_orchestrator, WorkflowExecution
from app.threat_endpoints import register_threat_detection_endpoints

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress ChromaDB telemetry errors (known PostHog library incompatibility)
logging.getLogger('chromadb.telemetry.product.posthog').setLevel(logging.CRITICAL)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent Email Brain with semantic search and RAG capabilities",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "message": "HackTheAgent Email Brain API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# ==================== EMAIL TOOLS ====================

@app.get(
    "/tool/emails/load",
    response_model=EmailsResponse,
    tags=["Email Tools"],
    summary="Load raw emails from dataset or Gmail",
    description="Fetches raw emails from local JSON dataset file or Gmail (if authenticated)"
)
async def load_emails_endpoint(
    source: str = Query("file", description="Source: 'file' or 'gmail'"),
    max_results: int = Query(100, ge=1, le=500, description="Max emails to fetch (Gmail only)"),
    query: str = Query("", description="Gmail search query (Gmail only)")
):
    """
    Load raw emails from dataset or Gmail
    
    Args:
        source: "file" for JSON dataset, "gmail" for Gmail API
        max_results: Maximum number of emails to fetch (for Gmail)
        query: Gmail search query (for Gmail)
    
    Returns:
        EmailsResponse: List of raw emails
    """
    try:
        logger.info(f"Loading emails from {source}")
        response = load_emails(source=source, max_results=max_results, query=query)
        logger.info(f"Successfully loaded {len(response.emails)} emails from {source}")
        return response
    except FileNotFoundError as e:
        logger.error(f"Email file not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error loading emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load emails: {str(e)}"
        )


@app.post(
    "/tool/emails/normalize",
    response_model=NormalizeResponse,
    tags=["Email Tools"],
    summary="Normalize raw emails",
    description="Converts raw emails into normalized messages with structured text and metadata"
)
async def normalize_emails_endpoint(request: NormalizeRequest):
    """
    Normalize raw emails into structured messages
    
    Args:
        request: NormalizeRequest containing raw emails
        
    Returns:
        NormalizeResponse: Normalized messages
    """
    try:
        logger.info(f"Normalizing {len(request.emails)} emails")
        response = normalize_emails(request.emails)
        logger.info(f"Successfully normalized {len(response.messages)} messages")
        return response
    except Exception as e:
        logger.error(f"Error normalizing emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to normalize emails: {str(e)}"
        )


# ==================== SEMANTIC TOOLS ====================

@app.post(
    "/tool/semantic/index",
    response_model=IndexResponse,
    tags=["Semantic Tools"],
    summary="Index messages for semantic search",
    description="Creates embeddings and stores messages in vector database for semantic search"
)
async def index_messages_endpoint(request: IndexRequest):
    """
    Index normalized messages into vector database
    
    Args:
        request: IndexRequest containing normalized messages
        
    Returns:
        IndexResponse: Indexing status and statistics
    """
    try:
        logger.info(f"Indexing {len(request.messages)} messages")
        search_engine = get_search_engine()
        chunks_indexed, stats = search_engine.index_messages(request.messages)
        logger.info(f"Successfully indexed {chunks_indexed} chunks")
        
        return IndexResponse(
            status="indexed",
            chunks_indexed=chunks_indexed
        )
    except Exception as e:
        logger.error(f"Error indexing messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index messages: {str(e)}"
        )


@app.post(
    "/tool/semantic/search",
    response_model=SearchResponse,
    tags=["Semantic Tools"],
    summary="Semantic search over emails",
    description="Performs semantic search to find relevant emails based on meaning, not just keywords"
)
async def semantic_search_endpoint(request: SearchRequest):
    """
    Perform semantic search over indexed emails
    
    Args:
        request: SearchRequest with query and top_k
        
    Returns:
        SearchResponse: Ranked search results with scores
    """
    try:
        logger.info(f"Searching for: '{request.query}' (top_k={request.top_k})")
        search_engine = get_search_engine()
        results = search_engine.search(query=request.query, top_k=request.top_k)
        logger.info(f"Found {len(results)} results")
        
        return SearchResponse(results=results)
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {str(e)}"
        )


# ==================== RAG TOOLS ====================

@app.post(
    "/tool/rag/answer",
    response_model=RAGResponse,
    tags=["RAG Tools"],
    summary="Answer questions using RAG",
    description="Retrieves relevant emails and uses LLM to generate grounded answers with citations"
)
async def rag_answer_endpoint(request: RAGRequest):
    """
    Answer questions using Retrieval-Augmented Generation
    
    Args:
        request: RAGRequest with question and top_k
        
    Returns:
        RAGResponse: Answer with citations
    """
    try:
        logger.info(f"Answering question: '{request.question}' (top_k={request.top_k})")
        rag_engine = get_rag_engine()
        response = rag_engine.answer_question(
            question=request.question,
            top_k=request.top_k
        )
        logger.info(f"Generated answer with {len(response.citations)} citations")
        
        return response
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {str(e)}"
        )


# ==================== ORCHESTRATOR / WORKFLOW ====================

@app.post(
    "/workflow/execute",
    tags=["Orchestrator"],
    summary="Execute multi-agent workflow",
    description="Executes coordinated multi-agent workflow: Intent Detection → Semantic Search → Classification → RAG Generation"
)
async def execute_workflow_endpoint(request: RAGRequest):
    """
    Execute the full multi-agent IBM Orchestrate-inspired workflow.
    
    Workflow steps:
    1. Intent Detection Agent - Analyzes user query
    2. Semantic Search Agent - Searches emails by meaning
    3. Classification Agent - Prioritizes results
    4. RAG Generation Agent - Generates grounded answer
    
    Args:
        request: RAGRequest with question and top_k
        
    Returns:
        WorkflowExecution: Complete workflow execution record with all steps
    """
    try:
        logger.info(f"Starting workflow execution for: '{request.question}'")
        orchestrator = get_orchestrator()
        execution = await orchestrator.execute_workflow(
            query=request.question,
            top_k=request.top_k,
            enable_rag=True
        )
        logger.info(f"Workflow execution completed: {execution.execution_id}")
        
        return execution.to_dict()
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@app.get(
    "/workflow/execution/{execution_id}",
    tags=["Orchestrator"],
    summary="Get workflow execution details",
    description="Retrieves detailed execution record for a specific workflow run"
)
async def get_workflow_execution(execution_id: str):
    """
    Get details of a specific workflow execution
    
    Args:
        execution_id: The execution ID to retrieve
        
    Returns:
        WorkflowExecution: Execution record with all steps and results
    """
    try:
        orchestrator = get_orchestrator()
        execution = orchestrator.get_execution(execution_id)
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution {execution_id} not found"
            )
        
        return execution.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve execution: {str(e)}"
        )


@app.get(
    "/workflow/recent",
    tags=["Orchestrator"],
    summary="Get recent workflow executions",
    description="Retrieves list of recent workflow executions"
)
async def get_recent_workflows(limit: int = Query(10, ge=1, le=100)):
    """
    Get recent workflow executions
    
    Args:
        limit: Maximum number of executions to return (1-100)
        
    Returns:
        List of recent workflow executions
    """
    try:
        orchestrator = get_orchestrator()
        executions = orchestrator.list_recent_executions(limit=limit)
        return [e.to_dict() for e in executions]
    except Exception as e:
        logger.error(f"Error retrieving recent workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve workflows: {str(e)}"
        )


# ==================== UTILITY ENDPOINTS ====================

@app.get("/stats", tags=["Utilities"])
async def get_stats():
    """Get system statistics"""
    try:
        search_engine = get_search_engine()
        collection_stats = search_engine.get_collection_stats()
        
        return {
            "vector_db": collection_stats,
            "config": {
                "embedding_model": settings.embedding_model,
                "llm_provider": settings.llm_provider,
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ==================== CLASSIFICATION TOOLS ====================

@app.post(
    "/tool/emails/classify",
    response_model=ClassifyResponse,
    tags=["Classification Tools"],
    summary="Classify emails into categories",
    description="Analyzes emails and assigns categories, tags, priority, and sentiment"
)
async def classify_emails_endpoint(request: ClassifyRequest):
    """
    Classify emails into categories with tags and metadata
    
    Args:
        request: ClassifyRequest containing emails to classify
        
    Returns:
        ClassifyResponse: Classifications for each email
    """
    try:
        logger.info(f"Classifying {len(request.emails)} emails")
        
        # Convert to dict for classifier
        emails_dict = [email.model_dump() for email in request.emails]
        classifications = classifier.classify_batch(emails_dict)
        
        logger.info(f"Successfully classified {len(classifications)} emails")
        return ClassifyResponse(classifications=classifications)
    except Exception as e:
        logger.error(f"Error classifying emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify emails: {str(e)}"
        )


@app.post(
    "/tool/emails/threads",
    response_model=ThreadsResponse,
    tags=["Classification Tools"],
    summary="Detect email conversation threads",
    description="Groups emails into conversation threads based on subject and reply chains"
)
async def detect_threads_endpoint(request: ClassifyRequest):
    """
    Detect conversation threads in emails
    
    Args:
        request: ClassifyRequest containing emails to analyze
        
    Returns:
        ThreadsResponse: Detected threads with metadata
    """
    try:
        logger.info(f"Detecting threads in {len(request.emails)} emails")
        
        # Convert to dict for thread detector
        emails_dict = [email.model_dump() for email in request.emails]
        thread_data = thread_detector.detect_threads(emails_dict)
        
        # Convert to response format
        threads = []
        for thread_id, thread_info in thread_data["threads"].items():
            threads.append(EmailThread(
                thread_id=thread_id,
                subject=thread_info["subject"],
                emails=thread_info["emails"],
                participants=thread_info["participants"],
                start_date=thread_info["start_date"],
                last_date=thread_info["last_date"],
                email_count=len(thread_info["emails"])
            ))
        
        logger.info(f"Detected {len(threads)} conversation threads")
        return ThreadsResponse(threads=threads, total_threads=len(threads))
    except Exception as e:
        logger.error(f"Error detecting threads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect threads: {str(e)}"
        )


# ==================== ANALYTICS ENDPOINTS ====================

@app.get(
    "/analytics/emails",
    response_model=AnalyticsResponse,
    tags=["Analytics"],
    summary="Get email analytics",
    description="Comprehensive analytics including senders, categories, timeline, and more"
)
async def get_email_analytics():
    """Get comprehensive email analytics"""
    try:
        logger.info("Generating email analytics")
        
        # Load emails
        emails_response = load_emails()
        emails_dict = [email.model_dump() for email in emails_response.emails]
        
        # Get classifications if available
        try:
            classifications = classifier.classify_batch(emails_dict)
        except Exception:
            classifications = []
        
        # Generate analytics
        analytics = email_analytics.analyze_emails(emails_dict, classifications)
        
        logger.info("Successfully generated email analytics")
        return analytics
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics: {str(e)}"
        )


@app.get(
    "/analytics/search",
    response_model=SearchStatsResponse,
    tags=["Analytics"],
    summary="Get search analytics",
    description="Statistics about search queries and performance"
)
async def get_search_analytics():
    """Get search analytics and statistics"""
    try:
        logger.info("Retrieving search analytics")
        stats = search_analytics.get_search_stats()
        logger.info("Successfully retrieved search analytics")
        return stats
    except Exception as e:
        logger.error(f"Error retrieving search analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve search analytics: {str(e)}"
        )


@app.delete(
    "/analytics/search/clear",
    tags=["Analytics"],
    summary="Clear search history",
    description="Clears all search analytics history"
)
async def clear_search_analytics():
    """Clear search analytics history"""
    try:
        search_analytics.search_history = []
        return {"status": "cleared", "message": "Search history cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing search analytics: {str(e)}")


@app.get(
    "/analytics/performance",
    tags=["Analytics"],
    summary="Get performance analytics",
    description="Get comprehensive performance metrics, benchmarks, and scalability data"
)
async def get_performance_analytics():
    """Get comprehensive performance analytics"""
    try:
        from app.analytics_tracker import analytics_tracker
        
        logger.info("Retrieving performance analytics")
        
        # Get all analytics data
        performance_metrics = analytics_tracker.get_performance_metrics()
        benchmarks = analytics_tracker.get_benchmark_data()
        scalability = analytics_tracker.get_scalability_data()
        impact = analytics_tracker.get_impact_metrics()
        system_health = analytics_tracker.get_system_health()
        
        response = {
            "performance_metrics": performance_metrics,
            "benchmarks": benchmarks,
            "scalability": scalability,
            "impact_metrics": impact,
            "system_health": system_health
        }
        
        logger.info("Successfully retrieved performance analytics")
        return response
    except Exception as e:
        logger.error(f"Error retrieving performance analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance analytics: {str(e)}"
        )


# ==================== GMAIL OAUTH ENDPOINTS ====================

@app.get(
    "/oauth/gmail/authorize",
    response_model=OAuthUrlResponse,
    tags=["Gmail OAuth"],
    summary="Get Gmail OAuth authorization URL",
    description="Returns the URL for user to authorize Gmail access"
)
async def get_gmail_auth_url(state: Optional[str] = Query(None)):
    """
    Get Gmail OAuth authorization URL
    
    Args:
        state: Optional state parameter for CSRF protection
        
    Returns:
        OAuthUrlResponse: Authorization URL
    """
    try:
        logger.info("Generating Gmail OAuth authorization URL")
        auth_url = gmail_service.get_authorization_url(state=state)
        return OAuthUrlResponse(authorization_url=auth_url, state=state)
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating auth URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}"
        )


@app.post(
    "/oauth/gmail/callback",
    response_model=OAuthTokenResponse,
    tags=["Gmail OAuth"],
    summary="Handle Gmail OAuth callback",
    description="Exchange authorization code for access token"
)
async def gmail_oauth_callback(request: OAuthCallbackRequest):
    """
    Handle OAuth callback and exchange code for token
    
    Args:
        request: OAuthCallbackRequest with authorization code
        
    Returns:
        OAuthTokenResponse: Token information
    """
    try:
        logger.info("Processing Gmail OAuth callback")
        token_info = gmail_service.exchange_code_for_token(request.code)
        return OAuthTokenResponse(**token_info)
    except Exception as e:
        logger.error(f"Error exchanging code for token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to exchange code for token: {str(e)}"
        )


@app.get(
    "/oauth/gmail/status",
    response_model=GmailAuthStatusResponse,
    tags=["Gmail OAuth"],
    summary="Check Gmail authentication status",
    description="Check if user is authenticated with Gmail"
)
async def check_gmail_auth_status():
    """Check Gmail authentication status"""
    try:
        is_authenticated = gmail_service.is_authenticated()
        
        email = None
        if is_authenticated:
            try:
                profile = gmail_service.get_user_profile()
                email = profile.get("email")
            except Exception:
                pass
        
        return GmailAuthStatusResponse(
            authenticated=is_authenticated,
            email=email
        )
    except Exception as e:
        logger.error(f"Error checking auth status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check authentication status: {str(e)}"
        )


@app.delete(
    "/oauth/gmail/revoke",
    tags=["Gmail OAuth"],
    summary="Revoke Gmail access",
    description="Revoke OAuth token and delete credentials"
)
async def revoke_gmail_access():
    """Revoke Gmail OAuth access"""
    try:
        logger.info("Revoking Gmail access")
        gmail_service.revoke_token()
        return {"status": "revoked", "message": "Gmail access revoked successfully"}
    except Exception as e:
        logger.error(f"Error revoking access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke access: {str(e)}"
        )


@app.get(
    "/gmail/profile",
    response_model=GmailProfileResponse,
    tags=["Gmail"],
    summary="Get Gmail user profile",
    description="Get authenticated user's Gmail profile information"
)
async def get_gmail_profile():
    """Get Gmail user profile"""
    try:
        if not gmail_service.is_authenticated():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated. Please authenticate with Gmail first."
            )
        
        logger.info("Fetching Gmail profile")
        profile = gmail_service.get_user_profile()
        return GmailProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )


@app.post(
    "/gmail/fetch",
    response_model=GmailFetchResponse,
    tags=["Gmail"],
    summary="Fetch emails from Gmail",
    description="Fetch emails from authenticated Gmail account"
)
async def fetch_gmail_emails(request: GmailFetchRequest):
    """
    Fetch emails from Gmail
    
    Args:
        request: GmailFetchRequest with max_results and query
        
    Returns:
        GmailFetchResponse: List of fetched emails
    """
    try:
        if not gmail_service.is_authenticated():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated. Please authenticate with Gmail first."
            )
        
        logger.info(f"Fetching {request.max_results} emails with query: '{request.query}'")
        emails = gmail_service.fetch_emails(
            max_results=request.max_results,
            query=request.query
        )
        
        # Convert to response format
        email_responses = [GmailEmailResponse(**email) for email in emails]
        
        return GmailFetchResponse(
            emails=email_responses,
            count=len(email_responses)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emails: {str(e)}"
        )


@app.get(
    "/gmail/labels",
    tags=["Gmail"],
    summary="Get Gmail labels",
    description="Get all labels from authenticated Gmail account"
)
async def get_gmail_labels():
    """Get Gmail labels"""
    try:
        if not gmail_service.is_authenticated():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated. Please authenticate with Gmail first."
            )
        
        logger.info("Fetching Gmail labels")
        labels = gmail_service.get_labels()
        return {"labels": labels, "count": len(labels)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching labels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch labels: {str(e)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear search analytics: {str(e)}"
        )

# Register threat detection endpoints (INNOVATION FEATURE)
register_threat_detection_endpoints(app)

logger.info("✅ HackTheAgent - Email Threat Detection System Ready")
logger.info(f"📊 API Documentation: http://localhost:8000/docs")
logger.info(f"🔐 Threat Detection: POST http://localhost:8000/security/threat-detection")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )