"""Build quizlet-import.html from sets.json and the TSV files in sets/.

Run from anywhere:  python3 mandarin/build_import_page.py
The page lists sets in the order of sets.json, grouped by each entry's "group".
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
manifest = json.loads((HERE / "sets.json").read_text(encoding="utf-8"))

sets = []
for entry in manifest:
    lines = [
        ln for ln in (HERE / "sets" / entry["file"]).read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    for n, ln in enumerate(lines, 1):
        if ln.count("\t") != 1:
            raise SystemExit(f"{entry['file']}:{n} needs exactly one tab: {ln!r}")
    sets.append({
        "id": entry["file"].removesuffix(".tsv"),
        "title": entry["title"],
        "group": entry["group"],
        "glyph": entry.get("glyph") or lines[0][0],
        "lines": lines,
    })

data = json.dumps(sets, ensure_ascii=False).replace("</", "<\\/")
template = (HERE / "import-page.template.html").read_text(encoding="utf-8")
if "__SETS_JSON__" not in template:
    raise SystemExit("template is missing the __SETS_JSON__ placeholder")
(HERE / "quizlet-import.html").write_text(template.replace("__SETS_JSON__", data), encoding="utf-8")
print(f"wrote quizlet-import.html: {len(sets)} sets, {sum(len(s['lines']) for s in sets)} cards")
