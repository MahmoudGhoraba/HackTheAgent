"""
Gmail Provider
Wraps existing gmail_oauth service to implement EmailProvider protocol.
"""
from typing import List, Dict, Any, Optional
from app.gmail_oauth import gmail_service


class GmailProvider:
    """Gmail email provider implementing EmailProvider protocol."""
    
    @property
    def provider_name(self) -> str:
        return "gmail"
    
    def is_authenticated(self) -> bool:
        return gmail_service.is_authenticated()
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        return gmail_service.get_authorization_url(state)
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        return gmail_service.exchange_code_for_token(code)
    
    def fetch_emails(self, max_results: int = 100, query: str = "") -> List[Dict[str, Any]]:
        emails = gmail_service.fetch_emails(max_results=max_results, query=query)
        # Add provider tag
        for email in emails:
            email["provider"] = "gmail"
        return emails
    
    def search_emails(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        return self.fetch_emails(max_results=max_results, query=query)
    
    def get_labels(self) -> List[Dict[str, Any]]:
        return gmail_service.get_labels()
    
    def get_profile(self) -> Dict[str, Any]:
        profile = gmail_service.get_user_profile()
        profile["provider"] = "gmail"
        return profile
    
    def revoke_access(self) -> bool:
        return gmail_service.revoke_access()


# Singleton instance
gmail_provider = GmailProvider()
