def normalize_messages(messages):
    # Convert all messages to a standard format
    normalized = []
    for msg in messages:
        normalized.append({
            "id": msg.get("id"),
            "platform": msg.get("platform"),
            "from": msg.get("sender"),
            "subject": msg.get("subject"),
            "content": msg.get("body"),
            "date": msg.get("date")
        })
    return normalized
