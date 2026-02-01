# 🎯 Manual Agent Import via IBM Orchestrate Web UI

**Status: Your 6 native agents are ready. Here's how to import them manually using the web interface.**

---

## ⚡ Quick Steps

### Step 1: Go to Orchestrate Dashboard
```
https://orchestrate.cloud.ibm.com/
```

### Step 2: Navigate to Manage Agents
```
Left Menu → Manage Agents (or look for "Agents" section)
```

### Step 3: For Each Agent File, Import Manually

Your agent files are ready in:
```
/Users/ghorabas/Hackathon/HackTheAgent/backend/agents/
```

Agent files to import (6 total):
1. `classification_agent.yaml`
2. `database_persistence_agent.yaml`
3. `intent_detection_agent.yaml`
4. `rag_generation_agent.yaml`
5. `semantic_search_agent.yaml`
6. `threat_detection_agent.yaml`

### Step 4: Import Each Agent

**In Orchestrate UI:**
1. Click "Import Agent" or "Create Agent"
2. Choose "Upload YAML" or "Native Agent"
3. Copy-paste the YAML content from each file
4. Click "Import" or "Create"
5. Repeat for all 6 agents

---

## 📋 Agent Details for Manual Import

### Agent 1: Intent Detection Agent
**File:** `classification_agent.yaml`
**Purpose:** Parse user intent from queries
**Tools:** intent_parser, entity_extractor

### Agent 2: Semantic Search Agent
**File:** `semantic_search_agent.yaml`
**Purpose:** Find emails by semantic meaning
**Tools:** semantic_indexer, semantic_search_tool

### Agent 3: Classification Agent
**File:** `classification_agent.yaml`
**Purpose:** Categorize emails by type, priority, sentiment
**Tools:** category_classifier, priority_detector, sentiment_analyzer

### Agent 4: RAG Generation Agent
**File:** `rag_generation_agent.yaml`
**Purpose:** Generate grounded answers with citations
**Tools:** context_retriever, answer_generator, citation_tracker

### Agent 5: Threat Detection Agent
**File:** `threat_detection_agent.yaml`
**Purpose:** Detect phishing and security threats
**Tools:** phishing_detector, domain_analyzer, threat_scorer

### Agent 6: Database Persistence Agent
**File:** `database_persistence_agent.yaml`
**Purpose:** Store workflow results and threats to database
**Tools:** execution_storage, threat_storage, analytics_logger

---

## 🔍 View Agent YAML Content

To see the content of each agent file, run:

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

# View each agent
cat intent_detection_agent.yaml
cat semantic_search_agent.yaml
cat classification_agent.yaml
cat rag_generation_agent.yaml
cat threat_detection_agent.yaml
cat database_persistence_agent.yaml
```

Or open them in VS Code:
```bash
code /Users/ghorabas/Hackathon/HackTheAgent/backend/agents/
```

---

## 📝 Manual Import Instructions (Detailed)

### Via Web UI (Easiest)

1. **Open Orchestrate:**
   - Go to: https://orchestrate.cloud.ibm.com/
   - Log in with your IBM account

2. **Navigate to Agents:**
   - Look for "Agents" in left menu
   - Click "Manage Agents" or similar

3. **Import Agent Option:**
   - Click "Import Agent", "Create Agent", or "+" button
   - Look for "Upload YAML", "Import from YAML", or "Paste YAML"

4. **For Each Agent:**
   - Open agent YAML file from `/Users/ghorabas/Hackathon/HackTheAgent/backend/agents/`
   - Copy all content (Ctrl+A, Ctrl+C in editor)
   - Paste into Orchestrate UI
   - Click "Import", "Create", or "Save"
   - Repeat for all 6 agents

5. **Verify:**
   - After import, agent should appear in "Agents" list
   - Status might be "Draft" initially
   - Can then Deploy to make "Live"

---

## 🚀 Alternative: Use ADK CLI (Command Line)

If you have npm installed and can use the ADK CLI:

```bash
# 1. Install ADK
npm install -g @ibm-generative-ai/watson-orchestrate-adk

# 2. Initialize (will prompt for login)
orchestrate init

# 3. Import all agents
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

for agent in *.yaml; do
  orchestrate agents import -f "$agent"
done

# 4. Verify
orchestrate agents list

# 5. Deploy (optional - makes them live)
orchestrate agents deploy --name intent_detection_agent
orchestrate agents deploy --name semantic_search_agent
orchestrate agents deploy --name classification_agent
orchestrate agents deploy --name rag_generation_agent
orchestrate agents deploy --name threat_detection_agent
orchestrate agents deploy --name database_persistence_agent
```

---

## 📂 File Locations

All agent YAML files are ready at:
```
/Users/ghorabas/Hackathon/HackTheAgent/backend/agents/
├── classification_agent.yaml
├── database_persistence_agent.yaml
├── intent_detection_agent.yaml
├── rag_generation_agent.yaml
├── semantic_search_agent.yaml
└── threat_detection_agent.yaml
```

---

## ✅ Success Criteria

**After Import:**
- ✅ All 6 agents visible in Orchestrate UI
- ✅ Status shows "Draft" or "Active"
- ✅ Each agent has correct name, description, tools
- ✅ Can create workflows using these agents
- ✅ Can deploy agents to make them "Live"

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't find import button | Look in left menu for "Agents" or "Manage Agents" |
| YAML format error | Copy entire YAML, check indentation (2 spaces) |
| Agent won't import | Try one agent first, check for spaces/tabs in YAML |
| Can't see agents after import | Refresh page, wait a moment, check "Draft" status |
| Need to edit after import | Agents should be editable in UI after creation |

---

## 📞 Next Steps

1. **Manual Import (Now):**
   - Open Orchestrate UI
   - Import each agent from YAML files
   - Verify they appear in agent list

2. **Deploy (Next):**
   - Click each agent
   - Click "Deploy" to make "Live"

3. **Create Workflows:**
   - Use agents in workflows
   - Build end-to-end automation

4. **Monitor:**
   - Run workflows
   - View execution logs
   - Monitor performance

---

## 📚 Resources

- **Orchestrate Dashboard:** https://orchestrate.cloud.ibm.com/
- **Agent Files:** `/Users/ghorabas/Hackathon/HackTheAgent/backend/agents/`
- **API Key:** Already configured in your environment
- **Documentation:** https://developer.watson-orchestrate.ibm.com/

---

## 💡 Why Manual Import?

**Note:** IBM Orchestrate's native agent creation API is not publicly exposed. The recommended way to import agents is through:
1. ✅ **Web UI (Manual)** - What we're doing now
2. ✅ **ADK CLI** - Command-line tool (requires npm)
3. ✅ **Watson Studio** - Visual editor

Since direct API import isn't available, manual import via the web UI is the most straightforward approach.

---

**Status: ✅ READY FOR MANUAL IMPORT**

All 6 native agents are prepared and ready. Open https://orchestrate.cloud.ibm.com/ and import them! 🚀

