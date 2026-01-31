"""
Email normalization module - converts raw emails to normalized messages
"""
from typing import List
from app.schemas import RawEmail, NormalizedMessage, MessageMetadata, NormalizeResponse


def normalize_email(email: RawEmail) -> NormalizedMessage:
    """
    Normalize a single email into a structured message format
    
    Args:
        email: Raw email object
        
    Returns:
        NormalizedMessage: Normalized message with text and metadata
    """
    # Create normalized text representation
    text = f"""From: {email.from_}
To: {email.to}
Subject: {email.subject}
Date: {email.date}

{email.body}"""
    
    # Create metadata
    metadata = MessageMetadata(
        **{
            "from": email.from_,
            "to": email.to,
            "subject": email.subject,
            "date": email.date
        }
    )
    
    return NormalizedMessage(
        id=email.id,
        text=text,
        metadata=metadata
    )


def normalize_emails(emails: List[RawEmail]) -> NormalizeResponse:
    """
    Normalize a list of raw emails
    
    Args:
        emails: List of raw email objects
        
    Returns:
        NormalizeResponse: Response containing normalized messages
    """
    messages = [normalize_email(email) for email in emails]
    return NormalizeResponse(messages=messages)


def validate_email_fields(email: RawEmail) -> bool:
    """
    Validate that email has all required fields
    
    Args:
        email: Raw email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['id', 'from_', 'to', 'subject', 'date', 'body']
    
    for field in required_fields:
        value = getattr(email, field, None)
        if not value or (isinstance(value, str) and not value.strip()):
            return False
    
    return True


def get_normalization_stats(messages: List[NormalizedMessage]) -> dict:
    """
    Get statistics about normalized messages
    
    Args:
        messages: List of normalized messages
        
    Returns:
        dict: Statistics about the messages
    """
    if not messages:
        return {"count": 0}
    
    total_length = sum(len(msg.text) for msg in messages)
    avg_length = total_length / len(messages)
    
    return {
        "count": len(messages),
        "total_characters": total_length,
        "average_length": round(avg_length, 2),
        "min_length": min(len(msg.text) for msg in messages),
        "max_length": max(len(msg.text) for msg in messages)
    }