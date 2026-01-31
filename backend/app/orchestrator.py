# app/orchestrator.py
import requests
from .config import API_KEY, INSTANCE_URL, WORKFLOW_ID

def get_iam_token(api_key: str) -> str:
    """Get IAM token from IBM Cloud."""
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    resp = requests.post(url, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def list_workflow_actions() -> dict:
    """List all actions/tools inside a workflow."""
    token = get_iam_token(API_KEY)
    url = f"{INSTANCE_URL.rstrip('/')}/v1/orchestrate/skillsets/{WORKFLOW_ID}/actions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.get(url, headers=headers)

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"error": resp.json()}

    return resp.json()

def list_agents() -> dict:
    token = get_iam_token(API_KEY)
    # Ensure '/v1/agents' is the suffix
    url = f"{INSTANCE_URL.rstrip('/')}/v1/orchestrate/agents" 

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    resp = requests.get(url, headers=headers)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"error": resp.json()}

    return resp.json()


def call_workflow(action: str, params: dict | None = None) -> dict:
    """Call a workflow action in Watson Orchestrate."""
    if params is None:
        params = {}

    token = get_iam_token(API_KEY)
    url = f"{INSTANCE_URL.rstrip('/')}/v1/orchestrate/workflows/{WORKFLOW_ID}/actions"

    payload = {
        "name": action,
        "parameters": params
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers)

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"error": resp.json()}

    return resp.json()


def register_tool(tool_definition: dict) -> dict:
    """
    Register a single tool with Watson Orchestrate
    
    Args:
        tool_definition: Tool definition with name, description, and parameters
    
    Returns:
        Registration response from Watson Orchestrate
    """
    token = get_iam_token(API_KEY)
    url = f"{INSTANCE_URL.rstrip('/')}/v1/orchestrate/tools"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(url, json=tool_definition, headers=headers)
    
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"error": resp.json()}
    
    return resp.json()


def register_gmail_tools() -> dict:
    """
    Register all Gmail tools independently with Watson Orchestrate
    
    Returns:
        Dictionary with registration results for each tool
    """
    tools = [
        {
            "name": "list_emails",
            "description": "List emails from Gmail inbox with pagination and filtering",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of emails to return",
                        "default": 10
                    },
                    "page_token": {
                        "type": "string",
                        "description": "Token for pagination"
                    },
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:example@gmail.com')"
                    }
                },
                "required": []
            }
        },
        {
            "name": "read_email_details",
            "description": "Read full details of a specific email by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Gmail message ID"
                    }
                },
                "required": ["email_id"]
            }
        },
        {
            "name": "send_email",
            "description": "Send an email via Gmail",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    },
                    "cc": {
                        "type": "string",
                        "description": "CC recipients (comma-separated)"
                    },
                    "bcc": {
                        "type": "string",
                        "description": "BCC recipients (comma-separated)"
                    },
                    "html": {
                        "type": "boolean",
                        "description": "Whether body is HTML",
                        "default": False
                    }
                },
                "required": ["to", "subject", "body"]
            }
        },
        {
            "name": "search_emails",
            "description": "Search emails with advanced filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_email": {
                        "type": "string",
                        "description": "Filter by sender email"
                    },
                    "to_email": {
                        "type": "string",
                        "description": "Filter by recipient email"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Filter by subject keywords"
                    },
                    "after_date": {
                        "type": "string",
                        "description": "Filter emails after date (YYYY/MM/DD)"
                    },
                    "before_date": {
                        "type": "string",
                        "description": "Filter emails before date (YYYY/MM/DD)"
                    },
                    "has_attachment": {
                        "type": "boolean",
                        "description": "Filter emails with attachments"
                    },
                    "is_unread": {
                        "type": "boolean",
                        "description": "Filter unread emails"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10
                    }
                },
                "required": []
            }
        }
    ]
    
    results = {}
    for tool in tools:
        tool_name = tool["name"]
        result = register_tool(tool)
        results[tool_name] = result
    
    return results


def register_gmail_agent(
    agent_name: str = "gmail_agent",
    agent_description: str = "Agent for managing Gmail emails with list, read, send, and search capabilities"
) -> dict:
    """
    Register Gmail agent with Watson Orchestrate
    
    Args:
        agent_name: Name of the agent
        agent_description: Description of the agent
    
    Returns:
        Registration response from Watson Orchestrate
    """
    token = get_iam_token(API_KEY)
    url = f"{INSTANCE_URL.rstrip('/')}/v1/orchestrate/agents"
    
    # Define agent with tools/actions
    # Note: Watson Orchestrate expects tools as an array of strings (tool names/IDs)
    # Tools should be registered separately or referenced by existing tool IDs
    agent_payload = {
        "name": agent_name,
        "description": agent_description,
        "style": "default",  # Agent style: 'default', 'react', 'planner', or 'react_intrinsic'
        "llm": "meta-llama/llama-3-70b-instruct",  # LLM model ID as string
        "tools": [
            "list_emails",
            "read_email_details",
            "send_email",
            "search_emails"
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(url, json=agent_payload, headers=headers)
    
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"error": resp.json()}
    
    return resp.json()
