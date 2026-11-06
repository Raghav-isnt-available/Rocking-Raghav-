from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Company:
    name: str
    ats: str
    slug: str
    sector: str = "other"


@dataclass
class Profile:
    resume_path: Path
    companies_path: Path
    sectors: list[str]
    use_remotive: bool
    use_adzuna: bool
    min_score: float
    max_results: int
    preferred_cities: list[str]
    allow_rest_of_canada: bool
    allow_remote: bool
    titles: list[str]
    skills: list[str]
    levels: list[str]
    max_years_experience: int
    exclude_title_words: list[str]
    resume_text: str = ""
    companies: list[Company] = field(default_factory=list)


def load(path: str | Path) -> Profile:
    path = Path(path)
    base = path.parent
    d = tomllib.loads(path.read_text())
    s, loc, t = d.get("search", {}), d.get("location", {}), d.get("target", {})
    p = Profile(
        resume_path=base / s.get("resume", "profile/resume.txt"),
        companies_path=base / s.get("companies", "companies.toml"),
        sectors=s.get("sectors", []),
        use_remotive=s.get("use_remotive", True),
        use_adzuna=s.get("use_adzuna", True),
        min_score=float(s.get("min_score", 30)),
        max_results=int(s.get("max_results", 75)),
        preferred_cities=[c.lower() for c in loc.get("preferred_cities", [])],
        allow_rest_of_canada=loc.get("allow_rest_of_canada", True),
        allow_remote=loc.get("allow_remote", True),
        titles=t.get("titles", []),
        skills=t.get("skills", []),
        levels=t.get("levels", ["intern", "entry", "mid"]),
        max_years_experience=int(t.get("max_years_experience", 3)),
        exclude_title_words=[w.lower() for w in t.get("exclude_title_words", [])],
    )
    if p.resume_path.exists():
        p.resume_text = p.resume_path.read_text()
    p.companies = load_companies(p.companies_path)
    if p.sectors:
        p.companies = [c for c in p.companies if c.sector in p.sectors]
    return p


def load_companies(path: str | Path) -> list[Company]:
    d = tomllib.loads(Path(path).read_text())
    return [Company(name=c["name"], ats=c["ats"], slug=c["slug"], sector=c.get("sector", "other"))
            for c in d.get("company", [])]
