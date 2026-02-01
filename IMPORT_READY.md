# 🚀 Native Agents Ready - Import Instructions

All 6 native agents are prepared and ready to import! Here's how to proceed:

## ✅ Verified Status

```
✅ classification_agent.yaml         - spec v1, kind native
✅ database_persistence_agent.yaml   - spec v1, kind native
✅ intent_detection_agent.yaml       - spec v1, kind native
✅ rag_generation_agent.yaml         - spec v1, kind native
✅ semantic_search_agent.yaml        - spec v1, kind native
✅ threat_detection_agent.yaml       - spec v1, kind native
```

All YAML files are syntactically valid and follow the official IBM Orchestrate native agent specification.

---

## 📌 Import Methods

### Method 1: Using Python Script (Recommended)

```bash
# Set your API key
export WATSON_ORCHESTRATE_API_KEY='your_ibm_orchestrate_api_key_here'

# Run the import script
python3 /Users/ghorabas/Hackathon/HackTheAgent/import_agents_via_api.py
```

**This script will:**
- ✅ Load all 6 YAML files
- ✅ Validate each agent
- ✅ Import via Watson Orchestrate API
- ✅ Verify imports succeeded
- ✅ Display summary

### Method 2: Manual API Import Using cURL

```bash
# Set your API key
API_KEY="your_ibm_orchestrate_api_key_here"
AGENT_DIR="/Users/ghorabas/Hackathon/HackTheAgent/backend/agents"

# Import each agent
for agent_file in "$AGENT_DIR"/*.yaml; do
  agent_json=$(python3 -c "import yaml, json; print(json.dumps(yaml.safe_load(open('$agent_file'))))")
  
  curl -X POST "https://api.watson-orchestrate.ibm.com/v1/agents" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$agent_json"
  
  echo "Imported: $agent_file"
done
```

### Method 3: Watson Orchestrate Web UI

1. Go to: **https://orchestrate.cloud.ibm.com/**
2. Navigate to: **Manage Agents**
3. Click: **Import Agent**
4. Upload each YAML file:
   - `intent_detection_agent.yaml`
   - `semantic_search_agent.yaml`
   - `classification_agent.yaml`
   - `rag_generation_agent.yaml`
   - `threat_detection_agent.yaml`
   - `database_persistence_agent.yaml`

---

## 🔑 Getting Your API Key

### Option A: From IBM Cloud Console

1. Go to: https://cloud.ibm.com/
2. Log in with your IBM account
3. Navigate to: **Manage** → **Access (IAM)**
4. Click: **Users**
5. Select your user
6. Go to: **API keys**
7. Click: **Create Classic infrastructure API key**
8. Copy the key and save it

### Option B: Using IBM Cloud CLI

```bash
# Install IBM Cloud CLI
# macOS: brew install --cask ibm-cloud-cli

# Log in
ibmcloud login

# Create API key
ibmcloud iam api-key-create my-orchestrate-key

# Copy the displayed API key
```

### Option C: From Watson Orchestrate UI

1. Go to: https://orchestrate.cloud.ibm.com/
2. Click your profile (top right)
3. Select: **API Keys**
4. Create new API key or copy existing

---

## 🎯 Step-by-Step Guide

### Step 1: Get Your API Key
```bash
# Set it in your environment
export WATSON_ORCHESTRATE_API_KEY='your_api_key_here'

# Verify it's set
echo $WATSON_ORCHESTRATE_API_KEY
```

### Step 2: Run the Import Script
```bash
cd /Users/ghorabas/Hackathon/HackTheAgent

python3 import_agents_via_api.py
```

### Step 3: Check the Orchestrate UI
```bash
# Go to: https://orchestrate.cloud.ibm.com/
# Navigate to: Manage Agents
# Should see all 6 agents with status "Draft"
```

### Step 4: Deploy Agents (Make Them Live)

**Via Orchestrate UI:**
1. Go to **Manage Agents**
2. For each agent, click **Deploy**
3. Confirm deployment

**Via API:**
```bash
API_KEY="your_api_key"

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
  
  echo "Deployed: $agent_name"
done
```

---

## ✨ Your 6 Agents

| Agent | Purpose | Tools |
|-------|---------|-------|
| **Intent Detection** | Parse user queries | intent_parser, entity_extractor |
| **Semantic Search** | Find emails by meaning | semantic_indexer, semantic_search_tool |
| **Classification** | Categorize emails | category_classifier, priority_detector, sentiment_analyzer |
| **RAG Generation** | Generate grounded answers | context_retriever, answer_generator, citation_tracker |
| **Threat Detection** | Detect phishing/threats | phishing_detector, domain_analyzer, threat_scorer |
| **Database Persistence** | Store results | execution_storage, threat_storage, analytics_logger |

---

## ✅ Verification Checklist

- [ ] API key obtained from IBM Cloud
- [ ] API key set in environment: `export WATSON_ORCHESTRATE_API_KEY='...'`
- [ ] Python script available: `/Users/ghorabas/Hackathon/HackTheAgent/import_agents_via_api.py`
- [ ] All YAML files in: `/Users/ghorabas/Hackathon/HackTheAgent/backend/agents/`
- [ ] YAML files validated (all 6 showing spec v1, kind native)
- [ ] Import script executed successfully
- [ ] All 6 agents appear in Orchestrate UI
- [ ] Agents deployed and status changed to "Live"
- [ ] Agents available for workflow creation

---

## 🆘 Troubleshooting

### Error: "No API Key Provided"
```bash
# Solution: Set the API key
export WATSON_ORCHESTRATE_API_KEY='your_api_key'

# Then run script
python3 import_agents_via_api.py
```

### Error: "Authentication failed (401)"
```
❌ API key is invalid or expired
Solution: 
  1. Get new API key from IBM Cloud
  2. Set in environment: export WATSON_ORCHESTRATE_API_KEY='new_key'
  3. Try import again
```

### Error: "Agent already exists"
```bash
# Solution: Delete the agent first
curl -X DELETE "https://api.watson-orchestrate.ibm.com/v1/agents/agent_name" \
  -H "Authorization: Bearer $WATSON_ORCHESTRATE_API_KEY"

# Then import again
python3 import_agents_via_api.py
```

### Error: "Connection error"
```
❌ Cannot connect to Orchestrate API
Solution:
  1. Check internet connection
  2. Verify API endpoint is correct
  3. Check firewall/proxy settings
```

---

## 📞 Support Resources

- **Orchestrate Dashboard**: https://orchestrate.cloud.ibm.com/
- **IBM Cloud Console**: https://cloud.ibm.com/
- **API Documentation**: https://developer.watson-orchestrate.ibm.com/
- **Python Script**: `/Users/ghorabas/Hackathon/HackTheAgent/import_agents_via_api.py`
- **Agent Files**: `/Users/ghorabas/Hackathon/HackTheAgent/backend/agents/`

---

## 📋 Next Steps After Import

1. ✅ Import agents via script
2. ✅ Verify in Orchestrate UI
3. ✅ Deploy agents
4. ✅ Create workflows using agents
5. ✅ Execute workflows
6. ✅ Monitor performance

---

**🎉 Ready to import? Get your API key and run:**
```bash
export WATSON_ORCHESTRATE_API_KEY='your_key'
python3 /Users/ghorabas/Hackathon/HackTheAgent/import_agents_via_api.py
```

