# Mandarin flashcards

Flashcard sets for Quizlet, in simplified characters with tone-marked pinyin and English. They cover HSK 2–3 vocabulary (from the classic 6-level HSK lists) and everyday phrases. Sets made from the textbook go at the top.

**Import page:** https://claude.ai/artifact/FEBv5K2uPV6Z578vXYmpnL has a Copy title and a Copy cards button for each set, step-by-step import instructions, and a checklist of what you've imported.

## Files

- `sets/*.tsv`: one set per file, one card per line, `characters<TAB>pinyin — English`.
- `sets.json`: the sets in study order, with titles and groups.
- `build_import_page.py`: rebuilds `quizlet-import.html` from the two above. It uses `import-page.template.html`.
- `tools/check_pinyin.py`: compares each card's pinyin with a pinyin dictionary.

## Import into Quizlet by hand

1. On a computer, go to **Create → Flashcard set → Import** in Quizlet.
2. Paste the contents of one `.tsv` file.
3. Set **Between term and definition** to **Tab** and **Between cards** to **New line**.
4. Set the term language to **Chinese (Simplified)** so Quizlet reads the characters aloud.

## Pinyin notes

- Neutral tones have no mark (xièxie), and erhua is written as -r (nǎr).
- 一 and 不 are marked with the tone they take in speech (yíxià, búcuò).
