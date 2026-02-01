# ⚡ ADK CLI Quick Reference

**One-page guide to import your native agents**

---

## 🚀 Quick Start (Copy-Paste)

### 1. Install ADK

```bash
npm install -g @ibm-generative-ai/watson-orchestrate-adk
orchestrate --version
```

### 2. Authenticate

```bash
orchestrate init
# Follow prompts to authenticate with IBM Cloud
```

### 3. Import All Agents (Automatic)

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent
bash import_native_agents.sh
```

### 4. Verify

```bash
orchestrate agents list
```

### 5. View in UI

```
https://orchestrate.cloud.ibm.com/ → Manage Agents
```

---

## 📋 Manual Commands

### Import One Agent

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

orchestrate agents import -f intent_detection_agent.yaml
orchestrate agents import -f semantic_search_agent.yaml
orchestrate agents import -f classification_agent.yaml
orchestrate agents import -f rag_generation_agent.yaml
orchestrate agents import -f threat_detection_agent.yaml
orchestrate agents import -f database_persistence_agent.yaml
```

### Import All (Loop)

```bash
cd /Users/ghorabas/Hackathon/HackTheAgent/backend/agents

for agent in *.yaml; do
  orchestrate agents import -f "$agent"
done
```

### List Agents

```bash
orchestrate agents list
```

### Get Agent Details

```bash
orchestrate agents describe intent_detection_agent
```

### Deploy Agent (Make Live)

```bash
orchestrate agents deploy --name intent_detection_agent
```

### Delete Agent

```bash
orchestrate agents delete --name intent_detection_agent
```

---

## 📂 Agent Files Location

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

## ✅ Success Checklist

- [ ] ADK installed: `orchestrate --version` works
- [ ] Authenticated: `orchestrate init` successful
- [ ] Agents imported: `orchestrate agents list` shows 6
- [ ] Verify in UI: https://orchestrate.cloud.ibm.com
- [ ] All agents show "Draft" status
- [ ] Deploy agents (optional): `orchestrate agents deploy`

---

## 🔧 Troubleshooting

**Command not found: orchestrate**
```bash
npm install -g @ibm-generative-ai/watson-orchestrate-adk
```

**Not authenticated**
```bash
orchestrate init
```

**Agent already exists**
```bash
orchestrate agents delete --name <agent-name>
orchestrate agents import -f <agent-name>.yaml
```

**Invalid YAML**
```bash
# Check file exists and is valid
cat backend/agents/<agent-name>.yaml
```

---

## 🎯 Your 6 Agents

1. **intent_detection_agent** - Parse user intent
2. **semantic_search_agent** - Find emails by meaning
3. **classification_agent** - Categorize emails
4. **rag_generation_agent** - Answer questions
5. **threat_detection_agent** - Find threats
6. **database_persistence_agent** - Store results

---

## 📚 Full Documentation

See: `ADK_NATIVE_AGENTS_GUIDE.md`

---

**That's it! 🎉 Import agents and start building workflows!**
