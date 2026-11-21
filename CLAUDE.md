# Rocking-Raghav-

## Mandarin flashcards (`mandarin/`)

The user is learning Mandarin at roughly HSK 2–3 level, studies with Quizlet, and uses simplified characters.

- Cards live in `mandarin/sets/*.tsv`, one card per line: `characters<TAB>pinyin — English`. Quizlet's import box takes this format directly, with Tab between term and definition and New line between cards.
- `mandarin/sets.json` lists the sets in display order, each with a title, a group and a tile character.
- After changing any set, run `python3 mandarin/build_import_page.py`. Then republish `mandarin/quizlet-import.html` to the existing artifact https://claude.ai/artifact/FEBv5K2uPV6Z578vXYmpnL so the user's link stays the same: read it first, then publish with it as `url`.
- Check pinyin with `pip install pypinyin && python3 mandarin/tools/check_pinyin.py mandarin/sets`.
- Pinyin conventions: tone marks; neutral tones unmarked (xièxie); erhua written as -r (nǎr); the tone changes of 一 and 不 written as spoken (yíxià, búcuò); third-tone sandhi not written (nǐ hǎo).

### Textbook pages come first

The user's textbook is their primary material. When they paste textbook pages:

1. Use the textbook's own words, pinyin and English glosses. If a character or tone is unclear on the page, ask rather than guess.
2. Make sets named `Textbook · Lesson N · Vocabulary` and `Textbook · Lesson N · Sentence Patterns`, using the textbook's lesson numbers. Give them the group `Textbook` and put them at the top of `sets.json`.
3. Write one card per sentence pattern. Term: the pattern and one example from the textbook, e.g. `A 比 B + adjective｜我比他高。`. Definition: the example's pinyin, then what the pattern means, e.g. `Wǒ bǐ tā gāo. — A is more (adjective) than B: I'm taller than him.`
4. Keep each set to 15–35 cards, splitting long lessons into parts. A word that is already in an HSK set still goes into the textbook set.

### Quizlet connector

If the Quizlet connector is connected in the session, use it to create the sets from the TSV files. Its tool generates flashcards rather than importing them verbatim, so compare a few created cards with the TSV before reporting success. If it is not connected, point the user to the import page above.
