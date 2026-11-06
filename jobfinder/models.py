from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Job:
    source: str  # "greenhouse", "lever", "ashby", "remotive", "adzuna"
    source_id: str
    company: str
    title: str
    location: str
    url: str
    description: str = ""  # plain text
    apply_url: str | None = None
    posted_at: datetime | None = None
    department: str | None = None
    employment_type: str | None = None
    salary: str | None = None
    # Structured hints some sources give us; the location module combines them.
    country_hint: str | None = None  # ISO-ish code or country name
    remote_hint: bool | None = None
    extra_locations: list[str] = field(default_factory=list)
    # Required credit line for sources whose terms ask for one (Remotive).
    attribution: str | None = None

    @property
    def key(self) -> str:
        return f"{self.source}:{self.source_id}"


@dataclass
class Scored:
    job: Job
    score: float
    in_canada: bool
    remote: bool
    level: str
    matched_skills: list[str]
    shared_terms: list[str]
    flags: list[str]
    parts: dict[str, float]
    location: str = ""  # display location (adds the Canadian one if the primary is abroad)
