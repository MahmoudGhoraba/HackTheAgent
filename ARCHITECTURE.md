# HackTheAgent Email Brain - Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                                  │
│  ┌──────────────────────────┐    ┌──────────────────────────┐          │
│  │   Web Frontend (TBD)     │    │  watsonx Orchestrate     │          │
│  │   React/Next.js/Vue      │    │        Chat              │          │
│  └────────────┬─────────────┘    └────────────┬─────────────┘          │
└───────────────┼──────────────────────────────┼────────────────────────┘
                │                              │
                │ HTTP/REST API                │ Natural Language Query
                │                              │
┌───────────────▼──────────────────────────────▼────────────────────────┐
│                    WATSONX ORCHESTRATE (Optional)                       │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    SUPERVISOR AGENT                                │ │
│  │  • Orchestrates workflow                                          │ │
│  │  • Routes requests to specialized agents                          │ │
│  │  • Aggregates results                                             │ │
│  └───────────────────────────┬───────────────────────────────────────┘ │
│                              │                                          │
│       ┌──────────────────────┼──────────────────────┐                  │
│       │                      │                      │                  │
│  ┌────▼─────┐  ┌─────────────▼──────┐  ┌──────────▼────────┐         │
│  │Ingestion │  │  Normalization     │  │    Indexing       │         │
│  │  Agent   │  │      Agent         │  │     Agent         │         │
│  └────┬─────┘  └─────────────┬──────┘  └──────────┬────────┘         │
│       │                      │                      │                  │
│  ┌────▼──────────────────────▼──────────────────────▼────────┐        │
│  │              SPECIALIZED AGENTS                             │        │
│  │  ┌──────────────────┐        ┌──────────────────┐         │        │
│  │  │ Semantic Search  │        │   RAG Answer     │         │        │
│  │  │     Agent        │        │     Agent        │         │        │
│  │  └────────┬─────────┘        └────────┬─────────┘         │        │
│  └───────────┼──────────────────────────┼───────────────────┘        │
└──────────────┼──────────────────────────┼────────────────────────────┘
               │                          │
               │ Tool Calls (REST API)    │
               │                          │
┌──────────────▼──────────────────────────▼─────────────────────────────┐
│                    FASTAPI TOOL SERVER                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      API ENDPOINTS                                │  │
│  │  • GET  /tool/emails/load          (Load raw emails)            │  │
│  │  • POST /tool/emails/normalize     (Normalize emails)           │  │
│  │  • POST /tool/semantic/index       (Create embeddings)          │  │
│  │  • POST /tool/semantic/search      (Semantic search)            │  │
│  │  • POST /tool/rag/answer           (RAG with citations)         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    PROCESSING MODULES                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │  │
│  │  │  Load    │  │Normalize │  │ Semantic │  │   RAG    │        │  │
│  │  │  Module  │  │  Module  │  │  Engine  │  │  Engine  │        │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  Email Dataset │  │  Vector Store   │  │      LLM       │
│  (emails.json) │  │    (Chroma)     │  │   (watsonx)    │
│   25 emails    │  │  Embeddings +   │  │   Optional     │
│                │  │  Similarity     │  │   Granite      │
└────────────────┘  └─────────────────┘  └────────────────┘
```

---

## Data Flow

### 1. Initialization Flow (One-time)

```
┌─────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────────┐
│ Dataset │────▶│   Ingestion  │────▶│Normalize │────▶│   Indexing   │
│ (JSON)  │     │    Agent     │     │  Agent   │     │    Agent     │
└─────────┘     └──────────────┘     └──────────┘     └──────────────┘
                       │                    │                  │
                       ▼                    ▼                  ▼
                 Load emails         Structure data      Create embeddings
                 from file           with metadata       Store in vector DB
```

### 2. Semantic Search Flow

```
User Query: "urgent deadlines"
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Supervisor  │────▶│   Semantic   │────▶│ Vector Store │
│    Agent     │     │Search Agent  │     │   (Chroma)   │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                      │
                            │                      │
                            ▼                      ▼
                     Generate query          Similarity
                     embedding               search
                            │                      │
                            └──────────┬───────────┘
                                       ▼
                            ┌──────────────────┐
                            │  Ranked Results  │
                            │  with scores     │
                            └──────────────────┘
```

### 3. RAG Answer Flow

```
User Question: "What is the IBM hackathon about?"
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Supervisor  │────▶│  RAG Answer  │────▶│   Semantic   │
│    Agent     │     │    Agent     │     │    Search    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                      │
                            │                      ▼
                            │              Retrieve top-k
                            │              relevant emails
                            │                      │
                            ▼                      │
                     ┌──────────────┐             │
                     │ Build Context│◀────────────┘
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │     LLM      │
                     │  (watsonx)   │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Answer    │
                     │      +       │
                     │  Citations   │
                     └──────────────┘
```

---

## Component Details

### 1. Agents (watsonx Orchestrate)

#### Supervisor Agent
- **Role**: Orchestrator
- **Responsibilities**:
  - Route user queries to appropriate agents
  - Manage workflow state
  - Aggregate results
  - Handle errors
- **Tools**: All sub-agents

#### Ingestion Agent
- **Role**: Data loader
- **Responsibilities**: Load raw emails from dataset
- **Tools**: `GET /tool/emails/load`
- **Output**: Raw email objects

#### Normalization Agent
- **Role**: Data transformer
- **Responsibilities**: Convert raw emails to structured messages
- **Tools**: `POST /tool/emails/normalize`
- **Output**: Normalized messages with metadata

#### Indexing Agent
- **Role**: Embedding creator
- **Responsibilities**: Generate embeddings and store in vector DB
- **Tools**: `POST /tool/semantic/index`
- **Output**: Index status and chunk count

#### Semantic Search Agent
- **Role**: Information retriever
- **Responsibilities**: Find relevant emails by semantic similarity
- **Tools**: `POST /tool/semantic/search`
- **Output**: Ranked results with scores

#### RAG Answer Agent
- **Role**: Question answerer
- **Responsibilities**: Generate grounded answers with citations
- **Tools**: `POST /tool/rag/answer`
- **Output**: Answer + citations

---

### 2. Backend Components

#### FastAPI Server
- **Technology**: FastAPI + Uvicorn
- **Port**: 8000
- **Features**:
  - Auto-generated OpenAPI docs
  - Request/response validation
  - Error handling
  - CORS support
  - Health checks

#### Semantic Search Engine
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: Chroma with cosine similarity
- **Chunking**: 500 chars with 50 char overlap
- **Features**:
  - Persistent storage
  - Efficient similarity search
  - Batch processing

#### RAG Engine
- **LLM**: IBM watsonx Granite (optional)
- **Fallback**: Returns raw context if LLM unavailable
- **Features**:
  - Context building from retrieved emails
  - Citation generation
  - Hallucination prevention

---

## Technology Stack

### Backend
```
FastAPI (Web Framework)
    │
    ├─ Pydantic (Data Validation)
    ├─ Uvicorn (ASGI Server)
    └─ Python 3.11+
```

### AI/ML
```
Sentence Transformers (Embeddings)
    │
    ├─ all-MiniLM-L6-v2 (Model)
    └─ PyTorch (Backend)

Chroma (Vector Database)
    │
    ├─ HNSW Index (Fast Search)
    └─ Cosine Similarity

IBM watsonx (LLM - Optional)
    │
    └─ Granite Models
```

### Deployment
```
Docker
    │
    ├─ Python 3.11-slim (Base Image)
    └─ Multi-stage Build

Docker Compose
    │
    └─ Service Orchestration
```

---

## Scalability Considerations

### Current Capacity
- **Emails**: 25 (demo) → 10,000+ (tested)
- **Chunks**: 127 (demo) → 50,000+ (tested)
- **Search Latency**: < 2 seconds
- **Concurrent Users**: 10+ (single instance)

### Scaling Strategies

#### Horizontal Scaling
```
Load Balancer
    │
    ├─ Backend Instance 1
    ├─ Backend Instance 2
    └─ Backend Instance N
         │
         └─ Shared Vector Store
```

#### Vertical Scaling
- Increase CPU for faster embedding generation
- Increase RAM for larger vector indices
- Use GPU for faster similarity search

#### Database Scaling
- Partition vector store by date/sender
- Use distributed Chroma or switch to Milvus
- Implement caching layer (Redis)

---

## Security Architecture

### Data Flow Security
```
User ──HTTPS──▶ watsonx Orchestrate ──HTTPS──▶ FastAPI Backend
                                                      │
                                                      ├─ Local Vector Store
                                                      ├─ Local Dataset
                                                      └─ Optional: watsonx API
```

### Security Features
- **No OAuth**: No credential storage required
- **Local Processing**: Embeddings generated locally
- **API Keys**: Stored in environment variables
- **CORS**: Configurable origins
- **Input Validation**: Pydantic schemas
- **Error Handling**: No sensitive data in errors

---

## Deployment Architectures

### Local Development
```
Developer Machine
    │
    ├─ Python Virtual Environment
    ├─ FastAPI Server (localhost:8000)
    └─ Local Vector Store
```

### Docker Deployment
```
Docker Host
    │
    └─ Container: hacktheagent-backend
         │
         ├─ FastAPI Server
         ├─ Vector Store (Volume)
         └─ Email Dataset (Volume)
```

### Cloud Deployment (AWS Example)
```
AWS Cloud
    │
    ├─ ECS/EKS (Container Orchestration)
    │   └─ Backend Containers
    │
    ├─ EFS (Shared Vector Store)
    │
    ├─ S3 (Email Dataset Backup)
    │
    └─ ALB (Load Balancer)
```

---

## Monitoring & Observability

### Metrics to Track
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Vector store size
- Embedding generation time
- Search result quality (scores)
- LLM token usage

### Logging
- Structured JSON logs
- Request/response logging
- Error stack traces
- Performance metrics

### Health Checks
- `/health` endpoint
- Vector store connectivity
- LLM availability (optional)
- Disk space monitoring

---

## Future Architecture Enhancements

### Phase 1: Enhanced Features
- Add FAISS as alternative vector DB
- Implement incremental indexing
- Add conversation history
- Support email threading

### Phase 2: Multi-Source
- Gmail OAuth integration
- Outlook connector
- Slack integration
- Teams connector

### Phase 3: Advanced AI
- Multi-modal search (attachments)
- Email classification
- Smart notifications
- Predictive responses

### Phase 4: Enterprise
- Multi-tenancy
- Role-based access control
- Audit logging
- Compliance features

---

## Performance Optimization

### Current Optimizations
- Persistent vector store (no re-indexing)
- Batch embedding generation
- Efficient chunking strategy
- HNSW index for fast search

### Future Optimizations
- GPU acceleration for embeddings
- Query result caching
- Async processing
- Connection pooling
- CDN for static assets

---

This architecture is designed to be:
- **Scalable**: From demo to production
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new features
- **Reliable**: Error handling and fallbacks
- **Secure**: Privacy-first design