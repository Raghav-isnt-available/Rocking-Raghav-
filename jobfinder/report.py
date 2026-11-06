"""Write results as JSON and as a single self-contained, phone-friendly HTML page."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import Scored

try:
    from zoneinfo import ZoneInfo
    _TZ = ZoneInfo("America/Toronto")
except Exception:  # no tz database: fall back to UTC
    _TZ = timezone.utc

SOURCE_NAMES = {"greenhouse": "Greenhouse", "lever": "Lever", "ashby": "Ashby",
                "remotive": "Remotive", "adzuna": "Adzuna"}


def to_records(results: list[Scored]) -> list[dict]:
    recs = []
    for s in results:
        j = s.job
        recs.append({
            "score": s.score,
            "title": j.title,
            "company": j.company,
            "location": s.location or j.location,
            "remote": s.remote,
            "level": s.level,
            "posted": j.posted_at.isoformat() if j.posted_at else None,
            "url": j.url,
            "apply_url": j.apply_url,
            "salary": j.salary,
            "type": j.employment_type,
            "department": j.department,
            "source": SOURCE_NAMES.get(j.source, j.source),
            "attribution": j.attribution,
            "skills": s.matched_skills,
            "terms": s.shared_terms,
            "flags": s.flags,
            "parts": {k: round(v, 2) for k, v in s.parts.items()},
            "key": j.key,
        })
    return recs


def write(results: list[Scored], stats: dict, counts: dict, errors: list[str], out_dir: Path,
          now: datetime | None = None) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    now = (now or datetime.now(timezone.utc)).astimezone(_TZ)
    recs = to_records(results)
    meta = {
        "generated": now.isoformat(),
        "generated_label": now.strftime("%b %-d, %Y, %-I:%M %p ") + (now.tzname() or ""),
        "stats": stats,
        "employers": len([k for k in counts if not k.startswith(("Adzuna", "Remotive"))]),
        "sources": sorted({k.split(" (")[0].split(" '")[0] for k in counts}),
        "errors": errors,
    }
    jp = out_dir / "jobs.json"
    jp.write_text(json.dumps({"meta": meta, "jobs": recs}, indent=2, ensure_ascii=False))
    hp = out_dir / "report.html"
    payload = json.dumps({"meta": meta, "jobs": recs}, ensure_ascii=False).replace("</", "<\\/")
    hp.write_text(PAGE.replace("__DATA__", payload))
    return {"json": jp, "html": hp}


PAGE = r"""<title>Canada Job Matches</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* Layout: one ranked column of match cards under a compact header and a sticky filter bar. */
:root {
  --bg: #f3f5f6;
  --surface: #ffffff;
  --ink: #15212b;
  --muted: #5a6874;
  --line: #d9e0e5;
  --accent: #0d6b6b;
  --accent-soft: #dff0ee;
  --warn: #835400;
  --warn-soft: #f9eed6;
  --bar: #c9d6dc;
  --display: "IBM Plex Sans Condensed", "Arial Narrow", system-ui, sans-serif;
  --body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f1619; --surface: #162026; --ink: #e4ecef; --muted: #98a8b2; --line: #26343c;
    --accent: #5cc2bb; --accent-soft: #173a3a; --warn: #f0c26a; --warn-soft: #3a2e14; --bar: #2c3c44;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0f1619; --surface: #162026; --ink: #e4ecef; --muted: #98a8b2; --line: #26343c;
  --accent: #5cc2bb; --accent-soft: #173a3a; --warn: #f0c26a; --warn-soft: #3a2e14; --bar: #2c3c44;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 15px/1.5 var(--body); }
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }
.wrap { max-width: 760px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
header { padding-block: 28px 8px; }
h1 { font: 600 28px/1.15 var(--display); letter-spacing: 0.01em; margin: 0 0 6px; text-wrap: balance; }
.sub { color: var(--muted); margin: 0; font-size: 14px; }
.note { color: var(--muted); font-size: 13px; margin: 8px 0 0; max-width: 65ch; }
.bar { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg); padding-block: 10px; border-bottom: 1px solid var(--line); }
.controls { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.chip { font: 500 13px/1 var(--body); padding: 8px 12px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); cursor: pointer; }
.chip[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--surface); }
.chip:focus-visible, input:focus-visible, select:focus-visible, a:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
#q { flex: 1 1 180px; min-width: 0; font: 15px var(--body); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); }
select { font: 13px var(--body); padding: 7px 8px; border-radius: 8px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); }
.count { color: var(--muted); font-size: 13px; margin: 10px 0 0; font-variant-numeric: tabular-nums; }
main { display: grid; gap: 12px; padding-block: 14px 40px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; display: grid; grid-template-columns: 52px minmax(0, 1fr); gap: 4px 14px; }
.score { grid-row: span 3; font: 600 22px/1 var(--mono); color: var(--accent); font-variant-numeric: tabular-nums; padding-top: 2px; }
.meter { margin-top: 8px; height: 4px; border-radius: 2px; background: var(--bar); overflow: hidden; }
.meter span { display: block; height: 100%; background: var(--accent); }
.lvl { display: block; margin-top: 8px; font: 500 10px/1 var(--body); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
.title { font: 600 16px/1.3 var(--body); margin: 0; min-width: 0; overflow-wrap: anywhere; }
.title a { color: var(--ink); text-decoration: none; }
.title a:hover { text-decoration: underline; }
.meta { color: var(--muted); font-size: 13.5px; margin: 0; overflow-wrap: anywhere; }
.meta b { color: var(--ink); font-weight: 500; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.tag { font-size: 12px; line-height: 1; padding: 5px 8px; border-radius: 4px; background: var(--accent-soft); color: var(--ink); }
.tag.warn { background: var(--warn-soft); color: var(--warn); }
.why { grid-column: 2; color: var(--muted); font-size: 12.5px; margin: 6px 0 0; font-variant-numeric: tabular-nums; }
.actions { grid-column: 2; display: flex; flex-wrap: wrap; gap: 14px; margin-top: 8px; font-size: 14px; align-items: center; }
.actions a { color: var(--accent); font-weight: 500; text-decoration: none; }
.actions a:hover { text-decoration: underline; }
.actions button { background: none; border: 0; padding: 0; color: var(--muted); font: 14px var(--body); cursor: pointer; }
.src { margin-left: auto; color: var(--muted); font-size: 12px; }
.empty { color: var(--muted); padding: 24px 0; }
footer { color: var(--muted); font-size: 12.5px; padding-block: 0 40px; }
footer ul { padding-left: 18px; margin: 6px 0; }
@media (max-width: 440px) { .card { grid-template-columns: 44px minmax(0, 1fr); gap: 4px 10px; } .score { font-size: 19px; } }
@media (prefers-reduced-motion: no-preference) { .chip { transition: background-color .15s, color .15s; } }
</style>

<script id="data" type="application/json">__DATA__</script>

<div class="wrap">
  <header>
    <h1>Canada Job Matches</h1>
    <p class="sub" id="sub"></p>
    <p class="note">Ranked against your resume. Scores weigh resume overlap, title fit, skills named in the posting, location and freshness. Sources are company job boards on Greenhouse, Lever and Ashby, plus Remotive and Adzuna when enabled. Hospital, university and big-pharma openings mostly aren't covered.</p>
  </header>
</div>
<div class="bar">
  <div class="wrap">
    <div class="controls" role="group" aria-label="Filter jobs">
      <button class="chip" id="f-all" data-f="all" aria-pressed="true">All</button>
      <button class="chip" id="f-gta" data-f="gta" aria-pressed="false">Toronto area</button>
      <button class="chip" id="f-remote" data-f="remote" aria-pressed="false">Remote</button>
      <button class="chip" id="f-intern" data-f="intern" aria-pressed="false">Intern &amp; entry</button>
      <input id="q" type="search" placeholder="Search title, company, skill" aria-label="Search">
      <select id="sort" aria-label="Sort"><option value="score">Best match</option><option value="new">Newest</option></select>
    </div>
    <p class="count" id="count"></p>
  </div>
</div>
<div class="wrap">
  <main id="list"></main>
  <footer id="foot"></footer>
</div>

<script>
(function () {
  var data = JSON.parse(document.getElementById("data").textContent);
  var jobs = data.jobs, meta = data.meta;
  var filter = "all", query = "", sort = "score";
  var hidden = {};
  try { hidden = JSON.parse(localStorage.getItem("hiddenJobs") || "{}"); } catch (e) { hidden = {}; }

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
  function ago(iso) {
    if (!iso) return "";
    var d = (Date.now() - new Date(iso).getTime()) / 86400000;
    if (d < 1) return "today";
    if (d < 2) return "yesterday";
    if (d < 60) return Math.floor(d) + " days ago";
    return Math.floor(d / 30) + " months ago";
  }
  var GTA = /toronto|mississauga|brampton|markham|vaughan|oakville|scarborough|etobicoke|north york|richmond hill|pickering|ajax|oshawa|burlington|\bgta\b/i;
  function pct(x) { return Math.round(x * 100) + "%"; }

  var s = meta.stats || {};
  document.getElementById("sub").textContent =
    jobs.length + " matches from " + (s.fetched || 0).toLocaleString() + " postings at " + meta.employers + " employers · " + meta.generated_label;

  function visible() {
    var q = query.toLowerCase();
    var out = jobs.filter(function (j) {
      if (hidden[j.key]) return false;
      if (filter === "gta" && !GTA.test(j.location)) return false;
      if (filter === "remote" && !j.remote) return false;
      if (filter === "intern" && j.level !== "intern" && j.level !== "entry") return false;
      if (q) {
        var hay = (j.title + " " + j.company + " " + j.location + " " + j.skills.join(" ") + " " + (j.department || "")).toLowerCase();
        if (hay.indexOf(q) < 0) return false;
      }
      return true;
    });
    if (sort === "new") out.sort(function (a, b) { return (b.posted || "").localeCompare(a.posted || ""); });
    return out;
  }

  function card(j) {
    var tags = j.skills.map(function (k) { return '<span class="tag">' + esc(k) + "</span>"; })
      .concat(j.flags.map(function (f) { return '<span class="tag warn">' + esc(f) + "</span>"; })).join("");
    var metaBits = ["<b>" + esc(j.company) + "</b>", esc(j.location)];
    if (j.posted) metaBits.push(ago(j.posted));
    if (j.salary) metaBits.push(esc(j.salary));
    var src = j.attribution ? "via " + esc(j.attribution) : esc(j.source);
    var p = j.parts || {};
    return '<article class="card">' +
      '<div class="score" aria-label="Match score ' + Math.round(j.score) + ' out of 100">' + Math.round(j.score) +
        '<div class="meter"><span style="width:' + Math.min(100, j.score) + '%"></span></div>' +
        '<span class="lvl">' + esc(j.level) + "</span></div>" +
      '<h2 class="title"><a href="' + esc(j.url) + '" target="_blank" rel="noopener">' + esc(j.title) + "</a></h2>" +
      '<p class="meta">' + metaBits.join(" · ") + "</p>" +
      (tags ? '<div class="tags">' + tags + "</div>" : "<div></div>") +
      '<p class="why">Resume overlap ' + pct(p.text || 0) + " · title fit " + pct(p.title || 0) +
        (j.terms.length ? " · shared terms: " + esc(j.terms.join(", ")) : "") + "</p>" +
      '<div class="actions">' +
        '<a href="' + esc(j.url) + '" target="_blank" rel="noopener">View posting</a>' +
        (j.apply_url ? '<a href="' + esc(j.apply_url) + '" target="_blank" rel="noopener">Apply</a>' : "") +
        '<button type="button" data-hide="' + esc(j.key) + '">Hide</button>' +
        '<span class="src">' + src + "</span>" +
      "</div></article>";
  }

  function render() {
    var v = visible();
    var nh = Object.keys(hidden).length;
    document.getElementById("count").textContent = v.length + " shown" + (nh ? " · " + nh + " hidden" : "");
    document.getElementById("list").innerHTML = v.length ? v.map(card).join("") :
      '<p class="empty">No jobs match this filter. Try All, or clear the search.</p>';
  }

  document.querySelectorAll(".chip").forEach(function (b) {
    b.addEventListener("click", function () {
      filter = b.getAttribute("data-f");
      document.querySelectorAll(".chip").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      render();
    });
  });
  document.getElementById("q").addEventListener("input", function (e) { query = e.target.value.trim(); render(); });
  document.getElementById("sort").addEventListener("change", function (e) { sort = e.target.value; render(); });
  document.getElementById("list").addEventListener("click", function (e) {
    var k = e.target.getAttribute && e.target.getAttribute("data-hide");
    if (!k) return;
    hidden[k] = 1;
    try { localStorage.setItem("hiddenJobs", JSON.stringify(hidden)); } catch (err) {}
    render();
  });

  var f = ["Dropped: " + (s.not_in_canada || 0) + " outside Canada, " + (s.excluded_title || 0) + " excluded titles, " +
           (s.wrong_level || 0) + " too senior, " + (s.duplicates || 0) + " duplicates, " + (s.below_min_score || 0) + " weak matches."];
  var foot = "<p>" + esc(f[0]) + "</p><p>Sources: " + esc(meta.sources.join(", ")) + ". Remotive listings link back to Remotive, as its terms ask.</p>";
  if (meta.errors && meta.errors.length) foot += "<p>Couldn't reach:</p><ul>" + meta.errors.map(function (e) { return "<li>" + esc(e) + "</li>"; }).join("") + "</ul>";
  document.getElementById("foot").innerHTML = foot;
  render();
})();
</script>
"""
