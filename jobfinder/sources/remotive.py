"""Remotive's free API. Its terms: link back to the Remotive URL, credit Remotive as
the source, and fetch at most ~4 times a day. The report does both of the first two."""
from __future__ import annotations

from ..http import get_json
from ..models import Job
from ..text import html_to_text


def fetch(search: str | None = None) -> list[Job]:
    from . import parse_time

    data = get_json("https://remotive.com/api/remote-jobs", {"search": search} if search else None)
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(Job(
            source="remotive",
            source_id=str(j["id"]),
            company=(j.get("company_name") or "").strip(),
            title=(j.get("title") or "").strip(),
            location=f"Remote ({j.get('candidate_required_location') or 'unspecified'})",
            url=j.get("url") or "",
            description=html_to_text(j.get("description")),
            posted_at=parse_time(j.get("publication_date")),
            department=j.get("category"),
            employment_type=j.get("job_type"),
            salary=j.get("salary") or None,
            remote_hint=True,
            attribution="Remotive",
        ))
    return jobs
