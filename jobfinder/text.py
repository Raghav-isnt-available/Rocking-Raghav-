"""Text helpers: HTML to plain text, tokenizing, stopwords."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser

_BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section"}


class _Stripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def html_to_text(raw: str | None) -> str:
    if not raw:
        return ""
    # Greenhouse double-escapes its HTML (&lt;p&gt;), so unescape until stable.
    for _ in range(3):
        un = html.unescape(raw)
        if un == raw:
            break
        raw = un
    p = _Stripper()
    p.feed(raw)
    text = "".join(p.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


STOPWORDS = frozenset(
    """
    a about above after again against all also am an and any are as at be because been before being below
    between both but by can could did do does doing down during each etc few for from further had has have
    having he her here hers herself him himself his how i if in into is it its itself just me more most my
    myself no nor not now of off on once only or other our ours ourselves out over own same she should so
    some such than that the their theirs them themselves then there these they this those through to too
    under until up very was we were what when where which while who whom why will with would you your yours
    yourself yourselves us via per within across including include includes well new may must able
    """.split()
)

# Words that appear in nearly every posting and carry no signal about fit.
JOB_BOILERPLATE = frozenset(
    """
    job jobs role roles position positions candidate candidates team teams work working company opportunity
    opportunities apply application applicants employer employment equal accommodation accommodations benefits
    benefit salary pay compensation please join looking ideal responsibilities responsibility requirements
    required preferred qualifications qualification experience experiences year years skills skill strong
    ability excellent environment help using use based day days time full part world people make like get
    one two three what's we're you're you'll we'll it's including located location office hybrid remote canada
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z][a-z0-9+\-]*[a-z0-9+]|[a-z]")


def tokenize(text: str) -> list[str]:
    toks = _TOKEN_RE.findall(text.lower().replace("’", "'"))
    return [t for t in toks if len(t) > 1 and t not in STOPWORDS and t not in JOB_BOILERPLATE]


def terms(text: str) -> list[str]:
    """Unigrams plus adjacent bigrams (so 'clinical research' counts as a phrase)."""
    toks = tokenize(text)
    return toks + [f"{a} {b}" for a, b in zip(toks, toks[1:])]


def normalize_phrase(s: str) -> str:
    return " ".join(tokenize(s))
