"""
Gmail OAuth2 Authentication and Email Fetching Service
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings

logger = logging.getLogger(__name__)


class GmailOAuthService:
    """Service for Gmail OAuth2 authentication and email operations"""
    
    def __init__(self):
        self.token_file = settings.data_dir / settings.gmail_token_file
        self.credentials: Optional[Credentials] = None
        self.service = None
        
    def _get_client_config(self) -> Dict[str, Any]:
        """Get client configuration dictionary"""
        return {
            "web": {
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.gmail_redirect_uri]
            }
        }
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate OAuth2 authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL for user to visit
        """
        if not settings.gmail_client_id or not settings.gmail_client_secret:
            raise ValueError("Gmail OAuth credentials not configured. Set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET")
        
        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=settings.gmail_scopes,
            redirect_uri=settings.gmail_redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='false',
            state=state,
            prompt='consent'
        )
        
        logger.info(f"Generated authorization URL with scopes: {settings.gmail_scopes}")
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Token information dictionary
        """
        if not settings.gmail_client_id or not settings.gmail_client_secret:
            raise ValueError("Gmail OAuth credentials not configured")
        
        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=settings.gmail_scopes,
            redirect_uri=settings.gmail_redirect_uri
        )
        
        logger.info(f"Exchanging code for token with scopes: {settings.gmail_scopes}")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save credentials
        self._save_credentials(credentials)
        self.credentials = credentials
        
        logger.info("Successfully exchanged code for token")
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def _save_credentials(self, credentials: Credentials):
        """Save credentials to file"""
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)
        
        logger.info(f"Saved credentials to {self.token_file}")
    
    def load_credentials(self) -> bool:
        """
        Load credentials from file
        
        Returns:
            True if credentials loaded successfully, False otherwise
        """
        if not self.token_file.exists():
            logger.warning(f"Token file not found: {self.token_file}")
            return False
        
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            # Convert expiry string back to datetime if present
            if token_data.get('expiry'):
                from datetime import datetime
                token_data['expiry'] = datetime.fromisoformat(token_data['expiry'])
            
            self.credentials = Credentials(**token_data)
            
            # Refresh if expired
            if self.credentials.expired and self.credentials.refresh_token:
                logger.info("Token expired, refreshing...")
                self.credentials.refresh(Request())
                self._save_credentials(self.credentials)
            
            logger.info("Successfully loaded credentials")
            return True
            
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if not self.credentials:
            return self.load_credentials()
        
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self._save_credentials(self.credentials)
                return True
            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}")
                return False
        
        return self.credentials.valid
    
    def revoke_token(self):
        """Revoke the current token and delete credentials file"""
        if self.credentials:
            try:
                self.credentials.revoke(Request())
                logger.info("Token revoked successfully")
            except Exception as e:
                logger.error(f"Error revoking token: {str(e)}")
        
        if self.token_file.exists():
            self.token_file.unlink()
            logger.info("Credentials file deleted")
        
        self.credentials = None
        self.service = None
    
    def get_service(self):
        """Get or create Gmail API service"""
        if not self.is_authenticated():
            raise ValueError("Not authenticated. Please authenticate first.")
        
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
        
        return self.service
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get user's Gmail profile information"""
        service = self.get_service()
        
        try:
            profile = service.users().getProfile(userId='me').execute()
            return {
                "email": profile.get('emailAddress'),
                "messages_total": profile.get('messagesTotal'),
                "threads_total": profile.get('threadsTotal'),
                "history_id": profile.get('historyId')
            }
        except HttpError as error:
            logger.error(f"Error fetching user profile: {error}")
            raise
    
    def fetch_emails(self, max_results: int = 100, query: str = "") -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
            
        Returns:
            List of email dictionaries
        """
        service = self.get_service()
        emails = []
        
        try:
            # Get list of messages
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages")
            
            # Fetch full message details
            for msg in messages:
                try:
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    email_data = self._parse_message(message)
                    emails.append(email_data)
                    
                except HttpError as error:
                    logger.error(f"Error fetching message {msg['id']}: {error}")
                    continue
            
            logger.info(f"Successfully fetched {len(emails)} emails")
            return emails
            
        except HttpError as error:
            logger.error(f"Error fetching emails: {error}")
            raise
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured format"""
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        
        # Extract body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        import base64
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            import base64
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        return {
            "id": message['id'],
            "thread_id": message.get('threadId'),
            "subject": headers.get('Subject', '(No Subject)'),
            "from": headers.get('From', ''),
            "to": headers.get('To', ''),
            "cc": headers.get('Cc', ''),
            "date": headers.get('Date', ''),
            "body": body,
            "snippet": message.get('snippet', ''),
            "labels": message.get('labelIds', []),
            "internal_date": message.get('internalDate')
        }
    
    def search_emails(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search emails using Gmail query syntax
        
        Args:
            query: Gmail search query
            max_results: Maximum results to return
            
        Returns:
            List of matching emails
        """
        return self.fetch_emails(max_results=max_results, query=query)
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all Gmail labels"""
        service = self.get_service()
        
        try:
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return labels
        except HttpError as error:
            logger.error(f"Error fetching labels: {error}")
            raise


# Global instance
gmail_service = GmailOAuthService()