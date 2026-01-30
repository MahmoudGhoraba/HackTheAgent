from __future__ import annotations

from typing import Dict, Any, List
from collections import Counter

from .gmail import fetch_gmail
from .outlook import fetch_outlook
from .normalize import normalize_messages
from .models import QueryRequest, QueryResponse, Summary


def _contains_any(text: str | None, needles: List[str]) -> bool:
    if not needles:
        return True
    if not text:
        return False
    t = text.lower()
    return any(n.lower() in t for n in needles)


def _summarize(messages: List[Dict[str, Any]]) -> str:
    if not messages:
        return "No messages found."
    # Top platforms, top senders, and a little numeric context
    platforms = Counter(m.get("source", "unknown") for m in messages)
    senders = Counter(m.get("sender", "unknown") for m in messages)
    top_platforms = ", ".join(f"{p}: {c}" for p, c in platforms.most_common())
    top_senders = ", ".join(f"{s}: {c}" for s, c in senders.most_common(5))

    # Surface common keywords from subjects
    subjects = " ".join((m.get("subject") or "") for m in messages)
    import re

    tokens = [t.lower() for t in re.split(r"[^A-Za-z0-9]+", subjects) if len(t) >= 5]
    keywords = Counter(tokens)
    top_keywords = ", ".join(k for k, _ in keywords.most_common(10))

    return (
        f"Found {len(messages)} messages. "
        f"Platforms: {top_platforms}. "
        f"Top senders: {top_senders}. "
        f"Frequent keywords: {top_keywords}."
    )


def handle_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Parse request
    req = QueryRequest(**(payload or {}))

    # Orchestrate: fetch, normalize
    raw = []
    # If platform specified, only fetch those
    platforms = set(p.lower() for p in (req.platform or ["gmail", "outlook"]))
    if "gmail" in platforms:
        raw.extend(fetch_gmail(limit=200))
    if "outlook" in platforms:
        raw.extend(fetch_outlook(limit=200))

    normalized = normalize_messages(raw)

    # Filter
    def _ok(m: Dict[str, Any]) -> bool:
        if req.platform and m.get("source") not in platforms:
            return False
        if req.sender and req.sender.lower() not in (m.get("sender") or "").lower():
            return False
        if req.keywords and not (
            _contains_any(m.get("subject"), req.keywords) or _contains_any(m.get("body"), req.keywords)
        ):
            return False
        # time range
        ts = m.get("timestamp")
        # timestamp comes as ISO string after model_dump; support both str and dict
        from datetime import datetime

        if isinstance(ts, str):
            try:
                # Pydantic uses ISO format; handle Z suffix
                s = ts
                if s.endswith("Z"):
                    s = s.replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
            except Exception:
                dt = None
        else:
            dt = None
        if req.since and dt and dt < req.since:
            return False
        if req.until and dt and dt > req.until:
            return False
        return True

    filtered = [m for m in normalized if _ok(m)]

    # Sort by timestamp desc
    def _sort_key(m: Dict[str, Any]):
        ts = m.get("timestamp")
        return ts if isinstance(ts, str) else str(ts)

    filtered.sort(key=_sort_key, reverse=True)

    # Limit
    limit = req.limit or 50
    filtered = filtered[:limit]

    # Summary
    summary = Summary(text=_summarize(filtered)) if req.summarize else None
    resp = QueryResponse(messages=filtered, summary=summary)
    return resp.model_dump()
