# Phase 2 preparation — not a frozen evaluation release

Prepared on 3 October 2026 by Joanna's GPT-family development agent. The files
below are evaluation material and must not enter a training-generation context.
Jabin must respect the firewall in `OWNERS.md` before opening this directory.

## Current measured state

- 150 generated hard-case candidates: 50 English, 50 Hindi, 50 Tamil. They are
  designed model-authored examples, not real user queries or native-speaker data.
- Annotator A has semantically labelled those 150 items. The annotations have
  passed schema validation. No B review or adjudication has occurred.
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
| `annotations/heldout_a.jsonl` and `.meta.json` | Actual first annotation pass and declared model/context metadata. Do not show these to B. |
| `preparation/blind_heldout/` | Query-only packet, rubric and closed vocabulary for the independent reviewer. |
| `ANNOTATION_RUBRIC.md` | Semantic labelling instructions, planned support scope and disagreement rules. |
| `tools/review.py` | Export allowlisted blind packets; reject missing/duplicate labels, invalid contracts, same declared model families, contaminated review declarations and unresolved disagreements. It does not automatically prove independence or freeze data. |
| `preparation/benchmark_seeds.jsonl` | Designed English prompts; proposed interpretations still require independent annotation. |
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

## Independent second review

Use a different model family in a fresh context that has never seen Jabin's
training examples or A's labels. Access is still awaiting Joanna's answer.
Give that reviewer only `preparation/blind_heldout/` for the generated set.
Record the exact available model label and actual run date; retain the raw reply.
Fresh GPT chats still belong to the same family and do not satisfy the requirement.
Do not ask Jabin's training agent to perform this review.

The metadata JSON must identify `model`, `model_family`, ISO `run_date`, and actual
Boolean `seen_training_data` / `seen_other_annotator_labels`. These are attestations,
not proof established by the script. Disagreements require an explicit chosen
annotation and a specific reason in a separate JSONL file; no missing B entries
may be copied from A. Reconciliation writes drafts and never a `FROZEN.md`.

## Translation requirements still pending

Use the actual [IndicTrans2 distilled English-to-Indic model](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M)
for the required real-query and benchmark translations. Its access gate requires
Joanna to log in and accept the provider's conditions. Never paste access tokens
in chat or commit them. The [model files](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M/tree/main)
include approximately 1.1 GB of safetensors weights; avoid downloading the duplicate
PyTorch weights. Runtime packages add further download/storage requirements.

The project instruction in `document/joanna_split.md` §0 is: **"Ask Joanna before
downloads larger than 1 GB or jobs longer than 20 minutes."** No such download or
long-running translation job has been authorised or started. Before requesting it,
prepare the exact pinned model/package plan, inspect required custom model code,
and estimate runtime with a small sample. Do not label GPT-authored translations
as `indictrans2`. Keep model revision, generation settings, English origin IDs,
raw output and translation-review notes.

## Remaining work before K-P2 DONE

Select real NQ/Aya queries semantically and log exclusions; finish both annotation
passes for all sets, including the benchmark; run actual IndicTrans2 translations;
adjudicate disagreements; publish the required CSVs and provenance; validate counts,
hash and freeze all final inputs before any evaluation output is inspected. Post
the final handoff and push only with an accurate completion status. No measured
model accuracy or benchmark outcome exists yet.
