def handle_query(payload):
    # payload example: {"query": "internship"}
    query_text = payload.get("query", "").lower()
    messages = payload.get("messages", [])

    # Filter messages containing the query text in subject or content
    filtered = []
    for msg in messages:
        if query_text in msg.get("subject", "").lower() or query_text in msg.get("content", "").lower():
            filtered.append(msg)

    # Return filtered messages (mock summary)
    return {
        "query": query_text,
        "count": len(filtered),
        "results": filtered
    }
