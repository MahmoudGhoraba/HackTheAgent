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
    top_k: int = Field(default=100, ge=1, le=500, description="Number of emails to retrieve (1-500)")


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


# Gmail OAuth Models
class OAuthUrlResponse(BaseModel):
    """Response for OAuth authorization URL"""
    authorization_url: str
    state: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    """Request for OAuth callback"""
    code: str
    state: Optional[str] = None


class OAuthTokenResponse(BaseModel):
    """Response for OAuth token exchange"""
    access_token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    scopes: List[str]
    expiry: Optional[str] = None


class GmailProfileResponse(BaseModel):
    """Gmail user profile response"""
    email: str
    messages_total: int
    threads_total: int
    history_id: str


class GmailFetchRequest(BaseModel):
    """Request to fetch Gmail emails"""
    max_results: int = Field(default=100, ge=1, le=500)
    query: str = Field(default="", description="Gmail search query")


class GmailEmailResponse(BaseModel):
    """Single Gmail email"""
    id: str
    thread_id: str
    subject: str
    from_: str = Field(..., alias="from")
    to: str
    cc: Optional[str] = None
    date: str
    body: str
    snippet: str
    labels: List[str]
    internal_date: str

    class Config:
        populate_by_name = True


class GmailFetchResponse(BaseModel):
    """Response for Gmail fetch"""
    emails: List[GmailEmailResponse]
    count: int


class GmailAuthStatusResponse(BaseModel):
    """Gmail authentication status"""
    authenticated: bool
    email: Optional[str] = None