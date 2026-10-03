# Paraphrase provenance (dev time only)

`paraphrases/{en,hi,ta}.jsonl` hold about 30 hand-labelled natural-phrasing queries per language (plus a few non-cricket controls).

- Written by Claude Code at dev time, from this instruction: "Write realistic fan questions about cricket records in {language}, including
  sloppy spelling, romanised forms and gender-neutral, women's, men's and both-gender phrasings. Label each with gender_signal, topic,
  family, stat, format from the closed label sets in `src/mak/labels.py`."
- Labels were assigned by the writer, not by the rules system, and checked by `validate_row` in `build_dataset.py`.
- The test-set generator never saw these, and the test sets were never shown to this step (G-011).
- Hindi and Tamil lines need native-speaker review before Gate G3. Until then they are synthetic, not native.
- Nothing here runs at runtime. Models only choose categories; all numbers come from the verified database.
