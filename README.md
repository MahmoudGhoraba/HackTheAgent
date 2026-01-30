# HackTheAgent – Personalized Multi-Platform Email & Message Assistant

Backend implemented in FastAPI with modular agents for Gmail/Outlook ingestion, normalization, and query/summarization.

## What’s inside

- `backend/app/main.py` – FastAPI app with endpoints
- `backend/app/gmail.py` – Gmail connector (demo stub)
- `backend/app/outlook.py` – Outlook connector (demo stub)
- `backend/app/normalize.py` – Normalization into a common message schema
- `backend/app/query.py` – Orchestrated query + summarization logic
- `backend/app/models.py` – Pydantic models for message and query types

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

## Orchestration

This demo simulates orchestration by calling platform agents inside `query.py`. For hackathon judging, you can map these steps in watsonx Orchestrate:

1. Detect intent (e.g., "Show me emails about job applications from IBM").
2. Call Gmail/Outlook agents with appropriate filters.
3. Normalize with `Normalization Agent`.
4. Query/summarize with `Query Agent`.
5. Return messages + summary to the UI.

## Next steps

- Integrate real Gmail API and Microsoft Graph (Outlook) with OAuth.
- Add Slack/Messenger agents and extend normalization.
- Persist messages and preferences (PostgreSQL or MongoDB).
- Improve summarization using an LLM (or distilbart/PEGASUS) with caching.
- Add React dashboard to visualize messages, filters, and summaries.
 - Wire the Next.js frontend to the FastAPI backend (`/ingest`, `/query`) and show summaries.
