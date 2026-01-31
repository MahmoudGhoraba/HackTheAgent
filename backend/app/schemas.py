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


# Classification Models
class EmailClassification(BaseModel):
    """Email classification result"""
    id: str
    categories: List[str]
    tags: List[str]
    priority: str
    sentiment: str
    is_reply: bool
    is_forward: bool
    has_attachments: bool
    word_count: int


class ClassifyRequest(BaseModel):
    """Request for /tool/emails/classify"""
    emails: List[RawEmail]


class ClassifyResponse(BaseModel):
    """Response for /tool/emails/classify"""
    classifications: List[EmailClassification]


# Thread Models
class EmailThread(BaseModel):
    """Email conversation thread"""
    thread_id: str
    subject: str
    emails: List[str]
    participants: List[str]
    start_date: str
    last_date: str
    email_count: int


class ThreadsResponse(BaseModel):
    """Response for /tool/emails/threads"""
    threads: List[EmailThread]
    total_threads: int


# Analytics Models
class AnalyticsResponse(BaseModel):
    """Response for /analytics/emails"""
    overview: Dict[str, Any]
    senders: List[Dict[str, Any]]
    categories: Dict[str, int]
    timeline: Dict[str, Any]
    priorities: Dict[str, int]
    sentiments: Dict[str, int]
    keywords: List[Dict[str, Any]]
    threads: Dict[str, Any]


class SearchStatsResponse(BaseModel):
    """Response for /analytics/search"""
    total_searches: int
    avg_latency_ms: float
    avg_results: float
    popular_queries: List[Dict[str, Any]]
    zero_result_queries: List[str]