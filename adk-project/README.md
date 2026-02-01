# Watson Orchestrate ADK Project

**Watson Orchestrate Agent Development Kit (ADK) Project with 6 Email Analysis Agents**

---

## 📁 Project Structure

```
adk-project/
├── agents/                           # Native agent YAML files
│   ├── intent_detection_agent.yaml
│   ├── semantic_search_agent.yaml
│   ├── classification_agent.yaml
│   ├── rag_generation_agent.yaml
│   ├── threat_detection_agent.yaml
│   └── database_persistence_agent.yaml
│
├── tools/                            # Custom tools (for future expansion)
│   └── (Your custom tools here)
│
├── knowledge/                        # Knowledge bases (for future expansion)
│   └── (Your knowledge files here)
│
├── flows/                            # Workflow definitions (for future expansion)
│   └── (Your workflow files here)
│
└── README.md                         # This file
```

---

## 🚀 Your 6 Ready-to-Import Agents

### 1. **Intent Detection Agent** 🎯
- **File:** `agents/intent_detection_agent.yaml`
- **Purpose:** Analyzes user queries to determine intent and extract entities
- **Tools:** intent_parser, entity_extractor
- **LLM:** watsonx/ibm/granite-3-8b-instruct

### 2. **Semantic Search Agent** 🔍
- **File:** `agents/semantic_search_agent.yaml`
- **Purpose:** Performs semantic search over emails by meaning
- **Tools:** semantic_indexer, semantic_search_tool
- **LLM:** watsonx/ibm/granite-3-8b-instruct

### 3. **Classification Agent** 📧
- **File:** `agents/classification_agent.yaml`
- **Purpose:** Classifies emails by category, priority, and sentiment
- **Tools:** category_classifier, priority_detector, sentiment_analyzer
- **LLM:** watsonx/ibm/granite-3-8b-instruct

### 4. **RAG Generation Agent** 📝
- **File:** `agents/rag_generation_agent.yaml`
- **Purpose:** Generates grounded answers with citations from email content
- **Tools:** context_retriever, answer_generator, citation_tracker
- **LLM:** watsonx/ibm/granite-3-8b-instruct

### 5. **Threat Detection Agent** 🛡️
- **File:** `agents/threat_detection_agent.yaml`
- **Purpose:** Detects phishing and security threats in emails
- **Tools:** phishing_detector, domain_analyzer, threat_scorer
- **LLM:** watsonx/ibm/granite-3-8b-instruct

### 6. **Database Persistence Agent** 💾
- **File:** `agents/database_persistence_agent.yaml`
- **Purpose:** Stores workflow results and threat analysis to database
- **Tools:** execution_storage, threat_storage, analytics_logger
- **LLM:** watsonx/ibm/granite-3-8b-instruct

---

## 📋 How to Import These Agents

### Option 1: Using Watson Orchestrate Web UI (Easiest)

1. **Go to IBM Orchestrate Dashboard:**
   ```bash
   open https://orchestrate.cloud.ibm.com/
   ```

2. **Log in** with your IBM Cloud credentials

3. **Import each agent:**
   - Navigate to: **Agents** → **Import Agent**
   - Open the YAML file from `agents/` folder
   - Click **Import**
   - Repeat for all 6 agents

### Option 2: Using ADK CLI (If installed)

```bash
# Set your API key
export ORCHESTRATE_API_KEY='your_api_key_here'

# Navigate to project
cd /Users/ghorabas/Hackathon/HackTheAgent/adk-project

# Import all agents
for agent in agents/*.yaml; do
  orchestrate agents import -f "$agent"
done

# Verify imports
orchestrate agents list

# Describe specific agent
orchestrate agents describe intent_detection_agent
```

### Option 3: Using REST API

```bash
# Get IAM token
TOKEN=$(curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY" \
  | jq -r '.access_token')

# Import agent
curl -X POST "https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/YOUR_INSTANCE_ID/v1/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @agents/intent_detection_agent.yaml
```

---

## ✅ Verification

After importing, verify your agents:

```bash
# In Watson Orchestrate UI
1. Go to: https://orchestrate.cloud.ibm.com/
2. Navigate to: Manage Agents
3. You should see all 6 agents in "Draft" status

# Or via CLI
orchestrate agents list
```

---

## 🔧 Next Steps

1. ✅ **Import agents** using one of the methods above
2. ✅ **Deploy agents** to make them live
3. ✅ **Create workflows** using your agents
4. ✅ **Test workflows** end-to-end
5. ✅ **Monitor performance** and iterate

---

## 📄 Agent Specifications

All agents follow the **Watson Orchestrate native agent specification (v1)**:

```yaml
spec_version: v1              # Orchestrate API version
kind: native                  # Native agent type
name: agent_id               # Unique identifier
display_name: Display Name   # UI display name
description: ...             # What agent does
instructions: ...            # System prompt for LLM
style: default              # Reasoning style
llm: watsonx/ibm/granite... # LLM model to use
tools: [...]                # Available tools
collaborators: []           # Other agents it can call
hide_reasoning: false       # Show reasoning in UI
restrictions: editable      # Can be edited after import
icon: '<svg>...</svg>'      # SVG icon for UI
```

---

## 🔑 Your Orchestrate Credentials

```
Instance URL: https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4
Region: jp-tok (Tokyo)
Instance ID: 0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4
API Key: (stored in .env file)
```

---

## 📚 Resources

- **Orchestrate Dashboard:** https://orchestrate.cloud.ibm.com/
- **IBM Cloud Console:** https://cloud.ibm.com/
- **Watson Documentation:** https://cloud.ibm.com/docs/watson-orchestrate
- **ADK Documentation:** https://developer.watson-orchestrate.ibm.com/

---

## 📞 Troubleshooting

### Agents not importing?
1. Check your API key is valid
2. Verify instance URL and ID
3. Ensure YAML files are valid
4. Check file permissions

### CLI not working?
1. Install ADK: `npm install -g @ibm-generative-ai/watson-orchestrate-adk`
2. Set API key: `export ORCHESTRATE_API_KEY='your_key'`
3. Run: `orchestrate agents list`

### Agents not appearing in UI?
1. Refresh page in browser
2. Check if they're in "Draft" status
3. Try deploying an agent first
4. Clear browser cache

---

## 🎯 Success Checklist

- [ ] All 6 YAML files are in `agents/` folder
- [ ] YAML files are valid (no syntax errors)
- [ ] You have valid Orchestrate API credentials
- [ ] Agents imported successfully
- [ ] All 6 agents appear in Orchestrate UI
- [ ] Agents deployed and status is "Live"
- [ ] Agents available for workflow creation

---

## ✨ Summary

You now have a complete ADK project with 6 production-ready email analysis agents! 

**Import them using your preferred method and start building powerful email automation workflows!** 🚀

---

**Last Updated:** February 1, 2026  
**Status:** ✅ Ready for Import  
**All 6 Agents:** ✅ Prepared and Validated
