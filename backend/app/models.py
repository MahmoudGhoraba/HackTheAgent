from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str = Field(..., description="Platform message ID")
    source: str = Field(..., description="Source platform, e.g., gmail, outlook, slack")
    sender: str = Field(..., description="Sender email or handle")
    subject: Optional[str] = Field(None, description="Message subject or title")
    body: Optional[str] = Field(None, description="Message body or content")
    timestamp: datetime = Field(..., description="When the message was received")
    platform_thread_id: Optional[str] = Field(None, description="Thread/conversation ID on the platform")
    url: Optional[str] = Field(None, description="Deep-link URL to open the message on the platform")
    tags: List[str] = Field(default_factory=list, description="Simple keywords or labels")


class Summary(BaseModel):
    text: str


class QueryRequest(BaseModel):
    keywords: Optional[List[str]] = Field(None, description="Keywords to filter by (subject/body contains any)")
    sender: Optional[str] = Field(None, description="Filter by sender substring (case-insensitive)")
    platform: Optional[List[str]] = Field(None, description="One or more platforms to include, e.g., ['gmail','outlook']")
    since: Optional[datetime] = Field(None, description="Only include messages at or after this time")
    until: Optional[datetime] = Field(None, description="Only include messages at or before this time")
    summarize: bool = Field(False, description="If true, return a short summary of the results")
    limit: Optional[int] = Field(50, description="Max number of messages to return after filtering")


class QueryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    summary: Optional[Summary] = None
