# Gmail Agent Setup and Usage Guide

This guide will help you set up and use the Gmail Agent with Watson Orchestrate.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Gmail API Setup](#gmail-api-setup)
3. [Installation](#installation)
4. [Authentication](#authentication)
5. [Usage](#usage)
6. [Watson Orchestrate Integration](#watson-orchestrate-integration)
7. [API Endpoints](#api-endpoints)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.12+
- Google Cloud Platform account
- Gmail account
- Watson Orchestrate instance

---

## Gmail API Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "HackTheAgent Gmail")
4. Click "Create"

### Step 2: Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" and click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (for testing) or Internal (for organization)
   - App name: "HackTheAgent Gmail Agent"
   - User support email: Your email
   - Developer contact: Your email
   - Add scopes: `gmail.readonly`, `gmail.send`, `gmail.modify`
   - Add test users (your Gmail account)
4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "Gmail Agent Desktop Client"
   - Click "Create"
5. Download the JSON file and save it as `credentials.json` in the `backend/` directory

### Step 4: File Structure

Your backend directory should look like this:
```
backend/
├── credentials.json          # OAuth 2.0 credentials (from Google Cloud)
├── token.json               # Auto-generated after first authentication
├── gmail_agent_openapi.yaml # OpenAPI specification
├── app/
│   ├── gmail_agent.py       # Gmail agent module
│   ├── main.py              # FastAPI endpoints
│   └── orchestrator.py      # Watson Orchestrate integration
```

---

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The required packages include:
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`
- `fastapi`
- `uvicorn`
- `pydantic`

### 2. Verify Installation

```bash
python -c "import google.auth; print('Google Auth installed successfully')"
```

---

## Authentication

### First-Time Authentication

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

2. Make any Gmail API call (e.g., list emails):
```bash
curl http://localhost:8000/gmail/list?max_results=5
```

3. A browser window will open automatically for OAuth consent
4. Sign in with your Gmail account
5. Grant the requested permissions
6. The `token.json` file will be created automatically
7. Future requests will use this token (no need to re-authenticate)

### Token Refresh

The token automatically refreshes when expired. If you encounter authentication issues:

1. Delete `token.json`
2. Restart the server
3. Re-authenticate through the browser

---

## Usage

### 1. List Emails

**Endpoint:** `GET /gmail/list`

**Parameters:**
- `max_results` (optional): Number of emails to return (default: 10)
- `page_token` (optional): Pagination token
- `query` (optional): Gmail search query

**Examples:**

```bash
# List 10 most recent emails
curl "http://localhost:8000/gmail/list?max_results=10"

# List unread emails
curl "http://localhost:8000/gmail/list?query=is:unread"

# List emails from specific sender
curl "http://localhost:8000/gmail/list?query=from:example@gmail.com"

# List emails with subject containing "meeting"
curl "http://localhost:8000/gmail/list?query=subject:meeting"
```

**Response:**
```json
{
  "success": true,
  "emails": [
    {
      "id": "18d4f2c3a1b2c3d4",
      "thread_id": "18d4f2c3a1b2c3d4",
      "subject": "Meeting Tomorrow",
      "from": "sender@example.com",
      "to": "you@gmail.com",
      "date": "Thu, 30 Jan 2026 10:30:00 +0000",
      "snippet": "Hi, let's meet tomorrow at 2 PM...",
      "labels": ["INBOX", "UNREAD"]
    }
  ],
  "next_page_token": "NEXT_PAGE_TOKEN_HERE",
  "result_size_estimate": 42
}
```

### 2. Read Email Details

**Endpoint:** `GET /gmail/read/{email_id}`

**Example:**

```bash
curl "http://localhost:8000/gmail/read/18d4f2c3a1b2c3d4"
```

**Response:**
```json
{
  "success": true,
  "email": {
    "id": "18d4f2c3a1b2c3d4",
    "subject": "Meeting Tomorrow",
    "from": "sender@example.com",
    "to": "you@gmail.com",
    "date": "Thu, 30 Jan 2026 10:30:00 +0000",
    "body": "Full email body content here...",
    "labels": ["INBOX", "UNREAD"]
  }
}
```

### 3. Send Email

**Endpoint:** `POST /gmail/send`

**Example:**

```bash
curl -X POST "http://localhost:8000/gmail/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "This is a test email from Gmail Agent",
    "cc": "cc@example.com",
    "html": false
  }'
```

**Response:**
```json
{
  "success": true,
  "message_id": "18d4f2c3a1b2c3d5",
  "thread_id": "18d4f2c3a1b2c3d5"
}
```

### 4. Search Emails

**Endpoint:** `POST /gmail/search`

**Example:**

```bash
curl -X POST "http://localhost:8000/gmail/search" \
  -H "Content-Type: application/json" \
  -d '{
    "from_email": "boss@company.com",
    "subject": "urgent",
    "is_unread": true,
    "after_date": "2026/01/01",
    "max_results": 20
  }'
```

**Response:**
```json
{
  "success": true,
  "emails": [...],
  "next_page_token": null,
  "result_size_estimate": 5
}
```

---

## Watson Orchestrate Integration

### Register Gmail Agent

**Endpoint:** `POST /gmail/register`

This endpoint registers the Gmail agent with your Watson Orchestrate instance.

```bash
curl -X POST "http://localhost:8000/gmail/register"
```

**What it does:**
1. Authenticates with Watson Orchestrate using your API key
2. Registers the Gmail agent with 4 tools:
   - `list_emails`
   - `read_email_details`
   - `send_email`
   - `search_emails`
3. Makes the agent available in your Watson Orchestrate workflows

### Using in Watson Orchestrate Workflows

Once registered, you can use the Gmail agent in your workflows:

1. **Create a new workflow** in Watson Orchestrate
2. **Add the Gmail Agent** from the available agents
3. **Configure actions:**
   - List recent emails
   - Read specific email
   - Send email
   - Search with filters

**Example Workflow:**
```
1. User: "Show me unread emails from my boss"
2. Watson Orchestrate → Gmail Agent: search_emails
   - from_email: "boss@company.com"
   - is_unread: true
3. Gmail Agent → Returns: List of matching emails
4. Watson Orchestrate → User: Displays results
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gmail/list` | List emails with pagination |
| GET | `/gmail/read/{email_id}` | Read full email details |
| POST | `/gmail/send` | Send a new email |
| POST | `/gmail/search` | Search emails with filters |
| POST | `/gmail/register` | Register agent with Watson Orchestrate |

---

## Troubleshooting

### Issue: "credentials.json not found"

**Solution:** Download OAuth 2.0 credentials from Google Cloud Console and save as `credentials.json` in the `backend/` directory.

### Issue: "Token has been expired or revoked"

**Solution:**
```bash
rm token.json
# Restart server and re-authenticate
```

### Issue: "Access blocked: This app's request is invalid"

**Solution:** 
1. Go to Google Cloud Console → OAuth consent screen
2. Add your Gmail account as a test user
3. Ensure all required scopes are added

### Issue: "Insufficient permissions"

**Solution:** 
1. Delete `token.json`
2. Re-authenticate with all required scopes:
   - `gmail.readonly`
   - `gmail.send`
   - `gmail.modify`

### Issue: "Rate limit exceeded"

**Solution:** Gmail API has quotas. Wait a few minutes or request quota increase in Google Cloud Console.

### Issue: Watson Orchestrate registration fails

**Solution:**
1. Verify your Watson Orchestrate credentials in `backend/app/config.py`
2. Check that `INSTANCE_URL` and `API_KEY` are correct
3. Ensure your Watson Orchestrate instance supports custom agents

---

## Gmail Search Query Syntax

The `query` parameter supports Gmail's search operators:

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:john@example.com` | Emails from specific sender |
| `to:` | `to:jane@example.com` | Emails to specific recipient |
| `subject:` | `subject:meeting` | Emails with subject containing word |
| `is:unread` | `is:unread` | Unread emails only |
| `is:read` | `is:read` | Read emails only |
| `has:attachment` | `has:attachment` | Emails with attachments |
| `after:` | `after:2026/01/01` | Emails after date |
| `before:` | `before:2026/12/31` | Emails before date |
| `newer_than:` | `newer_than:7d` | Emails newer than 7 days |
| `older_than:` | `older_than:1m` | Emails older than 1 month |
| `label:` | `label:important` | Emails with specific label |

**Combine operators:**
```
from:boss@company.com subject:urgent is:unread
```

---

## Security Best Practices

1. **Never commit credentials:**
   - Add `credentials.json` and `token.json` to `.gitignore`
   
2. **Use environment variables:**
   - Store sensitive data in `.env` file
   - Use `python-dotenv` to load them

3. **Limit OAuth scopes:**
   - Only request necessary permissions
   - Review scopes regularly

4. **Rotate credentials:**
   - Regenerate OAuth credentials periodically
   - Revoke old tokens

5. **Monitor API usage:**
   - Check Google Cloud Console for unusual activity
   - Set up billing alerts

---

## Next Steps

1. ✅ Set up Gmail API credentials
2. ✅ Install dependencies
3. ✅ Authenticate with Gmail
4. ✅ Test all endpoints
5. ✅ Register with Watson Orchestrate
6. 🚀 Build workflows in Watson Orchestrate
7. 🚀 Integrate with your frontend application

---

## Support

For issues or questions:
- Check the [Gmail API documentation](https://developers.google.com/gmail/api)
- Review [Watson Orchestrate docs](https://www.ibm.com/docs/en/watson-orchestrate)
- Open an issue in the project repository

---

**Happy coding! 🚀**