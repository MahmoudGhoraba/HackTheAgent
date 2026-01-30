# app/orchestrator.py
import requests
from .config import ORCHESTRATOR_BASE_URL, WORKFLOW_ID, API_KEY

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_workflow(action: str, payload: dict = None):
    """Call the Orchestrator workflow with optional action and payload"""
    data = {
        "workflow": WORKFLOW_ID,
        "action": action,
        "params": payload or {}
    }
    response = requests.post(f"{ORCHESTRATOR_BASE_URL}/execute", json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()
