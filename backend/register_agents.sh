#!/bin/bash

# ========================================
# HackTheAgent SDK Agent Registration
# Complete Terminal Workflow
# ========================================

echo "🚀 HackTheAgent Agent Registration Workflow"
echo "==========================================="
echo ""

# Step 1: Check configuration
echo "📋 Step 1: Checking configuration..."
echo ""

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create backend/.env with:"
    echo "  ORCHESTRATOR_API_KEY=<your-key>"
    echo "  ORCHESTRATOR_BASE_URL=https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/<instance-id>"
    exit 1
fi

echo "✓ .env file found"
echo ""

# Step 2: Verify credentials
echo "🔌 Step 2: Verifying credentials..."
python3 diagnose_orchestrate.py
echo ""

# Step 3: Ask if connection is successful
read -p "Is connection status ✅ SUCCESS? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Connection failed. Get new API key from IBM Cloud:"
    echo "   https://cloud.ibm.com/ → Watson Orchestrate → Access Management → API Keys"
    echo ""
    echo "Then update backend/.env with new key and try again."
    exit 1
fi

echo ""
echo "✅ Connection successful!"
echo ""

# Step 4: Start backend
echo "🔧 Step 3: Starting FastAPI backend..."
echo ""
echo "Starting on port 8000..."
echo "Press Ctrl+C to stop"
echo ""

cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python3 -m uvicorn app.main:app --reload --port 8000 &

BACKEND_PID=$!
sleep 3

# Check if backend started
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✓ Backend running on http://localhost:8000"
echo ""

# Step 5: Register agents
echo "📤 Step 4: Registering agents with IBM Orchestrate..."
echo ""
echo "Sending 6 agents:"
echo "  1. Intent Detection Agent"
echo "  2. Semantic Search Agent"
echo "  3. Classification Agent"
echo "  4. RAG Generation Agent"
echo "  5. Threat Detection Agent"
echo "  6. Database Persistence Agent"
echo ""

RESPONSE=$(curl -X POST http://localhost:8000/orchestrate/agents/register -s)

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool

echo ""

# Check if successful
if echo "$RESPONSE" | grep -q '"status":"success"'; then
    echo "✅ Agents registered successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Go to IBM Orchestrate dashboard: https://orchestrate.cloud.ibm.com"
    echo "2. Check Agents section for your 6 agents"
    echo "3. Build workflows using these agents"
else
    echo "⚠️  Check response above for errors"
fi

echo ""
echo "Backend still running (Ctrl+C to stop)..."

wait $BACKEND_PID
