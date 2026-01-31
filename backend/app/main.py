"""
FastAPI main application - HackTheAgent Email Brain Tool Server
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict

from app.config import settings
from app.schemas import (
    EmailsResponse, NormalizeRequest, NormalizeResponse,
    IndexRequest, IndexResponse, SearchRequest, SearchResponse,
    RAGRequest, RAGResponse, ErrorResponse
)
from app.load import load_emails
from app.normalize import normalize_emails
from app.semantic import get_search_engine
from app.rag import get_rag_engine

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
    summary="Load raw emails from dataset",
    description="Fetches raw emails from the local JSON dataset file"
)
async def load_emails_endpoint():
    """
    Load raw emails from the dataset
    
    Returns:
        EmailsResponse: List of raw emails
    """
    try:
        logger.info("Loading emails from dataset")
        response = load_emails()
        logger.info(f"Successfully loaded {len(response.emails)} emails")
        return response
    except FileNotFoundError as e:
        logger.error(f"Email file not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )