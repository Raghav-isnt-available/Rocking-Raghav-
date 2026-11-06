"""Fetch every enabled source in parallel."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from . import sources
from .models import Job
from .profile import Profile


def fetch_all(profile: Profile, log=print) -> tuple[list[Job], list[str], dict[str, int]]:
    tasks = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for c in profile.companies:
            fn = sources.BOARDS.get(c.ats)
            if fn is None:
                log(f"  ! {c.name}: unknown ats '{c.ats}'")
                continue
            tasks[ex.submit(fn, c.slug, c.name)] = f"{c.name} ({c.ats})"
        if profile.use_remotive:
            tasks[ex.submit(sources.remotive.fetch)] = "Remotive"
        if profile.use_adzuna and sources.adzuna.available():
            where = profile.preferred_cities[0] if profile.preferred_cities else None
            for t in profile.titles[:8]:
                tasks[ex.submit(sources.adzuna.search, t, where)] = f"Adzuna '{t}'"

        jobs: list[Job] = []
        errors: list[str] = []
        counts: dict[str, int] = {}
        for fut in as_completed(tasks):
            name = tasks[fut]
            try:
                got = fut.result()
            except Exception as e:  # one dead board shouldn't sink the run
                errors.append(f"{name}: {e}")
                continue
            counts[name] = len(got)
            jobs.extend(got)
    return jobs, errors, counts
