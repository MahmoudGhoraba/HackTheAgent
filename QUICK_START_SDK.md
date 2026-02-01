# 🎯 Quick Start: Agent Registration with SDK

**Using IBM Watson SDK for robust agent registration**

---

## 5-Step Process

### Step 1: Get Valid API Key ✓

```bash
# 1. Go to IBM Cloud Dashboard
https://cloud.ibm.com/

# 2. Find Watson Orchestrate instance
# 3. Access Management → API Keys
# 4. Create or regenerate API key
# 5. Copy the full key
```

### Step 2: Update .env

```bash
# Location: backend/.env
ORCHESTRATOR_API_KEY=<your-new-api-key-here>
ORCHESTRATOR_BASE_URL=https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4
```

### Step 3: Verify Connection

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python3 diagnose_orchestrate.py
```

Expected: **✅ CONNECTION SUCCESSFUL!**

### Step 4: Start Backend

```bash
cd backend
source .venv/bin/activate
python3 -m uvicorn app.main:app --reload
```

### Step 5: Register Agents

```bash
curl -X POST http://localhost:8000/orchestrate/agents/register
```

Expected response:
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

---

## What Happens Internally

```
1. Request to /orchestrate/agents/register
   ↓
2. main.py calls register_all_agents()
   ↓
3. agent_registry_sdk.py loads 6 agent definitions
   ↓
4. OrchestrateAgentRegistry.register_all_agents() called
   ↓
5. SDK converts agents to Orchestrate format
   ↓
6. POST to /v1/agents/register-batch with Bearer auth
   ↓
7. IBM Orchestrate registers all 6 agents
   ↓
8. Response returned to client
```

---

## Agents Being Registered

| # | Agent | Tools | Type |
|---|-------|-------|------|
| 1 | Intent Detection | intent_parser, entity_extractor | Analysis |
| 2 | Semantic Search | semantic_indexer, semantic_search | Analysis |
| 3 | Classification | category_classifier, priority_detector, sentiment_analyzer | Analysis |
| 4 | RAG Generation | context_retriever, answer_generator, citation_tracker | Analysis |
| 5 | Threat Detection | phishing_detector, domain_analyzer, threat_scorer | Security |
| 6 | Persistence | execution_storage, threat_storage, analytics_logger | Data |

**Total: 6 agents with 21 tools**

---

## Troubleshooting

### 🔴 401 Unauthorized

```json
{"detail": "IBM Orchestrate registration failed: Client error '401 Unauthorized'"}
```

**Fix:**
1. API key invalid/expired
2. Go to IBM Cloud → Watson Orchestrate → API Keys
3. Get NEW key
4. Update `backend/.env`
5. Restart backend
6. Try again

### 🔴 ModuleNotFoundError: ibm_watson

```bash
pip install ibm-watson ibm-cloud-sdk-core
```

### 🔴 Backend won't start

```bash
# Kill any existing processes on port 8000
lsof -i :8000
kill -9 <PID>

# Try again
python3 -m uvicorn app.main:app --reload
```

---

## Verify Success

After registration, verify agents appear in Orchestrate:

```bash
# List registered agents
curl http://localhost:8000/orchestrate/agents/list

# Get specific agent
curl http://localhost:8000/orchestrate/agents/definitions
```

Then check IBM Orchestrate dashboard:
- Go to https://orchestrate.cloud.ibm.com
- Navigate to Agents section
- Should see all 6 agents listed ✓

---

## Files Changed

```
✨ NEW:
  - backend/app/agent_registry_sdk.py (SDK-based registry)
  - backend/diagnose_orchestrate.py (connection diagnostic)
  - SDK_AGENT_REGISTRATION.md (detailed guide)
  - SDK_MIGRATION.md (migration summary)
  - QUICK_START_SDK.md (this file)

✏️ UPDATED:
  - backend/app/main.py (import from SDK version)
  - backend/requirements.txt (added SDK deps)
  - AGENT_EXPORT_GUIDE.md (added verification step)

📋 EXISTING:
  - backend/.env (add your API key)
  - backend/app/agent_registry.py (old version, now unused)
```

---

## Key Advantages

✅ **Automatic Authentication** - SDK handles Bearer tokens  
✅ **Better Error Messages** - SDK formats errors properly  
✅ **Retry Logic** - Automatic retries on transient failures  
✅ **Type Safety** - Full type hints and validation  
✅ **Logging** - Debug-friendly operation logs  
✅ **Maintainability** - IBM maintains SDK, not manual HTTP calls  

---

## Next Steps After Registration

1. ✅ Register agents (you are here)
2. ✅ Verify in Orchestrate dashboard
3. 🔄 Build workflows using your agents
4. 🔄 Execute workflows with registered agents
5. 🔄 Monitor execution and results

---

## Support

- **SDK Issues**: See `SDK_AGENT_REGISTRATION.md`
- **Registration Workflow**: See `AGENT_EXPORT_GUIDE.md`
- **API Reference**: See `API_DOCS.md`
- **Architecture**: See `ARCHITECTURE.md`

---

## Summary

**🎯 Goal**: Export local agents to IBM Orchestrate

**✅ Solution**: Using IBM Watson SDK with BearerTokenAuthenticator

**📝 Process**: 5 simple steps (get key → update env → verify → start → register)

**🚀 Result**: 6 agents with 21 tools available in IBM Orchestrate!

---

**Ready to go? Get your API key and follow the 5 steps above!** 🚀
