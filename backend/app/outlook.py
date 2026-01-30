def fetch_outlook():
    # Mock Outlook messages
    messages = [
        {
            "id": "o1",
            "platform": "Outlook",
            "sender": "recruiter@microsoft.com",
            "subject": "Software Engineering Internship",
            "body": "We would like to invite you to apply...",
            "date": "2026-01-30"
        },
        {
            "id": "o2",
            "platform": "Outlook",
            "sender": "team@university.edu",
            "subject": "Project Submission Reminder",
            "body": "Don't forget to submit your final project by Friday...",
            "date": "2026-01-29"
        }
    ]
    return messages
