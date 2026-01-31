"""
Pydantic schemas for request/response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Email Models
class RawEmail(BaseModel):
    """Raw email from dataset"""
    id: str
    from_: str = Field(..., alias="from")
    to: str
    subject: str
    date: str
    body: str

    class Config:
        populate_by_name = True


class EmailsResponse(BaseModel):
    """Response for /tool/emails/load"""
    emails: List[RawEmail]


# Normalized Message Models
class MessageMetadata(BaseModel):
    """Metadata for normalized message"""
    from_: str = Field(..., alias="from")
    to: str
    subject: str
    date: str

    class Config:
        populate_by_name = True


class NormalizedMessage(BaseModel):
    """Normalized message with text and metadata"""
    id: str
    text: str
    metadata: MessageMetadata


class NormalizeRequest(BaseModel):
    """Request for /tool/emails/normalize"""
    emails: List[RawEmail]


class NormalizeResponse(BaseModel):
    """Response for /tool/emails/normalize"""
    messages: List[NormalizedMessage]


# Semantic Index Models
class IndexRequest(BaseModel):
    """Request for /tool/semantic/index"""
    messages: List[NormalizedMessage]


class IndexResponse(BaseModel):
    """Response for /tool/semantic/index"""
    status: str
    chunks_indexed: int


# Semantic Search Models
class SearchRequest(BaseModel):
    """Request for /tool/semantic/search"""
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    """Single search result"""
    id: str
    subject: str
    date: str
    score: float
    snippet: str


class SearchResponse(BaseModel):
    """Response for /tool/semantic/search"""
    results: List[SearchResult]


# RAG Models
class RAGRequest(BaseModel):
    """Request for /tool/rag/answer"""
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    """Citation for RAG answer"""
    id: str
    subject: str
    date: str
    snippet: str


class RAGResponse(BaseModel):
    """Response for /tool/rag/answer"""
    answer: str
    citations: List[Citation]


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None