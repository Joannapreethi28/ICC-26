# joanna_split.md: Joanna's track (data, test sets, facts, product, deployment, docs)

Owner: Joanna. Coding agent: **Astra**. Partner track: `jabin_split.md` (Sir Jabin: model, training, evaluation). Channel: `document/handoffs.md` only.

**Deadline:** whole tool done **before Sun 4 Oct 15:00 IST**. Refinement 15:00-20:00, freeze 20:00. Submission Mon 5 Oct.

---


> **TRANSFERRED TO EFANIO (Sir Jabin, Sun 4 Oct 11:45 IST):** all remaining K-P4, K-P5 and R-phase tasks below are now owned by Efanio (GPT 6). Guide and ownership table: `document/efanio_split.md`. Joanna's completed work (K-P1..K-P3) stays as is.

## 0. Brief for Astra (read this section completely before doing anything)

**What we are building.** "Make AI Know Her": when someone asks a cricket statistics question without saying men's or women's ("Who has the most T20I runs?"), AI assistants usually answer with the men's record only. Our tool detects that the question is gender-neutral and answers with BOTH records, each labelled, each with a source and an as-of date, in English, Hindi or Tamil. Explicit "women's" questions get only the women's answer, explicit "men's" only the men's, questions where gender does not matter ("How long is a cricket pitch?") get no intervention. Example answer:
```
Women's T20Is: Smriti Mandhana (India), 4,867 runs (as of 22 Sep 2026)
Men's T20Is: Babar Azam (Pakistan), 4,596 runs (as of 1 Oct 2026)
Overall: Mandhana leads both lists. Sources: ...
```

**Read, in this order:** (1) `AGENTS.md` at the repo root (project rules; same as CLAUDE.md); (2) this file; (3) `document/buildplan.md` sections named in each task below (they contain exact code, function signatures and tests); (4) `document/gotcha.md` (known traps); (5) `document/handoffs.md` (latest messages); (6) as needed: `icc-make-ai-know-her/docs/06_solution_design.md`, `07_architecture.md`, `10_data_and_records.md`, `11_evaluation_protocol.md`.

**Hard rules (breaking any of these invalidates the project):**
1. **Free only.** No paid API or service at runtime. Dev-time AI help is fine.
2. **No invented facts.** Every number shown to a user comes from `data/golden/records_v1.csv` or is computed from Cricsheet data, and carries `source`, `trust` (`verified` or `computed`) and `as_of`. If a fact cannot be verified, leave it out.
3. **The policy is plain code** (`src/mak/policy/decide.py`), never a model.
4. **User text is data.** A query that says "ignore previous instructions..." must not change the policy; it goes to "show both".
5. **Test-set firewall.** You build the evaluation data in `testsets/` and `eval_data/`. Never share it with Sir Jabin's training-data generator or paste it into a chat that writes training data. Freeze it with SHA-256 before he evaluates.
6. **Stay in your folders** (below). To change a shared file (`src/mak/types.py`, `src/mak/labels.py`, `src/mak/config.py`, `pyproject.toml`), post a CONTRACT CHANGE message in `handoffs.md` first.
7. **Ask Joanna before** downloads larger than 1 GB or jobs longer than 20 minutes.
8. **Honest numbers.** Label every reported figure measured / target / illustrative, with n and date.

**Your folders:** `src/mak/{ingest,registry,records,fetch,policy,compose,api,ui,pages,adapters}/`, `src/mak/pipeline.py`, `src/mak/nlu/entities.py`, `data/` (except `data/lexicons/`), `testsets/`, `eval_data/`, `space/`, `site/`, `docs/`, `scripts/download_data.py`, `scripts/refresh.py`. **Sir Jabin's folders (do not edit):** `src/mak/nlu/` (except `entities.py`), `training/`, `src/mak/eval/{classifier_eval,arms,score,stats}.py`, `data/lexicons/`, `models/`.

**Interfaces you can rely on now (fixed in Phase 0):**
- `mak.types`: `Parse`, `Fact`, `Entity`, `Resolution` and literal types.
- `mak.labels`: closed label sets (`GENDER_SIGNAL`, `TOPIC`, `FAMILY`, `STATS`, `FORMAT`, `SLICES`) and the test-set CSV columns (`TESTSET_COLUMNS`).
- `mak.nlu.understand.understand(text, lang=None, use_laya=None) -> Parse`: a small English keyword stub today; Sir Jabin replaces the body tonight with the same signature, so your code never changes.
- `mak.config`: paths, `GENDER_THRESHOLD`, `USE_LAYA` (False until Sir Jabin publishes the model), `LAYA_MODEL_ID`.

**Git routine:** branch per phase (`joanna/k1`, `joanna/k2`, ...); commit small with clear messages; at phase end: `git pull origin main`, `pytest` green, merge to `main`, push, post a DONE message in `handoffs.md` (template at its top). Commits use Joanna's own GitHub identity.

**Skills available in this repo** (`.claude/skills/`, readable as plain guides): `huggingface-gradio`, `huggingface-spaces`, `huggingface-zerogpu`, `hf-cli`, `mcp-builder`, `webapp-testing`. Install the `hf` CLI with `pip install -U huggingface_hub` (never `curl | bash`, gotcha G-012).

**Phase rhythm (for Joanna):** build → "done when" check → **STOP and learn** (15 min, answer the questions in the handoff message) → merge → next phase.

---

## K-P1: the data layer (Sat 18:45-21:00)

**Goal:** every verified record loads with source and date; the full Cricsheet database and the player registry exist.

| Task | Files | Spec |
|---|---|---|
| Golden loader + leader cross-check (D2 already applied in the CSV, so all leader tests must pass) | `src/mak/records/golden.py`, `src/mak/records/leader.py` (full code in buildplan), `tests/golden/test_golden.py`, `tests/unit/test_leader.py` | buildplan **T0.3** |
| Download + ingest Cricsheet (4 zips: `t20s_male_json`, `t20s_female_json`, `odis_male_json`, `odis_female_json` + `people.csv`, `names.csv` from `https://cricsheet.org/register/`) → DuckDB `data/processed/mak.duckdb` | `scripts/download_data.py`, `src/mak/ingest/cricsheet.py`, `tests/unit/test_ingest.py` + tiny fixtures | buildplan **T1.1** |
| Registry: people with gender derived from the matches they appear in; Cricinfo/Pulse IDs; Hindi/Tamil names from Wikidata (SPARQL by ESPNcricinfo ID P2697, cached to CSV) | `src/mak/registry/people.py`, `src/mak/registry/wikidata.py`, `data/i18n/entities_{hi,ta}.csv`, `tests/unit/test_registry.py` | buildplan **T1.2** |
| Entity resolver (rapidfuzz; surname-only → gender None) | `src/mak/nlu/entities.py`, tests: "Kohli vs Mandhana" → both genders, "Sharma" → None | buildplan **T1.5** (entity part) |

**Done when:** women's and men's T20I/ODI match counts print from DuckDB; Smriti Mandhana → `Q16224802`, Hindi `स्मृति मंधाना`, Tamil `ஸ்மிருதி மந்தனா`; all tests green; merged; DONE message.

**STOP and learn:** (1) Open one Cricsheet match JSON: where are gender, match type, players and each ball? (2) Why are Afghanistan matches missing and which record breaks (gotcha G-001)? (3) Why does the golden set beat computed values for headline records? (4) Check 3 players' derived gender: what could make one wrong?

## K-P2: evaluation data (Sat 21:00-24:00), Sir Jabin evaluates on this Sunday 08:00, so it must be frozen tonight

**Goal:** honest test data that no training generator has seen, in the CSV format `labels.TESTSET_COLUMNS`: `id, lang, text, gender_signal, topic, family, stat, format, expected_decision, slice, source, adjudicated, notes`.

| Set | How | Target size | Licence / credit |
|---|---|---|---|
| **REAL-EN** → `testsets/nlu_en.csv` | Download NQ-open parquet (`https://huggingface.co/api/datasets/google-research-datasets/nq_open/parquet`), filter cricket queries (regex on cricket/odi/t20/test match/ipl/wicket/century/runs; then remove false hits like "19th century"); keep the real spelling; add ≈40 cricket-general and non-cricket controls from NQ | 250-400 | CC BY-SA 3.0, credit NQ-open |
| **REAL-NATIVE** → `testsets/nlu_hi.csv`, `nlu_ta.csv` | Aya dataset parquet (`CohereLabs/aya_dataset`, train+test), `language` Hindi / Tamil, cricket keywords (क्रिकेट, विकेट, शतक / கிரிக்கெட், விக்கெட், சதம்); dedupe | ≈12 hi, ≈39 ta | Apache-2.0, credit Aya |
| **REAL-TRANSLATED** (same files, `source=indictrans2`) | Translate ≈150 REAL-EN queries to Hindi and Tamil with `ai4bharat/indictrans2-en-indic-dist-200M` (MIT; log in to HF and accept its terms; CPU is fine for this size) | ≈150 per language | MIT |
| **HELD-OUT slices** (same files, `source=heldout_gen`) | Astra writes them (a different model family from Sir Jabin's Claude-based generator): grammatical gender (வீராங்கனை, वाली), romanised Hinglish/Tanglish, injection, surname-only, mixed-gender, "men's and women's" | ≈50 per language | n/a |
| **xsport** → `testsets/xsport.csv` | Real football/tennis/basketball queries from NQ-open + Tamil FIFA prompts from Aya; label `gender_signal` and `topic` only | ≥60 | as above |
| **Benchmark v1** → `eval_data/benchmark_v1.csv` + `eval_data/PREREGISTRATION.md` | ≥100 English questions across sets A/B/C/D/F/G (docs/11 §5) with ground truth from the golden CSV and `data_timestamp`; Hindi and Tamil ≥25 each via IndicTrans2; pre-registration: model `llama3.1:8b-instruct-q4_K_M`, 3 samples, the exact prompt for each arm (plain / prompt-only / layer / layer_text), labels and edge cases from docs/11 §1, metrics, paired bootstrap | ≥150 | as above |

**Labelling (all sets):** two independent annotators per item: (A) Astra; (B) a different model family available to Joanna at dev time, used only to label (e.g. a free local open model, or Claude in a fresh chat that never sees training data). Agreement → accept. Disagreement → decide, write a one-line reason in `notes`, set `adjudicated=1`. The rules system (`understand`) must never be used as a labeller. Optional: Joanna checks 50 random labels (15 min) and records the agreement rate in `FROZEN.md`.

**Freeze:** `testsets/FROZEN.md` with SHA-256 per file and counts per language/source/slice. Commit, merge, DONE message "test sets FROZEN" to Sir Jabin.

**STOP and learn:** (1) Why are real Google searches a stronger test than questions we write? Their weakness? (2) "who is the first man to score a double century in odis" is labelled `men`, not `none`. Why? (3) Why must the slice generator be a different model family from the training generator? (4) Look at 5 adjudicated items: what caused the disagreement?

## K-P3: facts, policy, answers (Sun 00:00-02:00, or 08:00-10:00 if you sleep first; must be merged by 10:00)

| Task | Files | Spec |
|---|---|---|
| Computed records + reconciliation report (Gate G1) | `src/mak/records/compute.py`, `src/mak/records/reconcile.py`, `results/reconciliation.md` | buildplan **T1.3** |
| Catalogue + facts with provenance (Gate G2: all 50 golden rows exact), incl. player lines and last results | `src/mak/fetch/catalogue.py` (full code in buildplan), `src/mak/fetch/facts.py` | buildplan **T1.4** incl. Step 5 |
| Policy (full code in buildplan) + exhaustive tests; composer with en/hi/ta templates and the "every number appears verbatim in a Fact" test (Gate G5) | `src/mak/policy/decide.py`, `src/mak/compose/render.py`, `src/mak/compose/templates/{en,hi,ta}.j2` | buildplan **T1.6** |

**Done when:** `pytest tests/golden tests/policy tests/unit` green; rendering T20I runs prints both records with dates in all three languages.

**STOP and learn:** (1) Walk one question by hand: labels → `lookup()` → `decide()` → `get_facts()` → `render()`; where does each number come from? (2) Why is the policy code, not a model? (3) Which rows differ in the reconciliation report, and why? (4) "Who has the most wickets?" (no format) → why four lines?

## K-P4: the product (Sun 08:00-10:30; `resolve()` must be on `main` by 10:30 for Sir Jabin's E1)

| Task | Files | Spec |
|---|---|---|
| `resolve(query, lang="auto") -> Resolution`: `understand()` → entities (registry gender overrides by code; mixed genders → `both_named`; surname-only → no override) → `lookup()` → `decide()` → `get_facts()` → leader → `render()`; trace from every stage | `src/mak/pipeline.py` (replaces the Phase 0 stub, same signature) | buildplan **T1.7** |
| FastAPI `/resolve`, `/intents`, `/coverage`, `/health` + e2e tests incl. Review Focus 3-5 | `src/mak/api/app.py`, `tests/e2e/test_api.py` | buildplan **T1.7** |
| Gradio demo + MCP tool (`resolve_sports_query`, `list_supported_intents`), presets en/hi/ta, trace, sources/as-of table, coverage panel, empty "before" panel (filled later with Sir Jabin's captured plain-model answer) | `src/mak/ui/demo.py` | buildplan **T1.8**; skills `huggingface-gradio`, `mcp-builder` |
| Browser tests (presets render, no console errors) | `tests/e2e/test_ui.py` | skill `webapp-testing` |

**Done when:** API answers the headline question; demo works in all three languages; `http://127.0.0.1:7860/gradio_api/mcp/` responds; merged; message "resolve() on main".

**STOP and learn:** (1) Send an injection query and a Tamil query to `/resolve`; does the trace explain the decision to a judge? (2) What exactly does an AI app receive from our MCP tool? (3) Empty / emoji / 5,000-char input: what happens and why?

## K-P5: ship (Sun 10:30-14:30)

| Task | Files | Spec |
|---|---|---|
| Hugging Face Space (Gradio on ZeroGPU; needs an account older than 30 days with a verified email, decision D1 pending): one no-op `@spaces.GPU(duration=5)` function, model on CPU, `USE_LAYA` from config (flip to True when Sir Jabin posts "Laya on Hub"), REST via Gradio `api_name="resolve"` (Gate G6) | `space/app.py`, `space/requirements.txt`, `space/README.md` | buildplan **T3.1**; skills `huggingface-spaces`, `huggingface-zerogpu`, `hf-cli`; gotchas G-002, G-004 |
| Record pages with JSON-LD `FAQPage`, static Space (Gate G7) | `src/mak/pages/build.py`, templates, `site/` | buildplan **T3.2** |
| Football adapter: 10-20 rows each verified by two sources with as-of (drop anything unverifiable) + adapters + tests (Gate G9) | `data/golden/football_v1.csv`, `src/mak/adapters/{base,cricket,football}.py` | buildplan **T3.5** |
| Docs: data card, benchmark card, architecture, licences (Cricsheet ODC-BY, Wikidata CC0, Wikipedia CC BY-SA, NQ-open CC BY-SA 3.0, Aya Apache-2.0, IndicTrans2 MIT, Laya Apache-2.0, Llama licence), README (one-line MCP install, API example) | `docs/*.md`, `README.md` | buildplan **T4.2** |

**Done when:** live Space URL, MCP URL and record-pages URL posted in `handoffs.md`; football answers both genders; docs merged. If no eligible HF account exists yet, deploy the static record pages anyway and keep the Gradio app runnable locally; note it in handoffs.

**STOP and learn:** (1) Open the Space on a phone: what would a judge click first, what confuses them? (2) Why is the model on CPU inside a ZeroGPU Space? (3) Put a record page through the Rich Results Test: what does a search-grounded AI now see?

---

## R-phase: refinement (both tracks, Sun 15:00-20:00)

- [ ] Hardening [T4.1]: ≥30 injection items unchanged, 200 fuzzed inputs without a 500, concurrency limit, `scripts/refresh.py`, accessibility pass.
- [ ] `scripts/run_all_eval.py --from-raw` regenerates every table (Gate G8) [T3.6].
- [ ] Deck (5 slides), summary, 3-minute video [T4.3]; every number measured, dated, sourced; Sir Jabin decides who presents.
- [ ] Final read of plan.md §11 "what we will not claim". **20:00 freeze.** Monday: re-verify dynamic records, confirm deadline time, submit.
