# Terminal Commands to Register Agents Using SDK

**Complete step-by-step terminal workflow**

---

## ⚠️ IMPORTANT: Fix Your API Key First!

Your diagnostic shows **401 Unauthorized** - you need a VALID API key.

### Get New API Key from IBM Cloud

```bash
# 1. Go to IBM Cloud (in browser):
https://cloud.ibm.com/

# 2. Click on "Watson Orchestrate" instance
# 3. Click "Manage" tab
# 4. Click "Access (IAM)" 
# 5. Click "Users" → "API Keys"
# 6. Click "Create" (or "Regenerate" existing)
# 7. Copy the full API key
```

### Update Your .env File

```bash
# Open backend/.env and update:
cd /Users/ghorabas/Hackathon/HackTheAgent/backend

# Edit the file (use your favorite editor)
nano .env

# Update these lines with your NEW key:
ORCHESTRATOR_API_KEY=<paste-your-new-key-here>
ORCHESTRATOR_BASE_URL=https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4

# Save and exit (Ctrl+X in nano, then Y to confirm)
```

---

## 🚀 Terminal Commands to Register Agents

Once you have a valid API key, run these commands:

### Command 1: Verify Connection (Test New Credentials)

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python3 diagnose_orchestrate.py
```

**Expected output:**
```
✓ ORCHESTRATOR_API_KEY is set
✓ ORCHESTRATOR_BASE_URL is set
Status Code: 200
✅ CONNECTION SUCCESSFUL!
```

If you still see **401**, your key is still invalid. Get a new one.

### Command 2: Start the Backend Server

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python3 -m uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/Users/ghorabas/Hackathon/HackTheAgent/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [XXXXX]
```

⚠️ **Keep this terminal running!** Open a new terminal for the next commands.

### Command 3: Test Backend Health (In New Terminal)

```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status":"healthy","app":"HackTheAgent Email Brain","version":"1.0.0"}
```

### Command 4: Register All Agents

```bash
curl -X POST http://localhost:8000/orchestrate/agents/register -s | python3 -m json.tool
```

**Expected output on SUCCESS:**
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
  ],
  "details": {
    "agents_registered": 6,
    "message": "Successfully registered 6 agents"
  },
  "timestamp": "2026-02-01T..."
}
```

**Expected output on ERROR (401):**
```json
{
  "detail": "IBM Orchestrate registration failed: Client error '401 Unauthorized'"
}
```

If you see 401, your API key is still invalid. Get a new one from IBM Cloud.

### Command 5: Verify Agents Are Registered

```bash
curl http://localhost:8000/orchestrate/agents/list -s | python3 -m json.tool
```

**Expected output:**
```json
{
  "status": "success",
  "agents_count": 6,
  "agents": [
    {
      "agent_id": "intent_detection_agent",
      "agent_name": "Intent Detection Agent",
      "status": "ACTIVE"
    },
    {
      "agent_id": "semantic_search_agent",
      "agent_name": "Semantic Search Agent",
      "status": "ACTIVE"
    },
    ...
  ]
}
```

### Command 6: Get Agent Definitions (Export)

```bash
curl http://localhost:8000/orchestrate/agents/definitions -s | python3 -m json.tool
```

Shows all agent definitions with capabilities and tools.

---

## 📋 Complete Workflow (Copy-Paste Ready)

### Terminal 1: Start Backend

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python3 -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Register Agents

```bash
# First verify connection with new API key
cd /Users/ghorabas/Hackathon/HackTheAgent/backend
python3 diagnose_orchestrate.py

# If ✅ SUCCESS, register agents:
curl -X POST http://localhost:8000/orchestrate/agents/register -s | python3 -m json.tool

# Verify they were registered:
curl http://localhost:8000/orchestrate/agents/list -s | python3 -m json.tool
```

---

## 🔧 Troubleshooting

### Error: 401 Unauthorized

```
"detail": "IBM Orchestrate registration failed: Client error '401 Unauthorized'"
```

**Solution:**
1. Get NEW API key from IBM Cloud
2. Update `backend/.env`
3. Restart backend
4. Try again

### Error: Connection Refused

```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Solution:**
- Make sure backend is running in Terminal 1
- Check: `curl http://localhost:8000/health`

### Error: Module Not Found

```
ModuleNotFoundError: No module named 'ibm_watson'
```

**Solution:**
```bash
pip install ibm-watson ibm-cloud-sdk-core
```

### Port Already in Use

```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Try again
python3 -m uvicorn app.main:app --reload --port 8000
```

---

## 📊 What Each Command Does

| Command | Purpose |
|---------|---------|
| `diagnose_orchestrate.py` | Test connection with current credentials |
| `uvicorn app.main:app` | Start FastAPI backend server |
| `curl /health` | Check backend is running |
| `POST /orchestrate/agents/register` | Register all 6 agents with Orchestrate |
| `GET /orchestrate/agents/list` | List registered agents |
| `GET /orchestrate/agents/definitions` | Export all agent definitions |

---

## 🎯 Success Checklist

✅ Get valid API key from IBM Cloud  
✅ Update `backend/.env`  
✅ Run diagnostic: `python3 diagnose_orchestrate.py` → ✅ CONNECTION SUCCESSFUL  
✅ Start backend: `python3 -m uvicorn app.main:app --reload`  
✅ Register agents: `curl -X POST http://localhost:8000/orchestrate/agents/register`  
✅ Verify: `curl http://localhost:8000/orchestrate/agents/list`  
✅ Check IBM Orchestrate dashboard - see all 6 agents  

---

## 🚀 What Happens When You Register

1. **Your SDK sends**: POST request to local backend
2. **Backend processes**: Loads 6 agent definitions from Python code
3. **SDK formats**: Converts to Orchestrate API format with BearerTokenAuthenticator
4. **Sends to IBM**: POST to `/v1/agents/register-batch` with your Bearer token
5. **IBM registers**: All 6 agents with 21 tools
6. **You get back**: Success response with agent count
7. **Result**: Agents appear in IBM Orchestrate dashboard ✨

---

## 📱 Next Steps After Registration

1. Go to https://orchestrate.cloud.ibm.com
2. Log in with your IBM Cloud account
3. Look for Agents section
4. Should see all 6 HackTheAgent agents
5. Create workflows using these agents
6. Execute workflows from Orchestrate dashboard

---

## 💡 Pro Tips

- **Keep Terminal 1 running** - backend needs to stay online
- **Use new Terminal 2** - for curl commands while backend runs
- **Save commands** - save these curl commands to a file for reuse
- **Check logs** - Terminal 1 shows all backend activity
- **Pretty JSON** - pipe curl to `python3 -m json.tool` for readable output

---

**Ready? Get your API key and start registering!** 🎉
