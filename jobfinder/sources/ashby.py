from __future__ import annotations

from ..http import get_json
from ..models import Job
from ..text import html_to_text


def _addr(a: dict | None) -> str:
    p = (a or {}).get("postalAddress") or {}
    return ", ".join(x for x in [p.get("addressLocality"), p.get("addressRegion"), p.get("addressCountry")] if x)


def fetch(slug: str, company: str | None = None) -> list[Job]:
    from . import parse_time

    data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", {"includeCompensation": "true"})
    jobs = []
    for j in data.get("jobs", []):
        if j.get("isListed") is False:
            continue
        extra = [_addr(j.get("address"))]
        for s in j.get("secondaryLocations") or []:
            extra += [s.get("location") or "", _addr(s.get("address"))]
        country = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry")
        comp = (j.get("compensation") or {}).get("compensationTierSummary")
        jobs.append(Job(
            source="ashby",
            source_id=j["id"],
            company=company or slug,
            title=(j.get("title") or "").strip(),
            location=(j.get("location") or "").strip(),
            extra_locations=[x for x in extra if x],
            url=j.get("jobUrl") or "",
            apply_url=j.get("applyUrl"),
            description=j.get("descriptionPlain") or html_to_text(j.get("descriptionHtml")),
            posted_at=parse_time(j.get("publishedAt")),
            department=j.get("department") or j.get("team"),
            employment_type=j.get("employmentType"),
            salary=comp or None,
            country_hint=country,
            remote_hint=bool(j.get("isRemote")) or None,
        ))
    return jobs
