# Phase 2 preparation — not a frozen evaluation release

Prepared on 3 October 2026 by Joanna's GPT-family development agent. The files
below are evaluation material and must not enter a training-generation context.
Jabin must respect the firewall in `OWNERS.md` before opening this directory.

## Current measured state

- 150 generated hard-case candidates: 50 English, 50 Hindi, 50 Tamil. They are
  designed model-authored examples, not real user queries or native-speaker data.
- Astra annotated and then semantically rechecked all 150 generated items under
  Joanna's selected same-agent method. All original labels were retained; per-item
  review notes, original/reviewed annotations and input hashes are recorded.
  This is not independent agreement or human review. The resulting CSVs remain
  in `preparation/self_reviewed_heldout/`, not the final frozen test sets.
- 120 English benchmark draft questions: 100 neutral paraphrases across 25
  golden intents and 20 controls/unsupported/ambiguous cases. Golden answer fields
  copy the source CSV rows exactly, including evidence limitations and dates.
- No natural-query sources have been downloaded in this session yet; no source
  selection counts, IndicTrans2 translations, or frozen results are claimed.
- The full first-phase snapshot is on `main` at `7076416`. Phase 2 remains on the
  local `joanna/k2` branch until the remaining gates are satisfied.

## Files and purpose

| File | Purpose |
|---|---|
| `tools/fetch_sources.py` | Download official source parquet under a 900 MiB ceiling; preserve checksums, row references, spelling and duplicate references. Keyword retrieval produces candidates, never labels. |
| `preparation/heldout_candidates.jsonl` | Model-generated difficult queries with source and generator provenance. |
| `annotations/heldout_a.jsonl` and `.meta.json` | Original annotation pass and declared model/context metadata, retained for comparison. |
| `annotations/heldout_self_review.jsonl` and `.meta.json` | Actual same-agent review notes and process metadata. |
| `preparation/self_reviewed_heldout/` | 150 reviewed generated rows as draft CSVs, with blank adjudication values and a correction/provenance manifest. |
| `preparation/blind_heldout/` | Existing query-only packet and vocabulary; using this does not make same-session self-review blind. |
| `ANNOTATION_RUBRIC.md` | Semantic labelling instructions, planned support scope and disagreement rules. |
| `tools/review.py` | Validate the selected self-review method and log corrections without false agreement claims. The original dual-review validator is retained separately. Neither route automatically freezes data. |
| `preparation/benchmark_seeds.jsonl` | Designed English prompts; proposed interpretations still require semantic review. |
| `tools/build_benchmark.py` | Rebuild the unreviewed benchmark draft and exact golden answer key. |
| `preparation/benchmark_en_draft.csv` and `.manifest.json` | English draft with source hashes, counts and source-evidence caveats. |
| `PREREGISTRATION.md` | Draft prompts, settings, scoring denominators and bootstrap design; no results. |

## Resume the public-source step

From the repository root with the project Python environment:

```powershell
python eval_data/tools/fetch_sources.py
```

The current Codex execution sandbox cannot make the download connections. Joanna
has been given the full-path equivalent to run in normal PowerShell. The script
does not require a Hugging Face account for these public datasets. If it fails,
retain its output; do not invent replacement source rows. After downloading,
`--extract-only` repeats checksum-validated retrieval offline.

Official references:
[dataset parquet API](https://huggingface.co/docs/dataset-viewer/en/parquet),
[NQ-open](https://huggingface.co/datasets/google-research-datasets/nq_open),
[Aya](https://huggingface.co/datasets/CohereLabs/aya_dataset).
Project source credits: NQ-open CC BY-SA 3.0; Aya Apache-2.0. Preserve attribution
in the final benchmark/data card and record the actual source file hashes.

## Review method chosen by Joanna

On 3 October 2026 Joanna instructed Astra to be the reviewer and declined another
Claude chat. This supersedes the earlier two-family requirement; the decision and
the shared CSV clarification are recorded in `document/handoffs.md`. Do not ask
Joanna for a second reviewer again unless she changes this instruction.

Astra semantically rechecks every question and label against the rubric, records
a `review_note` per item, preserves the first pass and explains corrections.
The same session has seen its prior labels, so a query-only packet does not make
this blind. No training-data generator or project NLU classifier labels the data.

Use `tools/review.py self-review` with `--items`, `--a`, `--reviewed`, `--meta` and
`--out`. Metadata identifies `model`, `model_family`, ISO `run_date`,
`review_method=same_agent_self_review`, `prior_labels_visible=true`,
`seen_training_data=false` and `independent=false`. These are honest process
declarations; the validator cannot independently certify them. Every reviewed
annotation needs a reason. Output uses blank `adjudicated` (not applicable),
method-identifying notes and a manifest with actual corrections. It stays a draft
until all remaining source, translation and freeze requirements are satisfied.

One model can repeat its own mistakes, particularly on questions it authored.
Report one reviewer and no independent agreement rate or completed human review.

## Translation requirements still pending

Use the actual [IndicTrans2 distilled English-to-Indic model](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M)
for the required real-query and benchmark translations. Its access gate requires
Joanna to log in and accept the provider's conditions. Never paste access tokens
in chat or commit them. The [model files](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M/tree/main)
include approximately 1.1 GB of safetensors weights; avoid downloading the duplicate
PyTorch weights. Runtime packages add further download/storage requirements.

Update: Joanna reports that account creation, email verification and model access
acceptance are done. The prepared terminal helper is awaiting execution; see
[HF_ACCESS.md](HF_ACCESS.md). No model weights or translation runtime are installed.

The project instruction in `document/joanna_split.md` §0 is: **"Ask Joanna before
downloads larger than 1 GB or jobs longer than 20 minutes."** No such download or
long-running translation job has been authorised or started. Before requesting it,
prepare the exact pinned model/package plan, inspect required custom model code,
and estimate runtime with a small sample. Do not label GPT-authored translations
as `indictrans2`. Keep model revision, generation settings, English origin IDs,
raw output and translation-review notes.

## Remaining work before K-P2 DONE

Select real NQ/Aya queries semantically and log exclusions; finish annotation and
self-review for all sets, including the benchmark; run actual IndicTrans2
translations; record corrections; publish the required CSVs and provenance; validate counts,
hash and freeze all final inputs before any evaluation output is inspected. Post
the final handoff and push only with an accurate completion status. No measured
model accuracy or benchmark outcome exists yet.
