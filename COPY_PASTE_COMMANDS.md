# 📝 Exact Commands to Run - Copy & Paste Ready

Follow these steps in order. Copy and paste each command exactly.

---

## Step 1: Get Your API Key

### Option A: Using IBM Cloud Web Console
1. Go to: https://cloud.ibm.com/
2. Log in with your IBM account
3. Click your profile (top right) → **Manage user**
4. Go to: **Access (IAM)** → **Users** → Select yourself
5. In **API keys** section, click **Create Classic infrastructure API key**
6. Copy the API key and save it somewhere safe
7. Come back to terminal with your API key

### Option B: Using IBM Cloud CLI
```bash
# Install IBM Cloud CLI (if not already installed)
# macOS:
brew install --cask ibm-cloud-cli

# Log in
ibmcloud login

# Create API key
ibmcloud iam api-key-create orchestrate-key --description "Watson Orchestrate Import"

# Copy the displayed API key
```

---

## Step 2: Set Your API Key

```bash
# Replace YOUR_API_KEY_HERE with your actual API key
export WATSON_ORCHESTRATE_API_KEY='L2Rd6XjJsMnP_fBPKkkcH3a0Nxpq0s-JjF6hzNUP1y_z'

# Verify it's set
echo $WATSON_ORCHESTRATE_API_KEY
```

**Example:**
```bash
export WATSON_ORCHESTRATE_API_KEY='Eby8vdMB24fVQH0sNY4u97sXM23O17ehsulw5aGoFn7'
```

---

## Step 3: Validate Your API Key

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent

python3 check_api_key.py
```

**Expected Output:**
```
✅ API Key is VALID!

You can now import agents:
  python3 import_agents_via_api.py
```

**If you see ❌ Unauthorized (401):**
- Your API key is invalid or expired
- Get a new one and try again with Step 2

---

## Step 4: Import All 6 Agents

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent

python3 import_agents_via_api.py
```

**Expected Output:**
```
============================================================
🚀 Watson Orchestrate Native Agent Importer
============================================================

📁 Found 6 agent files:

   • classification_agent.yaml
   • database_persistence_agent.yaml
   • intent_detection_agent.yaml
   • rag_generation_agent.yaml
   • semantic_search_agent.yaml
   • threat_detection_agent.yaml

✅ Validated 6 agents

📤 Importing agents...

  ✅ Imported: classification_agent
  ✅ Imported: database_persistence_agent
  ✅ Imported: intent_detection_agent
  ✅ Imported: rag_generation_agent
  ✅ Imported: semantic_search_agent
  ✅ Imported: threat_detection_agent

🔍 Verifying imports...

✅ Verified: Classification Agent
   Status: draft
✅ Verified: Database Persistence Agent
   Status: draft
✅ Verified: Intent Detection Agent
   Status: draft
✅ Verified: RAG Generation Agent
   Status: draft
✅ Verified: Semantic Search Agent
   Status: draft
✅ Verified: Threat Detection Agent
   Status: draft

📋 Next Steps:
  1. Go to: https://orchestrate.cloud.ibm.com/
  2. Navigate to: Manage Agents
  3. Verify all agents are listed
  4. Deploy agents to make them live
```

---

## Step 5: Verify Agents in Orchestrate UI

```
1. Go to: https://orchestrate.cloud.ibm.com/
2. Click: Manage Agents
3. You should see all 6 agents in "Draft" status:
   ✅ Classification Agent
   ✅ Database Persistence Agent
   ✅ Intent Detection Agent
   ✅ RAG Generation Agent
   ✅ Semantic Search Agent
   ✅ Threat Detection Agent
```

---

## Step 6: Deploy Agents (Make Them Live)

### Option A: Using UI (Easiest)
```
1. Go to: https://orchestrate.cloud.ibm.com/Manage Agents
2. For each agent, click the "..." menu → Deploy
3. Confirm deployment
4. Wait for status to change from "Draft" to "Live"
```

### Option B: Using API
```bash
# Make sure API key is still set
API_KEY=$WATSON_ORCHESTRATE_API_KEY

# Deploy each agent
for agent_name in \
  "intent_detection_agent" \
  "semantic_search_agent" \
  "classification_agent" \
  "rag_generation_agent" \
  "threat_detection_agent" \
  "database_persistence_agent"
do
  curl -X POST "https://api.watson-orchestrate.ibm.com/v1/agents/$agent_name/deploy" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json"
  
  echo "✅ Deployed: $agent_name"
done
```

---

## Step 7: Start Using Your Agents!

### Create a Workflow
```
1. In Orchestrate UI: Click "Create Workflow"
2. Drag your agents into the workflow
3. Connect them together
4. Test the workflow
5. Deploy and monitor
```

### Example Workflow
```
[User Query]
    ↓
[Intent Detection Agent]
    ↓
[Classification Agent]
    ↓
[Semantic Search Agent]
    ↓
[RAG Generation Agent]
    ↓
[Threat Detection Agent]
    ↓
[Database Persistence Agent]
    ↓
[Response to User]
```

---

## 🎯 All Commands in One Place

```bash
# 1. Set API key
export WATSON_ORCHESTRATE_API_KEY='YOUR_API_KEY_HERE'

# 2. Navigate to project
cd /Users/ghorabas/Hackathon/HackTheAgent

# 3. Check API key validity
python3 check_api_key.py

# 4. Import agents
python3 import_agents_via_api.py

# 5. Open in browser
open https://orchestrate.cloud.ibm.com/

# 6. Verify agents and deploy via UI
```

---

## ⏱️ Expected Time

- Get API key: 2-5 minutes
- Check validity: 10 seconds
- Import agents: 30 seconds
- Verify in UI: 1 minute
- Deploy agents: 2-5 minutes

**Total: ~10 minutes** ✨

---

## ❌ Error Codes & Solutions

| Error | Meaning | Solution |
|-------|---------|----------|
| `No API Key Provided` | API key not set | `export WATSON_ORCHESTRATE_API_KEY='...'` |
| `401 Unauthorized` | Invalid API key | Get new key from IBM Cloud |
| `Connection error` | Cannot reach API | Check internet connection |
| `Agent already exists` | Duplicate agent | Delete old version first |
| `YAML parse error` | Invalid YAML format | Contact support |

---

## 📱 Quick Reference Card

**File locations:**
```
Agents: /Users/ghorabas/Hackathon/HackTheAgent/backend/agents/
Check key: /Users/ghorabas/Hackathon/HackTheAgent/check_api_key.py
Import: /Users/ghorabas/Hackathon/HackTheAgent/import_agents_via_api.py
```

**Important URLs:**
```
Dashboard: https://orchestrate.cloud.ibm.com/
IBM Cloud: https://cloud.ibm.com/
API Docs: https://developer.watson-orchestrate.ibm.com/
```

**Important Commands:**
```
Set key: export WATSON_ORCHESTRATE_API_KEY='...'
Check: python3 check_api_key.py
Import: python3 import_agents_via_api.py
```

---

## 🚀 You're Ready!

Everything is prepared. Just follow the 7 steps above and your agents will be live in Watson Orchestrate!

**Start with Step 1: Get your API key** 🔑

