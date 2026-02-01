"""
Email loading module - handles reading emails from JSON dataset or Gmail
"""
import json
from pathlib import Path
from typing import List, Optional
from app.config import settings
from app.schemas import RawEmail, EmailsResponse, ErrorResponse


def load_emails(source: str = "file", max_results: int = 100, query: str = "") -> EmailsResponse:
    """
    Load emails from JSON dataset file or Gmail
    
    Args:
        source: "file" for JSON dataset, "gmail" for Gmail API
        max_results: Maximum number of emails to fetch (for Gmail)
        query: Gmail search query (for Gmail)
    
    Returns:
        EmailsResponse: Response containing list of raw emails
        
    Raises:
        FileNotFoundError: If emails.json doesn't exist (file source)
        ValueError: If Gmail not authenticated (gmail source)
    """
    if source == "gmail":
        return load_emails_from_gmail(max_results, query)
    else:
        return load_emails_from_file()


def load_emails_from_file() -> EmailsResponse:
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


def load_emails_from_gmail(max_results: int = 100, query: str = "") -> EmailsResponse:
    """
    Load emails from Gmail using OAuth and persist to database
    
    Args:
        max_results: Maximum number of emails to fetch
        query: Gmail search query
    
    Returns:
        EmailsResponse: Response containing list of raw emails
        
    Raises:
        ValueError: If Gmail not authenticated
    """
    from app.gmail_oauth import gmail_service
    from app.database import get_database
    
    if not gmail_service.is_authenticated():
        raise ValueError(
            "Gmail not authenticated. Please authenticate at /gmail-oauth first."
        )
    
    try:
        # Fetch emails from Gmail
        gmail_emails = gmail_service.fetch_emails(max_results=max_results, query=query)
        
        # Convert Gmail format to RawEmail format and persist
        raw_emails = []
        db = get_database()
        
        for email in gmail_emails:
            raw_email = RawEmail(
                id=email['id'],
                from_=email['from'],
                to=email['to'],
                subject=email['subject'],
                date=email['date'],
                body=email['body']
            )
            raw_emails.append(raw_email)
            
            # Persist email to SQLite database (Fix #4)
            db.store_email({
                'email_id': email['id'],
                'subject': email['subject'],
                'from': email['from'],
                'to': email['to'],
                'date': email['date'],
                'body': email['body'],
                'source': 'gmail',
                'timestamp': Path(__file__).resolve().parent.parent.parent / 'data'  # Using current time
            })
        
        return EmailsResponse(emails=raw_emails)
    
    except Exception as e:
        raise ValueError(f"Error loading emails from Gmail: {str(e)}")


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