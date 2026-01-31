#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🧪 Testing HackTheAgent Email Brain Workflow"
echo "=============================================="
echo ""

# 1. Health Check
echo "1️⃣  Health Check..."
HEALTH=$(curl -s $BASE_URL/health)
if [ $? -eq 0 ]; then
    echo "✅ Server is healthy"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo "❌ Server is not responding. Make sure it's running on port 8000"
    exit 1
fi
echo ""

# 2. Load Emails
echo "2️⃣  Loading emails..."
EMAILS=$(curl -s $BASE_URL/tool/emails/load)
EMAIL_COUNT=$(echo "$EMAILS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['emails']))" 2>/dev/null)
if [ ! -z "$EMAIL_COUNT" ]; then
    echo "✅ Loaded $EMAIL_COUNT emails"
else
    echo "❌ Failed to load emails"
    exit 1
fi
echo ""

# 3. Normalize Emails
echo "3️⃣  Normalizing emails..."
NORMALIZED=$(curl -s -X POST $BASE_URL/tool/emails/normalize \
  -H "Content-Type: application/json" \
  -d "$EMAILS")
MSG_COUNT=$(echo "$NORMALIZED" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['messages']))" 2>/dev/null)
if [ ! -z "$MSG_COUNT" ]; then
    echo "✅ Normalized $MSG_COUNT messages"
else
    echo "❌ Failed to normalize emails"
    exit 1
fi
echo ""

# 4. Index Messages
echo "4️⃣  Indexing messages (this may take a minute)..."
INDEX_RESULT=$(curl -s -X POST $BASE_URL/tool/semantic/index \
  -H "Content-Type: application/json" \
  -d "$NORMALIZED")
CHUNKS=$(echo "$INDEX_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['chunks_indexed'])" 2>/dev/null)
if [ ! -z "$CHUNKS" ]; then
    echo "✅ Indexed $CHUNKS chunks"
else
    echo "❌ Failed to index messages"
    echo "$INDEX_RESULT"
    exit 1
fi
echo ""

# 5. Semantic Search
echo "5️⃣  Testing semantic search: 'urgent deadlines'..."
SEARCH_RESULT=$(curl -s -X POST $BASE_URL/tool/semantic/search \
  -H "Content-Type: application/json" \
  -d '{"query": "urgent deadlines", "top_k": 3}')
RESULT_COUNT=$(echo "$SEARCH_RESULT" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['results']))" 2>/dev/null)
if [ ! -z "$RESULT_COUNT" ]; then
    echo "✅ Found $RESULT_COUNT relevant emails"
    echo ""
    echo "Top result:"
    echo "$SEARCH_RESULT" | python3 -c "import sys, json; r=json.load(sys.stdin)['results'][0]; print(f\"  Subject: {r['subject']}\n  Score: {r['score']}\n  Date: {r['date']}\n  Snippet: {r['snippet'][:100]}...\")" 2>/dev/null
else
    echo "❌ Search failed"
    exit 1
fi
echo ""

# 6. RAG Answer
echo "6️⃣  Testing RAG answer: 'What is the IBM Dev Day hackathon about?'..."
RAG_RESULT=$(curl -s -X POST $BASE_URL/tool/rag/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the IBM Dev Day hackathon about?", "top_k": 3}')
ANSWER=$(echo "$RAG_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['answer'][:200])" 2>/dev/null)
if [ ! -z "$ANSWER" ]; then
    echo "✅ Generated answer with citations"
    echo ""
    echo "Answer preview:"
    echo "  $ANSWER..."
else
    echo "❌ RAG answer failed"
    exit 1
fi
echo ""

# 7. Stats
echo "7️⃣  System statistics..."
STATS=$(curl -s $BASE_URL/stats)
echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"
echo ""

echo "=============================================="
echo "✅ All tests passed! System is working correctly."
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:8000/docs for interactive API"
echo "  2. Configure watsonx Orchestrate agents (see orchestrate/agent_configurations.md)"
echo "  3. Run demo questions (see orchestrate/demo_script.md)"
echo ""