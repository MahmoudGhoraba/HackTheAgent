# app/main.py
from fastapi import FastAPI
from .orchestrator import call_workflow

app = FastAPI(title="HackTheAgent Backend")

@app.get("/")
def root():
    return {"status": "HackTheAgent backend running"}

@app.get("/fetch-messages")
def fetch_messages():
    """Fetch merged emails from Orchestrator workflow"""
    result = call_workflow(action="fetch_messages")
    return {"messages": result.get("merged_messages", [])}

@app.post("/query")
def query(payload: dict):
    """Query messages via Orchestrator workflow"""
    result = call_workflow(action="query", payload=payload)
    return result
