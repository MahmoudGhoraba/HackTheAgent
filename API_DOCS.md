# API Documentation

Complete REST API reference for HackTheAgent Email Brain backend.

**Base URL:** `http://localhost:8000`

**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

Currently, most endpoints are open. For future production use:
- Gmail OAuth: See `/oauth/gmail/authorize` for OAuth flow
- API Key: Configure via environment variables

---

## Email Tools

### Load Emails

Load emails from dataset or Gmail.

```
GET /tool/emails/load
```

**Query Parameters:**
- `source` (string): `"dataset"` or `"gmail"` (default: `"dataset"`)
- `limit` (integer): Maximum emails to load (default: 25)

**Response:**
```json
{
  "success": true,
  "emails_loaded": 25,
  "emails": [
    {
      "id": "email_1",
      "from": "sender@example.com",
      "to": ["recipient@example.com"],
      "subject": "Meeting Tomorrow",
      "body": "Hi, let's meet tomorrow at 2pm...",
      "date": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Normalize Emails

Convert emails to structured format.

```
POST /tool/emails/normalize
```

**Request Body:**
```json
{
  "emails": [
    {
      "id": "email_1",
      "from": "sender@example.com",
      "to": ["recipient@example.com"],
      "subject": "Meeting",
      "body": "Let's meet tomorrow..."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "normalized_count": 1,
  "messages": [
    {
      "id": "email_1",
      "content": "From: sender@example.com\nTo: recipient@example.com\nSubject: Meeting\n\nLet's meet tomorrow...",
      "metadata": {
        "sender": "sender@example.com",
        "recipients": ["recipient@example.com"],
        "subject": "Meeting",
        "date": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

---

### Classify Emails

Classify emails into categories.

```
POST /tool/emails/classify
```

**Request Body:**
```json
{
  "emails": [
    {
      "id": "email_1",
      "subject": "Project Update",
      "body": "The project is on schedule..."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "classifications": [
    {
      "id": "email_1",
      "category": "Work",
      "priority": "Medium",
      "sentiment": "Neutral",
      "tags": ["project", "update"]
    }
  ]
}
```

**Categories:** Work, Urgent, Financial, Security, Social, Other

**Priority:** High, Medium, Low

**Sentiment:** Positive, Neutral, Negative

---

## Semantic Search

### Search Emails

Find emails by semantic meaning.

```
POST /tool/semantic/search
```

**Request Body:**
```json
{
  "query": "Find emails about meetings",
  "top_k": 5,
  "score_threshold": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "query": "Find emails about meetings",
  "results": [
    {
      "email_id": "email_1",
      "score": 0.92,
      "subject": "Meeting Tomorrow",
      "body_snippet": "Let's meet tomorrow at 2pm to discuss the project...",
      "sender": "alice@example.com",
      "date": "2024-01-15T10:30:00Z"
    },
    {
      "email_id": "email_2",
      "score": 0.85,
      "subject": "Team Standup",
      "body_snippet": "Our daily standup is scheduled for 10am...",
      "sender": "bob@example.com",
      "date": "2024-01-15T09:00:00Z"
    }
  ],
  "total_results": 2,
  "latency_ms": 1250
}
```

**Parameters:**
- `query` (string, required): Search query
- `top_k` (integer): Number of results (default: 5)
- `score_threshold` (float): Minimum similarity score 0-1 (default: 0.0)

---

### Index Embeddings

Create embeddings and index emails.

```
POST /tool/semantic/index
```

**Request Body:**
```json
{
  "emails": [
    {
      "id": "email_1",
      "content": "Meeting tomorrow at 2pm..."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "indexed": 1,
  "chunks_created": 1,
  "total_tokens": 45
}
```

---

## RAG (Retrieval-Augmented Generation)

### Answer Question with Citations

Get AI-generated answer with email citations.

```
POST /tool/rag/answer
```

**Request Body:**
```json
{
  "question": "What meetings do I have scheduled?",
  "context_emails": 5,
  "use_llm": true
}
```

**Response:**
```json
{
  "success": true,
  "question": "What meetings do I have scheduled?",
  "answer": "Based on your emails, you have two meetings scheduled: 1) Meeting tomorrow with Alice at 2pm to discuss the project, and 2) Daily team standup tomorrow at 10am.",
  "citations": [
    {
      "email_id": "email_1",
      "sender": "alice@example.com",
      "subject": "Meeting Tomorrow",
      "relevant_excerpt": "Let's meet tomorrow at 2pm to discuss the project",
      "confidence": 0.95
    },
    {
      "email_id": "email_2",
      "sender": "bob@example.com",
      "subject": "Team Standup",
      "relevant_excerpt": "Our daily standup is scheduled for 10am",
      "confidence": 0.92
    }
  ],
  "latency_ms": 3450
}
```

**Parameters:**
- `question` (string, required): Question to answer
- `context_emails` (integer): Number of context emails (default: 5)
- `use_llm` (boolean): Use LLM for generation (default: true)

---

## Gmail OAuth

### Get Authorization URL

Get OAuth authorization URL for Gmail.

```
GET /oauth/gmail/authorize
```

**Response:**
```json
{
  "success": true,
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "state": "random_state_token"
}
```

---

### Handle OAuth Callback

Called by Gmail after user authorizes.

```
POST /oauth/gmail/callback
```

**Request Body:**
```json
{
  "code": "authorization_code",
  "state": "state_token"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Gmail authentication successful",
  "user_email": "user@gmail.com"
}
```

---

### Check Authentication Status

Check if Gmail is connected.

```
GET /oauth/gmail/status
```

**Response:**
```json
{
  "authenticated": true,
  "email": "user@gmail.com",
  "connected_at": "2024-01-15T10:30:00Z"
}
```

---

### Revoke Gmail Access

Disconnect Gmail.

```
DELETE /oauth/gmail/revoke
```

**Response:**
```json
{
  "success": true,
  "message": "Gmail access revoked"
}
```

---

## Gmail Operations

### Get Gmail Profile

Get authenticated user's Gmail profile.

```
GET /gmail/profile
```

**Response:**
```json
{
  "success": true,
  "email": "user@gmail.com",
  "name": "John Doe",
  "history_id": "12345"
}
```

---

### Fetch Emails from Gmail

Fetch emails directly from Gmail inbox.

```
POST /gmail/fetch
```

**Request Body:**
```json
{
  "query": "is:unread",
  "max_results": 10,
  "include_body": true
}
```

**Response:**
```json
{
  "success": true,
  "fetched": 5,
  "emails": [
    {
      "id": "gmail_msg_1",
      "from": "sender@gmail.com",
      "to": ["user@gmail.com"],
      "subject": "Important Update",
      "body": "Here's the update you requested...",
      "date": "2024-01-15T10:30:00Z",
      "labels": ["INBOX", "IMPORTANT"]
    }
  ]
}
```

**Parameters:**
- `query` (string): Gmail search query (e.g., `is:unread`, `from:alice@example.com`)
- `max_results` (integer): Max emails (default: 10)
- `include_body` (boolean): Include email body (default: true)

---

### Get Gmail Labels

List Gmail labels.

```
GET /gmail/labels
```

**Response:**
```json
{
  "success": true,
  "labels": [
    {
      "id": "INBOX",
      "name": "INBOX",
      "message_count": 45,
      "unread_count": 3
    },
    {
      "id": "SENT",
      "name": "SENT",
      "message_count": 120,
      "unread_count": 0
    }
  ]
}
```

---

## Analytics

### Get Email Analytics

Get statistics about your emails.

```
GET /analytics/emails
```

**Response:**
```json
{
  "success": true,
  "total_emails": 25,
  "categories": {
    "Work": 12,
    "Personal": 8,
    "Urgent": 3,
    "Other": 2
  },
  "priority_distribution": {
    "High": 3,
    "Medium": 10,
    "Low": 12
  },
  "sentiment_distribution": {
    "Positive": 8,
    "Neutral": 14,
    "Negative": 3
  },
  "top_senders": [
    {
      "sender": "alice@example.com",
      "count": 5,
      "latest": "2024-01-15T10:30:00Z"
    },
    {
      "sender": "bob@example.com",
      "count": 4,
      "latest": "2024-01-15T09:00:00Z"
    }
  ],
  "timeline": [
    {
      "date": "2024-01-15",
      "count": 3
    }
  ]
}
```

---

### Get Search Analytics

Get statistics about searches performed.

```
GET /analytics/search
```

**Response:**
```json
{
  "success": true,
  "total_searches": 12,
  "average_latency_ms": 1250,
  "popular_queries": [
    {
      "query": "meetings",
      "count": 3,
      "avg_results": 5
    },
    {
      "query": "urgent",
      "count": 2,
      "avg_results": 3
    }
  ],
  "zero_result_queries": [
    "birthday reminders",
    "invoice payments"
  ]
}
```

---

### Clear Search History

Clear search analytics.

```
DELETE /analytics/search
```

**Response:**
```json
{
  "success": true,
  "message": "Search history cleared"
}
```

---

## Utility Endpoints

### Health Check

Check backend health.

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 1234,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### System Statistics

Get system stats.

```
GET /stats
```

**Response:**
```json
{
  "success": true,
  "emails_loaded": 25,
  "emails_indexed": 25,
  "total_chunks": 127,
  "vector_store_size": "1.2 MB",
  "cache_size": 0,
  "uptime_seconds": 1234,
  "memory_usage_mb": 245
}
```

---

## Multi-Agent Workflow

### Execute Full Workflow

Execute the complete 5-step workflow.

```
POST /workflow/execute
```

**Request Body:**
```json
{
  "user_query": "What are my most recent emails about?",
  "load_emails": true,
  "run_classification": true,
  "run_threat_detection": true,
  "parallel": true
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "workflow_12345",
  "steps": [
    {
      "step": 1,
      "name": "Intent Detection",
      "status": "completed",
      "duration_ms": 150,
      "result": {
        "intent": "search",
        "entities": ["emails", "recent"]
      }
    },
    {
      "step": 2,
      "name": "Semantic Search",
      "status": "completed",
      "duration_ms": 1200,
      "result": {
        "results_found": 5,
        "top_result_score": 0.94
      }
    },
    {
      "step": 3,
      "name": "Classification",
      "status": "completed",
      "duration_ms": 500,
      "result": {
        "classified": 5
      }
    },
    {
      "step": 4,
      "name": "Threat Detection",
      "status": "completed",
      "duration_ms": 300,
      "result": {
        "threats_found": 0
      }
    },
    {
      "step": 5,
      "name": "Persistence",
      "status": "completed",
      "duration_ms": 200,
      "result": {
        "records_stored": 5
      }
    }
  ],
  "total_duration_ms": 2350,
  "execution_mode": "parallel"
}
```

---

## Error Responses

All endpoints may return errors with this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "error_code": "INVALID_REQUEST",
  "details": "Additional context if available"
}
```

**Common Error Codes:**
- `INVALID_REQUEST` - Missing or invalid parameters
- `NOT_FOUND` - Resource not found
- `UNAUTHORIZED` - Authentication required
- `INTERNAL_ERROR` - Server error
- `GMAIL_ERROR` - Gmail API error
- `LLM_ERROR` - LLM service error

---

## Rate Limiting

Currently no rate limiting. Future versions may include:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## Example Usage

### Python with Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Search emails
response = requests.post(
    f"{BASE_URL}/tool/semantic/search",
    json={
        "query": "Find emails about meetings",
        "top_k": 5
    }
)
results = response.json()

# Get answer with citations
response = requests.post(
    f"{BASE_URL}/tool/rag/answer",
    json={
        "question": "What meetings do I have?",
        "context_emails": 5
    }
)
answer = response.json()

print(f"Answer: {answer['answer']}")
for citation in answer['citations']:
    print(f"  - {citation['sender']}: {citation['subject']}")
```

### cURL

```bash
# Search emails
curl -X POST http://localhost:8000/tool/semantic/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find emails about meetings",
    "top_k": 5
  }'

# Get answer
curl -X POST http://localhost:8000/tool/rag/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What meetings do I have?",
    "context_emails": 5
  }'

# Check health
curl http://localhost:8000/health
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000";

// Search emails
const searchResponse = await fetch(
  `${BASE_URL}/tool/semantic/search`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: "Find emails about meetings",
      top_k: 5
    })
  }
);
const searchResults = await searchResponse.json();

// Get answer
const answerResponse = await fetch(
  `${BASE_URL}/tool/rag/answer`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: "What meetings do I have?",
      context_emails: 5
    })
  }
);
const answer = await answerResponse.json();
```

---

## See Also

- **[README.md](./README.md)** - Quick start guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design
- **[FINAL_OUTCOME.md](./FINAL_OUTCOME.md)** - Project results
- **Swagger UI**: http://localhost:8000/docs (when backend running)
