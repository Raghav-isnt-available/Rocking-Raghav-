from __future__ import annotations

import re

from ..http import get_json
from ..models import Job
from ..text import html_to_text


# Greenhouse "offices" are the employer's coarse office tree, often shared by sibling
# postings in other countries, so they're only used when the posting's own location
# says nothing ("Remote", "Multiple locations").
_GENERIC_LOC = re.compile(r"^\W*(remote|hybrid|flexible|multiple locations?|various|anywhere|\W)*\W*$", re.I)


def fetch(slug: str, company: str | None = None) -> list[Job]:
    from . import parse_time

    data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", {"content": "true"})
    jobs = []
    for j in data.get("jobs", []):
        loc = ((j.get("location") or {}).get("name") or "").strip()
        offices = []
        if _GENERIC_LOC.match(loc):
            offices = [o.get("location") or o.get("name") for o in j.get("offices") or [] if o]
        jobs.append(Job(
            source="greenhouse",
            source_id=str(j["id"]),
            company=company or j.get("company_name") or slug,
            title=(j.get("title") or "").strip(),
            location=loc,
            extra_locations=[o for o in offices if o],
            url=j.get("absolute_url") or "",
            description=html_to_text(j.get("content")),
            posted_at=parse_time(j.get("first_published") or j.get("updated_at")),
            department=", ".join(d["name"] for d in j.get("departments") or [] if d.get("name")) or None,
        ))
    return jobs
