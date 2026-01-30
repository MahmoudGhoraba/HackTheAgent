from fastapi import FastAPI
from .gmail import fetch_gmail
from .outlook import fetch_outlook
from .normalize import normalize_messages
from .query import handle_query

app = FastAPI(title="HackTheAgent Backend")

@app.get("/")
def root():
    return {"status": "HackTheAgent backend running"}

@app.get("/ingest")
def ingest():
    gmail_data = fetch_gmail()
    outlook_data = fetch_outlook()
    merged = gmail_data + outlook_data
    normalized = normalize_messages(merged)
    return {"messages": normalized}

@app.post("/query")
def query(payload: dict):
    return handle_query(payload)
