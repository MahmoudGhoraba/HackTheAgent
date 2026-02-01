"""
Outlook Provider
Implements EmailProvider protocol using Microsoft Graph API.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import msal
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OutlookProvider:
    """Outlook email provider using Microsoft Graph API."""
    
    # Microsoft Graph API endpoints
    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    AUTHORITY = "https://login.microsoftonline.com/{tenant}"
    
    # OAuth scopes
    SCOPES = [
        "https://graph.microsoft.com/Mail.Read",
        "https://graph.microsoft.com/User.Read",
        "offline_access"
    ]
    
    def __init__(self):
        self.token_file = settings.data_dir / "outlook_token.json"
        self.access_token: Optional[str] = None
        self._msal_app: Optional[msal.ConfidentialClientApplication] = None
        self._load_token()
    
    @property
    def provider_name(self) -> str:
        return "outlook"
    
    @property
    def msal_app(self) -> msal.ConfidentialClientApplication:
        """Get or create MSAL confidential client application."""
        if self._msal_app is None:
            client_id = getattr(settings, 'outlook_client_id', None)
            client_secret = getattr(settings, 'outlook_client_secret', None)
            tenant_id = getattr(settings, 'outlook_tenant_id', 'common')
            
            if not client_id or not client_secret:
                raise ValueError("Outlook OAuth not configured. Set OUTLOOK_CLIENT_ID and OUTLOOK_CLIENT_SECRET in .env")
            
            authority = self.AUTHORITY.format(tenant=tenant_id)
            
            self._msal_app = msal.ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=authority,
                token_cache=msal.SerializableTokenCache()
            )
        return self._msal_app
    
    def _load_token(self):
        """Load saved access token from file."""
        if self.token_file.exists():
            try:
                with open(self.token_file, "r") as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    logger.info("Loaded Outlook token from file")
            except Exception as e:
                logger.warning(f"Failed to load Outlook token: {e}")
    
    def _save_token(self, token_data: Dict[str, Any]):
        """Save access token to file."""
        try:
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, "w") as f:
                json.dump(token_data, f)
            logger.info("Saved Outlook token to file")
        except Exception as e:
            logger.error(f"Failed to save Outlook token: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with valid token."""
        if not self.access_token:
            return False
        
        # Try to validate token by making a simple API call
        try:
            profile = self._graph_request("/me")
            return profile is not None
        except Exception:
            return False
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get OAuth authorization URL for user consent."""
        redirect_uri = getattr(settings, 'outlook_redirect_uri', 'http://localhost:8000/oauth/outlook/callback')
        
        auth_url = self.msal_app.get_authorization_request_url(
            scopes=self.SCOPES,
            redirect_uri=redirect_uri,
            state=state or ""
        )
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        redirect_uri = getattr(settings, 'outlook_redirect_uri', 'http://localhost:8000/oauth/outlook/callback')
        
        result = self.msal_app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            self._save_token(result)
            logger.info("Successfully acquired Outlook token")
            return result
        else:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise ValueError(f"Failed to acquire token: {error}")
    
    def _graph_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Microsoft Graph API."""
        if not self.access_token:
            raise ValueError("Not authenticated with Outlook")
        
        url = f"{self.GRAPH_API_BASE}{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params)
            
            if response.status_code == 401:
                # Token expired, try to refresh
                self.access_token = None
                raise ValueError("Token expired. Please re-authenticate.")
            
            response.raise_for_status()
            return response.json()
    
    def fetch_emails(self, max_results: int = 100, query: str = "") -> List[Dict[str, Any]]:
        """Fetch emails from Outlook inbox."""
        params = {
            "$top": min(max_results, 100),
            "$select": "id,subject,from,toRecipients,receivedDateTime,bodyPreview,body,hasAttachments,parentFolderId",
            "$orderby": "receivedDateTime desc"
        }
        
        if query:
            # Convert to OData filter or search
            params["$search"] = f'"{query}"'
        
        result = self._graph_request("/me/messages", params)
        messages = result.get("value", [])
        
        # Normalize to common format
        emails = []
        for msg in messages:
            emails.append(self._normalize_email(msg))
        
        return emails
    
    def search_emails(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search emails using OData query."""
        return self.fetch_emails(max_results=max_results, query=query)
    
    def _normalize_email(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Outlook message to common email format."""
        from_addr = msg.get("from", {}).get("emailAddress", {})
        recipients = [r.get("emailAddress", {}).get("address", "") 
                     for r in msg.get("toRecipients", [])]
        
        return {
            "id": msg.get("id", ""),
            "subject": msg.get("subject", "(No Subject)"),
            "sender": from_addr.get("address", ""),
            "sender_name": from_addr.get("name", ""),
            "recipients": recipients,
            "date": msg.get("receivedDateTime", ""),
            "body": msg.get("body", {}).get("content", ""),
            "snippet": msg.get("bodyPreview", "")[:200],
            "has_attachments": msg.get("hasAttachments", False),
            "folder_id": msg.get("parentFolderId", ""),
            "provider": "outlook"
        }
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all mail folders (Outlook equivalent of labels)."""
        result = self._graph_request("/me/mailFolders")
        folders = result.get("value", [])
        
        return [
            {
                "id": f.get("id", ""),
                "name": f.get("displayName", ""),
                "type": "system" if f.get("displayName") in ["Inbox", "Sent Items", "Drafts", "Deleted Items"] else "user",
                "unread_count": f.get("unreadItemCount", 0),
                "total_count": f.get("totalItemCount", 0)
            }
            for f in folders
        ]
    
    def get_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        result = self._graph_request("/me")
        
        return {
            "email": result.get("mail") or result.get("userPrincipalName", ""),
            "name": result.get("displayName", ""),
            "id": result.get("id", ""),
            "provider": "outlook"
        }
    
    def revoke_access(self) -> bool:
        """Revoke access by deleting stored token."""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
            self.access_token = None
            self._msal_app = None
            logger.info("Revoked Outlook access")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke Outlook access: {e}")
            return False


# Singleton instance
outlook_provider = OutlookProvider()
