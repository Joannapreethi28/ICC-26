# Phase 2 preparation and audit trail

The final composition and limitations are in [DATA_CARD.md](DATA_CARD.md).
This directory contains evaluation material; it must never enter training generation.

- `preparation/source_manifest.json`: four official parquet downloads, hashes,
  source sizes and retrieval counts. Raw parquet remains gitignored.
- `preparation/source_candidates.jsonl`, `control_candidates.jsonl`: unlabelled
  retrieval archives. Keyword routes are not semantic labels.
- `preparation/nq_selected_indices.json`, `native_exclusions.jsonl`: natural-source
  sampling and exclusion decisions. Final source text exactly matches original rows.
- `preparation/raw_source_verification.json`: all 390 retained original NQ/Aya rows
  checked against their downloaded official parquet and recorded source indexes.
- `annotations/*_a.jsonl`: original annotation passes, preserved.
- `annotations/*_self_review.jsonl` and `.meta.json`: actual second semantic passes,
  reasons, corrections, reviewer declarations and input bindings where applicable.
- `preparation/translation*_requests.jsonl` and `translation*_output.jsonl`: actual
  input/output history for the pilot, main and reserve IndicTrans2 runs. The suffix
  reserve is an additional quality-replacement pool, not a second evaluation model.
- `preparation/translated_items.jsonl`, `benchmark_translation_items.jsonl`: selected
  raw model outputs, unchanged. Separate exclusion logs retain rejected/unused IDs.
- `tools/review.py`: label and self-review validator; never uses the project NLU.
- `tools/build_benchmark.py`: original English benchmark answer-key builder.
- `tools/build_release.py`: combines reviewed evidence, rejects mismatched sources,
  stale reviews and duplicates, and produces/checks the final release.
- `preparation/release/`: reproducible staging copy. The top-level final CSVs and
  `testsets/FROZEN.md` become authoritative at freeze; old drafts remain historical.

The original `blind_heldout/` packet is retained for audit history. It does not make
this same-session review blind. Joanna explicitly replaced the old second-model
requirement; do not request another reviewer or infer independent agreement.

Rebuild locally with `python eval_data/tools/build_release.py`; verify an existing
freeze with `--check`. `--freeze` creates the first local release and refuses to
replace an existing one. Git publication is a separate step, recorded in handoffs.

Source retrieval uses [Hugging Face's parquet API](https://huggingface.co/docs/dataset-viewer/en/parquet),
[NQ-open](https://huggingface.co/datasets/google-research-datasets/nq_open) and
[Aya](https://huggingface.co/datasets/CohereLabs/aya_dataset). No project classifier
or benchmark model results were used to select or label these questions.
