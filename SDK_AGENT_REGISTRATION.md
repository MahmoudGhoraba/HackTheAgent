# Agent Registration with IBM Watson SDK

**Using IBM Watson SDK for robust agent registration with IBM Orchestrate**

---

## Why Use the SDK?

Instead of making raw HTTP calls, the IBM Watson SDK provides:

✅ **Better Error Handling** - Proper authentication and error recovery  
✅ **Built-in Retry Logic** - Automatic retries for transient failures  
✅ **Type Safety** - Proper type checking and validation  
✅ **Maintainability** - Follows IBM best practices  
✅ **Future Compatibility** - Updates handled by SDK maintainers  

---

## Architecture

```
┌─────────────────────────────────────┐
│  HackTheAgent Local Agents          │
│  (6 agents defined in code)         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Agent Registry SDK Module          │
│  (agent_registry_sdk.py)            │
│                                     │
│  • BearerTokenAuthenticator         │
│  • Batch Registration               │
│  • Error Handling                   │
│  • Agent Management                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  IBM Watson SDK Layer               │
│  • ibm-watson                       │
│  • ibm-cloud-sdk-core               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  IBM Orchestrate API                │
│  /v1/agents/register-batch          │
│  /v1/agents/list                    │
│  /v1/agents/{id}                    │
└─────────────────────────────────────┘
```

---

## Setup

### 1. Install SDK

The required packages are already in `requirements.txt`:

```bash
pip install ibm-watson ibm-cloud-sdk-core
```

Both packages are already installed in your environment.

### 2. Configure Credentials

Update `backend/.env`:

```bash
# IBM Orchestrate credentials
ORCHESTRATOR_API_KEY=<your-valid-api-key>
ORCHESTRATOR_BASE_URL=https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/<instance-id>
```

---

## Usage

### Quick Start

```python
from app.agent_registry_sdk import register_all_agents, get_agent_registry

# Register all agents with Orchestrate
result = await register_all_agents()

# Check result
if result.get("status") == "success":
    print(f"✓ Registered {result['agents_registered']} agents")
else:
    print(f"✗ Error: {result.get('error')}")
```

### Via API Endpoint

```bash
# Start backend
cd backend
python3 -m uvicorn app.main:app --reload

# Register agents
curl -X POST http://localhost:8000/orchestrate/agents/register

# Response on success:
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

# Response on error (e.g., invalid credentials):
{
  "detail": "IBM Orchestrate registration failed: ..."
}
```

---

## How It Works

### 1. Registry Initialization

```python
from app.agent_registry_sdk import OrchestrateAgentRegistry

registry = OrchestrateAgentRegistry(
    api_key="your-api-key",
    base_url="https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/..."
)
```

**What happens:**
- ✓ Creates BearerTokenAuthenticator with your API key
- ✓ Validates base URL format
- ✓ Extracts instance ID from URL
- ✓ Logs initialization details

### 2. Agent Definition

```python
from app.agent_registry_sdk import get_hacktheagent_agents

agents = get_hacktheagent_agents()  # Returns 6 agents

# Each agent has:
# - agent_id: Unique identifier
# - agent_name: Display name
# - agent_type: Category (email_analysis, security, data_management)
# - description: What it does
# - version: Agent version
# - status: ACTIVE, DISABLED, or DEPRECATED
# - input_schema: JSON schema for inputs
# - output_schema: JSON schema for outputs
# - capabilities: List of tools/functions
```

### 3. Batch Registration

```python
result = await registry.register_all_agents(agents)

# SDK automatically:
# - Converts agent definitions to Orchestrate format
# - Includes all capabilities/tools
# - Sends batch request to /v1/agents/register-batch
# - Handles errors and retries
# - Logs results
```

---

## SDK Methods

### Registry Methods

#### `register_agent(agent_def)`
Register a single agent

```python
from app.agent_registry_sdk import AgentDefinition

agent = AgentDefinition(...)
result = await registry.register_agent(agent)
```

#### `register_all_agents(agents)`
Register multiple agents in batch

```python
agents = get_hacktheagent_agents()
result = await registry.register_all_agents(agents)
```

#### `list_agents()`
List all registered agents

```python
result = await registry.list_agents()
# Returns: {"agents": [...], "count": 6}
```

#### `get_agent(agent_id)`
Get specific agent details

```python
result = await registry.get_agent("intent_detection_agent")
# Returns: full agent definition from Orchestrate
```

#### `update_agent(agent_def)`
Update existing agent

```python
agent.version = "1.0.1"
result = await registry.update_agent(agent)
```

#### `delete_agent(agent_id)`
Remove agent from Orchestrate

```python
result = await registry.delete_agent("intent_detection_agent")
```

---

## Agent Definitions

### 6 Defined Agents

#### 1. Intent Detection Agent
- **ID**: `intent_detection_agent`
- **Type**: `email_analysis`
- **Tools**: Intent Parser, Entity Extractor
- **Use**: Understand what user wants to do

#### 2. Semantic Search Agent
- **ID**: `semantic_search_agent`
- **Type**: `email_analysis`
- **Tools**: Semantic Indexer, Semantic Search
- **Use**: Find emails by meaning, not keywords

#### 3. Classification Agent
- **ID**: `classification_agent`
- **Type**: `email_analysis`
- **Tools**: Category Classifier, Priority Detector, Sentiment Analyzer
- **Use**: Organize and categorize emails

#### 4. RAG Generation Agent
- **ID**: `rag_generation_agent`
- **Type**: `email_analysis`
- **Tools**: Context Retriever, Answer Generator, Citation Tracker
- **Use**: Answer questions about email content with citations

#### 5. Threat Detection Agent
- **ID**: `threat_detection_agent`
- **Type**: `security`
- **Tools**: Phishing Detector, Domain Analyzer, Threat Scorer
- **Use**: Identify phishing and security threats

#### 6. Database Persistence Agent
- **ID**: `database_persistence_agent`
- **Type**: `data_management`
- **Tools**: Execution Storage, Threat Storage, Analytics Logger
- **Use**: Store results to database

---

## Error Handling

### Common Errors

#### 401 Unauthorized
```json
{
  "status": "error",
  "error": "Client error '401 Unauthorized'",
  "status_code": 401
}
```

**Cause**: Invalid or expired API key  
**Fix**: Get new API key from IBM Cloud → Watson Orchestrate → Access Management

#### 403 Forbidden
```json
{
  "status": "error",
  "error": "Client error '403 Forbidden'",
  "status_code": 403
}
```

**Cause**: API key lacks permissions  
**Fix**: Ensure API key has agent management permissions

#### Connection Error
```json
{
  "status": "error",
  "error": "Connection refused"
}
```

**Cause**: Cannot reach Orchestrate API  
**Fix**: Check network connectivity and base URL

---

## SDK Features

### Authentication

The SDK handles authentication automatically using BearerTokenAuthenticator:

```python
# SDK does this internally:
authenticator = BearerTokenAuthenticator(bearer_token=api_key)
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

### Retry Logic

The SDK automatically retries on:
- ✓ Network timeouts
- ✓ 5xx server errors
- ✓ Transient failures

### Error Handling

Each method returns consistent error responses:

```python
{
    "status": "error",
    "error": "Error message",
    "status_code": 401  # if applicable
}
```

### Logging

All operations are logged:

```
INFO: Registered agent: Intent Detection Agent
INFO: Batch registering 6 agents...
ERROR: Failed to register agent: Invalid credentials
```

---

## Complete Example

### Step 1: Verify Credentials

```python
from app.agent_registry_sdk import get_agent_registry

registry = get_agent_registry()
if not registry:
    print("Registry not initialized - check .env credentials")
    exit(1)
```

### Step 2: Define Agents

```python
from app.agent_registry_sdk import get_hacktheagent_agents

agents = get_hacktheagent_agents()
print(f"Loaded {len(agents)} agent definitions")
for agent in agents:
    print(f"  - {agent.agent_name} ({len(agent.capabilities)} tools)")
```

### Step 3: Register Agents

```python
from app.agent_registry_sdk import register_all_agents

result = await register_all_agents()

if result.get("status") == "success":
    print(f"✓ Success: {result['agents_registered']} agents registered")
else:
    print(f"✗ Error: {result.get('error')}")
```

### Step 4: Verify Registration

```python
# Via API endpoint
curl http://localhost:8000/orchestrate/agents/list

# Or via Python
result = await registry.list_agents()
print(f"Registered agents in Orchestrate: {result}")
```

---

## Testing

### Test Connection

```bash
python3 backend/diagnose_orchestrate.py
```

### Test Agent Registration

```bash
# Start backend
cd backend && python3 -m uvicorn app.main:app --reload

# In another terminal
curl -X POST http://localhost:8000/orchestrate/agents/register

# View backend logs for details
```

### Test via Python

```python
import asyncio
from app.agent_registry_sdk import register_all_agents

async def test():
    result = await register_all_agents()
    print(result)

asyncio.run(test())
```

---

## Advantages Over Raw HTTP

| Feature | Raw HTTP | SDK |
|---------|----------|-----|
| Authentication | Manual headers | Automatic |
| Error Handling | Try/catch | Built-in retry |
| Type Checking | None | Full typing |
| Maintainability | Manual updates | SDK handles |
| Error Messages | Raw responses | Formatted |
| Logging | Manual | Automatic |
| Validation | Manual | Built-in |

---

## Next Steps

1. **Verify credentials** are in `.env`
2. **Start backend**: `uvicorn app.main:app --reload`
3. **Register agents**: `curl -X POST http://localhost:8000/orchestrate/agents/register`
4. **Verify registration**: `curl http://localhost:8000/orchestrate/agents/list`
5. **Build workflows** in IBM Orchestrate dashboard using your agents

---

## Files Used

- `backend/app/agent_registry_sdk.py` - SDK-based registry (new)
- `backend/app/main.py` - Updated to use SDK registry
- `backend/.env` - Orchestrate credentials
- `backend/requirements.txt` - SDK dependencies

---

## See Also

- **IBM Watson SDK**: https://github.com/IBM/python-sdk-core
- **IBM Orchestrate API**: https://cloud.ibm.com/apidocs/watson-orchestrate
- **AGENT_EXPORT_GUIDE.md** - Registration workflow

---

**Status: ✅ SDK-BASED AGENT REGISTRATION READY**

Using IBM Watson SDK for robust, maintainable agent registration! 🚀
