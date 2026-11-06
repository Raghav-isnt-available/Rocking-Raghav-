# Job finder (Canada)

Pulls live job postings from Canadian employers' public job boards, keeps the ones in
Canada (or remote and open to Canada), drops senior and off-target roles, and ranks
the rest against your resume. Output is a phone-friendly HTML page plus JSON.

```
python3 -m jobfinder search            # fetch, rank, write out/report.html
python3 -m jobfinder check-companies   # verify every board in companies.toml
python3 -m unittest discover -s tests
```

No dependencies beyond Python 3.11+.

## Setup

1. Put your resume as plain text in `profile/resume.txt` (git-ignored; this repo is public).
2. Edit `profile.toml`: target titles, skills, levels, cities, excluded title words.
3. Optional: add employers to `companies.toml` (any company whose careers page runs on
   Greenhouse, Lever or Ashby; the slug is the name in the board URL).
4. Optional: a free [Adzuna](https://developer.adzuna.com/) key in `ADZUNA_APP_ID` and
   `ADZUNA_APP_KEY` adds employers that don't use those boards.

## How a job is scored (0–100)

| Part | Weight | What it measures |
|---|---|---|
| Resume overlap | 40% | TF-IDF similarity between your resume + skills and the posting |
| Title fit | 25% | Share of your best-matching target title found in the job title (generic words like "associate" barely count) |
| Skills | 15% | How many of your listed skills the posting names (5 = full marks) |
| Place | 10% | Toronto/GTA > remote open to Canada > elsewhere in Canada |
| Freshness | 10% | Full marks for ≤14 days old, then declining |

Then it's scored down for asking more years of experience than `max_years_experience`, for
"Scientist" roles that mention a PhD, and slightly for mid-level titles. Flags (not penalties)
mark postings that mention citizenship/PR/clearance or need French.

## Coverage

Company boards cover biotech and health-tech startups and Canadian tech companies well.
Hospitals, universities and large pharma mostly use Workday or Taleo, which aren't
covered; Adzuna is the way to reach those.

Indeed isn't a source: it has no public API for job seekers and its terms forbid
automated logins and scraping.
