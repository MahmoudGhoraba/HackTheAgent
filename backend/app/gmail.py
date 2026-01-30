def fetch_gmail():
    # Mock Gmail messages
    messages = [
        {
            "id": "g1",
            "platform": "Gmail",
            "sender": "hr@ibm.com",
            "subject": "Internship Opportunity",
            "body": "We are excited to offer you an internship...",
            "date": "2026-01-30"
        },
        {
            "id": "g2",
            "platform": "Gmail",
            "sender": "newsletter@python.org",
            "subject": "Python Weekly",
            "body": "Check out the latest Python updates...",
            "date": "2026-01-29"
        }
    ]
    return messages
