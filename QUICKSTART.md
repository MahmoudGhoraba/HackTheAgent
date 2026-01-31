# 🚀 Quick Start Guide - HackTheAgent Email Brain

Get up and running in **under 5 minutes**!

---

## Option 1: Local Python Setup (Recommended for Development)

### Step 1: Install Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Run the Server

```bash
# Quick start script (Unix/Mac)
./run.sh

# Or manually
uvicorn app.main:app --reload
```

### Step 3: Test the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Option 2: Docker (Recommended for Production)

### Step 1: Build and Run

```bash
docker-compose up --build
```

### Step 2: Test the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Testing the Workflow

### 1. Load Emails

```bash
curl http://localhost:8000/tool/emails/load
```

Expected: JSON with 25 emails

### 2. Normalize Emails

```bash
curl -X POST http://localhost:8000/tool/emails/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      {
        "id": "test_001",
        "from": "test@example.com",
        "to": "user@example.com",
        "subject": "Test Email",
        "date": "2026-01-31",
        "body": "This is a test email."
      }
    ]
  }'
```

### 3. Index Messages

First, get normalized messages from step 2, then:

```bash
curl -X POST http://localhost:8000/tool/semantic/index \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "id": "test_001",
        "text": "From: test@example.com\nTo: user@example.com\nSubject: Test Email\nDate: 2026-01-31\n\nThis is a test email.",
        "metadata": {
          "from": "test@example.com",
          "to": "user@example.com",
          "subject": "Test Email",
          "date": "2026-01-31"
        }
      }
    ]
  }'
```

Expected: `{"status": "indexed", "chunks_indexed": 1}`

### 4. Semantic Search

```bash
curl -X POST http://localhost:8000/tool/semantic/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "urgent deadlines",
    "top_k": 5
  }'
```

Expected: JSON with search results and similarity scores

### 5. RAG Answer

```bash
curl -X POST http://localhost:8000/tool/rag/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the IBM Dev Day hackathon about?",
    "top_k": 5
  }'
```

Expected: JSON with answer and citations

---

## Complete Workflow Test Script

Save this as `test_workflow.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🧪 Testing HackTheAgent Email Brain Workflow"
echo ""

# 1. Health Check
echo "1️⃣ Health Check..."
curl -s $BASE_URL/health | jq
echo ""

# 2. Load Emails
echo "2️⃣ Loading emails..."
EMAILS=$(curl -s $BASE_URL/tool/emails/load)
echo "Loaded $(echo $EMAILS | jq '.emails | length') emails"
echo ""

# 3. Normalize Emails
echo "3️⃣ Normalizing emails..."
NORMALIZED=$(curl -s -X POST $BASE_URL/tool/emails/normalize \
  -H "Content-Type: application/json" \
  -d "$EMAILS")
echo "Normalized $(echo $NORMALIZED | jq '.messages | length') messages"
echo ""

# 4. Index Messages
echo "4️⃣ Indexing messages..."
INDEX_RESULT=$(curl -s -X POST $BASE_URL/tool/semantic/index \
  -H "Content-Type: application/json" \
  -d "$NORMALIZED")
echo $INDEX_RESULT | jq
echo ""

# 5. Semantic Search
echo "5️⃣ Testing semantic search..."
curl -s -X POST $BASE_URL/tool/semantic/search \
  -H "Content-Type: application/json" \
  -d '{"query": "urgent deadlines", "top_k": 3}' | jq
echo ""

# 6. RAG Answer
echo "6️⃣ Testing RAG answer..."
curl -s -X POST $BASE_URL/tool/rag/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the IBM Dev Day hackathon about?", "top_k": 3}' | jq
echo ""

echo "✅ Workflow test complete!"
```

Run it:
```bash
chmod +x test_workflow.sh
./test_workflow.sh
```

---

## Using the Interactive API Docs

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response below

This is the easiest way to test the API!

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Dependencies Not Installing
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -v -r requirements.txt
```

### Vector Store Errors
```bash
# Clear vector store
rm -rf backend/app/vector_store/*

# Re-index
# Run the index endpoint again
```

### Import Errors
```bash
# Make sure you're in the backend directory
cd backend

# Make sure virtual environment is activated
source .venv/bin/activate

# Run from backend directory
uvicorn app.main:app --reload
```

---

## Next Steps

1. ✅ Server running? → Test with demo questions
2. ✅ API working? → Set up watsonx Orchestrate agents
3. ✅ Agents configured? → Run the full demo

See:
- **Demo Questions**: `orchestrate/demo_script.md`
- **Agent Setup**: `orchestrate/agent_configurations.md`
- **Full Documentation**: `README.md`

---

## Need Help?

- Check the logs in the terminal
- Visit http://localhost:8000/docs for API documentation
- Review the error messages - they're descriptive!
- Check `backend/app/config.py` for configuration options

---

**You're ready to go! 🎉**

The system works even without LLM credentials - semantic search will work perfectly, and RAG will return retrieved context as fallback.