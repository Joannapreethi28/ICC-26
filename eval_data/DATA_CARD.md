# Evaluation release v1 — Make AI Know Her

Prepared by Joanna/Astra on 3 October 2026, before inspecting held-out classifier
evaluation or answer-benchmark outputs. This is evaluation material,
not training data. Jabin must publish `training/DATA_FROZEN.md` before opening
`testsets/` or `eval_data/`. Never feed these files to a training generator.

## Measured composition

| File | Total | Natural source | Actual IndicTrans2 | Designed hard cases |
|---|---:|---:|---:|---:|
| `testsets/nlu_en.csv` | 337 | 287 NQ-open | 0 | 50 |
| `testsets/nlu_hi.csv` | 203 | 8 Aya | 150 | 45 |
| `testsets/nlu_ta.csv` | 210 | 21 Aya | 142 | 47 |
| `testsets/xsport.csv` | 60 | 59 NQ-open + 1 Tamil Aya | 0 | 0 |

The answer benchmark has **188** questions: **120 English, 34 Hindi, 34 Tamil**.
The English design covers 25 golden intents with four neutral paraphrases each,
plus 20 explicit/unsupported/ambiguous/general controls. Each translated-language
benchmark covers all 25 intents and nine controls. Tamil uses a different retained
bowling-record paraphrase and both-category control after translation review.
Compare paired arms within a question, and use origin/intent clusters when pooling.

The 810 classifier/transfer rows and 188 answer questions have provenance in
`provenance_v1.jsonl`. Counts are dataset composition, **not model accuracy**.
`release_manifest.json` records counts by language, source, slice and decision,
all final-file hashes, annotation reports and evidence hashes. `testsets/FROZEN.md`
is created only by the final freeze command.

## Natural source collection and selection

The official parquet download contained NQ-open train 87,925 and validation 3,610
rows; Aya train 202,362 and test 1,750 rows. Collection scanned 91,535 English,
1,153 Hindi and 14,133 Tamil prompts. Keyword retrieval produced 4,800 candidates
and a separate deterministic sample of 100 potential controls. Retrieval assigns
no labels. Original spelling, punctuation, whitespace, split, physical row index,
download URL, licence and file SHA-256 are retained.

English cricket selection used a stronger 486-row retrieval pool, manual semantic
eligibility screening, and an ID-hash sample of 260 from a 381-row primary pool.
Another 20 cricket-general and 20 non-sport controls were selected semantically.
One initially statistical item became cricket-general during self-review. The
pool screen is purposive, not a probability sample of all cricket searches.
`preparation/nq_selected_indices.json` records this process; exclusion from a
sampling pool is not itself a definitive topic label.

All 75 Hindi/Tamil cricket/transfer candidates were read. We retained 29 NLU
prompts and one Tamil FIFA transfer prompt, and logged 45 exclusions in
`preparation/native_exclusions.jsonl`. Exclusions include unfinished paragraphs,
article continuation/summarization, unrelated multiple-choice options, prompts
with incompatible subquestions, and repeated question-prefix variants. The
approximate 12-Hindi/39-Tamil targets were not padded with unsuitable prompts.
Only 8 Hindi and 21 Tamil NLU items remain; neither subset supports precise claims
about native-user performance. Aya is contributed task prompts, not a measured
sample of real cricket fans' requests. Many retained Hindi examples concern one
player, and many Tamil examples are school-style questions.

Cross-sport selection has 20 English football, 19 tennis, 20 basketball and one
Tamil FIFA question. Only `gender_signal` and `topic` are scored. All cricket
family/stat/format/decision fields are empty. Event or country names alone do not
force men under the rubric. This is a narrow transfer check, not other-sport
factual accuracy or demonstrated fairness across all sports.

All **390 reviewed original NQ/Aya rows** were checked against their downloaded
parquet bytes and exact recorded source-row text. The four parquet hashes and
matched counts are in `preparation/raw_source_verification.json`. Of these, 376
remain after the overlap screen below. Raw parquet is
gitignored; the manifest and source-preserving selected items are committed.

## Translation provenance and review

Actual local inference used `ai4bharat/indictrans2-en-indic-dist-200M` revision
`173b94239f7c38886b2747b8d4a5db771a7e1232`, CPU float32, four Torch threads,
five beams, no sampling, one return, maximum 256 tokens and batch size two.
Pinned installation, processor source, package versions and hashes are documented
in `TRANSLATION_SETUP.md` and `preparation/indictrans2_install.json`.

An ID-hash sample of 150 English natural queries per language was translated,
then reserve queries supplied replacements for failures and exact duplicates.
After a four-output pilot, the main job generated 370 outputs in **248.98 seconds**
of measured generation time; a reserve job generated 85 in **56.08 seconds**.
These are generation timings for this laptop/run, not an end-user latency claim.
Final retention is 292 NLU and 68 benchmark translations after overlap screening.
Raw outputs, token IDs,
preprocessed inputs, source IDs, timestamps, model revision and settings are kept.

Every retained target text was compared with its original and read again with
its labels. Exclusions include entity replacement, lost international qualifiers,
triple-century/count mistakes and changed recommendation direction. Reserve
items not needed for the final size are identified as unused, not certified good.
Exclusion logs retain IDs and reasons. Exact normalized target-text duplicates
are removed; similar paraphrases remain and are correlated. No output was edited
by the agent and passed off as an IndicTrans2 result. Some retained search fragments
are awkward; semantic review is not native-speaker fluency validation.

## Labels, review and limits

Joanna explicitly selected Astra as annotator and reviewer. All final questions
have a recorded second semantic pass. This is **one GPT-family reviewer reviewing
its own work**, with prior labels visible. Original annotations are preserved,
corrections have reasons, `adjudicated` is blank, and per-row notes declare
`review_method=same_agent_self_review`. There is no independent annotator agreement
or completed human/native-speaker review. The project classifier and rules were
never used to create or approve labels. Structural validators cannot certify
semantic correctness; a model can repeat its own mistakes.

After labels and second passes were recorded, a newly fetched Jabin handoff was
read for integration. It included aggregate dev-only observations and illustrative
pilot examples. No corpus or prediction-file contents entered the reviewer's
context; those handoff observations did not change any question or label.

An automated, read-only comparison then treated the already-frozen training,
calibration and messy-calibration strings opaquely. Seven evaluation questions
had exact normalized overlaps; a broader character-similarity screen flagged 30
rows in total at 0.92 or above. All 30 were excluded **before evaluation freeze**,
without changing their labels or seeing any classifier output. The screen reports
only evaluation IDs/counts, never training text. `preparation/release_exclusions.jsonl`
records the exclusions; `preparation/final_overlap_audit.json` binds the final CSV
hashes and corpus hashes to a clean check. This reduced the approximate 50 hard-case
and 150 translation targets slightly; the measured counts above are authoritative.
It also introduces a conservative similarity-based selection bias: near matches
can be valid contrastive questions, not true leakage. Zero string matches does not
prove absence of semantic overlap or pretraining exposure.

`ANNOTATION_RUBRIC.md` fixes the closed labels and conservative support decisions.
Explicit country/season/opponent filters are not answered with unrestricted
headline facts. Unqualified domestic-capable T20 is not silently changed to T20I.
Awards and generic player wording do not alone imply men's cricket. These are
documented annotation choices, including ambiguous natural-search interpretations.
Report results separately by language, source and slice, with denominators and
unsupported coverage; do not pool the small native sets with translations and
call the result native-user accuracy.

Public NQ/Aya data may already appear in base-model pretraining. Held out means
isolated from **this project's** training generator, not proven absent from all
pretraining. NQ has repeated templates and old relative dates. Strong keyword
retrieval underrepresents queries expressed without cricket-specific words.
Generated hard cases reflect their author's assumptions. Cross-language questions
share English origins; benchmark paraphrases share only 25 underlying records.
The preregistration therefore requires intent-cluster sensitivity analysis.

## Answer keys and preregistration

Answer fields copy the exact women's and men's rows from `data/golden/records_v1.csv`.
Score only the requested category. Unsupported/general/entity-unresolved rows have
no invented fact key. The snapshot date is 3 October 2026; every fact keeps its own
`as_of`, sources and verification caveats. This phase did not freshly reverify the
cricket facts. Existing caveats include single-source records and repeated URLs.

`PREREGISTRATION.md` fixes Llama model, samples/seeds, four arm behaviours, exact
prompts, scoring denominators and paired bootstrap before model outputs exist.
Its hash is frozen with the release. No accuracy, visibility improvement, agreement
rate or benchmark result has been measured here. Future answer scoring still
requires the preregistered human review; it has not been performed in Phase 2.

## Credits and licences

- [NQ-open](https://huggingface.co/datasets/google-research-datasets/nq_open),
  Google Research / Natural Questions: CC BY-SA 3.0. Preserve attribution on source
  questions and their translations; the translation model's MIT licence does not
  replace the source-data licence.
- [Aya dataset](https://huggingface.co/datasets/CohereLabs/aya_dataset), Cohere For AI
  and Aya contributors: Apache-2.0. The retained text is unchanged.
- [IndicTrans2](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M),
  AI4Bharat, Gala et al., *IndicTrans2: Towards High-Quality and Accessible Machine
  Translation Models for all 22 Scheduled Indian Languages*: MIT model.
- [IndicTransToolkit processor](https://github.com/VarunGumma/IndicTransToolkit/tree/0e68fb5872f4d821578a5252f90ad43c9649370f):
  MIT. Its source revision and licence hash are recorded; binaries remain local.
- Designed questions and repository tooling follow the repository Apache-2.0
  licence. Golden factual sources/credits are preserved per row; this licence
  does not relabel third-party material.

## Reproduce and verify

From the repository root with project dependencies installed:

```powershell
python eval_data/tools/build_release.py --check
python eval_data/tools/build_release.py
```

The first verifies the frozen hashes without modifying files. The second rebuilds
the reviewed release under `eval_data/preparation/release/` without running models,
changing labels, or replacing the freeze. Original-source retrieval is reproducible
with `fetch_sources.py`; model installation/inference commands are in
`TRANSLATION_SETUP.md`. Never silently replace frozen v1 after inspecting results;
record a dated amendment and create a new version.
