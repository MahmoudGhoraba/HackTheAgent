"""
Email loading module - handles reading emails from JSON dataset
"""
import json
from pathlib import Path
from typing import List
from app.config import settings
from app.schemas import RawEmail, EmailsResponse, ErrorResponse


def load_emails() -> EmailsResponse:
    """
    Load emails from the JSON dataset file
    
    Returns:
        EmailsResponse: Response containing list of raw emails
        
    Raises:
        FileNotFoundError: If emails.json doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    emails_path = settings.data_dir / settings.emails_file
    
    if not emails_path.exists():
        raise FileNotFoundError(
            f"Emails file not found at {emails_path}. "
            f"Please ensure {settings.emails_file} exists in {settings.data_dir}"
        )
    
    try:
        with open(emails_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate and parse emails
        emails = [RawEmail(**email) for email in data]
        
        return EmailsResponse(emails=emails)
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in emails file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading emails: {str(e)}")


def get_email_stats() -> dict:
    """
    Get statistics about the email dataset
    
    Returns:
        dict: Statistics including count, date range, etc.
    """
    try:
        response = load_emails()
        emails = response.emails
        
        if not emails:
            return {"count": 0}
        
        dates = [email.date for email in emails]
        
        return {
            "count": len(emails),
            "earliest_date": min(dates),
            "latest_date": max(dates),
            "unique_senders": len(set(email.from_ for email in emails)),
            "unique_recipients": len(set(email.to for email in emails))
        }
    except Exception as e:
        return {"error": str(e)}