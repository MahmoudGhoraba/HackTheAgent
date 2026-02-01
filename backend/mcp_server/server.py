"""
FastMCP Server for Email Brain
Exposes email intelligence tools to IBM Watson Orchestrate via SSE transport.

Supports Gmail AND Outlook email providers with shared RAG capabilities.
"""
import os
from typing import Optional

from fastmcp import FastMCP

# Import services directly from app (path is set up in __init__.py)
from app.gmail_oauth import gmail_service
from app.email_providers.outlook import outlook_provider
from app.semantic import get_search_engine
from app.rag import get_rag_engine
from app.classify import classifier, thread_detector
from app.load import load_emails
from app.analytics import email_analytics, search_analytics


# Initialize FastMCP server
mcp = FastMCP(
    name="email-brain",
    instructions="""
    Email Brain MCP Server - AI-powered email intelligence tools.
    
    Available capabilities:
    1. Gmail: Fetch, search, and manage Gmail emails (requires Google OAuth)
    2. Outlook: Fetch, search, and manage Outlook emails (requires Microsoft OAuth)
    3. Search: Semantic search over indexed emails from ANY provider
    4. RAG: Answer questions with citations across all emails
    5. Analysis: Classify, detect threads, analytics
    
    Prerequisites:
    - Gmail tools: Complete Google OAuth via web interface
    - Outlook tools: Complete Microsoft OAuth (Azure AD)
    - Search/RAG: Emails must be indexed first
    """
)


# ==================== Gmail Tools ====================

@mcp.tool()
def check_gmail_auth() -> dict:
    """
    Check if Gmail is authenticated.
    Returns authentication status and email address if authenticated.
    """
    is_authenticated = gmail_service.is_authenticated()
    email = None
    
    if is_authenticated:
        try:
            profile = gmail_service.get_user_profile()
            email = profile.get("email")
        except Exception:
            pass
    
    return {"authenticated": is_authenticated, "email": email}


@mcp.tool()
def gmail_fetch_emails(max_results: int = 100, query: str = "") -> dict:
    """
    Fetch emails from Gmail.
    
    Args:
        max_results: Maximum emails to fetch (1-500)
        query: Gmail search query (e.g., 'is:unread', 'from:john@example.com')
    """
    if not gmail_service.is_authenticated():
        return {"error": "Not authenticated. Complete OAuth via web interface first."}
    
    max_results = max(1, min(500, max_results))
    emails = gmail_service.fetch_emails(max_results=max_results, query=query)
    return {"emails": emails, "count": len(emails)}


@mcp.tool()
def gmail_search(query: str, max_results: int = 50) -> dict:
    """
    Search Gmail using query syntax.
    
    Args:
        query: Gmail query (e.g., 'subject:urgent', 'has:attachment', 'after:2024/01/01')
        max_results: Maximum results (1-500)
    """
    if not gmail_service.is_authenticated():
        return {"error": "Not authenticated. Complete OAuth via web interface first."}
    
    if not query:
        return {"error": "Query is required"}
    
    max_results = max(1, min(500, max_results))
    emails = gmail_service.search_emails(query=query, max_results=max_results)
    return {"emails": emails, "count": len(emails)}


@mcp.tool()
def gmail_get_labels() -> dict:
    """Get all Gmail labels/folders."""
    if not gmail_service.is_authenticated():
        return {"error": "Not authenticated. Complete OAuth via web interface first."}
    
    labels = gmail_service.get_labels()
    return {"labels": labels, "count": len(labels)}


@mcp.tool()
def gmail_get_profile() -> dict:
    """Get Gmail user profile (email, message count, etc.)."""
    if not gmail_service.is_authenticated():
        return {"error": "Not authenticated. Complete OAuth via web interface first."}
    
    return gmail_service.get_user_profile()


# ==================== Outlook Tools ====================

@mcp.tool()
def check_outlook_auth() -> dict:
    """
    Check if Outlook is authenticated.
    Returns authentication status and email address if authenticated.
    """
    try:
        is_authenticated = outlook_provider.is_authenticated()
        email = None
        
        if is_authenticated:
            try:
                profile = outlook_provider.get_profile()
                email = profile.get("email")
            except Exception:
                pass
        
        return {"authenticated": is_authenticated, "email": email, "provider": "outlook"}
    except ValueError as e:
        return {"authenticated": False, "error": str(e), "provider": "outlook"}


@mcp.tool()
def outlook_fetch_emails(max_results: int = 100, query: str = "") -> dict:
    """
    Fetch emails from Outlook.
    
    Args:
        max_results: Maximum emails to fetch (1-100)
        query: Search query (text search in subject/body)
    """
    try:
        if not outlook_provider.is_authenticated():
            return {"error": "Not authenticated. Complete Microsoft OAuth first.", "provider": "outlook"}
        
        max_results = max(1, min(100, max_results))
        emails = outlook_provider.fetch_emails(max_results=max_results, query=query)
        return {"emails": emails, "count": len(emails), "provider": "outlook"}
    except ValueError as e:
        return {"error": str(e), "provider": "outlook"}


@mcp.tool()
def outlook_search(query: str, max_results: int = 50) -> dict:
    """
    Search Outlook emails.
    
    Args:
        query: Search text (searches subject, body, sender)
        max_results: Maximum results (1-100)
    """
    try:
        if not outlook_provider.is_authenticated():
            return {"error": "Not authenticated. Complete Microsoft OAuth first.", "provider": "outlook"}
        
        if not query:
            return {"error": "Query is required", "provider": "outlook"}
        
        max_results = max(1, min(100, max_results))
        emails = outlook_provider.search_emails(query=query, max_results=max_results)
        return {"emails": emails, "count": len(emails), "provider": "outlook"}
    except ValueError as e:
        return {"error": str(e), "provider": "outlook"}


@mcp.tool()
def outlook_get_folders() -> dict:
    """Get all Outlook mail folders (Inbox, Sent, custom folders, etc.)."""
    try:
        if not outlook_provider.is_authenticated():
            return {"error": "Not authenticated. Complete Microsoft OAuth first.", "provider": "outlook"}
        
        folders = outlook_provider.get_labels()
        return {"folders": folders, "count": len(folders), "provider": "outlook"}
    except ValueError as e:
        return {"error": str(e), "provider": "outlook"}


@mcp.tool()
def outlook_get_profile() -> dict:
    """Get Outlook user profile (email, name, etc.)."""
    try:
        if not outlook_provider.is_authenticated():
            return {"error": "Not authenticated. Complete Microsoft OAuth first.", "provider": "outlook"}
        
        return outlook_provider.get_profile()
    except ValueError as e:
        return {"error": str(e), "provider": "outlook"}


# ==================== Unified Email Tools ====================

@mcp.tool()
def get_all_providers_status() -> dict:
    """
    Check authentication status of all email providers.
    Returns which providers are connected and ready to use.
    """
    gmail_auth = False
    gmail_email = None
    outlook_auth = False
    outlook_email = None
    
    # Check Gmail
    try:
        gmail_auth = gmail_service.is_authenticated()
        if gmail_auth:
            profile = gmail_service.get_user_profile()
            gmail_email = profile.get("email")
    except Exception:
        pass
    
    # Check Outlook
    try:
        outlook_auth = outlook_provider.is_authenticated()
        if outlook_auth:
            profile = outlook_provider.get_profile()
            outlook_email = profile.get("email")
    except Exception:
        pass
    
    return {
        "providers": {
            "gmail": {"authenticated": gmail_auth, "email": gmail_email},
            "outlook": {"authenticated": outlook_auth, "email": outlook_email}
        },
        "total_connected": sum([gmail_auth, outlook_auth])
    }


# ==================== Search & RAG Tools ====================

@mcp.tool()
def search_emails_semantic(query: str, top_k: int = 5) -> dict:
    """
    Semantic search over indexed emails. Finds by meaning, not keywords.
    
    Args:
        query: Natural language query (e.g., 'urgent deadlines', 'project updates')
        top_k: Number of results (1-20)
    """
    top_k = max(1, min(20, top_k))
    search_engine = get_search_engine()
    results = search_engine.search(query=query, top_k=top_k)
    
    return {
        "query": query,
        "results": [
            {"id": r.id, "subject": r.subject, "date": r.date, "score": r.score, "snippet": r.snippet}
            for r in results
        ],
        "count": len(results)
    }


@mcp.tool()
def answer_question(question: str, top_k: int = 5) -> dict:
    """
    Answer questions using RAG (Retrieval-Augmented Generation).
    
    Args:
        question: Natural language question (e.g., 'What are my deadlines?')
        top_k: Number of emails for context (1-20)
    """
    top_k = max(1, min(20, top_k))
    rag_engine = get_rag_engine()
    response = rag_engine.answer_question(question=question, top_k=top_k)
    
    return {
        "question": question,
        "answer": response.answer,
        "citations": [
            {"id": c.id, "subject": c.subject, "date": c.date, "snippet": c.snippet}
            for c in response.citations
        ]
    }


# ==================== Analysis Tools ====================

@mcp.tool()
def classify_loaded_emails() -> dict:
    """
    Classify loaded emails by category, priority, and sentiment.
    Returns categories, priority (High/Medium/Low), sentiment, and tags.
    """
    emails_response = load_emails()
    emails_dict = [email.model_dump() for email in emails_response.emails]
    
    if not emails_dict:
        return {"classifications": [], "count": 0, "message": "No emails found"}
    
    classifications = classifier.classify_batch(emails_dict)
    
    return {
        "classifications": [
            {
                "id": c.id, "categories": c.categories, "tags": c.tags,
                "priority": c.priority, "sentiment": c.sentiment,
                "is_reply": c.is_reply, "is_forward": c.is_forward
            }
            for c in classifications
        ],
        "count": len(classifications)
    }


@mcp.tool()
def detect_email_threads() -> dict:
    """
    Detect conversation threads in loaded emails.
    Groups by subject and reply chains.
    """
    emails_response = load_emails()
    emails_dict = [email.model_dump() for email in emails_response.emails]
    
    if not emails_dict:
        return {"threads": [], "total_threads": 0, "message": "No emails found"}
    
    thread_data = thread_detector.detect_threads(emails_dict)
    
    return {
        "threads": [
            {
                "thread_id": tid,
                "subject": info["subject"],
                "participants": info["participants"],
                "email_count": len(info["emails"]),
                "start_date": info["start_date"],
                "last_date": info["last_date"]
            }
            for tid, info in thread_data["threads"].items()
        ],
        "total_threads": len(thread_data["threads"])
    }


@mcp.tool()
def analyze_emails() -> dict:
    """
    Get comprehensive email analytics: senders, categories, timeline, priorities.
    """
    emails_response = load_emails()
    emails_dict = [email.model_dump() for email in emails_response.emails]
    
    if not emails_dict:
        return {"overview": {"total_emails": 0}, "message": "No emails found"}
    
    try:
        classifications = classifier.classify_batch(emails_dict)
    except Exception:
        classifications = []
    
    analytics = email_analytics.analyze_emails(emails_dict, classifications)
    
    return {
        "overview": analytics.overview,
        "senders": analytics.senders,
        "categories": analytics.categories,
        "priorities": analytics.priorities,
        "sentiments": analytics.sentiments
    }


@mcp.tool()
def get_vector_index_stats() -> dict:
    """Get statistics about the indexed email collection."""
    search_engine = get_search_engine()
    return search_engine.get_collection_stats()


@mcp.tool()
def get_search_analytics() -> dict:
    """Get search usage analytics: total searches, latency, popular queries."""
    stats = search_analytics.get_search_stats()
    return {
        "total_searches": stats.total_searches,
        "avg_latency_ms": stats.avg_latency_ms,
        "avg_results": stats.avg_results,
        "popular_queries": stats.popular_queries
    }


# Entry point
if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 8001))
    mcp.run(transport="sse", port=port)
