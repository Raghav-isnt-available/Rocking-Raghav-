"""Job sources. Company boards (Greenhouse, Lever, Ashby) are public JSON APIs the
companies publish for exactly this purpose; Remotive and Adzuna are aggregators."""
from __future__ import annotations

from datetime import datetime, timezone

from . import adzuna, ashby, greenhouse, lever, remotive

BOARDS = {"greenhouse": greenhouse.fetch, "lever": lever.fetch, "ashby": ashby.fetch}

__all__ = ["BOARDS", "adzuna", "remotive", "parse_time"]


def parse_time(value) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):  # Lever: epoch milliseconds
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    s = str(value).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
