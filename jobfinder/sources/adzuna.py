"""Adzuna aggregator (covers Canadian employers that don't use Greenhouse/Lever/Ashby).

Needs a free key from https://developer.adzuna.com/ in ADZUNA_APP_ID / ADZUNA_APP_KEY.
Adzuna returns a shortened snippet of each description, so these jobs rank
on less text than the company-board ones.
"""
from __future__ import annotations

import os

from ..http import get_json
from ..models import Job


def available() -> bool:
    return bool(os.environ.get("ADZUNA_APP_ID") and os.environ.get("ADZUNA_APP_KEY"))


def search(what: str, where: str | None = None, pages: int = 1, max_days_old: int = 30) -> list[Job]:
    from . import parse_time

    jobs = []
    for page in range(1, pages + 1):
        params = {
            "app_id": os.environ["ADZUNA_APP_ID"],
            "app_key": os.environ["ADZUNA_APP_KEY"],
            "what": what,
            "results_per_page": 50,
            "max_days_old": max_days_old,
            "content-type": "application/json",
        }
        if where:
            params["where"] = where
        data = get_json(f"https://api.adzuna.com/v1/api/jobs/ca/search/{page}", params)
        results = data.get("results") or []
        for j in results:
            loc = j.get("location") or {}
            lo, hi = j.get("salary_min"), j.get("salary_max")
            jobs.append(Job(
                source="adzuna",
                source_id=str(j.get("id")),
                company=((j.get("company") or {}).get("display_name") or "").strip(),
                title=(j.get("title") or "").strip(),
                location=loc.get("display_name") or "",
                extra_locations=[", ".join(loc.get("area") or [])],
                url=j.get("redirect_url") or "",
                description=j.get("description") or "",
                posted_at=parse_time(j.get("created")),
                employment_type=j.get("contract_time") or j.get("contract_type"),
                salary=f"CAD {lo:,.0f}–{hi:,.0f}" if lo and hi else None,
                country_hint="CA",
            ))
        if len(results) < 50:
            break
    return jobs
