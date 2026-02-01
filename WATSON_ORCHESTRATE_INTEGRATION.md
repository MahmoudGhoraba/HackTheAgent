# Watson Orchestrate Backend Integration Guide

## Overview

Your backend is now fully integrated with **IBM Watson Orchestrate**! All 6 imported agents are accessible through a comprehensive REST API.

---

## 🎯 What Was Integrated

### Components Added

1. **watson_orchestrate.py** - Core client for Watson Orchestrate
2. **orchestrate_routes.py** - FastAPI routes for agent access
3. **main.py** - Updated with Orchestrate router and startup events
4. **test_orchestrate_integration.py** - Test suite for verification

### Agents Available

All 6 agents from Watson Orchestrate are now accessible:

| Agent | Purpose | Endpoint |
|-------|---------|----------|
| **intent_detection_agent** | Parse user intent and extract entities | `POST /orchestrate/intent/parse` |
| **semantic_search_agent** | Search emails by semantic similarity | `POST /orchestrate/search/semantic` |
| **classification_agent** | Classify emails by category, priority, sentiment | `POST /orchestrate/classify` |
| **rag_generation_agent** | Generate grounded answers using RAG | `POST /orchestrate/generate-answer` |
| **threat_detection_agent** | Detect phishing and security threats | `POST /orchestrate/threats/detect` |
| **database_persistence_agent** | Store execution records and analytics | `POST /orchestrate/persist` |

---

## 📡 API Endpoints

### Health & Status

#### Check Orchestrate Connection
```http
GET /orchestrate/health
```

**Response:**
```json
{
  "status": "connected",
  "agent_count": 6,
  "region": "jp-tok",
  "instance_id": "0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4"
}
```

#### List All Agents
```http
GET /orchestrate/agents
```

**Response:**
```json
{
  "success": true,
  "agents": [...],
  "count": 6
}
```

#### Get Agent Status
```http
GET /orchestrate/agents/{agent_name}/status
```

---

### Intent Detection

#### Parse User Intent
```http
POST /orchestrate/intent/parse
Content-Type: application/json

{
  "query": "Find all emails from John about the project deadline"
}
```

**Response:**
```json
{
  "success": true,
  "agent": "intent_detection_agent",
  "result": {
    "intent": "search",
    "entities": ["John", "project deadline"],
    "confidence": 0.95
  },
  "timestamp": "2026-02-01T10:30:00"
}
```

---

### Semantic Search

#### Search Emails by Meaning
```http
POST /orchestrate/search/semantic
Content-Type: application/json

{
  "query": "emails about budget and financial planning"
}
```

**Response:**
```json
{
  "success": true,
  "agent": "semantic_search_agent",
  "result": {
    "emails": [...],
    "relevance_scores": [0.92, 0.87, 0.82],
    "total_results": 15
  },
  "timestamp": "2026-02-01T10:30:05"
}
```

---

### Email Classification

#### Classify Emails
```http
POST /orchestrate/classify
Content-Type: application/json

{
  "emails": [
    {
      "id": "email_123",
      "subject": "URGENT: Project Review",
      "body": "Please review the attached document...",
      "sender": "manager@company.com"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "agent": "classification_agent",
  "result": {
    "classifications": [
      {
        "email_id": "email_123",
        "category": "Work",
        "priority": "Urgent",
        "sentiment": "Neutral",
        "confidence": 0.94
      }
    ]
  },
  "timestamp": "2026-02-01T10:30:10"
}
```

---

### RAG Generation

#### Generate Grounded Answer
```http
POST /orchestrate/generate-answer
Content-Type: application/json

{
  "query": "What are the key points from recent client discussions?",
  "context": [
    "Email 1: Meeting notes about project timeline...",
    "Email 2: Client feedback on deliverables..."
  ]
}
```

**Response:**
```json
{
  "success": true,
  "agent": "rag_generation_agent",
  "result": {
    "answer": "Based on recent discussions, the key points are...",
    "citations": [
      {"email_id": "email_456", "text_fragment": "..."},
      {"email_id": "email_789", "text_fragment": "..."}
    ],
    "confidence": 0.88
  },
  "timestamp": "2026-02-01T10:30:15"
}
```

---

### Threat Detection

#### Detect Security Threats
```http
POST /orchestrate/threats/detect
Content-Type: application/json

{
  "emails": [
    {
      "id": "email_999",
      "subject": "Verify Your Account",
      "body": "Click here to verify your account...",
      "sender": "noreply@suspicious-domain.com"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "agent": "threat_detection_agent",
  "result": {
    "threats": [
      {
        "email_id": "email_999",
        "is_phishing": true,
        "phishing_score": 0.92,
        "threat_level": "High",
        "indicators": ["suspicious_domain", "phishing_keywords", "urgent_action"]
      }
    ]
  },
  "timestamp": "2026-02-01T10:30:20"
}
```

---

### Data Persistence

#### Store Data
```http
POST /orchestrate/persist
Content-Type: application/json

{
  "data_type": "execution_record",
  "data": {
    "workflow_id": "wf_12345",
    "status": "completed",
    "results": {...}
  }
}
```

**Response:**
```json
{
  "success": true,
  "agent": "database_persistence_agent",
  "result": {
    "stored": true,
    "storage_id": "record_xyz",
    "timestamp": "2026-02-01T10:30:25"
  },
  "timestamp": "2026-02-01T10:30:25"
}
```

---

### Batch Operations

#### Classify Multiple Emails
```http
POST /orchestrate/batch/classify
Content-Type: application/json

{
  "emails": [
    {...},
    {...},
    {...}
  ]
}
```

---

## 🚀 Quick Start

### 1. Start Your Backend
```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test the Integration
```bash
# In a new terminal
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python test_orchestrate_integration.py
```

### 3. Access API Documentation
Open your browser to: **http://localhost:8000/docs**

You'll see all Watson Orchestrate endpoints under "Watson Orchestrate Integration" section!

---

## 💻 Python Usage Examples

### Using the Client Directly

```python
from app.watson_orchestrate import get_orchestrate_client

# Get the client
client = get_orchestrate_client()

# Parse intent
result = client.parse_intent("Find emails about the Q4 budget")
print(result)

# Search semantically
result = client.semantic_search("important meetings")
print(result)

# Classify emails
emails = [{"id": "1", "subject": "Review needed", "body": "..."}]
result = client.classify_emails(emails)
print(result)

# Detect threats
result = client.detect_threats(emails)
print(result)

# Generate answer with RAG
result = client.generate_answer(
    "What are the main action items?",
    context=["Email 1 content", "Email 2 content"]
)
print(result)

# Store data
result = client.persist_data("analytics", {"event": "email_processed"})
print(result)
```

### Using the FastAPI Routes

```python
import requests

base_url = "http://localhost:8000"

# Parse intent
response = requests.post(
    f"{base_url}/orchestrate/intent/parse",
    json={"query": "Find important emails"}
)
print(response.json())

# Classify emails
response = requests.post(
    f"{base_url}/orchestrate/classify",
    json={
        "emails": [
            {
                "id": "1",
                "subject": "Meeting Tomorrow",
                "body": "Let's sync at 2pm"
            }
        ]
    }
)
print(response.json())
```

---

## 🔧 Configuration

### Environment Variables

Make sure your `.env` file has:
```bash
# Watson Orchestrate Configuration
WATSON_ORCHESTRATE_API_KEY=<your-api-key>
WATSON_ORCHESTRATE_INSTANCE_ID=0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4
WATSON_ORCHESTRATE_REGION=jp-tok
```

### Verify Configuration

```bash
cd backend
python3 -c "from app.watson_orchestrate import get_orchestrate_client; client = get_orchestrate_client(); print('✅ Connected!')"
```

---

## 📊 Agent Features

### Intent Detection Agent
- Extracts primary intent from user queries
- Identifies named entities (dates, names, topics)
- Provides confidence scores

### Semantic Search Agent
- Searches emails using semantic similarity
- Creates embeddings for email content
- Ranks results by relevance

### Classification Agent
- Categorizes emails (Work, Personal, Financial, etc.)
- Detects priority levels (Urgent, High, Medium, Low)
- Analyzes sentiment (Positive, Neutral, Negative)

### RAG Generation Agent
- Retrieves relevant context from emails
- Generates grounded answers using LLM
- Tracks citations to source emails

### Threat Detection Agent
- Identifies phishing attempts
- Analyzes sender domain reputation
- Calculates overall threat score

### Database Persistence Agent
- Stores execution records
- Archives security findings
- Logs analytics events

---

## 🧪 Testing

### Run Full Test Suite
```bash
python test_orchestrate_integration.py
```

### Test Individual Agents
```bash
# Parse intent
curl -X POST http://localhost:8000/orchestrate/intent/parse \
  -H "Content-Type: application/json" \
  -d '{"query": "Find emails from John"}'

# List agents
curl http://localhost:8000/orchestrate/agents

# Check health
curl http://localhost:8000/orchestrate/health
```

---

## 📝 Response Format

All agent responses follow this format:

```json
{
  "success": true,
  "agent": "agent_name",
  "result": {
    "...agent specific data..."
  },
  "timestamp": "2026-02-01T10:30:00"
}
```

---

## 🔍 Monitoring

### Check Agent Status
```bash
curl http://localhost:8000/orchestrate/agents/intent_detection_agent/status
```

### View All Agents
```bash
curl http://localhost:8000/orchestrate/agents
```

### Monitor Logs
The backend logs all agent invocations:
```
🤖 Invoking agent: intent_detection_agent
✅ Agent intent_detection_agent completed successfully
```

---

## 🚨 Error Handling

All endpoints return proper HTTP status codes:

- **200** - Success
- **400** - Bad Request (invalid input)
- **401** - Unauthorized
- **500** - Server Error
- **503** - Service Unavailable (Orchestrate down)

Example error response:
```json
{
  "detail": "Failed to invoke agent: timeout"
}
```

---

## 🔐 Security

- Authentication uses IBM IAM tokens
- Tokens are automatically refreshed when expired
- All communication is HTTPS
- API keys stored in environment variables

---

## 📚 Next Steps

1. **Test the API**: Run `test_orchestrate_integration.py`
2. **Explore the UI**: Open `http://localhost:8000/docs`
3. **Integrate with Frontend**: Use the API endpoints in your frontend
4. **Monitor Performance**: Check agent execution times and success rates
5. **Create Workflows**: Combine agents for complex email processing

---

## 📞 Support

For issues:
1. Check Watson Orchestrate connection: `GET /orchestrate/health`
2. View available agents: `GET /orchestrate/agents`
3. Check logs for agent invocation details
4. Verify API key is set in `.env`

---

**Status:** ✅ Integration Complete  
**Backend**: FastAPI with Watson Orchestrate  
**Agents**: 6 imported and ready  
**Endpoints**: 12+ REST endpoints available  
**Documentation**: http://localhost:8000/docs
