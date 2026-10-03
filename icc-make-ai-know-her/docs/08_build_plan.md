# 08. Build plan (your task list)

Rules: everything below gets built (no cut line). FREE ONLY. Building stops **Sun 4 Oct 2026, 8 pm**; Mon 5 Oct is buffer and submission only (no new features). Sir Jabin decides who does what; this plan is ordered by dependency, not by person. Update `CHANGELOG.md` and `docs/05_decisions_log.md` as you go. Ask Sir Jabin only when truly blocked.

## 0. Ground rules for the build
- Plan each workstream briefly before coding; commit small; write tests with the code.
- Every number shown to a user needs `source`, `trust` (verified/computed) and `as_of`.
- No runtime dependency on any paid or closed model. Dev-time use of Claude Code/GPT 6 is fine (code, training-data generation).
- When a quality gate fails, fix it and document; do not weaken the gate silently.
- Do not run long jobs (training, big downloads) without telling Sir Jabin what, why and the expected time.

## 1. Workstreams, in dependency order (parallelise where independent)
**WS1. Repo, environment, CI-lite.** Scaffold the layout in docs/07 section 9; pin versions; `pytest` runs; pre-commit optional. *Done when:* a fresh clone installs and runs tests.

**WS2. Data layer.** Download Cricsheet international T20I and ODI zips for men and women (check exact names on https://cricsheet.org/downloads/; the women's zips are named like `t20s_female_json`, `odis_female_json`), `people.csv`, `names.csv`; parse to DuckDB; derive player gender from which gender's matches they appear in; add Cricinfo/Opta/Pulse IDs from the register; pull Wikidata QIDs, gender (P21), Cricinfo ID (P2697) and Hindi/Tamil labels for players and teams. Load `data/records_v1.csv` as the golden set. Compute records/stats and reconcile with golden; write a reconciliation report (differences expected because Cricsheet withholds some matches). *Gate G1:* database loads; computed T20I/ODI runs/wickets/team totals/highest scores agree with golden or differences are explained and listed; every golden row has `as_of`.

**WS3. Facts API (Python).** Implement the query templates in docs/07 section 5 (groups A-F, H; G only with a verified free source). Return provenance and trust. *Gate G2:* all 50 golden rows are returned correctly by the matching templates (unit tests); unsupported intents return `unsupported`.

**WS4. Classifier: rules and lexicons.** Multilingual lexicons for gender cues (English, Hindi incl. Hinglish, Tamil incl. Tanglish) including grammatical-gender cues; intent/format patterns; entity resolver. This is the baseline and the override layer. Have native-speaker review the Hindi and Tamil lexicons and test sets. *Gate G3:* rules-only accuracy measured on the hand-written test sets (the baseline numbers).

**WS5. Classifier: trained Laya.** Follow docs/09 exactly: label schema, data generation, hand-written test sets, fine-tune laya-multilingual, calibrate, ablate against rules-only and a Qwen-class LoRA parser, test injection robustness, export for CPU. *Gate G4 (proposed targets, adjust only with a written reason):* gender-signal accuracy >= 98% per language after rules override; stat/format accuracy >= 90% English, >= 85% Hindi, >= 80% Tamil on the hand-written test sets; ECE <= 0.05 after calibration; the trained model beats rules-only on the messy/multilingual test set (report either way, with n and confidence intervals); CPU latency measured.

**WS6. Policy and composer.** Implement the decision table as a pure function with exhaustive tests; templates in en/hi/ta; decision trace. *Gate G5:* all policy cases tested including fail-safe, injection strings, mixed-gender mentions ("Kohli vs Mandhana"), surname ambiguity.

**WS7. Interfaces.** FastAPI; MCP server; Gradio demo (side-by-side with real captured answers only, free-text box, decision trace, coverage panel); deploy as a free Hugging Face Space; README with one-line install for the MCP tool. *Gate G6:* the hosted Space answers the headline questions in English, Hindi and Tamil, and an MCP client can call the tool.

**WS8. Record pages.** Static generator producing a page per supported neutral question with both records, sources, as-of, and JSON-LD; deploy free. *Gate G7:* pages validate (structured-data validator) and contain both records.

**WS9. Evaluation.** Implement docs/11: benchmark builder (EN 100+ questions; per-language sets), scorer, the three-arm test with a free local open model via Ollama (same model, plain / prompt-only / layer), classifier ablation, per-language metrics with confidence intervals, unnecessary-intervention test, cross-sport transfer test on unseen sports, optional pilot sheet for consumer apps. Save every raw output. *Gate G8:* one command regenerates all result tables and plots.

**WS10. Cross-sport adapter proof.** Define the `SportAdapter` interface; implement a small football (and optionally tennis/basketball) adapter from a free source (candidates: Wikidata/Wikipedia lists, StatsBomb open data; **verify licence and women's coverage first**); 10-20 questions with ground truth. *Gate G9:* same policy engine answers football neutral questions with both genders and sources.

**WS11. Documentation and deliverables.** Architecture doc, model card, data card, benchmark card, limits page, README; 5-slide deck, summary, 3-minute video script and recording plan (docs/12). Every deck number carries a date and a source; label target vs measured.

**WS12. Hardening.** Injection test set; error handling; rate limits; refresh job; reproducibility (seeds, versions); license/attribution page (Cricsheet ODC-BY credit; Wikidata CC0; Laya Apache-2.0); accessibility pass on the demo (labels, contrast, keyboard).

## 2. Time blocks (no owners assigned)
| Block | Target outcomes |
|---|---|
| Sat 3 Oct (rest of day) | WS1, WS2, WS3 to G2; start WS4 lexicons and the hand-written test sets; start generating training data; kick off first Laya fine-tune as early as data allows |
| Sat night / Sun early | WS5 iterations to G4; WS6; WS7 skeleton |
| Sun 4 Oct morning-midday | WS7 complete (Space + MCP), WS8, WS9 runs; WS10 |
| Sun 4 Oct afternoon | Final evaluation runs; WS11 deck, summary, video recording; WS12 |
| **Sun 4 Oct 8 pm** | **Build freeze.** Only bug fixes after this |
| Mon 5 Oct | Buffer, re-verify dynamic records (Mandhana, Rashid, Deepti, Kohli etc. may have changed), final submission. Confirm exact deadline time/timezone on the Ignyte page |

## 3. Training-data and model risks to manage
- Laya untrained is near chance; Tamil is weakest. Budget the most iteration for Tamil data quality and test coverage. If a gate fails, add data, adjust the hierarchy, re-calibrate, or try the Qwen-class parser; report all attempts honestly.
- Do not let generated paraphrases leak into the hand-written test sets.
- Keep the evaluation set private from the generators (Sir Jabin's own research: public-style benchmarks overstate accuracy).

## 4. Definition of done
- [ ] Hosted free Space with demo + API + MCP, working in en/hi/ta
- [ ] Repo public (or shareable) with README, licences, reproducible setup
- [ ] Trained model published (weights + model card) with per-language results and calibration
- [ ] Verified database + reconciliation report; no unverified rows in the golden set (dropped, not guessed)
- [ ] Three-arm result tables, ablation, cross-sport transfer, UIR, with n and intervals
- [ ] Record pages live
- [ ] Deck (5 slides), summary, 3-minute video
- [ ] Every figure labelled target / measured / illustrative; limits stated

## 5. First hour checklist for the coding agent
1. Read CLAUDE.md and docs 00-09.
2. Check Python, GPU (`nvidia-smi`), disk, network access to cricsheet.org, huggingface.co, wikidata.org.
3. Write a one-page plan for WS1-WS3 and start.
4. Read the Laya model card/README and the fine-tuning notebook linked there (https://github.com/NandhaKishorM/laya, notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb) to learn the exact training-data format before writing the data builder.
