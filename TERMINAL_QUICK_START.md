# 🎯 EXACT TERMINAL COMMANDS TO REGISTER AGENTS

Copy and paste these commands into your terminal!

---

## ⚠️ STEP 0: GET VALID API KEY (DO THIS FIRST!)

**Your current key is EXPIRED/INVALID (401 error)**

1. **Go to IBM Cloud in browser:**
   ```
   https://cloud.ibm.com/
   ```

2. **Find Watson Orchestrate:**
   - Click resource list
   - Find "Watson Orchestrate"
   - Click on it

3. **Get API Key:**
   - Click "Manage" tab
   - Click "Access (IAM)"
   - Click "Users"
   - Click "API Keys"
   - Click "Create new" (or "Regenerate")
   - **Copy the full key**

4. **Update .env:**
   ```bash
   nano backend/.env
   ```
   - Find: `ORCHESTRATOR_API_KEY=...`
   - Replace with your NEW key
   - Save: Ctrl+X, then Y, then Enter

---

## TERMINAL WORKFLOW

### TERMINAL 1: Start Backend (Keep Running)

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python3 -m uvicorn app.main:app --reload --port 8000
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this running! Don't close it.**

---

### TERMINAL 2: Register Agents (New Terminal)

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
```

#### Command 1: Verify Connection with New API Key

```bash
python3 diagnose_orchestrate.py
```

Look for: **✅ CONNECTION SUCCESSFUL!**

If you see **❌ AUTHENTICATION FAILED**, your API key is still invalid.

#### Command 2: Register All 6 Agents

```bash
curl -X POST http://localhost:8000/orchestrate/agents/register -s | python3 -m json.tool
```

**SUCCESS Response:**
```json
{
  "status": "success",
  "message": "All agents registered successfully",
  "agents_registered": 6,
  "agents": [
    "Intent Detection Agent",
    "Semantic Search Agent",
    "Classification Agent",
    "RAG Answer Generation Agent",
    "Threat Detection Agent",
    "Database Persistence Agent"
  ]
}
```

#### Command 3: Verify They Were Registered

```bash
curl http://localhost:8000/orchestrate/agents/list -s | python3 -m json.tool
```

Should show all 6 agents with status "ACTIVE"

#### Command 4: Export Agent Definitions

```bash
curl http://localhost:8000/orchestrate/agents/definitions -s | python3 -m json.tool
```

Shows complete definitions of all agents and their tools.

---

## ✅ Success = You See This

**Terminal 1 (Backend):**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Terminal 2 (After Command 2):**
```json
{
  "status": "success",
  "agents_registered": 6
}
```

**IBM Orchestrate Dashboard:**
- Go to https://orchestrate.cloud.ibm.com
- See all 6 agents in Agents section ✨

---

## 🔴 If You See 401 Error

```json
{
  "detail": "IBM Orchestrate registration failed: Client error '401 Unauthorized'"
}
```

**DO THIS:**
1. Get BRAND NEW API key (follow STEP 0 above)
2. Update `backend/.env` with new key
3. Kill Terminal 1: Ctrl+C
4. Restart Terminal 1: `python3 -m uvicorn app.main:app --reload --port 8000`
5. Try Command 2 again

---

## 🔴 If Backend Won't Start

**Error:** "Address already in use"

```bash
# Find what's using port 8000
lsof -i :8000

# Kill it (replace XXXXX with the PID number)
kill -9 XXXXX

# Try again
python3 -m uvicorn app.main:app --reload --port 8000
```

---

## QUICK COPY-PASTE SUMMARY

### Terminal 1 (Backend):
```
cd /Users/ghorabas/Hackathon/HackTheAgent/backend && python3 -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 (Register):
```
cd /Users/ghorabas/Hackathon/HackTheAgent/backend && python3 diagnose_orchestrate.py && sleep 2 && curl -X POST http://localhost:8000/orchestrate/agents/register -s | python3 -m json.tool
```

---

## WHAT HAPPENS INTERNALLY

```
You: curl -X POST /orchestrate/agents/register
  ↓
FastAPI: Receives request in main.py
  ↓
register_all_agents(): Gets 6 agent definitions
  ↓
OrchestrateAgentRegistry: Creates Bearer auth
  ↓
SDK: POST to IBM Orchestrate API
  ↓
IBM Orchestrate: Registers all 6 agents
  ↓
SDK: Returns success response
  ↓
You: See "status": "success"
  ↓
✨ Agents appear in Orchestrate dashboard!
```

---

## AGENTS BEING REGISTERED

1. **Intent Detection** - Understand what user wants
   - Tools: intent_parser, entity_extractor

2. **Semantic Search** - Find emails by meaning
   - Tools: semantic_indexer, semantic_search_tool

3. **Classification** - Categorize emails
   - Tools: category_classifier, priority_detector, sentiment_analyzer

4. **RAG Generation** - Answer questions with citations
   - Tools: context_retriever, answer_generator, citation_tracker

5. **Threat Detection** - Find phishing/threats
   - Tools: phishing_detector, domain_analyzer, threat_scorer

6. **Database Persistence** - Store results
   - Tools: execution_storage, threat_storage, analytics_logger

**Total: 6 agents + 21 tools**

---

## 🎉 AFTER REGISTRATION

1. ✅ Backend running
2. ✅ Agents registered
3. ✅ Check IBM Orchestrate dashboard
4. ✅ Build workflows with your agents
5. ✅ Execute from Orchestrate UI

---

**START WITH STEP 0 - GET NEW API KEY - THEN RUN TERMINAL COMMANDS ABOVE!**
