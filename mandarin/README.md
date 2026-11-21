# Mandarin flashcards

Simplified characters, pinyin with tone marks, and English. The level is HSK 2–3 (the classic 6-level HSK word lists) plus everyday phrases.

Each file in `sets/` is one Quizlet set. There is one card per line, with the term (characters) and the definition (pinyin — English) separated by a tab.

| File | Quizlet set title | Cards |
|---|---|---|
| `01-hsk2-verbs.tsv` | HSK 2 · Verbs | 32 |
| `02-hsk2-people-places.tsv` | HSK 2 · People & Places | 20 |
| `03-hsk2-things-food-time.tsv` | HSK 2 · Things, Food & Time | 24 |
| `04-hsk2-describing-words.tsv` | HSK 2 · Describing Words & Adverbs | 32 |
| `05-hsk2-grammar-numbers.tsv` | HSK 2 · Grammar Words & Numbers | 26 |
| `06-phrases-introductions.tsv` | Phrases · Introductions & Small Talk | 26 |
| `07-phrases-questions-help.tsv` | Phrases · Questions & Getting Help | 25 |
| `08-phrases-time-dates-numbers.tsv` | Phrases · Time, Dates & Numbers | 30 |
| `09-hsk3-verbs.tsv` | HSK 3 · Verbs | 30 |
| `10-hsk3-nouns.tsv` | HSK 3 · Nouns | 31 |
| `11-hsk3-adjectives.tsv` | HSK 3 · Adjectives | 20 |
| `12-hsk3-adverbs-connectors.tsv` | HSK 3 · Adverbs & Connectors | 20 |

## Import into Quizlet by hand

1. In Quizlet, go to **Create → Flashcard set → Import**.
2. Paste the contents of one file.
3. Set **Between term and definition** to **Tab** and **Between cards** to **New line**.
4. Set the term language to **Chinese (Simplified)** so Quizlet reads the characters aloud.

## With the Quizlet connector

Once the Quizlet connector is connected in claude.ai, start a new Claude Code session and ask it to create Quizlet sets from the files in `mandarin/sets/`.

## Notes

- Pinyin shows tones as they are spoken, so 一 and 不 change tone: yíxià, yìqǐ, búcuò.
- Recommended order: the phrase sets (06–08) and HSK 2 (01–05) first, then HSK 3 (09–12).
