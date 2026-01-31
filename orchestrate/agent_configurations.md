# watsonx Orchestrate Agent Configurations

## Overview
This document provides the complete agent setup for HackTheAgent Email Brain in watsonx Orchestrate. The system uses a **Supervisor Agent** that orchestrates 5 specialized agents to perform semantic search and RAG over emails.

## Architecture

```
User Question
     ↓
Supervisor Agent (Orchestrator)
     ↓
     ├─→ Ingestion Agent (loads emails)
     ├─→ Normalization Agent (normalizes emails)
     ├─→ Indexing Agent (creates embeddings)
     ├─→ Semantic Search Agent (finds relevant emails)
     └─→ RAG Answer Agent (generates grounded answers)
```

---

## Tool Server Configuration

**Base URL**: `http://localhost:8000` (or your deployed URL)

All agents will call these REST API endpoints as tools.

---

## Agent 1: Ingestion Agent

**Purpose**: Fetch raw emails from the dataset

### Configuration
- **Name**: Email Ingestion Agent
- **Description**: Loads raw emails from the local dataset
- **Type**: Tool-calling agent

### Tool Definition
```json
{
  "name": "load_emails",
  "description": "Loads raw emails from the JSON dataset file",
  "method": "GET",
  "url": "http://localhost:8000/tool/emails/load",
  "parameters": [],
  "response_schema": {
    "emails": [
      {
        "id": "string",
        "from": "string",
        "to": "string",
        "subject": "string",
        "date": "string",
        "body": "string"
      }
    ]
  }
}
```

### Agent Prompt
```
You are the Email Ingestion Agent. Your sole responsibility is to fetch raw emails from the dataset.

Instructions:
1. Call the load_emails tool to retrieve all emails
2. Return exactly what you retrieve without modification
3. Do not filter, summarize, or transform the data
4. If the tool fails, report the error clearly

Output format: Return the complete list of raw emails as JSON.
```

---

## Agent 2: Normalization Agent

**Purpose**: Convert raw emails into normalized messages with structured text and metadata

### Configuration
- **Name**: Email Normalization Agent
- **Description**: Normalizes raw emails into structured messages
- **Type**: Tool-calling agent

### Tool Definition
```json
{
  "name": "normalize_emails",
  "description": "Converts raw emails into normalized messages with text and metadata",
  "method": "POST",
  "url": "http://localhost:8000/tool/emails/normalize",
  "parameters": [
    {
      "name": "emails",
      "type": "array",
      "required": true,
      "description": "List of raw email objects to normalize"
    }
  ],
  "request_body": {
    "emails": []
  },
  "response_schema": {
    "messages": [
      {
        "id": "string",
        "text": "string",
        "metadata": {
          "from": "string",
          "to": "string",
          "subject": "string",
          "date": "string"
        }
      }
    ]
  }
}
```

### Agent Prompt
```
You are the Email Normalization Agent. Your responsibility is to normalize raw emails into structured messages.

Instructions:
1. Receive raw emails from the Ingestion Agent
2. Call the normalize_emails tool with the raw emails
3. Return the normalized messages exactly as received
4. Do not invent or modify any fields
5. Preserve all metadata accurately

Output format: Return the list of normalized messages as JSON.
```

---

## Agent 3: Indexing Agent

**Purpose**: Create semantic embeddings and index messages in vector database

### Configuration
- **Name**: Semantic Indexing Agent
- **Description**: Creates embeddings and indexes messages for semantic search
- **Type**: Tool-calling agent

### Tool Definition
```json
{
  "name": "index_messages",
  "description": "Creates embeddings and stores messages in vector database",
  "method": "POST",
  "url": "http://localhost:8000/tool/semantic/index",
  "parameters": [
    {
      "name": "messages",
      "type": "array",
      "required": true,
      "description": "List of normalized messages to index"
    }
  ],
  "request_body": {
    "messages": []
  },
  "response_schema": {
    "status": "string",
    "chunks_indexed": "integer"
  }
}
```

### Agent Prompt
```
You are the Semantic Indexing Agent. Your responsibility is to create semantic memory from normalized messages.

Instructions:
1. Receive normalized messages from the Normalization Agent
2. Call the index_messages tool to create embeddings and store in vector database
3. Report the indexing status and number of chunks created
4. Only index once unless explicitly asked to re-index
5. If already indexed, skip this step and report "Already indexed"

Output format: Return indexing status with chunk count.
```

---

## Agent 4: Semantic Search Agent

**Purpose**: Perform semantic search to find relevant emails

### Configuration
- **Name**: Semantic Search Agent
- **Description**: Performs semantic search over indexed emails
- **Type**: Tool-calling agent

### Tool Definition
```json
{
  "name": "semantic_search",
  "description": "Performs semantic search to find relevant emails based on meaning",
  "method": "POST",
  "url": "http://localhost:8000/tool/semantic/search",
  "parameters": [
    {
      "name": "query",
      "type": "string",
      "required": true,
      "description": "Search query"
    },
    {
      "name": "top_k",
      "type": "integer",
      "required": false,
      "default": 5,
      "description": "Number of results to return (1-20)"
    }
  ],
  "request_body": {
    "query": "string",
    "top_k": 5
  },
  "response_schema": {
    "results": [
      {
        "id": "string",
        "subject": "string",
        "date": "string",
        "score": "float",
        "snippet": "string"
      }
    ]
  }
}
```

### Agent Prompt
```
You are the Semantic Search Agent. Your responsibility is to find relevant emails using semantic search.

Instructions:
1. Receive a search query from the Supervisor
2. Call the semantic_search tool with the query and top_k parameter
3. Return ranked results with similarity scores and snippets
4. Explain why each result is relevant based on semantic similarity
5. If no results found, report clearly

Output format: Return search results with scores, subjects, dates, and snippets.
```

---

## Agent 5: RAG Answer Agent

**Purpose**: Generate grounded answers using retrieved email context

### Configuration
- **Name**: RAG Answer Agent
- **Description**: Answers questions using retrieval-augmented generation with citations
- **Type**: Tool-calling agent

### Tool Definition
```json
{
  "name": "rag_answer",
  "description": "Answers questions using retrieved email context and LLM",
  "method": "POST",
  "url": "http://localhost:8000/tool/rag/answer",
  "parameters": [
    {
      "name": "question",
      "type": "string",
      "required": true,
      "description": "User's question"
    },
    {
      "name": "top_k",
      "type": "integer",
      "required": false,
      "default": 5,
      "description": "Number of emails to retrieve for context (1-20)"
    }
  ],
  "request_body": {
    "question": "string",
    "top_k": 5
  },
  "response_schema": {
    "answer": "string",
    "citations": [
      {
        "id": "string",
        "subject": "string",
        "date": "string",
        "snippet": "string"
      }
    ]
  }
}
```

### Agent Prompt
```
You are the RAG Answer Agent. Your responsibility is to answer questions using ONLY retrieved email evidence.

Instructions:
1. Receive a question from the Supervisor
2. Call the rag_answer tool with the question and top_k parameter
3. The tool will retrieve relevant emails and generate a grounded answer
4. Return the answer with citations
5. NEVER make up information - only use what's in the retrieved emails
6. Always provide citations showing which emails were used
7. If the answer cannot be found in emails, say so clearly

Output format: Return the answer followed by numbered citations with email subjects, dates, and snippets.
```

---

## Supervisor Agent (Orchestrator)

**Purpose**: Main agent that orchestrates the workflow and interacts with users

### Configuration
- **Name**: Email Brain Supervisor
- **Description**: Orchestrates multi-agent workflow for email semantic search and RAG
- **Type**: Orchestrator agent with tool-calling capabilities

### Available Sub-Agents
- Ingestion Agent
- Normalization Agent
- Indexing Agent
- Semantic Search Agent
- RAG Answer Agent

### Supervisor Prompt
```
You are the Email Brain Supervisor Agent. You orchestrate a multi-agent system that provides semantic search and question-answering over a user's email dataset.

Your Workflow:

INITIALIZATION (Run once at startup):
1. Call Ingestion Agent to load raw emails
2. Send raw emails to Normalization Agent
3. Send normalized messages to Indexing Agent
4. Confirm indexing is complete

USER INTERACTION (For each user question):
1. Determine if user wants:
   - Semantic search (show matching emails)
   - RAG answer (answer question with citations)
   - Both (show matches + answer)

2. For semantic search:
   - Call Semantic Search Agent with user's query
   - Present results with scores and snippets
   - Explain why each email is relevant

3. For RAG answers:
   - Call RAG Answer Agent with user's question
   - Present answer with clear citations
   - Show which emails were used as evidence

4. For both:
   - First show semantic search results
   - Then provide RAG answer with citations

RULES:
- Never guess or make up information
- Always ground answers in retrieved email content
- Provide clear citations for all claims
- If information is not in emails, say so explicitly
- Be transparent about the retrieval and reasoning process
- Handle errors gracefully and inform the user

EXPLAINABILITY:
- Show which emails were retrieved and why
- Display similarity scores for transparency
- Explain the reasoning behind answers
- Cite specific email snippets as evidence

Output format: 
- For search: List of relevant emails with scores and snippets
- For answers: Clear answer followed by numbered citations
- Always be helpful, accurate, and transparent
```

### Workflow Logic
```python
# Pseudo-code for Supervisor workflow

def initialize():
    """Run once at startup"""
    raw_emails = call_agent("Ingestion Agent")
    normalized = call_agent("Normalization Agent", raw_emails)
    index_status = call_agent("Indexing Agent", normalized)
    return index_status

def handle_user_query(user_input):
    """Handle each user question"""
    
    # Determine intent
    if is_search_query(user_input):
        results = call_agent("Semantic Search Agent", user_input)
        return format_search_results(results)
    
    elif is_question(user_input):
        response = call_agent("RAG Answer Agent", user_input)
        return format_answer_with_citations(response)
    
    else:
        # Default: provide both search and answer
        search_results = call_agent("Semantic Search Agent", user_input)
        rag_response = call_agent("RAG Answer Agent", user_input)
        return format_combined_response(search_results, rag_response)
```

---

## Testing the Agents

### Test Sequence

1. **Initialize System**
   ```
   User: "Initialize the email brain"
   Expected: Supervisor runs ingestion → normalization → indexing
   ```

2. **Semantic Search Test**
   ```
   User: "Show me emails about deadlines"
   Expected: Semantic Search Agent returns relevant emails with scores
   ```

3. **RAG Answer Test**
   ```
   User: "What is the IBM Dev Day hackathon about?"
   Expected: RAG Answer Agent provides answer with citations
   ```

4. **Combined Test**
   ```
   User: "Find and summarize emails about security vulnerabilities"
   Expected: Both search results and RAG answer with citations
   ```

---

## Deployment Notes

1. **Tool Server**: Ensure FastAPI backend is running at the configured URL
2. **API Keys**: Configure watsonx or OpenAI credentials for RAG answers
3. **Network**: Ensure watsonx Orchestrate can reach the tool server
4. **Monitoring**: Check logs for agent interactions and tool calls
5. **Error Handling**: Each agent should handle and report errors gracefully

---

## Success Metrics

- **Initialization**: All 25 emails indexed successfully
- **Search Accuracy**: Relevant emails retrieved with scores > 0.7
- **Answer Quality**: Grounded answers with proper citations
- **Latency**: Search < 2s, RAG answer < 5s
- **Explainability**: Clear reasoning and citations provided

---

## Troubleshooting

**Issue**: Agents not calling tools
- **Solution**: Verify tool server URL and network connectivity

**Issue**: Poor search results
- **Solution**: Check embedding model, adjust chunk size/overlap

**Issue**: RAG answers without citations
- **Solution**: Verify RAG Agent prompt includes citation requirement

**Issue**: Indexing fails
- **Solution**: Check vector store permissions and disk space

---

## Next Steps

1. Import these agent configurations into watsonx Orchestrate
2. Configure tool server URL
3. Test each agent individually
4. Test full workflow with Supervisor
5. Run demo questions (see demo_script.md)