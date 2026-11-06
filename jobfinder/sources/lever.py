from __future__ import annotations

from ..http import get_json
from ..models import Job
from ..text import html_to_text


def _salary(j: dict) -> str | None:
    r = j.get("salaryRange") or {}
    if r.get("min") and r.get("max"):
        cur = r.get("currency") or ""
        per = (r.get("interval") or "").replace("-", " ")
        return f"{cur} {r['min']:,}–{r['max']:,} {per}".strip()
    return None


def fetch(slug: str, company: str | None = None) -> list[Job]:
    from . import parse_time

    data = get_json(f"https://api.lever.co/v0/postings/{slug}", {"mode": "json"})
    jobs = []
    for j in data:
        cats = j.get("categories") or {}
        lists = "\n\n".join(f"{x.get('text', '')}\n{html_to_text(x.get('content'))}" for x in j.get("lists") or [])
        desc = "\n\n".join(p for p in [j.get("descriptionPlain") or html_to_text(j.get("description")),
                                        lists, j.get("additionalPlain") or ""] if p)
        jobs.append(Job(
            source="lever",
            source_id=j["id"],
            company=company or slug,
            title=(j.get("text") or "").strip(),
            location=(cats.get("location") or "").strip(),
            extra_locations=[x for x in cats.get("allLocations") or [] if x],
            url=j.get("hostedUrl") or "",
            apply_url=j.get("applyUrl"),
            description=desc,
            posted_at=parse_time(j.get("createdAt")),
            department=cats.get("team") or cats.get("department"),
            employment_type=cats.get("commitment"),
            salary=_salary(j),
            country_hint=j.get("country"),
            remote_hint=(j.get("workplaceType") or "").lower() == "remote" or None,
        ))
    return jobs
