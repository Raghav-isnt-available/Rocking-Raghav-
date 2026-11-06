"""Filter jobs to Canada and score them against the resume and profile.

Score (0-100) = weighted mix of
  text     TF-IDF cosine similarity between resume+skills and the posting
  title    how much of the best-matching target title appears in the job title
  skills   share of profile skills that the posting mentions
  place    Toronto/GTA > remote open to Canada > elsewhere in Canada
  fresh    newer postings score higher
then multiplied down for asking more experience than you have, or a PhD.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime, timezone

from .location import classify
from .models import Job, Scored
from .profile import Profile
from .text import normalize_phrase, terms, tokenize

WEIGHTS = {"text": 0.40, "title": 0.25, "skills": 0.15, "place": 0.10, "fresh": 0.10}

_INTERN = re.compile(r"\b(intern|internship|co-?op|student|summer|practicum|placement|apprentice|trainee)\b", re.I)
_APM = re.compile(r"\bassociate (product|program|project) manager\b", re.I)
_SENIOR = re.compile(
    r"\b(senior|sr\.?|staff|principal|director|head|vp|vice president|chief|lead|manager|"
    r"architect|iii|iv|fellow)\b", re.I)
_MID = re.compile(r"\b(ii|specialist|scientist)\b", re.I)
_ENTRY = re.compile(
    r"\b(junior|jr\.?|entry|associate|assistant|coordinator|technician|technologist|"
    r"new grad|graduate|analyst|representative|agent|i)\b", re.I)

_YEARS = re.compile(r"(\d{1,2})\s*(?:\+|plus)?\s*(?:-|–|to)?\s*(?:\d{1,2})?\s*\+?\s*years?", re.I)
_PHD = re.compile(r"\b(ph\.?\s?d\.?|doctorate|doctoral degree)\b", re.I)
_STATUS = re.compile(r"\b(canadian citizen(ship)?|permanent resident|security clearance|"
                     r"legally (eligible|entitled) to work)\b", re.I)
_FRENCH = re.compile(r"\b(bilingual|bilingue|french (is )?(required|an asset)|fluent in french|"
                     r"fran[cç]ais)\b", re.I)


def level_of(title: str) -> str:
    if _INTERN.search(title):
        return "intern"
    if _APM.search(title):
        return "entry"
    if _SENIOR.search(title):
        return "senior"
    if _MID.search(title):
        return "mid"
    if _ENTRY.search(title):
        return "entry"
    return "mid"


def years_asked(text: str) -> int | None:
    """Smallest 'N years' figure that sits next to the word experience."""
    best = None
    for m in _YEARS.finditer(text):
        window = text[m.end(): m.end() + 60].lower() + text[max(0, m.start() - 40): m.start()].lower()
        if "experience" not in window:
            continue
        n = int(m.group(1))
        if 0 < n <= 25:
            best = n if best is None else min(best, n)
    return best


def _tfidf(docs: list[list[str]]):
    df = Counter()
    for d in docs:
        df.update(set(d))
    n = len(docs)
    idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
    vecs = []
    for d in docs:
        tf = Counter(d)
        v = {t: (1 + math.log(c)) * idf[t] for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({t: x / norm for t, x in v.items()})
    return vecs


def _cos(a: dict, b: dict) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0.0) for t, x in a.items())


# Title words that say how senior or what kind of contract, not what the work is.
# Matching only these ("Shipping Coordinator" vs "research coordinator") barely counts.
GENERIC_TITLE_WORDS = frozenset("""
    associate assistant coordinator intern internship co-op coop analyst specialist technician
    technologist junior student summer consultant manager officer representative administrator
    agent contract month i ii iii winter fall spring term full-time part-time
""".split())


_NOT_INFORMATIVE = GENERIC_TITLE_WORDS | {"university", "student", "team", "development", "research",
                                          "study", "product", "management", "senior", "lead", "project"}


def _title_score(title: str, targets: list[str]) -> float:
    have = set(tokenize(title))
    best = 0.0
    for t in targets:
        want = tokenize(t)
        if not want:
            continue
        hits = [w for w in want if w in have]
        frac = len(hits) / len(want)
        if hits and all(w in GENERIC_TITLE_WORDS for w in hits):
            frac *= 0.25
        best = max(best, frac)
    return best


def _fresh(posted: datetime | None, now: datetime) -> float:
    if posted is None:
        return 0.7
    days = max(0.0, (now - posted).total_seconds() / 86400)
    if days <= 14:
        return 1.0
    return max(0.3, 1.0 - (days - 14) / 150)


def job_text(j: Job) -> str:
    return f"{j.title}\n{j.title}\n{j.title}\n{j.department or ''}\n{j.description}"


def rank(jobs: list[Job], profile: Profile, now: datetime | None = None) -> tuple[list[Scored], dict]:
    now = now or datetime.now(timezone.utc)
    stats = Counter(fetched=len(jobs))

    # 1. Location, exclusions, seniority.
    kept: list[tuple[Job, object, str]] = []
    for j in jobs:
        place = classify(j.location, extra=j.extra_locations, country_hint=j.country_hint, remote_hint=j.remote_hint)
        onsite_ok = place.in_canada and not place.remote and (
            profile.allow_rest_of_canada or (place.city or "") in profile.preferred_cities or place.gta)
        remote_ok = profile.allow_remote and place.remote_open_to_canada
        if not (onsite_ok or remote_ok):
            stats["not_in_canada"] += 1
            continue
        tl = j.title.lower()
        if any(re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", tl) for w in profile.exclude_title_words):
            stats["excluded_title"] += 1
            continue
        lvl = level_of(j.title)
        if lvl not in profile.levels:
            stats["wrong_level"] += 1
            continue
        kept.append((j, place, lvl))

    # 2. Same title at the same company in several cities -> keep one (the best-placed).
    def place_rank(p) -> int:
        return 3 if p.gta else 2 if p.in_canada and not p.remote else 1
    best: dict[tuple, tuple] = {}
    for item in kept:
        j, p, _ = item
        k = (j.company.lower(), " ".join(tokenize(j.title)))
        if k not in best or place_rank(p) > place_rank(best[k][1]):
            best[k] = item
    stats["duplicates"] = len(kept) - len(best)
    kept = list(best.values())
    if not kept:
        return [], dict(stats)

    # 3. Text similarity, fitted on this batch of postings.
    profile_doc = "\n".join([profile.resume_text] + profile.skills * 2 + profile.titles)
    docs = [terms(job_text(j)) for j, _, _ in kept] + [terms(profile_doc)]
    vecs = _tfidf(docs)
    pv = vecs[-1]
    sims = [_cos(v, pv) for v in vecs[:-1]]
    ref = sorted(sims)[int(0.98 * (len(sims) - 1))] or 1.0  # top ~2% get full marks

    skill_phrases = [(s, normalize_phrase(s)) for s in profile.skills]
    preferred = set(profile.preferred_cities)

    out: list[Scored] = []
    for (j, place, lvl), sim, v in zip(kept, sims, vecs):
        body = " " + " ".join(tokenize(job_text(j))) + " "
        matched = [s for s, norm in skill_phrases if norm and f" {norm} " in body]
        parts = {
            "text": min(1.0, sim / ref),
            "title": _title_score(j.title, profile.titles),
            "skills": min(1.0, len(matched) / 5),
            "place": 1.0 if (place.gta or (place.city or "") in preferred) else 0.8 if place.remote else 0.6,
            "fresh": _fresh(j.posted_at, now),
        }
        score = 100 * sum(WEIGHTS[k] * parts[k] for k in WEIGHTS)

        flags = []
        yrs = years_asked(j.description)
        if yrs is not None and yrs > profile.max_years_experience:
            flags.append(f"Asks for {yrs}+ yrs experience")
            score *= 0.75 if yrs <= profile.max_years_experience + 2 else 0.55
        if _PHD.search(j.description):
            flags.append("Mentions a PhD")
            if re.search(r"\bscientist\b", j.title, re.I):
                score *= 0.7
        if _STATUS.search(j.description):
            flags.append("Mentions citizenship / PR / clearance")
        if _FRENCH.search(j.title + " " + j.description):
            flags.append("French / bilingual")
        if lvl == "mid":
            score *= 0.9

        shared = sorted((t for t in v if t in pv and " " not in t and t not in _NOT_INFORMATIVE),
                        key=lambda t: -v[t] * pv[t])[:6]
        # Show the Canadian location too when the posting's primary one is elsewhere.
        shown_loc = j.location
        if place.where and place.where.lower() not in (j.location or "").lower():
            shown_loc = f"{j.location} · also {place.where}" if j.location else place.where
        out.append(Scored(job=j, score=round(score, 1), in_canada=place.in_canada, remote=place.remote,
                          level=lvl, matched_skills=matched, shared_terms=shared, flags=flags, parts=parts,
                          location=shown_loc))

    out.sort(key=lambda s: -s.score)
    stats["below_min_score"] = sum(s.score < profile.min_score for s in out)
    out = [s for s in out if s.score >= profile.min_score][: profile.max_results]
    stats["shown"] = len(out)
    return out, dict(stats)
