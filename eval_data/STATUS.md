# K-P2 evaluation release v1

Final reviewed composition: 350 English, 208 Hindi and 221 Tamil NLU rows;
61 cross-sport rows; 188 answer-benchmark questions (120 en / 34 hi / 34 ta).
Actual IndicTrans2 inference and semantic self-review are complete. See
[DATA_CARD.md](DATA_CARD.md) for provenance, exclusions, licences and limitations.

`testsets/FROZEN.md` and `release_manifest.json` are the authoritative freeze
records once present. Validate with `python eval_data/tools/build_release.py --check`.
Git publication status is recorded separately in `document/handoffs.md`; local
completion does not prove a successful push.

Joanna selected Astra as annotator and reviewer: one reviewer, prior labels visible,
no independent agreement or completed human/native-speaker validation. No classifier
accuracy or answer-benchmark results are claimed. All source and translation rows
retain their original text; raw model output and review corrections are preserved.

**Training firewall:** Jabin must publish `training/DATA_FROZEN.md` before opening
`testsets/` or `eval_data/`. Never send these inputs to a training-data generator.
