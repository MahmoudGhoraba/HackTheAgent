# 🚀 Quick Reference - Watson Orchestrate API

## 🎯 What You Can Do Now

Your backend is connected to 6 AI agents in Watson Orchestrate. Use them like this:

---

## 1️⃣ Parse User Intent

**What it does:** Understand what user wants to do

**Request:**
```bash
curl -X POST http://localhost:8000/orchestrate/intent/parse \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find all emails from John about the project deadline"
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/orchestrate/intent/parse",
    json={"query": "Find emails from John"}
)
print(response.json())
```

**What you get:**
```json
{
  "success": true,
  "agent": "intent_detection_agent",
  "result": {
    "intent": "search",
    "entities": ["John", "project deadline"],
    "confidence": 0.95
  }
}
```

---

## 2️⃣ Semantic Search

**What it does:** Find emails by meaning, not just keywords

**Request:**
```bash
curl -X POST http://localhost:8000/orchestrate/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "emails about budget and financial planning"
  }'
```

**Python:**
```python
response = requests.post(
    "http://localhost:8000/orchestrate/search/semantic",
    json={"query": "budget planning"}
)
```

---

## 3️⃣ Classify Emails

**What it does:** Organize emails into categories with priority & sentiment

**Request:**
```bash
curl -X POST http://localhost:8000/orchestrate/classify \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      {
        "id": "1",
        "subject": "URGENT: Meeting Tomorrow",
        "body": "Please join the call at 2pm",
        "sender": "boss@company.com"
      }
    ]
  }'
```

**Python:**
```python
response = requests.post(
    "http://localhost:8000/orchestrate/classify",
    json={
        "emails": [
            {
                "id": "1",
                "subject": "Important Review",
                "body": "Review the document...",
                "sender": "john@example.com"
            }
        ]
    }
)
result = response.json()
print(f"Category: {result['result']['classifications'][0]['category']}")
print(f"Priority: {result['result']['classifications'][0]['priority']}")
print(f"Sentiment: {result['result']['classifications'][0]['sentiment']}")
```

**Returns:**
```
Category: Work
Priority: Urgent
Sentiment: Neutral
Confidence: 0.94
```

---

## 4️⃣ Detect Threats (Phishing, etc.)

**What it does:** Find dangerous emails before they cause damage

**Request:**
```bash
curl -X POST http://localhost:8000/orchestrate/threats/detect \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      {
        "id": "phishing_test",
        "subject": "Verify Your Account",
        "body": "Click here to verify: suspicious-link.com",
        "sender": "noreply@not-real-bank.com"
      }
    ]
  }'
```

**Python:**
```python
response = requests.post(
    "http://localhost:8000/orchestrate/threats/detect",
    json={
        "emails": [
            {
                "id": "email_id",
                "subject": "Verify Account",
                "body": "Click to verify...",
                "sender": "suspicious@domain.com"
            }
        ]
    }
)
threat_result = response.json()['result']
if threat_result['threats'][0]['is_phishing']:
    print("🚨 PHISHING DETECTED!")
```

**Returns:**
```
is_phishing: true
phishing_score: 0.92
threat_level: High
indicators: ["suspicious_domain", "phishing_keywords"]
```

---

## 5️⃣ Generate Answer (RAG)

**What it does:** Answer questions using email content as source

**Request:**
```bash
curl -X POST http://localhost:8000/orchestrate/generate-answer \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main action items?",
    "context": [
      "Meeting notes: Need to finish report by Friday",
      "Action item: Schedule follow-up call next week"
    ]
  }'
```

**Python:**
```python
response = requests.post(
    "http://localhost:8000/orchestrate/generate-answer",
    json={
        "query": "What needs to be done?",
        "context": [
            "Email 1: We need to complete the proposal",
            "Email 2: Call with client scheduled for Monday"
        ]
    }
)
answer = response.json()['result']
print(f"Answer: {answer['answer']}")
print(f"Confidence: {answer['confidence']}")
```

---

## 6️⃣ Store Data

**What it does:** Save execution records, analytics, threats, etc.

**Request:**
```bash
curl -X POST http://localhost:8000/orchestrate/persist \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "execution_record",
    "data": {
      "workflow_id": "wf_123",
      "status": "completed",
      "emails_processed": 42
    }
  }'
```

---

## 🔍 Check Status

**List all agents:**
```bash
curl http://localhost:8000/orchestrate/agents
```

**Check connection:**
```bash
curl http://localhost:8000/orchestrate/health
```

**Agent specific status:**
```bash
curl http://localhost:8000/orchestrate/agents/intent_detection_agent/status
```

---

## 📊 Interactive Testing

### Option 1: Browser
Open: http://localhost:8000/docs

Click on any endpoint and hit "Try it out"

### Option 2: Postman/Thunder Client
Import endpoints and test with GUI

### Option 3: Command Line
```bash
# Create a test file: test.sh
chmod +x test.sh
./test.sh
```

---

## 🐍 Python Client Usage

```python
# Direct client usage (bypasses FastAPI)
from app.watson_orchestrate import get_orchestrate_client

client = get_orchestrate_client()

# Intent
result = client.parse_intent("Find important emails")

# Search
result = client.semantic_search("budget topics")

# Classify
result = client.classify_emails([
    {"id": "1", "subject": "Meeting", "body": "...", "sender": "..."}
])

# Threats
result = client.detect_threats(emails_list)

# Answer
result = client.generate_answer("What happened?", ["context1", "context2"])

# Store
result = client.persist_data("event", {"action": "email_processed"})

# List agents
agents = client.list_agents()

# Check specific agent
status = client.get_agent_status("intent_detection_agent")
```

---

## 🎯 Common Use Cases

### Use Case 1: Process New Email
```python
# 1. Parse what user wants
intent = client.parse_intent(user_query)

# 2. Search for relevant emails
emails = client.semantic_search(user_query)

# 3. Classify them
classified = client.classify_emails(emails)

# 4. Check for threats
threats = client.detect_threats(emails)

# 5. Store results
client.persist_data("workflow", {"intent": intent, "results": classified})
```

### Use Case 2: Answer Questions
```python
# 1. Search for relevant emails
emails = client.semantic_search(user_question)

# 2. Extract context
context = [email['content'] for email in emails]

# 3. Generate answer
answer = client.generate_answer(user_question, context)

# 4. Store the Q&A
client.persist_data("qa_log", {"question": user_question, "answer": answer})
```

### Use Case 3: Security Screening
```python
# 1. Get all new emails
new_emails = fetch_new_emails()

# 2. Run threat detection
threats = client.detect_threats(new_emails)

# 3. Store threats
for threat in threats['result']['threats']:
    if threat['is_phishing']:
        client.persist_data("threat", threat)
        quarantine_email(threat['email_id'])
```

---

## 📈 Response Times

Typical response times (may vary):
- **Intent Detection:** 1-2 seconds
- **Semantic Search:** 2-3 seconds
- **Classification:** 2-3 seconds
- **Threat Detection:** 1-2 seconds
- **RAG Generation:** 3-5 seconds
- **Persistence:** 1 second

---

## ❌ Common Errors & Solutions

### "Failed to get IAM token"
✅ Solution: Check `WATSON_ORCHESTRATE_API_KEY` in `.env`

### "Agent not found"
✅ Solution: Check agent name is correct. Run: `curl http://localhost:8000/orchestrate/agents`

### "Service unavailable"
✅ Solution: Watson Orchestrate might be down. Wait a moment and retry.

### "Timeout"
✅ Solution: Request took too long. Retry or reduce input size.

---

## 🚀 Starting Backend

```bash
# Navigate to backend
cd backend

# Create/activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: **http://localhost:8000**

---

## 📚 API Documentation

Interactive docs at: **http://localhost:8000/docs**

Alternative docs at: **http://localhost:8000/redoc**

---

## 💡 Tips

1. **Start with `/orchestrate/health`** to verify connection
2. **Use `/orchestrate/agents`** to see all available agents
3. **Check logs** for debugging: Backend will print agent invocation details
4. **Test with small inputs first** before processing large emails
5. **Batch process** using `/orchestrate/batch/classify` for multiple emails

---

## ✅ You're Ready!

Your backend is now fully connected to Watson Orchestrate. Start using the endpoints above!

Questions? Check the full documentation: `WATSON_ORCHESTRATE_INTEGRATION.md`
