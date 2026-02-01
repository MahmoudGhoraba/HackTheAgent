# HackTheAgent Email Brain 🧠

**An intelligent, multi-agent email processing and security platform powered by AI orchestration**

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Agents](#agents)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Development](#development)

---

## 🎯 Overview

**HackTheAgent** is a sophisticated email intelligence platform that combines semantic search, RAG (Retrieval-Augmented Generation), threat detection, and multi-agent orchestration to provide comprehensive email analysis and security.

The platform processes emails through a network of specialized AI agents that work collaboratively to:
- Analyze email content and semantics
- Detect security threats (phishing, malware, spoofing)
- Classify and organize emails
- Extract insights and generate intelligent responses
- Track analytics and performance metrics

### Innovation Features

🔒 **Advanced Threat Detection** - AI-powered security analysis detecting phishing, spoofing, malware vectors, and suspicious patterns

📊 **Semantic Intelligence** - Vector embeddings and similarity search for intelligent email retrieval

🤖 **Multi-Agent Orchestration** - Collaborative agents using IBM Watson Orchestrate and native agents

🔍 **RAG Engine** - Context-aware generation with email history retrieval

---

## ✨ Key Features

### Email Processing
- **Email Loading & Normalization** - Standardize email data across formats
- **Semantic Indexing** - Convert emails to embeddings for intelligent search
- **Thread Detection** - Automatically organize emails into conversations
- **Gmail OAuth Integration** - Direct Gmail account connectivity

### Security & Threat Detection
- **Phishing Detection** - Identifies phishing attempts and tactics
- **Domain Analysis** - Reputation and legitimacy analysis
- **Malware Pattern Recognition** - Detects malware distribution vectors
- **Typosquatting Detection** - Catches domain impersonation attempts
- **Threat Scoring** - Comprehensive threat level classification (SAFE, CAUTION, WARNING, CRITICAL)

### Search & Retrieval
- **Semantic Search** - Find emails by meaning, not just keywords
- **Vector Database** - ChromaDB for fast similarity search
- **RAG Query** - Generate answers with email context
- **Advanced Filtering** - Search by threat level, classification, etc.

### Analytics & Insights
- **Search Analytics** - Track search patterns and performance
- **Threat Statistics** - Monitor security metrics
- **Classification Metrics** - Email categorization insights
- **Performance Monitoring** - System health and latency tracking

### Agent Framework
- **Intent Detection** - Understand user intentions
- **Classification** - Categorize emails and threats
- **Semantic Search** - Specialized search agents
- **RAG Generation** - Context-aware response generation
- **Database Persistence** - Store and retrieve analysis results
- **Threat Detection** - Security-focused agent

---

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│                  TypeScript + React + Tailwind              │
│                   (localhost:3000)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                          │
│                   Python 3.10+                              │
│                  (localhost:8000)                           │
├─────────────────────────────────────────────────────────────┤
│ Core Services Layer                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Email Engine   │  │ Semantic     │  │ RAG Engine   │   │
│  │ - Loader       │  │ Search       │  │ - Context    │   │
│  │ - Normalizer   │  │ - Embeddings │  │ - Generation │   │
│  │ - Thread Mgmt  │  │ - ChromaDB   │  │ - LLM Calls  │   │
│  └────────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Threat Engine  │  │ Classifier   │  │ Analytics    │   │
│  │ - Phishing     │  │ - Categories │  │ - Metrics    │   │
│  │ - Malware      │  │ - Labels     │  │ - Tracking   │   │
│  │ - Spoofing     │  │ - Scoring    │  │ - Reporting  │   │
│  └────────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Multi-Agent Orchestration Layer                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  IBM Watson Orchestrate Integration                 │  │
│  │  - Agent Registry (SDK)                             │  │
│  │  - Workflow Execution                               │  │
│  │  - Agent Communication                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Native Agent Framework                             │  │
│  │  - Threat Detection Agent                           │  │
│  │  - Classification Agent                             │  │
│  │  - Intent Detection Agent                           │  │
│  │  - Semantic Search Agent                            │  │
│  │  - RAG Generation Agent                             │  │
│  │  - Database Persistence Agent                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ External Integrations                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Gmail OAuth  │  │ WatsonX      │  │ ChromaDB     │    │
│  │ - Auth Flow  │  │ - LLM        │  │ - Vector DB  │    │
│  │ - User Email │  │ - Embeddings │  │ - Storage    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ SQLAlchemy   │  │ Sentence     │  │ IBM Cloud    │    │
│  │ - Database   │  │ Transformers │  │ - Watson     │    │
│  │ - ORM        │  │ - Embeddings │  │ - Orchestrate│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Raw Emails
    │
    ▼
┌─────────────────────┐
│ Email Normalization │
└────────┬────────────┘
         │
         ▼
    ┌─────────────────────────┐
    │ Threat Analysis         │
    │ Classification          │
    │ Intent Detection        │
    └────────┬────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Store in DB  │  │ Create       │
│              │  │ Embeddings   │
└──────────────┘  └────────┬─────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │ Vector Store    │
                    │ (ChromaDB)      │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Semantic     │  │ Threat       │  │ Analytics    │
    │ Search       │  │ Queries      │  │ Tracking     │
    └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 💻 Tech Stack

### Backend
- **Framework**: FastAPI (modern async Python web framework)
- **Server**: Uvicorn (ASGI server)
- **Language**: Python 3.10+
- **API Docs**: Swagger/OpenAPI, ReDoc

### Frontend
- **Framework**: Next.js 13.5.6
- **Language**: TypeScript
- **UI**: React 18.2.0
- **Styling**: Tailwind CSS 3.3.3
- **HTTP Client**: Axios

### AI/ML Services
- **LLM Provider**: IBM Watson (WatsonX) with Granite models
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB
- **ORM**: SQLAlchemy

### Agent Framework
- **Orchestration**: IBM Watson Orchestrate
- **Agent Development Kit**: ADK (Agent Development Kit)
- **Agent Types**: Native Python agents + Watson orchestrated agents

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: SQLite (emails.db)
- **Cache**: In-memory cache layer
- **Authentication**: Google OAuth 2.0 (Gmail integration)

---

## 📁 Project Structure

```
HackTheAgent/
│
├── frontend/                          # Next.js React Application
│   ├── src/                          # Source code
│   ├── public/                       # Static assets
│   ├── package.json                  # Dependencies
│   ├── next.config.js                # Next.js config
│   ├── tailwind.config.ts            # Tailwind CSS config
│   └── tsconfig.json                 # TypeScript config
│
├── backend/                           # FastAPI Python Backend
│   ├── app/                          # Main application
│   │   ├── main.py                   # FastAPI app initialization
│   │   ├── config.py                 # Configuration management
│   │   ├── schemas.py                # Pydantic models
│   │   ├── routes/                   # API routes
│   │   │   └── workflow.py           # Workflow endpoints
│   │   ├── email_providers/          # Email integrations
│   │   ├── load.py                   # Email loading
│   │   ├── normalize.py              # Email normalization
│   │   ├── semantic.py               # Semantic search engine
│   │   ├── rag.py                    # RAG engine
│   │   ├── classify.py               # Classification logic
│   │   ├── threat_detection.py       # Threat analysis
│   │   ├── threat_endpoints.py       # Threat detection API
│   │   ├── analytics.py              # Analytics tracking
│   │   ├── database.py               # Database management
│   │   ├── cache.py                  # Caching layer
│   │   ├── gmail_oauth.py            # Gmail OAuth flow
│   │   ├── orchestrator.py           # Agent orchestration
│   │   ├── local_agent_engine.py     # Local agent execution
│   │   ├── ibm_orchestrate.py        # IBM Watson integration
│   │   ├── watson_orchestrate.py     # Watson client
│   │   ├── agent_registry.py         # Agent registry
│   │   ├── agent_registry_sdk.py     # SDK agent management
│   │   ├── orchestrate_routes.py     # Orchestration endpoints
│   │   ├── data/                     # Email data storage
│   │   └── vector_store/             # ChromaDB storage
│   ├── agents/                       # YAML agent definitions
│   │   ├── threat_detection_agent.yaml
│   │   ├── classification_agent.yaml
│   │   ├── intent_detection_agent.yaml
│   │   ├── semantic_search_agent.yaml
│   │   ├── rag_generation_agent.yaml
│   │   └── database_persistence_agent.yaml
│   ├── mcp_server/                   # Model Context Protocol Server
│   ├── tests/                        # Unit tests
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Docker configuration
│   ├── run.sh                        # Run script
│   └── start.sh                      # Start script
│
├── adk-project/                       # Agent Development Kit Project
│   ├── agents/                       # Agent definitions
│   │   ├── threat_detection_agent.yaml
│   │   ├── classification_agent.yaml
│   │   ├── intent_detection_agent.yaml
│   │   ├── semantic_search_agent.yaml
│   │   ├── rag_generation_agent.yaml
│   │   └── database_persistence_agent.yaml
│   ├── tools/                        # Tool definitions
│   │   ├── threat_scorer.yaml
│   │   ├── phishing_detector.yaml
│   │   ├── domain_analyzer.yaml
│   │   ├── semantic_indexer.yaml
│   │   ├── context_retriever.yaml
│   │   ├── category_classifier.yaml
│   │   ├── intent_parser.yaml
│   │   ├── answer_generator.yaml
│   │   ├── citation_tracker.yaml
│   │   ├── entity_extractor.yaml
│   │   ├── sentiment_analyzer.yaml
│   │   ├── analytics_logger.yaml
│   │   ├── execution_storage.yaml
│   │   ├── threat_storage.yaml
│   │   └── priority_detector.yaml
│   ├── flows/                        # Workflow definitions
│   └── knowledge/                    # Knowledge base
│
├── orchestrate/                       # Orchestration configuration
│   └── agent_configurations.md       # Agent config docs
│
├── data/                             # Shared data directory
│   └── emails.db                     # Email database
│
├── docker-compose.yml                # Docker Compose configuration
├── .env                              # Environment variables
├── .env.example                      # Example environment
│
└── Utility Scripts/
    ├── check_api_key.py              # API key validation
    ├── display_agents.py             # List agents
    ├── find_correct_endpoint.py      # Endpoint discovery
    ├── fix_401_error.py              # Auth debugging
    ├── import_agents_via_api.py      # Import agents
    ├── orchestrate_workflow_setup.py # Setup workflows
    ├── register_agents_sdk.py        # Register agents
    ├── test_orchestrate_agents.py    # Test agents
    └── test_workflow.sh              # Test workflow
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- IBM Cloud Account with Watson services (WatsonX)
- Google OAuth credentials for Gmail integration

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/MahmoudGhoraba/HackTheAgent.git
cd HackTheAgent
```

#### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

#### 4. Environment Configuration

Create `.env` file in the root and backend directories:

```bash
# Backend (.env or backend/.env)
DEBUG=false
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB=chroma
LLM_PROVIDER=watsonx

# Watson/IBM Cloud
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Gmail OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Database
DATABASE_URL=sqlite:///./app/data/emails.db
```

### Running Locally

#### Terminal 1: Start Backend

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

#### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:3000`

### Running with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 📚 API Documentation

### Swagger/OpenAPI

Access the interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core API Endpoints

#### Health & Root

```
GET /health                    - Health check
GET /                         - API information
```

#### Email Management

```
POST /load-emails             - Load emails from file
POST /normalize               - Normalize email data
GET /emails                   - Retrieve all emails
GET /emails/{email_id}        - Get specific email
GET /email-threads            - Get email threads
```

#### Semantic Search

```
POST /index                   - Build embeddings index
POST /search                  - Semantic search
POST /rag-query               - RAG-based query with context
```

#### Classification

```
POST /classify                - Classify emails
POST /classify-batch          - Batch classification
```

#### Threat Detection (INNOVATION)

```
POST /security/threat-detection           - Detect email threats
GET /security/threat-detection/{email_id} - Get email threat analysis
POST /security/threat-detection/batch     - Batch threat analysis
GET /security/stats                       - Threat statistics
```

#### Analytics

```
GET /analytics/search-stats     - Search analytics
GET /analytics/email-stats      - Email statistics
GET /analytics/threat-stats     - Threat statistics
GET /analytics/dashboard        - Dashboard metrics
```

#### Gmail Integration

```
GET /auth/google/oauth-url      - Get OAuth URL
POST /auth/google/callback      - OAuth callback handler
GET /gmail/profile              - Get Gmail profile
POST /gmail/fetch               - Fetch emails from Gmail
GET /gmail/auth-status          - Check Gmail auth status
```

#### Multi-Agent Orchestration

```
GET /agents                     - List all agents
POST /agents/register           - Register new agent
POST /workflows/execute         - Execute workflow
GET /workflows/{execution_id}   - Get workflow status
POST /orchestrate/threat-detection - Use threat detection agent
POST /orchestrate/classify      - Use classification agent
POST /orchestrate/search        - Use search agent
```

### Example Requests

#### Semantic Search

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "billing problems",
    "top_k": 5
  }'
```

#### Threat Detection

```bash
curl -X POST "http://localhost:8000/security/threat-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "phishing spoofing threats",
    "num_results": 50
  }'
```

#### Classification

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "email": {
      "sender": "support@company.com",
      "subject": "Your account has been suspended",
      "body": "Please verify your account..."
    }
  }'
```

---

## 🤖 Agents

HackTheAgent uses a network of specialized AI agents that collaborate to process emails:

### 1. **Threat Detection Agent** 🔒
- **Purpose**: Detect email security threats
- **Capabilities**:
  - Phishing detection and pattern analysis
  - Domain reputation analysis
  - Threat scoring and categorization
  - Malware vector identification
  - Typosquatting detection
- **LLM**: Granite 3 8B Instruct
- **Tools**: phishing_detector, domain_analyzer, threat_scorer

### 2. **Classification Agent** 📂
- **Purpose**: Categorize and label emails
- **Capabilities**:
  - Email categorization (spam, urgent, informational, etc.)
  - Priority classification
  - Subject matter identification
  - Sentiment analysis
- **Tools**: category_classifier, priority_detector, sentiment_analyzer

### 3. **Intent Detection Agent** 💭
- **Purpose**: Understand user intent and email purpose
- **Capabilities**:
  - Intent classification (support request, inquiry, complaint, etc.)
  - Action extraction
  - Requirement identification
- **Tools**: intent_parser, entity_extractor

### 4. **Semantic Search Agent** 🔍
- **Purpose**: Find relevant emails based on semantic meaning
- **Capabilities**:
  - Semantic similarity matching
  - Context-aware search
  - Multi-language support
- **Tools**: semantic_indexer, context_retriever

### 5. **RAG Generation Agent** 📝
- **Purpose**: Generate contextual responses using email history
- **Capabilities**:
  - Context-aware generation
  - Citation tracking
  - Relevant document retrieval
- **Tools**: answer_generator, citation_tracker, context_retriever

### 6. **Database Persistence Agent** 💾
- **Purpose**: Store and retrieve analysis results
- **Capabilities**:
  - Execution logging
  - Analysis result storage
  - Historical tracking
  - Query indexing
- **Tools**: execution_storage, threat_storage, analytics_logger

---

## ⚙️ Configuration

### Application Settings

All settings are managed through `backend/app/config.py`:

```python
# App Settings
app_name = "HackTheAgent Email Brain"
app_version = "1.0.0"
debug = False

# Embedding Configuration
embedding_provider = "sentence-transformers"
embedding_model = "all-MiniLM-L6-v2"
chunk_size = 500

# Vector Database
vector_db = "chroma"
collection_name = "email_embeddings"

# LLM Configuration
llm_provider = "watsonx"
llm_model = "ibm/granite-13b-chat-v2"
llm_temperature = 0.1
llm_max_tokens = 2048

# Search Configuration
default_top_k = 5

# CORS Configuration
cors_origins = ["http://localhost:3000", "http://localhost:8000"]
```

### Environment Variables

Key environment variables:

```bash
# AI/ML
WATSONX_API_KEY              # IBM Watson API key
WATSONX_PROJECT_ID           # Watson project ID
WATSONX_URL                  # Watson endpoint URL

# Gmail
GOOGLE_CLIENT_ID             # Gmail OAuth client ID
GOOGLE_CLIENT_SECRET         # Gmail OAuth secret
GOOGLE_REDIRECT_URI          # OAuth redirect URL

# Database
DATABASE_URL                 # SQLAlchemy database URL

# Embedding
EMBEDDING_PROVIDER           # Embedding service provider
EMBEDDING_MODEL              # Model name

# Application
DEBUG                        # Debug mode (true/false)
```

---

## 🐳 Docker Deployment

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: hacktheagent-backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - EMBEDDING_PROVIDER=sentence-transformers
      - EMBEDDING_MODEL=all-MiniLM-L6-v2
      - VECTOR_DB=chroma
      - LLM_PROVIDER=watsonx
      - WATSONX_API_KEY=${WATSONX_API_KEY}
      - WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID}
    volumes:
      - ./backend/app/data:/app/app/data
      - ./backend/app/vector_store:/app/app/vector_store
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Building and Running

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean up
docker-compose down -v
```

---

## 🛠️ Development

### Backend Development

#### Setting up for Development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_semantic.py

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_semantic.py::test_search
```

#### Key Backend Files

- **main.py** - FastAPI app initialization and route mounting
- **config.py** - Application settings and configuration
- **schemas.py** - Pydantic request/response models
- **semantic.py** - Semantic search implementation
- **rag.py** - RAG engine implementation
- **threat_detection.py** - Threat analysis logic
- **orchestrator.py** - Agent orchestration logic

### Frontend Development

```bash
cd frontend
npm install
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # Run ESLint
npm run type-check   # Check TypeScript
```

### Agent Development

#### Adding New Agents

1. Create agent YAML in `adk-project/agents/`:

```yaml
spec_version: v1
kind: native
name: my_agent
display_name: My Custom Agent
description: Agent description
instructions: |
  You are a specialized agent for...
style: default
llm: watsonx/ibm/granite-3-8b-instruct
tools:
  - tool_1
  - tool_2
```

2. Register with backend:

```python
# In backend/app/main.py
from app.agent_registry_sdk import register_all_agents

@app.on_event("startup")
async def startup_event():
    register_all_agents()
```

3. Create endpoints to use the agent:

```python
@app.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    # Use orchestrator to invoke agent
    result = orchestrator.execute_agent("my_agent", request)
    return result
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/
```

#### Integration Tests

```bash
pytest tests/integration/
```

#### E2E Tests

```bash
# Start backend and frontend
cd backend && python -m uvicorn app.main:app --reload &
cd frontend && npm run dev &

# Run E2E tests
pytest tests/e2e/
```

---

## 📊 Monitoring & Logging

### Logging

The application uses Python's standard logging module:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing email")
logger.error("Error occurred", exc_info=True)
```

Log levels:
- **DEBUG** - Detailed debugging information
- **INFO** - General informational messages
- **WARNING** - Warning messages
- **ERROR** - Error messages
- **CRITICAL** - Critical error messages

### Health Checks

Backend health check:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "app": "HackTheAgent Email Brain",
  "version": "1.0.0"
}
```

---

## 🔐 Security Considerations

1. **API Key Management** - Use environment variables, never commit keys
2. **Gmail OAuth** - Implements OAuth 2.0 flow with secure token storage
3. **CORS** - Configure allowed origins in settings
4. **Input Validation** - Pydantic models validate all inputs
5. **Database Security** - SQLAlchemy ORM prevents SQL injection
6. **Threat Detection** - Email security scanning before processing

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

---

## 📝 License

This project is part of a hackathon initiative by Mahmoud Ghoraba.

---

## 📞 Support & Questions

For questions or issues:
- Review the API documentation at `/docs`
- Check test files for usage examples
- Review agent YAML configurations
- Check environment variables in `.env.example`

---

## 🎯 Roadmap

- [ ] Advanced multi-turn conversation support
- [ ] Custom model fine-tuning
- [ ] Additional email providers (Office 365, etc.)
- [ ] Mobile app
- [ ] Real-time collaboration features
- [ ] Advanced filtering and aggregation
- [ ] Machine learning model optimization
- [ ] Expanded threat detection patterns
- [ ] Integration with security tools (SIEM, etc.)

---

**Made with ❤️ for intelligent email processing**

Last Updated: February 1, 2026
