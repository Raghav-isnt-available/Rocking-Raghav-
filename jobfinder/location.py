"""Decide whether a posting is in Canada (or remote and open to Canada)."""
from __future__ import annotations

import re
from dataclasses import dataclass

PROVINCES = {
    "ontario": "ON", "british columbia": "BC", "quebec": "QC", "québec": "QC", "alberta": "AB",
    "manitoba": "MB", "saskatchewan": "SK", "nova scotia": "NS", "new brunswick": "NB",
    "newfoundland": "NL", "prince edward island": "PE", "yukon": "YT", "northwest territories": "NT",
    "nunavut": "NU",
}
PROVINCE_CODES = set(PROVINCES.values())

# Unambiguous Canadian cities -> province. (London, Richmond, Victoria, Kingston,
# Windsor, Hamilton, Cambridge, Waterloo also exist elsewhere, so they only count
# next to a province code or "Canada".)
CITIES = {
    "toronto": "ON", "ottawa": "ON", "mississauga": "ON", "brampton": "ON", "markham": "ON",
    "vaughan": "ON", "oakville": "ON", "burlington": "ON", "kitchener": "ON", "guelph": "ON",
    "scarborough": "ON", "etobicoke": "ON", "north york": "ON", "richmond hill": "ON", "oshawa": "ON",
    "pickering": "ON", "ajax": "ON", "sudbury": "ON", "thunder bay": "ON", "barrie": "ON",
    "montreal": "QC", "montréal": "QC", "laval": "QC", "gatineau": "QC", "sherbrooke": "QC",
    "quebec city": "QC", "québec city": "QC", "longueuil": "QC", "saint-laurent": "QC",
    "vancouver": "BC", "burnaby": "BC", "surrey": "BC", "kelowna": "BC", "coquitlam": "BC",
    "north vancouver": "BC", "nanaimo": "BC",
    "calgary": "AB", "edmonton": "AB", "lethbridge": "AB", "red deer": "AB",
    "winnipeg": "MB", "saskatoon": "SK", "regina": "SK", "halifax": "NS", "dartmouth": "NS",
    "fredericton": "NB", "moncton": "NB", "saint john": "NB", "st. john's": "NL", "charlottetown": "PE",
    "whitehorse": "YT", "yellowknife": "NT", "iqaluit": "NU",
}
GTA = {"toronto", "mississauga", "brampton", "markham", "vaughan", "oakville", "scarborough", "etobicoke",
       "north york", "richmond hill", "pickering", "ajax", "oshawa", "burlington"}

_REMOTE_RE = re.compile(r"\b(remote|work from home|wfh|anywhere|distributed|telecommute|virtual)\b", re.I)
# Remote postings that are open to people in Canada without saying "Canada".
_OPEN_REGIONS_RE = re.compile(r"\b(worldwide|global|anywhere|north america|americas|na|namer|amer)\b", re.I)
# Only codes that don't double as common country codes (NL=Netherlands, PE=Peru,
# SK=Slovakia); those provinces are still caught by name or city.
_SAFE_CODES = ("ON", "BC", "QC", "AB", "MB", "NS", "NB")
_PROV_CODE_RE = re.compile(r"(?:,|\s|\()(%s)(?:\)|,|\s|$)" % "|".join(_SAFE_CODES))
_COUNTRY_CA = {"ca", "can", "canada"}


@dataclass
class Place:
    in_canada: bool
    remote: bool
    remote_open_to_canada: bool  # remote and region includes Canada (explicitly or worldwide/NA)
    province: str | None
    city: str | None
    gta: bool
    where: str | None = None  # the location text that made it Canadian, for display


def _has_word(hay: str, needle: str) -> bool:
    return re.search(r"(?<![a-zà-ÿ])" + re.escape(needle) + r"(?![a-zà-ÿ])", hay) is not None


US_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware",
    "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky",
    "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri",
    "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",
    "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming",
}
# "CA" is left out on purpose: it means California or Canada depending on who wrote it.
_US_CODE_RE = re.compile(
    r",\s*(AL|AK|AZ|AR|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|"
    r"NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC)\b"
)
_US_RE = re.compile(r"\b(united states|usa|u\.s\.a?\.?|us only)\b", re.I)


def _segment_province(seg: str) -> tuple[str | None, str | None]:
    low = seg.lower()
    for name, code in CITIES.items():
        if _has_word(low, name):
            return code, name
    for name, code in PROVINCES.items():
        if _has_word(low, name):
            return code, None
    m = _PROV_CODE_RE.search(" " + seg + " ")
    return (m.group(1), None) if m else (None, None)


def _segment_is_us(seg: str) -> bool:
    low = seg.lower()
    if _has_word(low, "canada"):
        return False
    return bool(_US_CODE_RE.search(seg) or _US_RE.search(seg) or any(_has_word(low, s) for s in US_STATES))


def classify(location: str, *, extra: list[str] | None = None, country_hint: str | None = None,
             remote_hint: bool | None = None) -> Place:
    # Split multi-location strings ("Toronto, ON; New York, NY") so a US city in one
    # part can't veto, and "New Brunswick, NJ" isn't mistaken for the province.
    segs = [s.strip() for t in [location or ""] + list(extra or []) for s in re.split(r"[;|/•]| or ", t) if s.strip()]
    blob = " | ".join(segs)
    low = blob.lower()

    province = city = where = None
    for seg in segs:
        if _segment_is_us(seg):
            continue
        p, c = _segment_province(seg)
        if p:
            province, city, where = p, c, seg
            break
    if where is None:
        where = next((s for s in segs if _has_word(s.lower(), "canada")), None)

    says_canada = _has_word(low, "canada") or _has_word(low, "canadian")
    hint_canada = (country_hint or "").strip().lower() in _COUNTRY_CA
    in_canada = says_canada or hint_canada or province is not None

    remote = bool(remote_hint) or _REMOTE_RE.search(blob) is not None
    # "Anywhere in the United States" is not open to Canada, so only non-US parts count.
    open_region = any(_OPEN_REGIONS_RE.search(s) for s in segs if not _segment_is_us(s))
    remote_open = remote and (in_canada or open_region)

    return Place(
        in_canada=in_canada,
        remote=remote,
        remote_open_to_canada=remote_open,
        province=province,
        city=city,
        gta=city in GTA if city else False,
        where=where if in_canada else None,
    )
