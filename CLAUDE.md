# Job finder

Python (stdlib only, 3.11+) engine that pulls Canadian job postings from public
company job boards and ranks them against the owner's resume. The owner usually
drives it from their phone, so the normal request is "find me jobs" / "refresh my
job matches": run the search and republish the results page.

## Refreshing results

1. If `profile/resume.txt` is missing (fresh container), rebuild it from the owner's
   newest resume and write its text there, leaving out the phone/email line. The
   current one is `Resume_Official_7-21.pdf` in Google Drive (July 2026; targets pharma
   marketing, communications and business development). Search Drive for the newest
   file with "Resume" in the title. Ignore `Resume Official.pdf` (January 2025,
   second-year, lab focus). If the owner mentions a newer resume, use that.
2. `python3 -m jobfinder search` (about 15 s). Writes `out/report.html` and `out/jobs.json`.
3. Publish `out/report.html` to the existing artifact
   https://claude.ai/artifact/Cu7zSqmMAt1koLzFpziY16 (read it first, then publish with
   that `url`) so the link stays the same. Summarize the top few matches in chat.

## Rules

- This repo is public. Never commit the resume, contact details, or `out/`.
  `.gitignore` covers `profile/resume.txt`, `profile/*.pdf` and `out/`.
- Remotive's free API: at most ~4 fetches a day, and every Remotive listing must
  link back to Remotive and credit it (the report does both).
- Indeed has no API for this and its terms forbid scraped/automated logins; don't
  build one. Adzuna (optional) needs `ADZUNA_APP_ID` / `ADZUNA_APP_KEY`.
- Network: the cloud environment `Rocking-Raghav-` allows boards-api.greenhouse.io,
  api.lever.co, api.ashbyhq.com, remotive.com and api.adzuna.com. A new source host
  needs that environment's allowlist changed.

## Code map

- `jobfinder/sources/` one module per source, each returns `list[Job]`
- `jobfinder/location.py` Canada / remote-open-to-Canada detection
- `jobfinder/rank.py` filters (location, excluded titles, seniority, dedupe) and the score
- `jobfinder/report.py` JSON + the self-contained HTML page
- `profile.toml` target titles, skills, levels, exclusions; `companies.toml` boards to pull

## Checks

- `python3 -m unittest discover -s tests`
- `python3 -m jobfinder check-companies` confirms every board slug still answers
