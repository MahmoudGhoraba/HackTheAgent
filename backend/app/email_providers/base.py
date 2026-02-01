"""
Email Provider Base Protocol
Defines the interface that all email providers must implement.
"""
from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Email:
    """Normalized email structure across providers."""
    id: str
    subject: str
    sender: str
    recipients: List[str]
    date: str
    body: str
    snippet: str
    labels: List[str]
    has_attachments: bool
    provider: str  # 'gmail' or 'outlook'


@dataclass
class Label:
    """Email label/folder."""
    id: str
    name: str
    type: str  # 'system' or 'user'


@dataclass
class Profile:
    """User profile information."""
    email: str
    name: Optional[str]
    provider: str


class EmailProvider(Protocol):
    """Protocol for email providers (Gmail, Outlook, etc.)."""
    
    @property
    def provider_name(self) -> str:
        """Return provider name ('gmail' or 'outlook')."""
        ...
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        ...
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get OAuth authorization URL."""
        ...
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        ...
    
    def fetch_emails(self, max_results: int = 100, query: str = "") -> List[Dict[str, Any]]:
        """Fetch emails with optional search query."""
        ...
    
    def search_emails(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search emails using provider-specific query syntax."""
        ...
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all labels/folders."""
        ...
    
    def get_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        ...
    
    def revoke_access(self) -> bool:
        """Revoke OAuth access."""
        ...
