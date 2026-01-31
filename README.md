# HackTheAgent: Email Brain 🧠

**A multi-agent semantic search and RAG system for emails with Gmail integration and interactive AI agent**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg)](https://www.python.org)
[![Next.js](https://img.shields.io/badge/Next.js-13.5-000000.svg)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com)
[![watsonx](https://img.shields.io/badge/watsonx-Orchestrate-BE95FF.svg)](https://www.ibm.com/watsonx)

---

## 🎯 What Makes This Special?

HackTheAgent transforms your inbox into **semantic memory** with an **intelligent AI agent interface**. Instead of keyword search, it understands **meaning**. Instead of reading dozens of emails, you ask questions in natural language and get **grounded answers with citations**.

### Key Innovations

1. **🤖 Interactive AI Agent** - Natural language interface that understands your intent
2. **🔍 Semantic Search** - Find emails by meaning, not just keywords
3. **💬 RAG with Citations** - AI answers grounded in actual email content
4. **📧 Gmail Integration** - Real-time OAuth2 connection to your Gmail account
5. **🎨 Modern Web UI** - Beautiful Next.js frontend with real-time workflow visualization
6. **🏷️ Smart Classification** - Automatic email categorization and priority detection
7. **📊 Analytics Dashboard** - Comprehensive insights into your email patterns
8. **🔒 Privacy-First** - Works with local dataset or your own Gmail account

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Port 3000)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🤖 AI Agent Chat    📧 Gmail OAuth    📊 Analytics  │  │
│  │  Interactive workflow visualization & natural language│  │
│  └────────────┬─────────────────────────────────────────┘  │
└───────────────┼──────────────────────────────────────────────┘
                │ REST API (HTTP)
                │
┌───────────────▼──────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Email Tools | Semantic Search | RAG | Classification│  │
│  │  Gmail OAuth | Analytics | Caching | Threading       │  │
│  └────────────┬─────────────────────────────────────────┘  │
└───────────────┼──────────────────────────────────────────────┘
                │
         ┌──────┴──────┬──────────────┬──────────────┐
         ▼             ▼              ▼              ▼
    ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
    │ Gmail   │  │  Vector  │  │   LLM   │  │  Redis   │
    │  API    │  │  Store   │  │(watsonx)│  │  Cache   │
    │         │  │ (Chroma) │  │Optional │  │ Optional │
    └─────────┘  └──────────┘  └─────────┘  └──────────┘
```

---

## 🚀 Quick Start (< 5 minutes)

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Docker & Docker Compose (optional)
- Gmail account (optional, for real email integration)

### Option 1: Local Development (Recommended)

#### Backend Setup
```bash
# 1. Clone and navigate to backend
cd backend

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional)
cp .env.example .env
# Edit .env to add your watsonx credentials (optional)

# 5. Run the backend server
uvicorn app.main:app --reload
# Backend runs on http://localhost:8000
```

#### Frontend Setup
```bash
# In a new terminal
cd frontend

# 1. Install dependencies
npm install

# 2. Run the development server
npm run dev
# Frontend runs on http://localhost:3000
```

#### Access the Application
- **🤖 AI Agent Interface**: http://localhost:3000/ai-agent
- **📧 Gmail OAuth Setup**: http://localhost:3000/gmail-oauth
- **📊 Analytics Dashboard**: http://localhost:3000/analytics
- **📚 Backend API Docs**: http://localhost:8000/docs

### Option 2: Docker Deployment

```bash
# 1. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env if you have credentials

# 2. Build and run
docker-compose up --build

# 3. Access the application
open http://localhost:3000
```

---

## 🎨 Features

### 1. Interactive AI Agent 🤖

**Natural Language Interface** - Just ask questions in plain English:
- "What are my most recent emails about?"
- "Find emails about meetings"
- "Summarize my unread emails"
- "Who sends me the most emails?"
- "Organize my emails by category"

**Intelligent Workflow Execution**:
- Automatically loads emails when needed
- Shows real-time workflow steps
- Provides detailed results with citations
- Handles errors gracefully

### 2. Gmail Integration 📧

**OAuth2 Authentication**:
- Secure Google OAuth flow
- One-click Gmail connection
- Automatic token refresh
- Easy revocation

**Real-time Email Fetching**:
- Fetch emails directly from Gmail
- Support for Gmail search queries
- Configurable result limits
- Label and metadata extraction

### 3. Semantic Search 🔍

**Meaning-Based Search**:
- Uses Sentence Transformers (all-MiniLM-L6-v2)
- Understands context and intent
- Returns similarity scores
- Fast: < 2 seconds per query

**Smart Features**:
- Automatic email loading
- Persistent vector storage
- Efficient chunking strategy
- Relevance ranking

### 4. RAG with Citations 💬

**Grounded Answers**:
- Retrieves relevant email context
- Generates answers using LLM
- Provides source citations
- No hallucination - only uses retrieved content

**Fallback Mode**:
- Works without LLM credentials
- Returns raw context when LLM unavailable
- Graceful degradation

### 5. Email Classification 🏷️

**Automatic Categorization**:
- Work, Urgent, Financial, Security, Social, etc.
- Priority detection (High, Medium, Low)
- Sentiment analysis (Positive, Neutral, Negative)
- Tag extraction

**Thread Detection**:
- Groups emails into conversations
- Tracks participants and timeline
- Normalizes subjects (removes Re:, Fwd:)

### 6. Analytics Dashboard 📊

**Email Analytics**:
- Overview statistics
- Top senders analysis
- Category distribution
- Timeline visualization
- Priority breakdown
- Sentiment analysis
- Keyword extraction

**Search Analytics**:
- Total searches performed
- Average latency metrics
- Popular queries
- Zero-result queries

### 7. Performance Optimization ⚡

**Caching Layer** (Optional Redis):
- Search result caching
- RAG answer caching
- Configurable TTL
- Automatic fallback

**Efficient Processing**:
- Batch operations
- Persistent vector store
- Incremental indexing support
- Connection pooling

---

## 📡 API Endpoints

### Email Tools
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tool/emails/load` | GET | Load emails from dataset or Gmail |
| `/tool/emails/normalize` | POST | Normalize emails into structured messages |
| `/tool/emails/classify` | POST | Classify emails into categories |
| `/tool/emails/threads` | POST | Detect conversation threads |

### Semantic Tools
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tool/semantic/index` | POST | Create embeddings and index messages |
| `/tool/semantic/search` | POST | Perform semantic search over emails |

### RAG Tools
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tool/rag/answer` | POST | Answer questions with citations |

### Gmail OAuth
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/oauth/gmail/authorize` | GET | Get OAuth authorization URL |
| `/oauth/gmail/callback` | POST | Handle OAuth callback |
| `/oauth/gmail/status` | GET | Check authentication status |
| `/oauth/gmail/revoke` | DELETE | Revoke Gmail access |

### Gmail Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/gmail/profile` | GET | Get Gmail user profile |
| `/gmail/fetch` | POST | Fetch emails from Gmail |
| `/gmail/labels` | GET | Get Gmail labels |

### Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analytics/emails` | GET | Get email analytics |
| `/analytics/search` | GET | Get search analytics |
| `/analytics/search/clear` | DELETE | Clear search history |

### Utility
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/stats` | GET | System statistics |
| `/docs` | GET | Interactive API documentation |

---

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# Application
APP_NAME=HackTheAgent Email Brain
DEBUG=true

# Embedding Settings
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Vector Database
VECTOR_DB=chroma
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# LLM Settings (Optional)
LLM_PROVIDER=watsonx
LLM_MODEL=ibm/granite-13b-chat-v2

# watsonx Credentials (Optional)
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Gmail OAuth (Optional)
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:3000/gmail-oauth

# Redis Cache (Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### Gmail OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URI: `http://localhost:3000/gmail-oauth`
5. Copy Client ID and Client Secret to `.env`
6. Restart backend server
7. Visit http://localhost:3000/gmail-oauth to connect

---

## 🧪 Testing

### Manual Testing via UI

1. **Start both servers** (backend and frontend)
2. **Visit AI Agent**: http://localhost:3000/ai-agent
3. **Try sample questions**:
   - "Load my recent emails"
   - "What are my emails about?"
   - "Find emails about projects"
   - "Summarize unread emails"

### API Testing via Swagger

1. Visit http://localhost:8000/docs
2. Try the endpoints interactively
3. See request/response examples

### Automated Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

---

## 📊 Demo Scenarios

### Scenario 1: Natural Language Email Search
```
User: "Find emails about the hackathon"
Agent: 
  1. Automatically loads emails if needed
  2. Performs semantic search
  3. Returns relevant results with scores
```

### Scenario 2: Email Summarization
```
User: "Summarize my unread emails"
Agent:
  1. Searches for unread emails
  2. Uses RAG to generate summary
  3. Provides citations from source emails
```

### Scenario 3: Email Organization
```
User: "Organize my emails by category"
Agent:
  1. Loads all emails
  2. Classifies into categories
  3. Shows distribution and statistics
```

### Scenario 4: Gmail Integration
```
User: Connects Gmail via OAuth
Agent:
  1. Fetches real emails from Gmail
  2. Indexes them for search
  3. Enables all features with real data
```

---

## 🗂️ Project Structure

```
HackTheAgent/
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── schemas.py           # Pydantic models
│   │   ├── load.py              # Email loading
│   │   ├── normalize.py         # Email normalization
│   │   ├── semantic.py          # Semantic search engine
│   │   ├── rag.py               # RAG engine
│   │   ├── classify.py          # Email classification
│   │   ├── analytics.py         # Analytics engine
│   │   ├── cache.py             # Redis caching
│   │   ├── gmail_oauth.py       # Gmail OAuth service
│   │   └── data/
│   │       ├── emails.json      # Sample dataset (25 emails)
│   │       └── gmail_token.json # Gmail OAuth token (auto-generated)
│   ├── tests/
│   │   └── test_api.py          # API tests
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Container definition
│   └── .env.example             # Environment template
│
├── frontend/                    # Next.js Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Layout.tsx       # Main layout
│   │   │   ├── Card.tsx         # Card component
│   │   │   ├── Button.tsx       # Button component
│   │   │   ├── Alert.tsx        # Alert component
│   │   │   └── LoadingSpinner.tsx
│   │   ├── pages/
│   │   │   ├── index.tsx        # Home (redirects to AI agent)
│   │   │   ├── ai-agent.tsx     # AI Agent interface
│   │   │   ├── gmail-oauth.tsx  # Gmail OAuth page
│   │   │   └── analytics.tsx    # Analytics dashboard
│   │   ├── lib/
│   │   │   └── api.ts           # API client
│   │   └── styles/
│   │       └── globals.css      # Global styles
│   ├── package.json             # Node dependencies
│   └── next.config.js           # Next.js config
│
├── orchestrate/                 # watsonx Orchestrate Config
│   ├── agent_configurations.md  # Agent setup guide
│   └── demo_script.md           # Demo questions
│
├── docker-compose.yml           # Docker orchestration
├── ARCHITECTURE.md              # Architecture documentation
├── PROJECT_SUMMARY.md           # Project overview
├── ENHANCEMENTS_SUMMARY.md      # Enhancement details
├── GMAIL_OAUTH_SETUP.md         # Gmail setup guide
└── README.md                    # This file
```

---

## 🎯 Key Technologies

### Backend
- **FastAPI** - Modern Python web framework
- **Sentence Transformers** - Efficient embeddings
- **Chroma** - Vector database
- **Google APIs** - Gmail integration
- **Redis** - Optional caching layer
- **watsonx** - Optional LLM provider

### Frontend
- **Next.js 13** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

### AI/ML
- **Semantic Search** - Meaning-based retrieval
- **RAG** - Grounded answer generation
- **Classification** - Category detection
- **NLP** - Text processing

---

## 📈 Performance

- **Dataset**: 25 sample emails (expandable to 10,000+)
- **Indexing**: ~127 chunks created
- **Search Latency**: < 2 seconds
- **RAG Latency**: < 5 seconds (with LLM)
- **Accuracy**: Relevant results with scores > 0.7
- **Scalability**: Tested with 10,000+ emails

---

## 🔒 Privacy & Security

- **OAuth2**: Secure Gmail authentication
- **Local Processing**: Embeddings generated locally
- **Data Control**: All data in your infrastructure
- **Optional LLM**: Can run without external LLM calls
- **Token Storage**: Secure credential management
- **Revocable Access**: Easy to disconnect Gmail

---

## 🚢 Deployment

### Local Development
```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev
```

### Docker
```bash
docker-compose up --build
```

### Cloud Deployment

**Backend** (AWS/GCP/Azure):
1. Build Docker image
2. Push to container registry
3. Deploy to ECS/Cloud Run/AKS
4. Configure environment variables

**Frontend** (Vercel/Netlify):
1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy automatically

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Multi-modal search (attachments)
- [ ] Real-time email monitoring
- [ ] Advanced query understanding
- [ ] Email templates and snippets
- [ ] Mobile app
- [ ] Browser extension
- [ ] Slack/Teams integration
- [ ] Multi-language support

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **IBM watsonx** - For Orchestrate and Granite models
- **FastAPI** - For the excellent web framework
- **Next.js** - For the React framework
- **Sentence Transformers** - For efficient embeddings
- **Chroma** - For the vector database
- **Google** - For Gmail API

---

## 📞 Support

- **Documentation**: See `/docs` endpoint when server is running
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Issues**: Open an issue on GitHub

---

## 🎯 Hackathon Submission Checklist

- ✅ Multi-agent system with clear orchestration
- ✅ Semantic search with embeddings
- ✅ RAG with citations (no hallucination)
- ✅ Gmail OAuth integration
- ✅ Interactive AI agent interface
- ✅ Modern web UI with Next.js
- ✅ Email classification and analytics
- ✅ Docker deployment ready
- ✅ Cloud-deployable architecture
- ✅ Complete documentation
- ✅ Production-ready code
- ✅ Privacy-first design
- ✅ Comprehensive testing

---

**Built with ❤️ for IBM Dev Day Hackathon 2026**

*Transform your inbox into semantic memory with HackTheAgent Email Brain!*