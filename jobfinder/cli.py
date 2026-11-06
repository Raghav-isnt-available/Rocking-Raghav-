from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import engine, rank, report, sources
from .http import HTTPError
from .profile import load, load_companies


def cmd_search(args) -> int:
    p = load(args.profile)
    if not p.resume_text.strip():
        print(f"No resume text at {p.resume_path}. Put your resume there as plain text first.", file=sys.stderr)
        return 2
    print(f"Fetching from {len(p.companies)} company boards"
          + (", Remotive" if p.use_remotive else "")
          + (", Adzuna" if p.use_adzuna and sources.adzuna.available() else
             " (Adzuna off: no ADZUNA_APP_ID/ADZUNA_APP_KEY)" if p.use_adzuna else "") + " ...")
    t0 = time.time()
    jobs, errors, counts = engine.fetch_all(p)
    print(f"  {len(jobs)} postings in {time.time() - t0:.0f}s" + (f", {len(errors)} source errors" if errors else ""))
    for e in errors:
        print(f"  ! {e}")
    results, stats = rank.rank(jobs, p)
    paths = report.write(results, stats, counts, errors, Path(args.out))
    print(f"  kept {stats.get('shown', 0)}: dropped {stats.get('not_in_canada', 0)} outside Canada, "
          f"{stats.get('excluded_title', 0)} excluded titles, {stats.get('wrong_level', 0)} too senior, "
          f"{stats.get('duplicates', 0)} duplicates, {stats.get('below_min_score', 0)} below min score")
    print()
    for s in results[: args.top]:
        j = s.job
        print(f"{s.score:5.1f}  {j.title}  —  {j.company}  [{s.location}]")
        if s.matched_skills or s.flags:
            print(f"       {', '.join(s.matched_skills)}" + (f"  ⚠ {'; '.join(s.flags)}" if s.flags else ""))
        print(f"       {j.url}")
    print(f"\nWrote {paths['html']} and {paths['json']}")
    return 0


def cmd_check(args) -> int:
    comps = load_companies(args.companies)

    def probe(c):
        try:
            return c, len(sources.BOARDS[c.ats](c.slug, c.name)), None
        except HTTPError as e:
            return c, 0, f"HTTP {e.status}"
        except Exception as e:
            return c, 0, type(e).__name__
    bad = 0
    with ThreadPoolExecutor(12) as ex:
        for c, n, err in ex.map(probe, comps):
            status = err or ("ok" if n else "no open jobs")
            bad += bool(err)
            print(f"{c.name:28} {c.ats:10} {c.slug:26} {n:5}  {status}")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="jobfinder", description="Find Canadian jobs that fit your resume.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="fetch, rank and write the report")
    s.add_argument("--profile", default="profile.toml")
    s.add_argument("--out", default="out")
    s.add_argument("--top", type=int, default=15, help="how many to print here")
    s.set_defaults(fn=cmd_search)
    c = sub.add_parser("check-companies", help="verify every board slug in companies.toml")
    c.add_argument("--companies", default="companies.toml")
    c.set_defaults(fn=cmd_check)
    args = ap.parse_args(argv)
    return args.fn(args)
