# HackTheAgent Email Brain - Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (Port 3000)                         │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │  │
│  │  │  AI Agent      │  │  Gmail OAuth   │  │   Analytics    │    │  │
│  │  │  Chat UI       │  │  Management    │  │   Dashboard    │    │  │
│  │  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘    │  │
│  └───────────┼──────────────────┼──────────────────┼──────────────┘  │
└──────────────┼──────────────────┼──────────────────┼─────────────────┘
               │                  │                  │
               │ HTTP/REST API (Axios)               │
               │                  │                  │
┌──────────────▼──────────────────▼──────────────────▼─────────────────┐
│                    FastAPI Backend (Port 8000)                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                      API LAYER                                    │ │
│  │  • 20+ REST Endpoints                                            │ │
│  │  • Request/Response Validation (Pydantic)                        │ │
│  │  • Error Handling & Logging                                      │ │
│  │  • CORS Middleware                                               │ │
│  │  • Auto-generated OpenAPI Docs                                   │ │
│  └────────────┬─────────────────────────────────────────────────────┘ │
│               │                                                         │
│  ┌────────────▼─────────────────────────────────────────────────────┐ │
│  │                    SERVICE LAYER                                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│  │  │  Email   │  │ Semantic │  │   RAG    │  │  Gmail   │        │ │
│  │  │  Loader  │  │  Search  │  │  Engine  │  │  OAuth   │        │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│  │  │Normalize │  │ Classify │  │Analytics │  │  Cache   │        │ │
│  │  │  Module  │  │  Module  │  │  Engine  │  │  Layer   │        │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┬──────────────┐
         │                   │                   │              │
┌────────▼────────┐  ┌───────▼────────┐  ┌──────▼──────┐  ┌──▼────┐
│  Gmail API      │  │  Vector Store  │  │     LLM     │  │ Redis │
│  (Google)       │  │    (Chroma)    │  │  (watsonx)  │  │ Cache │
│  • OAuth2       │  │  • Embeddings  │  │  • Optional │  │Optional│
│  • Fetch Emails │  │  • Similarity  │  │  • Granite  │  │        │
│  • Search       │  │  • Persistent  │  │  • Fallback │  │        │
└─────────────────┘  └────────────────┘  └─────────────┘  └────────┘
```

---

## Data Flow

### 1. User Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Types Query                              │
│              "What are my recent emails about?"                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend (AI Agent Interface)                       │
│  1. Capture user input                                          │
│  2. Send to backend API                                         │
│  3. Display workflow steps in real-time                         │
│  4. Show results with formatting                                │
└────────────────────────┬────────────────────────────────────────┘
                         │ POST /tool/rag/answer
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Backend API Layer                              │
│  1. Validate request (Pydantic)                                 │
│  2. Check cache (if enabled)                                    │
│  3. Route to appropriate service                                │
│  4. Handle errors gracefully                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Engine                                    │
│  1. Perform semantic search                                     │
│  2. Retrieve top-k relevant emails                              │
│  3. Build context from results                                  │
│  4. Generate answer with LLM (or fallback)                      │
│  5. Extract citations                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Response to User                                │
│  • Answer text                                                  │
│  • Source citations                                             │
│  • Confidence scores                                            │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Gmail Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              User Clicks "Connect Gmail"                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         Frontend: GET /oauth/gmail/authorize                     │
│  Receives authorization URL                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Redirect to Google OAuth                            │
│  User authenticates with Google                                 │
│  Grants permissions to app                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │ Authorization Code
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         Google Redirects to Callback URL                         │
│  http://localhost:3000/gmail-oauth?code=...                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│      Frontend: POST /oauth/gmail/callback                        │
│  Exchange code for access token                                 │
│  Save token to gmail_token.json                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Gmail Connected Successfully                        │
│  Can now fetch real emails                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Email Processing Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────────┐
│   Source    │────▶│  Ingestion   │────▶│Normalize │────▶│   Indexing   │
│ File/Gmail  │     │    Agent     │     │  Agent   │     │    Agent     │
└─────────────┘     └──────────────┘     └──────────┘     └──────────────┘
      │                    │                    │                  │
      ▼                    ▼                    ▼                  ▼
  Raw emails         Load emails         Structure data      Create embeddings
  (JSON/API)         from source         with metadata       Store in vector DB
                                                             (~127 chunks)
```

### 4. Semantic Search Flow

```
User Query: "urgent deadlines"
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│   Semantic   │
│  AI Agent    │     │   API        │     │Search Engine │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                      │
                            │                      ▼
                            │              ┌──────────────┐
                            │              │Generate query│
                            │              │  embedding   │
                            │              └──────┬───────┘
                            │                     │
                            │                     ▼
                            │              ┌──────────────┐
                            │              │Vector Store  │
                            │              │  (Chroma)    │
                            │              │Similarity    │
                            │              │  search      │
                            │              └──────┬───────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────────────────────┐
                     │    Ranked Results            │
                     │    with scores & metadata    │
                     └──────────────────────────────┘
```

---

## Component Details

### 1. Frontend Components (Next.js)

#### Pages
```
pages/
├── index.tsx              # Home (redirects to AI agent)
├── ai-agent.tsx           # Main chat interface
│   ├── Message history
│   ├── Workflow visualization
│   ├── Input form
│   └── Quick actions
├── gmail-oauth.tsx        # Gmail connection
│   ├── Auth status
│   ├── OAuth flow
│   ├── Email fetching
│   └── Setup instructions
└── analytics.tsx          # Analytics dashboard
    ├── Email stats
    ├── Sender analysis
    ├── Category charts
    └── Search metrics
```

#### Components
```
components/
├── Layout.tsx             # Main layout with navigation
├── Card.tsx               # Reusable card container
├── Button.tsx             # Styled button
├── Alert.tsx              # Success/error alerts
└── LoadingSpinner.tsx     # Loading indicator
```

#### API Client
```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
});

export default api;
```

### 2. Backend Services (FastAPI)

#### Email Loader (`load.py`)
```python
class EmailLoader:
    def load_from_file() -> List[Email]
    def load_from_gmail() -> List[Email]
    def validate_emails() -> bool
```

**Features**:
- Loads from JSON file or Gmail API
- Validates email structure
- Handles missing fields
- Supports Gmail search queries

#### Normalizer (`normalize.py`)
```python
class EmailNormalizer:
    def normalize_batch() -> List[Message]
    def extract_metadata() -> Dict
    def clean_text() -> str
```

**Features**:
- Converts raw emails to structured messages
- Extracts metadata (date, sender, subject)
- Cleans and formats text
- Handles HTML content

#### Semantic Search Engine (`semantic.py`)
```python
class SemanticSearchEngine:
    def __init__():
        self.embeddings = SentenceTransformer()
        self.vector_store = Chroma()
    
    def index_messages() -> int
    def search() -> List[SearchResult]
    def get_collection_stats() -> Dict
```

**Features**:
- Sentence Transformers embeddings
- Chroma vector database
- Cosine similarity search
- Persistent storage
- Batch processing

#### RAG Engine (`rag.py`)
```python
class RAGEngine:
    def __init__():
        self.search_engine = SemanticSearchEngine()
        self.llm = WatsonxLLM()
    
    def answer_question() -> RAGResponse
    def build_context() -> str
    def extract_citations() -> List[Citation]
```

**Features**:
- Retrieval-augmented generation
- Context building from search results
- LLM integration (watsonx)
- Citation extraction
- Fallback mode without LLM

#### Gmail OAuth Service (`gmail_oauth.py`)
```python
class GmailOAuthService:
    def get_authorization_url() -> str
    def exchange_code_for_token() -> Dict
    def load_credentials() -> bool
    def is_authenticated() -> bool
    def revoke_token() -> None
    def get_service() -> Resource
    def fetch_emails() -> List[Dict]
    def get_user_profile() -> Dict
```

**Features**:
- OAuth2 flow implementation
- Token management (save/load/refresh)
- Gmail API integration
- Email fetching with queries
- Profile information
- Label management

#### Classifier (`classify.py`)
```python
class EmailClassifier:
    def classify_batch() -> List[Classification]
    def detect_category() -> List[str]
    def assign_priority() -> str
    def analyze_sentiment() -> str
    def extract_tags() -> List[str]

class ThreadDetector:
    def detect_threads() -> Dict
    def normalize_subject() -> str
    def group_by_subject() -> Dict
```

**Features**:
- Multi-category classification
- Priority scoring
- Sentiment analysis
- Tag extraction
- Thread detection
- Participant tracking

#### Analytics Engine (`analytics.py`)
```python
class EmailAnalytics:
    def analyze_emails() -> AnalyticsResponse
    def get_top_senders() -> List[Dict]
    def get_category_distribution() -> Dict
    def get_timeline() -> List[Dict]

class SearchAnalytics:
    def track_search() -> None
    def get_search_stats() -> SearchStatsResponse
    def get_popular_queries() -> List[str]
```

**Features**:
- Email statistics
- Sender analysis
- Category distribution
- Timeline generation
- Search tracking
- Performance metrics

#### Cache Layer (`cache.py`)
```python
class CacheService:
    def __init__():
        self.redis = Redis()
    
    def get() -> Optional[Any]
    def set() -> bool
    def delete() -> bool
    def clear_pattern() -> int

@cached(prefix="search", ttl=300)
def expensive_function():
    pass
```

**Features**:
- Redis-based caching
- Decorator for easy use
- Configurable TTL
- Pattern-based clearing
- Automatic fallback

---

## Technology Stack

### Frontend Stack
```
Next.js 13
    │
    ├─ React 18 (UI Library)
    ├─ TypeScript (Type Safety)
    ├─ Tailwind CSS (Styling)
    ├─ Axios (HTTP Client)
    └─ React Hooks (State Management)
```

### Backend Stack
```
FastAPI
    │
    ├─ Pydantic (Data Validation)
    ├─ Uvicorn (ASGI Server)
    ├─ Python 3.11+
    └─ Async/Await Support
```

### AI/ML Stack
```
Sentence Transformers
    │
    ├─ all-MiniLM-L6-v2 (Embedding Model)
    ├─ PyTorch (Backend)
    └─ 384-dimensional vectors

Chroma (Vector Database)
    │
    ├─ HNSW Index (Fast Search)
    ├─ Cosine Similarity
    └─ Persistent Storage

IBM watsonx (Optional LLM)
    │
    └─ Granite Models
```

### Integration Stack
```
Google APIs
    │
    ├─ google-auth (OAuth2)
    ├─ google-api-python-client (Gmail API)
    └─ OAuth2 Flow

Redis (Optional Cache)
    │
    └─ In-memory data store
```

---

## Scalability Architecture

### Current Capacity
- **Emails**: 25 (demo) → 10,000+ (tested)
- **Chunks**: 127 (demo) → 50,000+ (tested)
- **Search Latency**: < 2 seconds
- **Concurrent Users**: 10+ (single instance)
- **Gmail Fetch**: Up to 500 emails per request

### Horizontal Scaling
```
┌─────────────────┐
│  Load Balancer  │
│   (Nginx/ALB)   │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│Backend│ │Backend│ │Backend│ │Backend│
│   1   │ │   2   │ │   3   │ │   N   │
└───┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
    │        │        │        │
    └────────┴────────┴────────┘
             │
    ┌────────▼────────┐
    │ Shared Services │
    │ • Vector Store  │
    │ • Redis Cache   │
    │ • Gmail API     │
    └─────────────────┘
```

### Vertical Scaling
- **CPU**: Faster embedding generation
- **RAM**: Larger vector indices in memory
- **GPU**: Accelerated similarity search
- **SSD**: Faster vector store I/O

### Database Scaling
```
┌─────────────────────────────────────┐
│      Vector Store Partitioning      │
├─────────────────────────────────────┤
│  Partition 1: 2026-01 emails        │
│  Partition 2: 2026-02 emails        │
│  Partition 3: 2026-03 emails        │
│  ...                                │
└─────────────────────────────────────┘
```

---

## Security Architecture

### Authentication & Authorization
```
┌─────────────────────────────────────────────────────────┐
│                   Security Layers                        │
├─────────────────────────────────────────────────────────┤
│  1. OAuth2 (Gmail)                                      │
│     • Secure token exchange                             │
│     • Automatic token refresh                           │
│     • Revocable access                                  │
│                                                          │
│  2. API Security                                        │
│     • CORS configuration                                │
│     • Request validation (Pydantic)                     │
│     • Error sanitization                                │
│                                                          │
│  3. Data Security                                       │
│     • Local processing                                  │
│     • No password storage                               │
│     • Encrypted token storage                           │
│                                                          │
│  4. Network Security                                    │
│     • HTTPS in production                               │
│     • Secure redirect URIs                              │
│     • Environment variable secrets                      │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Security
```
User ──HTTPS──▶ Frontend ──HTTPS──▶ Backend ──OAuth2──▶ Gmail API
                                        │
                                        ├─ Local Vector Store
                                        ├─ Local Dataset
                                        ├─ Redis Cache (optional)
                                        └─ watsonx API (optional)
```

---

## Deployment Architectures

### Local Development
```
Developer Machine
    │
    ├─ Frontend (npm run dev)
    │   └─ http://localhost:3000
    │
    ├─ Backend (uvicorn)
    │   └─ http://localhost:8000
    │
    └─ Optional Services
        ├─ Redis (docker)
        └─ Vector Store (local)
```

### Docker Deployment
```
Docker Host
    │
    ├─ Container: frontend
    │   └─ Next.js app
    │
    ├─ Container: backend
    │   └─ FastAPI app
    │
    └─ Container: redis (optional)
        └─ Cache service
```

### Cloud Deployment (AWS Example)
```
AWS Cloud
    │
    ├─ CloudFront (CDN)
    │   └─ Frontend static files
    │
    ├─ ECS/EKS (Containers)
    │   ├─ Backend containers
    │   └─ Auto-scaling
    │
    ├─ EFS (Shared Storage)
    │   └─ Vector store data
    │
    ├─ ElastiCache (Redis)
    │   └─ Distributed cache
    │
    ├─ ALB (Load Balancer)
    │   └─ Traffic distribution
    │
    └─ S3 (Backup)
        └─ Email dataset backup
```

---

## Monitoring & Observability

### Metrics to Track
```
Application Metrics:
├─ Request latency (p50, p95, p99)
├─ Error rates by endpoint
├─ Cache hit/miss rates
├─ Gmail API quota usage
└─ LLM token consumption

System Metrics:
├─ CPU usage
├─ Memory usage
├─ Disk I/O
└─ Network throughput

Business Metrics:
├─ Active users
├─ Searches per day
├─ Gmail connections
└─ Email processing volume
```

### Logging Strategy
```python
# Structured JSON logging
{
    "timestamp": "2026-01-31T21:00:00Z",
    "level": "INFO",
    "service": "backend",
    "endpoint": "/tool/semantic/search",
    "user_id": "user_123",
    "query": "urgent emails",
    "latency_ms": 1234,
    "results_count": 5
}
```

### Health Checks
```
GET /health
{
    "status": "healthy",
    "checks": {
        "api": "ok",
        "vector_store": "ok",
        "gmail_auth": "ok",
        "redis": "ok",
        "llm": "ok"
    }
}
```

---

## Performance Optimization

### Current Optimizations
1. **Persistent Vector Store** - No re-indexing on restart
2. **Batch Embedding Generation** - Process multiple emails at once
3. **Efficient Chunking** - 500 chars with 50 overlap
4. **HNSW Index** - Fast approximate nearest neighbor search
5. **Redis Caching** - Cache search results and RAG answers
6. **Connection Pooling** - Reuse HTTP connections

### Future Optimizations
1. **GPU Acceleration** - Faster embedding generation
2. **Query Result Caching** - Cache popular queries
3. **Async Processing** - Non-blocking operations
4. **CDN for Frontend** - Faster static asset delivery
5. **Database Indexing** - Optimize metadata queries
6. **Lazy Loading** - Load data on demand

---

## Error Handling Strategy

### Error Types
```
1. User Errors (400-level)
   ├─ Invalid input
   ├─ Missing parameters
   └─ Authentication required

2. System Errors (500-level)
   ├─ Database connection failed
   ├─ External API timeout
   └─ Out of memory

3. Business Logic Errors
   ├─ No results found
   ├─ Quota exceeded
   └─ Invalid state
```

### Error Response Format
```json
{
    "error": "Error type",
    "detail": "Human-readable message",
    "code": "ERROR_CODE",
    "timestamp": "2026-01-31T21:00:00Z"
}
```

---

## Future Architecture Enhancements

### Phase 1: Enhanced Features
- WebSocket support for real-time updates
- Incremental indexing for new emails
- Multi-language support
- Advanced query understanding

### Phase 2: Multi-Source
- Outlook integration
- Slack connector
- Teams integration
- IMAP/POP3 support

### Phase 3: Advanced AI
- Multi-modal search (images, PDFs)
- Email classification with ML
- Smart notifications
- Predictive responses

### Phase 4: Enterprise
- Multi-tenancy
- Role-based access control
- Audit logging
- Compliance features (GDPR, SOC2)

---

This architecture is designed to be:
- **Scalable**: From demo to production
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new features
- **Reliable**: Error handling and fallbacks
- **Secure**: Privacy-first design
- **Modern**: Latest technologies and best practices

---

**Built with ❤️ for IBM Dev Day Hackathon 2026**