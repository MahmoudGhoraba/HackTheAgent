from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime, timezone

from .models import Message


def _extract_tags(text: str | None) -> List[str]:
    if not text:
        return []
    # naive keyword extraction: split on non-alphanum, drop short tokens
    import re

    tokens = [t.lower() for t in re.split(r"[^A-Za-z0-9]+", text) if len(t) >= 4]
    # de-duplicate while preserving order
    seen = set()
    tags: List[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            tags.append(t)
    return tags[:10]


def _parse_dt(value: Any, source: str) -> datetime:
    if source == "gmail":
        # Gmail internal_date is epoch milliseconds
        try:
            ms = int(value)
            return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
        except Exception:
            return datetime.now(tz=timezone.utc)
    elif source == "outlook":
        # Outlook receivedDateTime is ISO8601, often ending with 'Z'
        try:
            s = str(value)
            if s.endswith("Z"):
                s = s.replace("Z", "+00:00")
            return datetime.fromisoformat(s)
        except Exception:
            return datetime.now(tz=timezone.utc)
    else:
        # Fallback: assume ISO
        try:
            s = str(value)
            if s.endswith("Z"):
                s = s.replace("Z", "+00:00")
            return datetime.fromisoformat(s)
        except Exception:
            return datetime.now(tz=timezone.utc)


def normalize_messages(raw_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize raw platform messages to a common Message shape and return dicts.
    """
    norm: List[Message] = []
    for m in raw_messages:
        source = str(m.get("source", "unknown")).lower()
        if source == "gmail":
            msg = Message(
                id=str(m.get("id")),
                source=source,
                sender=str(m.get("from", "unknown")),
                subject=(m.get("subject") or None),
                body=(m.get("snippet") or None),
                timestamp=_parse_dt(m.get("internal_date"), source),
                platform_thread_id=m.get("threadId") or None,
                url=m.get("url") or None,
                tags=_extract_tags((m.get("subject") or "") + " " + (m.get("snippet") or "")),
            )
            norm.append(msg)
        elif source == "outlook":
            msg = Message(
                id=str(m.get("id")),
                source=source,
                sender=str(m.get("from", "unknown")),
                subject=(m.get("subject") or None),
                body=(m.get("body_preview") or None),
                timestamp=_parse_dt(m.get("receivedDateTime"), source),
                platform_thread_id=m.get("conversationId") or None,
                url=m.get("webLink") or None,
                tags=_extract_tags((m.get("subject") or "") + " " + (m.get("body_preview") or "")),
            )
            norm.append(msg)
        else:
            # Unknown source: attempt generic mapping
            msg = Message(
                id=str(m.get("id")),
                source=source,
                sender=str(m.get("sender", m.get("from", "unknown"))),
                subject=(m.get("subject") or None),
                body=(m.get("body") or m.get("snippet") or None),
                timestamp=_parse_dt(m.get("timestamp"), source),
                platform_thread_id=m.get("threadId") or m.get("conversationId") or None,
                url=m.get("url") or m.get("webLink") or None,
                tags=_extract_tags((m.get("subject") or "") + " " + (m.get("body") or m.get("snippet") or "")),
            )
            norm.append(msg)

    # return as plain dicts with ISO timestamps for easy JSON serialization
    out: List[Dict[str, Any]] = []
    for m in norm:
        d = m.model_dump()
        # Ensure timestamp is ISO string
        ts = m.timestamp
        d["timestamp"] = ts.isoformat()
        out.append(d)
    return out
