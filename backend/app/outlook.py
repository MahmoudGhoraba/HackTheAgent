from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime, timedelta


# NOTE: In a production setup, replace this with Microsoft Graph Outlook integration.
# For hackathon/demo, we return a small, realistic sample.

def fetch_outlook(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch sample Outlook messages. Return raw platform-shaped dicts.
    Keys used by normalization: id, from, subject, body_preview/snippet, receivedDateTime (ISO), conversationId, webLink, source
    """
    now = datetime.utcnow()
    samples: List[Dict[str, Any]] = [
        {
            "id": "ol_3001",
            "from": "manager@startup.com",
            "subject": "Sprint Planning – Action Items",
            "body_preview": "Please finalize estimates and update Jira by EOD.",
            "receivedDateTime": (now - timedelta(hours=1)).isoformat() + "Z",
            "conversationId": "ol_conv_5001",
            "webLink": "https://outlook.office.com/mail/inbox/ol_3001",
            "source": "outlook",
        },
        {
            "id": "ol_3002",
            "from": "careers@ibm.com",
            "subject": "IBM Graduate Program – Application Received",
            "body_preview": "Your application has been received. We will be in touch soon.",
            "receivedDateTime": (now - timedelta(days=2)).isoformat() + "Z",
            "conversationId": "ol_conv_5002",
            "webLink": "https://outlook.office.com/mail/inbox/ol_3002",
            "source": "outlook",
        },
    ]
    return samples[:limit]
