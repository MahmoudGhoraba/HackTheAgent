# app/utils.py

def format_messages(messages):
    """Optional: clean/format messages for frontend"""
    formatted = []
    for msg in messages:
        formatted.append({
            "subject": msg.get("subject", ""),
            "sender": msg.get("sender", ""),
            "body": msg.get("body", ""),
            "date": msg.get("date", "")
        })
    return formatted
