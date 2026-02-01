# 🎯 Import Native Agents Using Watson Orchestrate ADK CLI

**Use the ADK CLI to import YAML-based native agents into IBM Orchestrate**

---

## What You're Doing

Converting your 6 local agents into **native Watson Orchestrate agents** using:
- ✅ Official YAML format (spec_version: v1)
- ✅ ADK CLI tool (`orchestrate agents import`)
- ✅ No API authentication issues
- ✅ Full native agent capabilities

---

## Setup Steps

### Step 1: Install Watson Orchestrate ADK

```bash
# Install the ADK CLI globally
npm install -g @ibm-generative-ai/watson-orchestrate-adk

# Verify installation
orchestrate --version
```

### Step 2: Authenticate with IBM Cloud

```bash
# Log in to IBM Cloud
ibmcloud login

# Set your Watson Orchestrate environment
ibmcloud watson-orchestrate environment set <instance-name>

# Or use interactive setup
orchestrate init
```

### Step 3: Verify Agent YAML Files Exist

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

# List all agent YAML files
ls -la *.yaml

# Should show:
# - intent_detection_agent.yaml
# - semantic_search_agent.yaml
# - classification_agent.yaml
# - rag_generation_agent.yaml
# - threat_detection_agent.yaml
# - database_persistence_agent.yaml
```

---

## Import Agents

### Option 1: Import One Agent at a Time

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

# Import Intent Detection Agent
orchestrate agents import -f intent_detection_agent.yaml

# Import Semantic Search Agent
orchestrate agents import -f semantic_search_agent.yaml

# Import Classification Agent
orchestrate agents import -f classification_agent.yaml

# Import RAG Generation Agent
orchestrate agents import -f rag_generation_agent.yaml

# Import Threat Detection Agent
orchestrate agents import -f threat_detection_agent.yaml

# Import Database Persistence Agent
orchestrate agents import -f database_persistence_agent.yaml
```

### Option 2: Import All Agents at Once (Batch)

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

# Import all YAML files in directory
for agent in *.yaml; do
  orchestrate agents import -f "$agent"
done
```

### Option 3: Import with Specific Output

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

# Import and save output
orchestrate agents import -f intent_detection_agent.yaml --output import_results.json
```

---

## Verify Agents Imported Successfully

### Check in CLI

```bash
# List all imported agents
orchestrate agents list

# Get specific agent details
orchestrate agents describe intent_detection_agent

# Get agent in YAML format
orchestrate agents describe intent_detection_agent --output yaml
```

### Check in Watson Orchestrate UI

```bash
# Go to Orchestrate Dashboard
https://orchestrate.cloud.ibm.com/

# Navigate to: Manage Agents
# Should see all 6 agents in "Draft" status
```

---

## Deploy Agents (Make Them Live)

Once imported (in draft state), deploy to make them available:

```bash
# Deploy Intent Detection Agent
orchestrate agents deploy --name intent_detection_agent

# Deploy all agents
orchestrate agents list | grep "Draft" | awk '{print $1}' | while read agent; do
  orchestrate agents deploy --name "$agent"
done
```

---

## Your 6 Native Agents

### 1. Intent Detection Agent
- **File**: `intent_detection_agent.yaml`
- **Name**: `intent_detection_agent`
- **Style**: default
- **LLM**: watsonx/ibm/granite-3-8b-instruct
- **Tools**: intent_parser, entity_extractor

### 2. Semantic Search Agent
- **File**: `semantic_search_agent.yaml`
- **Name**: `semantic_search_agent`
- **Style**: default
- **LLM**: watsonx/ibm/granite-3-8b-instruct
- **Tools**: semantic_indexer, semantic_search_tool

### 3. Classification Agent
- **File**: `classification_agent.yaml`
- **Name**: `classification_agent`
- **Style**: default
- **LLM**: watsonx/ibm/granite-3-8b-instruct
- **Tools**: category_classifier, priority_detector, sentiment_analyzer

### 4. RAG Generation Agent
- **File**: `rag_generation_agent.yaml`
- **Name**: `rag_generation_agent`
- **Style**: default
- **LLM**: watsonx/ibm/granite-3-8b-instruct
- **Tools**: context_retriever, answer_generator, citation_tracker

### 5. Threat Detection Agent
- **File**: `threat_detection_agent.yaml`
- **Name**: `threat_detection_agent`
- **Style**: default
- **LLM**: watsonx/ibm/granite-3-8b-instruct
- **Tools**: phishing_detector, domain_analyzer, threat_scorer

### 6. Database Persistence Agent
- **File**: `database_persistence_agent.yaml`
- **Name**: `database_persistence_agent`
- **Style**: default
- **LLM**: watsonx/ibm/granite-3-8b-instruct
- **Tools**: execution_storage, threat_storage, analytics_logger

---

## YAML Agent Format Explained

Each agent YAML file contains:

```yaml
spec_version: v1                    # Orchestrate version
kind: native                        # Native agent type
name: agent_id                      # Unique agent identifier
display_name: Agent Name            # Display name in UI
description: |                      # What agent does
  Multi-line description
instructions: |                     # Agent system prompt
  Detailed instructions for LLM
style: default                      # Agent reasoning style
llm: watsonx/ibm/granite-...       # LLM to use
tools:                             # Tools available
  - tool_1
  - tool_2
collaborators: []                  # Other agents this can call
hide_reasoning: false              # Show reasoning in UI
restrictions: editable             # Can be edited after import
icon: '<svg>...</svg>'             # SVG icon for UI
```

---

## Troubleshooting

### Error: Command Not Found

```
orchestrate: command not found
```

**Solution:**
```bash
npm install -g @ibm-generative-ai/watson-orchestrate-adk
orchestrate --version
```

### Error: Not Authenticated

```
Error: Not authenticated. Please run 'orchestrate init' first.
```

**Solution:**
```bash
orchestrate init
# Follow interactive prompts
```

### Error: Agent Already Exists

```
Error: Agent 'intent_detection_agent' already exists
```

**Solution:**
```bash
# Delete and reimport
orchestrate agents delete --name intent_detection_agent
orchestrate agents import -f intent_detection_agent.yaml
```

### Error: Invalid YAML Format

```
Error: Invalid YAML syntax in file
```

**Solution:**
- Check YAML indentation (must be 2 spaces)
- Validate with: `yamllint intent_detection_agent.yaml`
- Compare with provided YAML files

---

## Complete Terminal Workflow

```bash
# 1. Install ADK
npm install -g @ibm-generative-ai/watson-orchestrate-adk

# 2. Authenticate
orchestrate init

# 3. Go to agent directory
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

# 4. Import all agents
for agent in *.yaml; do
  echo "Importing $agent..."
  orchestrate agents import -f "$agent"
done

# 5. Verify imports
orchestrate agents list

# 6. Deploy agents (optional - makes them live)
orchestrate agents list | while read agent; do
  orchestrate agents deploy --name "$agent"
done

# 7. Check in UI
echo "Go to: https://orchestrate.cloud.ibm.com/Manage Agents"
```

---

## What Happens After Import

1. ✅ Agents imported into Watson Orchestrate
2. ✅ Agents appear in "Draft" status
3. ✅ Can edit agents in UI
4. ✅ Can add tools and collaborators
5. ✅ Deploy to make live
6. ✅ Use in workflows
7. ✅ Monitor execution

---

## Next Steps

1. **Import agents** using CLI commands above
2. **Verify in UI** - https://orchestrate.cloud.ibm.com
3. **Deploy agents** - make them live
4. **Create workflows** - use imported agents
5. **Execute workflows** - test end-to-end
6. **Monitor** - view execution logs

---

## ADK CLI Commands Reference

```bash
# Initialize/Authenticate
orchestrate init                    # Set up authentication
orchestrate auth login              # Log in to IBM Cloud

# Import/Export
orchestrate agents import -f file   # Import from YAML
orchestrate agents export           # Export agents to file

# Manage
orchestrate agents list             # List all agents
orchestrate agents describe <name>  # Get agent details
orchestrate agents delete <name>    # Delete agent

# Deploy
orchestrate agents deploy <name>    # Deploy agent (make live)
orchestrate agents undeploy <name>  # Undeploy agent

# Tools
orchestrate tools list              # List available tools
orchestrate tools describe <name>   # Get tool details

# Environment
orchestrate environment list        # List environments
orchestrate environment set <name>  # Set active environment
```

---

## File Locations

```
/Users/ghorabas/Hackathon/HackTheAgent/backend/agents/
├── intent_detection_agent.yaml
├── semantic_search_agent.yaml
├── classification_agent.yaml
├── rag_generation_agent.yaml
├── threat_detection_agent.yaml
└── database_persistence_agent.yaml
```

---

## Success Indicators

✅ All commands complete without errors  
✅ `orchestrate agents list` shows 6 agents  
✅ IBM Orchestrate UI shows agents in "Manage Agents"  
✅ Agents can be deployed successfully  
✅ Agents appear in workflow builder  

---

**Ready to import? Install ADK and follow the terminal workflow above!** 🚀
