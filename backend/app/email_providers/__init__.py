"""
Email Providers Package
Provides unified interface for Gmail and Outlook email operations.
"""
from app.email_providers.base import EmailProvider
from app.email_providers.gmail import GmailProvider
from app.email_providers.outlook import OutlookProvider

__all__ = ["EmailProvider", "GmailProvider", "OutlookProvider"]
