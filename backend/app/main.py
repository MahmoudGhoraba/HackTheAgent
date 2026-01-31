from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from .orchestrator import call_workflow, list_workflow_actions, list_agents, register_gmail_agent, register_gmail_tools
from .gmail_agent import get_gmail_agent

app = FastAPI(title="HackTheAgent Backend")


# Pydantic models for request validation
class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    html: bool = False


class SearchEmailsRequest(BaseModel):
    from_email: Optional[str] = None
    to_email: Optional[str] = None
    subject: Optional[str] = None
    after_date: Optional[str] = None
    before_date: Optional[str] = None
    has_attachment: Optional[bool] = None
    is_unread: Optional[bool] = None
    max_results: int = 10


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/agents")
def get_agents():
    return list_agents()


@app.get("/actions")
def get_actions():
    actions = list_workflow_actions()
    print(actions)
    return actions


@app.get("/fetch-messages")
def fetch_messages(limit: int = 5, subject: Optional[str] = None, to_address: Optional[str] = None, next_page_token: Optional[str] = None):
    params: dict[str, Any] = {
        "limit": limit
    }
    if subject:
        params["subject"] = subject
    if to_address:
        params["to_address"] = to_address
    if next_page_token:
        params["next_page_token"] = next_page_token

    return call_workflow(action="list_emails_in_gmail", params=params)


@app.post("/query")
def query(payload: dict):
    return call_workflow(action="Query Messages", params=payload)


# ============================================
# Gmail Agent Endpoints
# ============================================

@app.get("/gmail/list")
def gmail_list_emails(
    max_results: int = 10,
    page_token: Optional[str] = None,
    query: Optional[str] = None
):
    """
    List emails from Gmail inbox
    
    Query examples:
    - "from:example@gmail.com"
    - "subject:meeting"
    - "is:unread"
    - "after:2026/01/01"
    """
    try:
        agent = get_gmail_agent()
        return agent.list_emails(
            max_results=max_results,
            page_token=page_token,
            query=query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gmail/read/{email_id}")
def gmail_read_email(email_id: str):
    """
    Read full details of a specific email by ID
    """
    try:
        agent = get_gmail_agent()
        return agent.read_email_details(email_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gmail/send")
def gmail_send_email(request: SendEmailRequest):
    """
    Send an email via Gmail
    """
    try:
        agent = get_gmail_agent()
        return agent.send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            bcc=request.bcc,
            html=request.html
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gmail/search")
def gmail_search_emails(request: SearchEmailsRequest):
    """
    Search emails with advanced filters
    
    Example request:
    {
        "from_email": "example@gmail.com",
        "subject": "meeting",
        "is_unread": true,
        "after_date": "2026/01/01",
        "max_results": 20
    }
    """
    try:
        agent = get_gmail_agent()
        return agent.search_emails(
            from_email=request.from_email,
            to_email=request.to_email,
            subject=request.subject,
            after_date=request.after_date,
            before_date=request.before_date,
            has_attachment=request.has_attachment,
            is_unread=request.is_unread,
            max_results=request.max_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gmail/register")
def register_gmail_agent_endpoint():
    """
    Register Gmail agent with Watson Orchestrate
    """
    try:
        return register_gmail_agent()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
