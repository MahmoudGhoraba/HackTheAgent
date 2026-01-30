from fastapi import FastAPI
from app.gmail import fetch_gmail
from app.outlook import fetch_outlook
from app.normalize import normalize_messages
from app.query import handle_query

app = FastAPI(title="HackTheAgent Backend (Mock Demo)", version="1.0.0")

# ----------------------------
# Root endpoint
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "HackTheAgent backend skeleton running",
        "agents": [
            "Gmail Agent",
            "Outlook Agent",
            "Ingestion/Normalization Agent",
            "Query / Summary Agent"
        ]
    }

# ----------------------------
# Gmail Agent Tool
# ----------------------------
@app.get("/gmail/fetch")
def gmail_fetch():
    messages = fetch_gmail()
    return {"messages": messages}

# ----------------------------
# Outlook Agent Tool
# ----------------------------
@app.get("/outlook/fetch")
def outlook_fetch():
    messages = fetch_outlook()
    return {"messages": messages}

# ----------------------------
# Ingestion / Normalization Agent Tool
# ----------------------------
@app.get("/ingest")
def ingest():
    gmail_data = fetch_gmail()
    outlook_data = fetch_outlook()
    merged = gmail_data + outlook_data
    normalized = normalize_messages(merged)
    return {"normalized_messages": normalized}

# ----------------------------
# Query / Summary Agent Tool
# ----------------------------
@app.post("/query")
def query(payload: dict):
    """
    Expected payload format:
    {
        "query": "internship",
        "messages": [ ... normalized messages ... ]
    }
    """
    result = handle_query(payload)
    return result
