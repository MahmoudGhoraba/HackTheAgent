from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime, timedelta


# NOTE: In a production setup, replace this with Gmail API integration.
# For hackathon/demo, we return a small, realistic sample.

def fetch_gmail(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch sample Gmail messages. Return raw platform-shaped dicts.
    Keys used by normalization: id, from, subject, snippet/body, internal_date (epoch ms), threadId, url, source
    """
    now = datetime.utcnow()
    samples: List[Dict[str, Any]] = [
        {
            "id": "gm_1001",
            "from": "recruiter@ibm.com",
            "subject": "IBM Internship Application - Next Steps",
            "snippet": "Hi there, thanks for applying to IBM. Please submit your coding challenge by Friday.",
            "internal_date": int((now - timedelta(hours=2)).timestamp() * 1000),
            "threadId": "gm_thread_2001",
            "url": "https://mail.google.com/mail/u/0/#inbox/gm_1001",
            "source": "gmail",
        },
        {
            "id": "gm_1002",
            "from": "team@newsletter.com",
            "subject": "Weekly Tech Digest",
            "snippet": "AI trends and tools roundup for this week.",
            "internal_date": int((now - timedelta(days=1)).timestamp() * 1000),
            "threadId": "gm_thread_2002",
            "url": "https://mail.google.com/mail/u/0/#inbox/gm_1002",
            "source": "gmail",
        },
        {
            "id": "gm_1003",
            "from": "hiring@ibm.com",
            "subject": "IBM Job Application - Interview Schedule",
            "snippet": "We would like to schedule a 30-minute call to discuss your application.",
            "internal_date": int((now - timedelta(days=3)).timestamp() * 1000),
            "threadId": "gm_thread_2003",
            "url": "https://mail.google.com/mail/u/0/#inbox/gm_1003",
            "source": "gmail",
        },
    ]
    return samples[:limit]
