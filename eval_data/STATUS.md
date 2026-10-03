# K-P2 evaluation preparation — DRAFT, NOT FROZEN

Phase 1 was published at `7076416`. Phase 2 is building independent evaluation
data under Joanna's ownership. Do not use this directory or `testsets/` as input
to any training-data generator. Jabin may open the eventual frozen data only after
publishing `training/DATA_FROZEN.md`.

Current preparation: 150 generated hard-case queries with A-only annotations;
120 English benchmark drafts with exact source-row answer keys; blind packet,
review validator and preregistration draft. See [PREPARATION.md](PREPARATION.md)
for measured progress and the pending source-download, second-review and
IndicTrans2 access steps. These are not frozen test sets.

Required before freeze:

- Source-preserving NQ-open English and Aya Hindi/Tamil selections, with licences,
  original row references, deduplication and documented exclusions.
- Actual IndicTrans2 translations of approximately 150 real English queries per
  language, with model revision and translation provenance. Human or GPT-written
  text must never be labelled `indictrans2`.
- Independently generated hard slices in en/hi/ta and at least 60 cross-sport rows.
- Two independent annotation passes from different model families; annotator B
  receives queries and the rubric, not annotator A's answers. Disagreements are
  adjudicated individually with reasons. No project NLU/rules output is a label.
- Benchmark and preregistration completed before any model results are inspected.
- Validation, measured source/language/slice counts, SHA-256 freeze and handoff.

The public datasets can have appeared in base-model pretraining. "Held out" means
held out from this project's fine-tuning/generation, not proven absent from every
model's pretraining.
