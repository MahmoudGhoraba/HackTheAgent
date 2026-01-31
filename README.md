# HackTheAgent – Personalized Multi-Platform Email & Message Assistant

Backend implemented in FastAPI with modular agents for Gmail/Outlook ingestion, normalization, and query/summarization.

## What's inside

- `backend/app/main.py` – FastAPI app with endpoints
- `backend/app/gmail_agent.py` – **Gmail Agent with 4 tools (list, read, send, search)**
- `backend/app/orchestrator.py` – Watson Orchestrate integration
- `backend/app/config.py` – Configuration for Watson Orchestrate
- `backend/gmail_agent_openapi.yaml` – OpenAPI specification for Gmail agent
- `backend/GMAIL_AGENT_SETUP.md` – **Complete setup guide for Gmail agent**

## Run locally

### Backend (FastAPI)

Requires Python 3.12 and the workspace virtual environment (already set up). Start the API:

```bash
# Start API (port 8000)
/Users/ghorabas/Hackathon/HackTheAgent/.venv/bin/python -m uvicorn backend.app.main:app --port 8000
```

Open http://127.0.0.1:8000/docs for interactive Swagger UI.

### Frontend (Next.js + NextAuth + Tailwind)

The frontend lives in `frontend/` and uses Next.js 13 (pages router) for easier Tailwind integration.

1. Copy `.env.example` to `.env.local` and fill in the OAuth secrets:

```bash
cp frontend/.env.example frontend/.env.local
```

2. Install dependencies and run dev server:

```bash
cd frontend
npm install
npm run dev
```

Navigate to http://localhost:3000 and use the login page to sign in with Google or Microsoft.

## Endpoints

- `GET /` – Health check
- `GET /ingest` – Fetch Gmail + Outlook, normalize, and return messages
- `POST /query` – Filter + summarize

### Query payload

```json
{
  "keywords": ["IBM", "internship"],
  "sender": "ibm.com",
  "platform": ["gmail", "outlook"],
  "since": "2026-01-30T00:00:00Z",
  "until": "2026-01-31T00:00:00Z",
  "summarize": true,
  "limit": 50
}
```

Notes:
- `keywords`: any match in subject/body (case-insensitive)
- `sender`: substring match (e.g., `ibm.com`)
- `platform`: a subset of platforms to include
- `since`/`until`: ISO timestamps
- `summarize`: return a compact aggregate summary

## Gmail Agent

A fully functional Gmail agent with Watson Orchestrate integration is now available!

### Features

✅ **4 Core Tools:**
- `list_emails` - List emails with pagination and filtering
- `read_email_details` - Get full email content by ID
- `send_email` - Send emails with cc/bcc support
- `search_emails` - Advanced search with multiple filters

✅ **Watson Orchestrate Integration:**
- Register agent via `/gmail/register` endpoint
- Use in workflows and automation
- OpenAPI specification included

✅ **Complete Documentation:**
- See `backend/GMAIL_AGENT_SETUP.md` for detailed setup instructions
- Includes Gmail API setup, authentication, and usage examples

### Quick Start

1. **Set up Gmail API credentials** (see `GMAIL_AGENT_SETUP.md`)
2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Start the server:**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
4. **Test the agent:**
   ```bash
   curl "http://localhost:8000/gmail/list?max_results=5"
   ```
5. **Register with Watson Orchestrate:**
   ```bash
   curl -X POST "http://localhost:8000/gmail/register"
   ```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gmail/list` | List emails with pagination |
| GET | `/gmail/read/{email_id}` | Read full email details |
| POST | `/gmail/send` | Send a new email |
| POST | `/gmail/search` | Search emails with filters |
| POST | `/gmail/register` | Register with Watson Orchestrate |

### OpenAPI Specification

The complete OpenAPI spec is available at `backend/gmail_agent_openapi.yaml` for Watson Orchestrate integration.

## Orchestration

The Gmail agent integrates seamlessly with Watson Orchestrate:

1. **Detect intent** (e.g., "Show me unread emails from my boss")
2. **Call Gmail Agent** with appropriate filters
3. **Process results** with Watson Orchestrate workflows
4. **Return formatted response** to the user

Example workflow:
```
User → Watson Orchestrate → Gmail Agent → Gmail API → Results → User
```

## Next steps

- Integrate real Gmail API and Microsoft Graph (Outlook) with OAuth.
- Add Slack/Messenger agents and extend normalization.
- Persist messages and preferences (PostgreSQL or MongoDB).
- Improve summarization using an LLM (or distilbart/PEGASUS) with caching.
- Add React dashboard to visualize messages, filters, and summaries.
 - Wire the Next.js frontend to the FastAPI backend (`/ingest`, `/query`) and show summaries.
