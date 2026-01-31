"""
Gmail Agent Module

This module provides a Gmail agent that interacts with the Gmail API
to list, read, send, and search emails.
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Paths for credentials
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


class GmailAgent:
    """Gmail Agent for managing email operations"""
    
    def __init__(self):
        """Initialize the Gmail agent with authentication"""
        self.service: Any  # Gmail API service (dynamically typed)
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None
        
        # Check if token.json exists (previously authenticated)
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # New authentication flow
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"{CREDENTIALS_FILE} not found. Please download OAuth 2.0 credentials "
                        "from Google Cloud Console and save as credentials.json"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        # Build Gmail API service - This ensures service is always initialized
        self.service = build('gmail', 'v1', credentials=creds)
    
    def list_emails(
        self,
        max_results: int = 10,
        page_token: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List emails from Gmail inbox
        
        Args:
            max_results: Maximum number of emails to return (1-100)
            page_token: Token for pagination
            query: Gmail search query (e.g., 'from:example@gmail.com', 'is:unread')
        
        Returns:
            Dictionary with success status, emails list, and pagination info
        """
        try:
            # Build request parameters
            params = {
                'userId': 'me',
                'maxResults': min(max_results, 100)
            }
            
            if page_token:
                params['pageToken'] = page_token
            
            if query:
                params['q'] = query
            
            # Call Gmail API - Fixed: Properly access users().messages().list()
            results = self.service.users().messages().list(**params).execute()
            
            messages = results.get('messages', [])
            next_page_token = results.get('nextPageToken')
            result_size_estimate = results.get('resultSizeEstimate', 0)
            
            # Get details for each message
            emails = []
            for message in messages:
                email_data = self._get_email_summary(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return {
                'success': True,
                'emails': emails,
                'next_page_token': next_page_token,
                'result_size_estimate': result_size_estimate
            }
        
        except HttpError as error:
            return {
                'success': False,
                'error': f'Gmail API error: {error}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _get_email_summary(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary information for an email
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Dictionary with email summary data
        """
        try:
            # Get message details - Fixed: Properly access users().messages().get()
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}
            
            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'subject': header_dict.get('Subject', '(No Subject)'),
                'from': header_dict.get('From', ''),
                'to': header_dict.get('To', ''),
                'date': header_dict.get('Date', ''),
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }
        
        except Exception as e:
            print(f"Error getting email summary for {message_id}: {e}")
            return None
    
    def read_email_details(self, email_id: str) -> Dict[str, Any]:
        """
        Read full details of a specific email
        
        Args:
            email_id: Gmail message ID
        
        Returns:
            Dictionary with success status and email details
        """
        try:
            # Get full message - Fixed: Properly access users().messages().get()
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}
            
            # Extract body
            body = self._get_email_body(message.get('payload', {}))
            
            email_data = {
                'id': message['id'],
                'thread_id': message['threadId'],
                'subject': header_dict.get('Subject', '(No Subject)'),
                'from': header_dict.get('From', ''),
                'to': header_dict.get('To', ''),
                'date': header_dict.get('Date', ''),
                'body': body,
                'labels': message.get('labelIds', [])
            }
            
            return {
                'success': True,
                'email': email_data
            }
        
        except HttpError as error:
            return {
                'success': False,
                'error': f'Gmail API error: {error}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _get_email_body(self, payload: Dict) -> str:
        """
        Extract email body from message payload
        
        Args:
            payload: Message payload from Gmail API
        
        Returns:
            Email body as string
        """
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            # Single part message
            data = payload.get('body', {}).get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        Send an email via Gmail
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            html: Whether body is HTML formatted
        
        Returns:
            Dictionary with success status and message info
        """
        try:
            # Create message
            if html:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'html'))
            else:
                message = MIMEText(body)
            
            message['To'] = to
            message['Subject'] = subject
            
            if cc:
                message['Cc'] = cc
            
            if bcc:
                message['Bcc'] = bcc
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message - Fixed: Properly access users().messages().send()
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }
        
        except HttpError as error:
            return {
                'success': False,
                'error': f'Gmail API error: {error}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def search_emails(
        self,
        from_email: Optional[str] = None,
        to_email: Optional[str] = None,
        subject: Optional[str] = None,
        after_date: Optional[str] = None,
        before_date: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search emails with advanced filters
        
        Args:
            from_email: Filter by sender email
            to_email: Filter by recipient email
            subject: Filter by subject keywords
            after_date: Filter emails after date (YYYY/MM/DD format)
            before_date: Filter emails before date (YYYY/MM/DD format)
            has_attachment: Filter emails with attachments
            is_unread: Filter unread emails
            max_results: Maximum results to return
        
        Returns:
            Dictionary with success status and search results
        """
        # Build Gmail search query
        query_parts = []
        
        if from_email:
            query_parts.append(f'from:{from_email}')
        
        if to_email:
            query_parts.append(f'to:{to_email}')
        
        if subject:
            query_parts.append(f'subject:{subject}')
        
        if after_date:
            query_parts.append(f'after:{after_date}')
        
        if before_date:
            query_parts.append(f'before:{before_date}')
        
        if has_attachment:
            query_parts.append('has:attachment')
        
        if is_unread:
            query_parts.append('is:unread')
        
        query = ' '.join(query_parts) if query_parts else None
        
        # Use list_emails with the constructed query
        return self.list_emails(
            max_results=max_results,
            query=query
        )


# Singleton instance
_gmail_agent_instance: Optional[GmailAgent] = None


def get_gmail_agent() -> GmailAgent:
    """
    Get or create Gmail agent singleton instance
    
    Returns:
        GmailAgent instance
    """
    global _gmail_agent_instance
    
    if _gmail_agent_instance is None:
        _gmail_agent_instance = GmailAgent()
    
    return _gmail_agent_instance