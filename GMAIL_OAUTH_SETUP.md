# Gmail OAuth Integration Setup Guide

This guide will walk you through setting up Gmail OAuth integration for the HackTheAgent Email Brain application.

## Overview

The Gmail OAuth integration allows you to:
- Connect your Gmail account securely using OAuth 2.0
- Fetch emails directly from your Gmail account
- Search and filter emails using Gmail's query syntax
- Analyze emails using the Email Brain's AI capabilities

## Prerequisites

- A Google account with Gmail
- Access to Google Cloud Console
- Backend and frontend servers running locally

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "HackTheAgent Email Brain")
5. Click "Create"

## Step 2: Enable Gmail API

1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required information:
   - **App name**: HackTheAgent Email Brain
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Add the following scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/userinfo.email`
8. Click "Update" and then "Save and Continue"
9. On the "Test users" page, add your Gmail address as a test user
10. Click "Save and Continue"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application" as the application type
4. Enter a name (e.g., "HackTheAgent Web Client")
5. Under "Authorized redirect URIs", click "Add URI"
6. Add the following URI:
   ```
   http://localhost:3000/gmail-oauth
   ```
7. Click "Create"
8. A dialog will appear with your Client ID and Client Secret
9. **Important**: Copy both values - you'll need them in the next step

## Step 5: Configure Backend Environment

1. Navigate to the `backend` directory
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and add your Gmail OAuth credentials:
   ```env
   GMAIL_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=your_client_secret_here
   GMAIL_REDIRECT_URI=http://localhost:3000/gmail-oauth
   ```
4. Save the file

## Step 6: Install Dependencies

If you haven't already installed the dependencies, run:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Step 7: Start the Servers

1. Start the backend server:
   ```bash
   cd backend
   python -m app.main
   # Or use the run script
   ./run.sh
   ```

2. Start the frontend server (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

## Step 8: Connect Your Gmail Account

1. Open your browser and go to: http://localhost:3000/gmail-oauth
2. Click "Connect Gmail Account"
3. You'll be redirected to Google's OAuth consent screen
4. Sign in with your Google account
5. Review the permissions requested
6. Click "Allow" to grant access
7. You'll be redirected back to the application
8. Your Gmail account is now connected!

## Using the Gmail Integration

### Check Authentication Status

The Gmail OAuth page shows your authentication status and account information.

### Fetch Emails

1. Set the number of emails to fetch (1-500)
2. Optionally add a search query using Gmail's query syntax:
   - `is:unread` - Unread emails
   - `from:example@gmail.com` - Emails from specific sender
   - `subject:meeting` - Emails with "meeting" in subject
   - `after:2024/01/01` - Emails after a specific date
   - `has:attachment` - Emails with attachments
3. Click "Fetch Emails"

### API Endpoints

The following API endpoints are available:

#### Get Authorization URL
```http
GET /oauth/gmail/authorize?state=optional_state
```

#### Handle OAuth Callback
```http
POST /oauth/gmail/callback
Content-Type: application/json

{
  "code": "authorization_code",
  "state": "optional_state"
}
```

#### Check Authentication Status
```http
GET /oauth/gmail/status
```

#### Get User Profile
```http
GET /gmail/profile
```

#### Fetch Emails
```http
POST /gmail/fetch
Content-Type: application/json

{
  "max_results": 100,
  "query": "is:unread"
}
```

#### Get Labels
```http
GET /gmail/labels
```

#### Revoke Access
```http
DELETE /oauth/gmail/revoke
```

## Gmail Query Syntax Examples

Here are some useful Gmail query examples:

- `is:unread` - Unread messages
- `is:starred` - Starred messages
- `from:john@example.com` - From specific sender
- `to:me` - Sent to you
- `subject:invoice` - Subject contains "invoice"
- `has:attachment` - Has attachments
- `filename:pdf` - Has PDF attachments
- `after:2024/01/01` - After specific date
- `before:2024/12/31` - Before specific date
- `newer_than:7d` - Newer than 7 days
- `older_than:1m` - Older than 1 month
- `label:important` - Has "important" label
- `category:social` - In social category

You can combine queries with AND/OR:
- `from:john@example.com subject:meeting` - From John with "meeting" in subject
- `is:unread OR is:starred` - Unread or starred

## Security Notes

1. **Client Secret**: Keep your `GMAIL_CLIENT_SECRET` secure and never commit it to version control
2. **Token Storage**: OAuth tokens are stored locally in `backend/app/data/gmail_token.json`
3. **Scopes**: The application requests minimal necessary scopes:
   - `gmail.readonly` - Read emails
   - `gmail.modify` - Modify labels (for marking as read, etc.)
   - `userinfo.email` - Get user's email address
4. **Revoke Access**: You can revoke access anytime from the Gmail OAuth page or from your [Google Account settings](https://myaccount.google.com/permissions)

## Troubleshooting

### "OAuth credentials not configured" Error

Make sure you've added `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` to your `.env` file and restarted the backend server.

### "Redirect URI mismatch" Error

Ensure the redirect URI in your Google Cloud Console matches exactly:
```
http://localhost:3000/gmail-oauth
```

### "Access blocked: This app's request is invalid" Error

Make sure you've:
1. Enabled the Gmail API in Google Cloud Console
2. Configured the OAuth consent screen
3. Added yourself as a test user (for external apps)

### Token Expired

If your token expires, the application will automatically refresh it. If refresh fails, you'll need to re-authenticate.

### Rate Limits

Gmail API has rate limits:
- 250 quota units per user per second
- 1 billion quota units per day

Fetching a message costs 5 quota units, so you can fetch ~50 messages per second.

## Integration with Email Brain

Once you've fetched emails from Gmail, you can:

1. **Normalize** them for processing
2. **Index** them for semantic search
3. **Search** using natural language queries
4. **Classify** them into categories
5. **Analyze** with RAG (Retrieval-Augmented Generation)

Example workflow:
1. Fetch emails from Gmail
2. Go to the main page and load the fetched emails
3. Normalize and index them
4. Use semantic search or RAG to query your emails

## Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail Search Operators](https://support.google.com/mail/answer/7190)

## Support

If you encounter issues:
1. Check the browser console for errors
2. Check the backend logs
3. Verify your OAuth credentials are correct
4. Ensure all required scopes are enabled
5. Try revoking and re-authenticating

For more help, refer to the main project documentation or create an issue on GitHub.