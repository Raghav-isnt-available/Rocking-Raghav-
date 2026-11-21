"""Compare each card's pinyin with pypinyin's reading and print the differences.

Usage: pip install pypinyin && python3 mandarin/tools/check_pinyin.py mandarin/sets
It also flags convention differences (neutral tones, erhua, third-tone sandhi,
characters with several readings); fix only real errors.
"""
import pathlib
import re
import sys
import unicodedata

from pypinyin import Style, lazy_pinyin

def norm(s, keep_tones=True):
    s = s.lower().replace("…", "").replace("'", "")
    s = re.sub(r"[^\w]", "", s)
    if not keep_tones:
        s = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
        s = unicodedata.normalize("NFC", s)
    return unicodedata.normalize("NFC", s)

hard, soft = [], []
for f in sorted(pathlib.Path(sys.argv[1]).glob("*.tsv")):
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        term, definition = line.split("\t")
        mine = definition.split(" — ")[0]
        han = re.sub(r"[^一-鿿]", "", term)
        if not han:
            continue
        ref = " ".join(lazy_pinyin(han, style=Style.TONE, tone_sandhi=True))
        if norm(mine) == norm(ref):
            continue
        row = f"{f.stem}:{i}  {term}  mine={mine!r}  ref={ref!r}"
        (soft if norm(mine, False) == norm(ref, False) else hard).append(row)

print("== letters differ (check carefully) ==")
print("\n".join(hard) or "none")
print("\n== tone marks differ only ==")
print("\n".join(soft) or "none")
