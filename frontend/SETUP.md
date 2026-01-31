# Frontend Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Backend (Required)
The frontend needs the backend API running:
```bash
cd ../backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

Backend will run on: http://localhost:8000

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:3000

## Pages Overview

### 🔍 Search (/)
- **URL**: http://localhost:3000/
- **Features**:
  - Semantic email search
  - Adjustable result count (top_k)
  - Example queries
  - Relevance scores
  - Real-time search

### 🤖 Ask AI (/rag)
- **URL**: http://localhost:3000/rag
- **Features**:
  - RAG-powered Q&A
  - AI-generated answers
  - Source citations
  - Context control
  - No hallucinations

### 📧 Manage (/manage)
- **URL**: http://localhost:3000/manage
- **Features**:
  - Load emails from dataset
  - Normalize email structure
  - Index for semantic search
  - Step-by-step workflow
  - Progress tracking

### 📊 Stats (/stats)
- **URL**: http://localhost:3000/stats
- **Features**:
  - System health check
  - Vector DB statistics
  - Configuration details
  - Performance metrics
  - Quick actions

## Testing the Integration

### Step 1: Initialize the System
1. Go to http://localhost:3000/manage
2. Click "Load Emails from Dataset"
3. Click "Normalize X Emails"
4. Click "Index X Messages"
5. Wait for completion

### Step 2: Test Search
1. Go to http://localhost:3000/
2. Try example queries:
   - "urgent deadlines"
   - "IBM hackathon"
   - "invoice payment"
3. Verify results appear with scores

### Step 3: Test RAG
1. Go to http://localhost:3000/rag
2. Ask questions:
   - "What is the IBM Dev Day hackathon about?"
   - "What are the urgent deadlines?"
3. Verify answer and citations appear

### Step 4: Check Stats
1. Go to http://localhost:3000/stats
2. Verify:
   - System shows "Healthy"
   - Total chunks > 0
   - Configuration is correct

## Troubleshooting

### Backend Not Running
**Error**: "Failed to perform search. Make sure the backend is running."

**Solution**:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

### CORS Issues
**Error**: CORS policy blocking requests

**Solution**: Backend is configured to allow all origins. Check backend/.env:
```
CORS_ORIGINS=["*"]
```

### Port Already in Use
**Error**: Port 3000 already in use

**Solution**:
```bash
# Use different port
npm run dev -- -p 3001
```

### TypeScript Errors
**Error**: Module not found or type errors

**Solution**:
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Environment Variables

Create `.env.local` for custom configuration:

```env
# API URL (default: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Or for production
# NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Build for Production

```bash
# Build
npm run build

# Start production server
npm start
```

## Features Checklist

- ✅ Semantic search with scores
- ✅ RAG Q&A with citations
- ✅ Email management workflow
- ✅ System statistics dashboard
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling
- ✅ Success notifications
- ✅ Example queries/questions
- ✅ Navigation between pages
- ✅ API integration
- ✅ TypeScript support
- ✅ Tailwind CSS styling

## Tech Stack

- **Framework**: Next.js 13.5 (Pages Router)
- **Language**: TypeScript 5.2
- **Styling**: Tailwind CSS 3.3
- **HTTP Client**: Axios 1.6
- **UI Components**: Custom React components

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx      # Main layout with navigation
│   │   ├── Card.tsx        # Card component
│   │   ├── Button.tsx      # Button with variants
│   │   ├── LoadingSpinner.tsx
│   │   └── Alert.tsx       # Alert notifications
│   ├── lib/
│   │   └── api.ts          # API client with all endpoints
│   ├── pages/
│   │   ├── _app.tsx        # App wrapper
│   │   ├── _document.tsx   # HTML document
│   │   ├── index.tsx       # Search page
│   │   ├── rag.tsx         # RAG Q&A page
│   │   ├── manage.tsx      # Email management
│   │   └── stats.tsx       # Statistics page
│   └── styles/
│       └── globals.css     # Global styles + Tailwind
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## API Endpoints Used

All endpoints are defined in `src/lib/api.ts`:

- `GET /tool/emails/load` - Load emails
- `POST /tool/emails/normalize` - Normalize emails
- `POST /tool/semantic/index` - Index messages
- `POST /tool/semantic/search` - Semantic search
- `POST /tool/rag/answer` - RAG Q&A
- `GET /stats` - System statistics
- `GET /health` - Health check

## Development Tips

1. **Hot Reload**: Changes auto-reload in dev mode
2. **TypeScript**: Use types from `src/lib/api.ts`
3. **Components**: Reuse components from `src/components/`
4. **Styling**: Use Tailwind utility classes
5. **API Calls**: Use functions from `src/lib/api.ts`

## Support

- **Backend API Docs**: http://localhost:8000/docs
- **Frontend Dev Server**: http://localhost:3000
- **Issues**: Check browser console and terminal logs