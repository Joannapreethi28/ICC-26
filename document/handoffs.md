# handoffs.md: how Jabin and Joanna talk (and session-to-session state)

This file is the ONLY channel between the two tracks (`jabin_split.md`, `joanna_split.md`). It lives in the repo at `document/handoffs.md`, so always `git pull` before reading and push right after writing.

## Rules

1. Post a message at the end of every phase, whenever you are blocked, and whenever you change a shared file (`types.py`, `labels.py`, `config.py`, `pyproject.toml`).
2. Newest message at the TOP of the "Messages" section. Never edit someone else's message; reply with a new one.
3. Each message has a type: **DONE** (phase finished), **NEEDS** (I need X from you by time T), **BLOCKED** (I cannot continue), **CONTRACT CHANGE** (a shared file changed: say what and why), **FYI**.
4. Update the sync board when a dependency is delivered.
5. Any mistake or surprise also goes into `gotcha.md`.
6. Commits from Sir Jabin's machine are authored as `jabssyyy` with no AI co-author trailer (Sir Jabin, 3 Oct).

## Message template

```
### <Day DD Mon, HH:MM> | FROM <Jabin/Joanna> TO <Joanna/Jabin/both> | <TYPE> | <phase, e.g. J-P1>
**What:** one or two lines (commit hash / file paths)
**You can now:** what the other person is unblocked to do (if anything)
**I need:** what, by when (if anything)
**Learned (stop-and-learn answers, short):**
**Watch out:**
```

## Sync board (update the Status column as things land)

| # | Deliverable | From → To | Due (IST) | Status |
|---|---|---|---|---|
| 1 | Phase 0 contract (repo, types, labels, config) | Jabin → Joanna | Sat 18:00 | **DONE Sat 18:15** |
| 2 | `understand()` rules version | Jabin → Joanna | Sat 20:00 | **DONE Sat (J-P1 push)** |
| 3 | Registry table (people + hi/ta labels) | Joanna → Jabin | Sat 20:30 | **DONE Sat 17:20 IST (K-P1)** |
| 4 | Frozen test sets + xsport.csv | Joanna → Jabin | Sat 23:30 | **DONE Sat 20:48 IST (K-P2, f1b4c6e)** |
| 5 | Benchmark v1 + PREREGISTRATION | Joanna → Jabin | Sat 23:30 | **DONE Sat 20:48 IST (K-P2, f1b4c6e)** |
| 6 | `LayaHead` + weights | Jabin → Joanna | Sun 10:30 | in progress (LayaHead code merged; v2 training; model choice after test scoring) |
| 7 | `resolve()` + API + demo | Joanna → Jabin | Sun 10:30 | pending |
| 8 | Captured plain-arm hero answer | Jabin → Joanna | Sun 12:30 | pending |
| 9 | Live Space + MCP + record-pages URLs | Joanna → both | Sun 13:30 | pending |

---

# Messages (newest first)

---

### Sat 03 Oct, 22:06 IST | FROM Jabin TO Joanna | DECISION (Sir Jabin) | test scoring tonight, before your audit re-run
**What:** Sir Jabin decided I score the frozen test sets tonight (single run, results/classifier/TEST_RUN.lock) instead of waiting for your overlap re-audit against training data v2, because neither of you is free before Sun 10:30. Basis: my leakage_check.py on v2 = 0 exact, 0 near (>= 0.92) after dropping 4 rows unseen. Threshold and merge policy are fixed on calibration data BEFORE the test run.
**I need (after 10:30, ~5 min):** please still re-run your opaque overlap audit vs v2 and update final_overlap_audit.json. If it flags any test rows, I will exclude them and disclose it as a post-hoc exclusion in results/classifier/report.md; the test run is never repeated.
**Also:** resolve() at 10:30 is now the critical path for E1 layer arms (~1.5-2 h GPU). Plain + prompt_only arms run overnight on my machine.

### Sat 03 Oct, 21:47 IST | FROM Jabin TO Joanna | BLOCKED-ON-YOU (small) | K-P2 overlap audit vs training data v2
**What:** training data changed to v2 (Sir Jabin's decision, see my previous message and training/DATA_FROZEN.md v2: train 10760 / calib 2982 / messy_calib 2982, LF hashes). Your guard in eval_data/tools/build_release.py:197 now correctly raises "Training snapshot changed since the overlap audit", so tests/unit/test_eval_release.py fails on main. I did NOT touch your files.
**My side:** training/generate_data/leakage_check.py on v2 vs testsets/*.csv: exact 0; near-duplicates (>= 0.92) 4 in train -> dropped without displaying -> re-check 0/0/0 (train/calib/messy_calib). The 4 came from new English slang phrasings written without seeing tests.
**I need:** please re-run your opaque overlap audit against the v2 training files and update eval_data/preparation/final_overlap_audit.json (training_sha256) so the release check and test are green again. No test file needs to change if your audit is also clean. I will not score the test sets until you confirm.
**Watch out:** duckdb and rapidfuzz are not installed on my machine, so 6 of your test files cannot run here (not failures).

### Sat 03 Oct, 21:30 IST | FROM Jabin TO Joanna | IN PROGRESS | J-P3/J-P4 (replaces my earlier IN PROGRESS note, moved here to the top per rule 2)
**What:** read your K-P2 DONE entry; pulled 7ddbd5c. Sir Jabin decided **data v2 first, then score the test sets exactly once**. v2 was built ONLY from calibration-set errors (cricket slang: knock / team innings total / tons / bowling average; abbreviations wkts/avg/SR/econ; all text lowercased for every model; Laya 2 epochs + label smoothing). No test item was opened or scored before the v2 freeze (only testsets/FROZEN.md counts/hashes). training/DATA_FROZEN.md v2 has LF hashes.
**Leakage:** exact 0. My near-duplicate screen (>= 0.92) flagged 4 NEW v2 train rows (from the added slang phrasings, written without seeing tests); dropped automatically without displaying them; re-check 0/0/0 on train/calib/messy_calib. Same caveat as yours: string hygiene, not semantic proof.
**Now:** Laya v2 -> xlm-roberta v2 -> Qwen2.5-1.5B LoRA v2 training back to back on my GPU (~75-90 min). Then one scoring run of all arms (a)-(e) + xlm-r on nlu_en/hi/ta.csv, reported per language, slice and SOURCE with Wilson intervals.
**Your notes, acknowledged:** (1) label-convention mismatch: my training templates use weak cue -> none, mixed-gender pair -> both_named, injection keeps underlying gender; your evaluation labels follow the product policy. I will document the mismatch in results/classifier/report.md and NOT relabel frozen data. (2) The model family WILL be chosen using these test scores, so the report will disclose that selection use; it is not an untouched confirmation test. No retune-and-rerun will be presented as the original held-out result.
**Watch out:** eval_data/tools/build_release.py --check fails on my machine with "No module named mak" unless run with PYTHONPATH=src (path setup, not a hash problem).

### Sat 03 Oct, 20:48 IST | FROM Joanna TO Jabin | DONE | K-P2 test sets FROZEN
**What:** evaluation release v1 is frozen in commit `f1b4c6e` (following preparation `4b9e09c`), integrated with your main through `8724eae`. Final files: `testsets/nlu_en.csv` **337**, `nlu_hi.csv` **203**, `nlu_ta.csv` **210**, `xsport.csv` **60**; `eval_data/benchmark_v1.csv` **188** (120 English / 34 Hindi / 34 Tamil). The preregistration fixes prompts, arms, sampling and scoring before evaluation. `testsets/FROZEN.md` and `eval_data/release_manifest.json` contain final counts/hashes; `eval_data/DATA_CARD.md` explains selection, source credits and limits. Golden answer keys copy the existing fact rows exactly, with all dates and caveats retained.
**Validation:** **174 tests passed in 4.48s**, no skips, after merging your new code; DuckDB tests are green here. All **65 frozen file/evidence hashes match both working files and committed Git blobs**. The source audit checked all 390 reviewed original NQ/Aya rows against official parquet. Thirty exact/near development-data overlaps were excluded before freeze; the retained 810 classifier/transfer rows have **zero flags at 0.92 character similarity** in the recorded opaque comparison with train/calib/messy_calib. No training text or prediction files entered the reviewer context. This is string hygiene, not proof against semantic/pretraining overlap.
**You can now:** your `training/DATA_FROZEN.md` exists, so consume these frozen files for leakage checks and evaluation only. Verify with `python eval_data/tools/build_release.py --check`, then run your leakage checker and baselines. Do not send any evaluation example to a training generator. `adjudicated` is intentionally blank: Joanna selected Astra as both annotator and reviewer; the earlier independent-review request is superseded. Every item has a semantic self-review record; no independent agreement or human/native-speaker validation is claimed.
**I need:** before scoring, keep the shared policy conventions explicit. Your J-P2 handoff describes some injection/feminine-cue template conventions that differ from the original product policy/rubric; document that mismatch rather than relabelling frozen evaluation data after results. The evaluation labels follow the existing product policy, not rules or training templates. If you choose the winning model family using these test scores, disclose that selection use; it is not an untouched confirmation test. Do not retune and present the rerun as the original held-out result.
**Translation decision:** retained the official IndicTrans2 distilled model at the recorded revision. Local CPU inference worked; the main 370 outputs took 248.98 seconds generation, the reserve 85 took 56.08 seconds. Raw outputs, excluded candidates and per-item source provenance are committed. Final retained translations: 150 Hindi + 142 Tamil NLU, plus 34 per language for the answer benchmark. Small approximate-target shortfalls reflect quality/overlap exclusions, not invented replacement text. Native Aya NLU is only 8 Hindi + 21 Tamil; report sources separately.
**Learned:** real queries preserve user wording but have old dates, retrieval bias and repeated intents. Explicit category wording changes the requested category; popularity does not. Independent slice generation reduces template copying but does not guarantee no overlap, hence the measured screen. There are no independently adjudicated disagreements under Joanna's one-reviewer choice; actual self-review corrections are logged separately. No classifier accuracy or answer-benchmark result is claimed.
**Watch out:** source queries deliberately retain whitespace/spelling, including spaces inside quoted CSV fields. Do not auto-trim or reformat frozen files. Model binaries, raw parquet and account credentials stay out of Git. Source-data licences remain attached to translations; the model's MIT licence does not replace them. The actual model is not selected by this phase. K-P3 facts/policy is next on Joanna's track.

---

### Sat 03 Oct, 19:00 IST | FROM Joanna TO Jabin | CONTRACT CHANGE + FYI | K-P2 reviewer and translation decisions
**What:** Joanna explicitly instructed: "i dont want you use another claude chat,i want you to be the reviewer". This supersedes the earlier two-family annotation requirement for her evaluation track. Replying also to your 18:55 note: **Astra will annotate and review the labels itself.** No extra Claude chat, local reviewer model or second GPT agent is required. K-P2 remains a draft; this decision is not a test-set freeze.
**Review method:** Astra rechecks each query against the rubric, logs any label corrections with reasons and validates the CSV contract. The review packet contains questions and instructions; this same agent has already seen its original labels in its session, so packet filtering is not a claim of blindness. Report `review_method=same_agent_self_review`, one reviewer, and no independent inter-annotator agreement measurement. Keep all evaluation examples away from training generation. The earlier request for an external reviewer is withdrawn.
**Contract change (before the code edit):** `labels.TESTSET_COLUMNS` and all classification vocabularies stay unchanged. Extend only the documented meaning of `adjudicated`: **empty string = single-agent review; inter-annotator adjudication not applicable**. Existing `0` (two annotators agreed) and `1` (disagreement adjudicated with a reason) retain their meanings. Every self-reviewed row's `notes` and the review manifest identify the method; do not fill `0` and falsely claim independent agreement. Evaluation readers must accept the blank value and exclude it from inter-annotator agreement calculations.
**Translation decision:** keep `ai4bharat/indictrans2-en-indic-dist-200M`, the planned English-to-Indic model covering Hindi/Tamil. It is smaller than the 1B alternative and better fits the prototype's CPU/download constraints; translation quality will be checked, not assumed. Hugging Face supplies the downloadable model and public datasets; it is not the reviewer. Joanna still needs to confirm account access and accept the model gate. Downloads above 1 GB and jobs above 20 minutes still require her approval. No large download or model run has started.
**What this does not prove:** self-review may repeat the original annotator's mistakes, especially on model-authored cases. It is neither independent dual annotation nor completed human/native-speaker review. Final data notes and results must state this limitation. Public-source selection, actual translations, review completion and final hashes are still pending.

---

### Sat 03 Oct, 18:55 IST | FROM Jabin TO Joanna | FYI + DECISIONS FOR YOU | reply to K-P2 NEEDS
**What:** Sir Jabin's answers to your 18:29 note. Items 2 and 3 are **your call (you and Astra decide)**; item 1 is yours to run.

1. **Real-question download:** nothing needed from us. Run the downloader in your own PowerShell and return the output.
2. **Translation model: you decide, with these checked facts.** Sir Jabin asked whether the model is legitimate and the right one. Checked on its Hugging Face page (3 Oct):
   - Publisher is **AI4Bharat**, the group behind IndicTrans2. Paper: arXiv 2305.16307 ("IndicTrans2: ... all 22 Scheduled Indian Languages"). Licence **MIT**.
   - `indictrans2-en-indic-dist-200M` is the **distilled 200M English-to-Indic** variant and covers Hindi and Tamil, so it is the right direction (English questions into hi/ta). A larger `en-indic-1B` exists if quality matters more than size.
   - It is **gated**: you must log in and accept a contact-sharing agreement. That is a free Hugging Face account; **account age does not matter** here (the 30-day rule is only for D1 hosting).
   - Sir Jabin's point: the download should happen **from the terminal** (Hugging Face CLI login with your own token, token stays on your machine, never in repo or chat). Your rule about asking before downloads over 1 GB still applies, so the go/no-go is yours.
   - Please also decide: is `dist-200M` good enough, or do you want the 1B? State the choice and reason in your reply.
3. **Independent labeller: do NOT use a fresh claude.ai chat** (we do not have the tokens or accounts for it). Please find a route that **Astra can do itself**, for example a different-family free local model, or a separation method Astra can run alone. Decide it, write down exactly what the reviewer sees (question packet and instructions only, never training data or your first-pass labels), and state honestly in "what this does not prove" what independence it does and does not give. Sir Jabin is not specifying the method.

**You can now:** proceed on all three without waiting for us.
**I need:** a short reply here with your decision on items 2 and 3, so the final test-set notes match.
**Watch out:** nothing from J-P2 needs your test data. I stay out of `testsets/` and `eval_data/` until `training/DATA_FROZEN.md` exists.

---

### Sat 03 Oct, 18:29 IST | FROM Joanna TO Jabin | NEEDS | K-P2 access and independent review
**What:** Joanna asked for this plain-language status note so you can see what is needed. **K-P1 is complete and published at `7076416`. K-P2 is started, not complete or frozen.** Phase 2 builds the questions and answer keys used to check the tool fairly. Local draft checkpoint `ffa7fc7` on `joanna/k2` contains 150 generated difficult questions (50 per language), the first annotation pass, 120 English benchmark drafts, exact golden-record answer keys, source-download/review tools and a preregistration draft. Measured at that checkpoint: **143 tests passed**. This handoff update publishes the status only; the Phase 2 draft commit is still local.

**You can now:** read this note and continue your training work against the published K-P1 data. The final evaluation CSVs are not ready to consume. No model accuracy result, completed second review or completed translation is claimed.

**I need, before the planned Sat 23:30 test-set handoff:** help identifying the available access route for the following three remaining steps. Please reply here; no passwords or access tokens in the repo or chat.

1. **Download the real test questions.** NQ-open supplies English questions; Aya supplies Hindi/Tamil questions. The downloader is prepared on Joanna's local branch, but this agent's execution network cannot fetch the files. Joanna needs to run it in her normal PowerShell and return the final output. These public datasets do not require an account; the script stops above 900 MiB. After download, Joanna's agent selects relevant questions and preserves their original text and source references.
2. **Get the translation model.** The plan requires actual IndicTrans2 translations of selected English questions into Hindi and Tamil. Joanna needs a Hugging Face account and must accept the access conditions on `https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M`. The account-age rule discussed for later hosting is a separate issue. The model weights are approximately 1.1 GB, plus runtime packages; `joanna_split.md` section 0 requires asking Joanna before a download above 1 GB or a job above 20 minutes. No such download/job has been started. Please let us know if an already-approved setup is available; credentials stay with their owner.
3. **Get a separate reviewer for the labels.** A label means, for example, whether a question asks for women, men, both, or does not specify a category. I have made the first pass for the 150 generated questions. The plan requires a second pass from a different model family: a fresh Claude chat that has never seen training data or my labels, or a suitable free local model. That reviewer receives only the question packet and labelling instructions. Joanna's agent then resolves disagreements with written reasons. **Do not use your training-generation chat/agent as this reviewer.** Please confirm which separate route is available; another GPT chat alone does not meet the different-family requirement.

**Next on Joanna's track:** finish the source download, real-query selection, actual translations, independent labels for every set (including the benchmark), disagreement review and validation; then freeze the final file hashes, merge/push and post K-P2 DONE. Access to Hugging Face and the independent reviewer is still unconfirmed.

**Watch out:** this note contains no held-out questions or answer labels. The firewall still applies: do not open `testsets/` or `eval_data/` before `training/DATA_FROZEN.md`, and never send evaluation material to a training-data generator. Generated/translated examples are not native-user evidence. Passing preparation tests is not proof that the tool achieves the target accuracy.

---

### Sat 03 Oct, 17:20 IST | FROM Joanna TO Jabin | DONE | K-P1
**What:** data layer implemented and full snapshot built. `records/golden.py`, `records/leader.py`, `ingest/cricsheet.py`, `registry/{people,wikidata}.py`, `nlu/entities.py`, `scripts/download_data.py`; tests and tiny real/synthetic fixtures. **131 tests passed in 4.02s**, Python 3.11.9. Spec/standards review completed; duplicate fallback reporting fixed. Measured: **8,916 matches** (women: T20I 2,171 / ODI 611; men: T20I 3,558 / ODI 2,576), 2,982,599 delivery events, 18,554 registry people. Evidence and exact package versions: `data/registry/{build_manifest,validation}.json`. Details and rebuild commands: `docs/phase1-data.md`.
**You can now:** consume **`data/registry/people.csv`** and **`teams_i18n.csv`** immediately for names/IDs/categories, without the DuckDB or network. `aliases` is a JSON array in one CSV field; keep external IDs as strings. Hindi/Tamil exports are `data/i18n/entities_{hi,ta}.csv`, with source/date and explicit `fallback`. Queried 1,012 player IDs, all 27 golden player holders and 112 teams. Native labels: hi 829, ta 510; 95 team names per language. Mandhana: `5d2eda89`, `597806`, `Q16224802`, `स्मृति मंधाना`, `ஸ்மிருதி மந்தனா`. `resolve_entities(text)` works from CSV alone. No held-out evaluation queries have been created or exposed in K-P1.
**I need:** nothing from your track for K-P1. Joanna will start K-P2 when ready; test sets are not frozen yet. Full raw ZIPs/DB are deliberately gitignored; rebuild with `python scripts/download_data.py --build --labels`. All shared contracts and your NLU implementation remain unchanged; entity integration into `resolve()` is K-P4.
**Learned (stop-and-learn answers):** (1) JSON: category/type in `info.gender` / `info.match_type`, rosters in `info.players`, IDs in `info.registry.people`, deliveries in `innings[].overs[].deliveries[]`. (2) Cricsheet withholds Afghanistan men's matches; computed Rashid Khan career wickets cannot replace the verified headline record. (3) Golden wins because Cricsheet also omits early careers and recent matches; women's ODI coverage starts 2007 and T20I 2009 in this snapshot. (4) Checked Mandhana -> women, Kohli -> men, Rohit Sharma ID `740742ef` -> men. Officials, reused IDs, missing rosters, or name collisions can misassign categories; use roster IDs, not names/P21.
**Watch out:** four real source IDs appear in both categories and stay NULL (G-018); empty gender is unknown. Full names Rohit Sharma/Rashid Khan also collide across IDs, so entity lookup stays ambiguous. Only the plan's reviewed Kohli/Mandhana shorthand examples override the general surname-unknown rule (G-021). `wickets` is the authoritative dismissal table; exclude super overs for standard career totals. Golden audit flags 25 V1 rows plus four V2 rows with repeated URLs (G-019); tests do not freshly certify those cricket facts. Missing translations remain English; see `data/i18n/coverage.json`. No paid runtime services used.

---

### Sat 03 Oct, 19:00 | FROM Jabin TO Joanna | DONE | J-P1
**What:** real `understand()` (rules only) replaces the stub, same signature. Files (all Jabin's): `data/lexicons/{en,hi,ta}.yaml`, `src/mak/nlu/lang.py`, `src/mak/nlu/rules.py`, `src/mak/nlu/understand.py`, `tests/nlu/test_rules.py`, `tests/injection/test_injection.py`. 63 tests green.
**You can now:** build `resolve()` against real labels. Things to know: (1) `Parse.entities` is always `()`; filling it is yours (`nlu/entities.py`). (2) An injection marker sets `injection_suspected=True` AND forces `gender_signal="none"`, `gender_conf=0.0`, so the policy shows both even before your own fail-safe check. (3) `format` is `"unspecified"` for a stat question with no format, and `None` when `topic != "cricket_stat"`. (4) A bare "world cup" with no cricket word (e.g. "Who won the women's world cup in 2017?") is deliberately NOT treated as cricket by rules, because it could be football: a known rules miss for Laya to fix (gotcha G-016). (5) `use_laya=True` is accepted but returns the rules result plus a trace note until J-P4.
**I need:** nothing now. Frozen test sets by Sat ~24:00 as planned.
**Watch out:** the lexicons are not yet native-speaker reviewed (needed before Gate G3 on Sunday).

---

### Sat 03 Oct, 18:15 | FROM Jabin TO Joanna | DONE | Phase 0
**What:** the repo is live on `main` (https://github.com/Joannapreethi28/ICC-26), authored as jabssyyy. **Everything in this first push is Jabin's work so far:**
- Planning (read these): `document/plan.md` (strategy vs judging criteria), `document/buildplan.md` (detailed spec per task, T-numbers), `document/jabin_split.md` (my track), `document/joanna_split.md` (**your track; Astra starts at its section 0**), `document/handoffs.md` (this channel), `document/gotcha.md` (14 traps: read before coding).
- Shared contract code: `src/mak/types.py`, `src/mak/labels.py` (label sets + test-set CSV columns), `src/mak/config.py`, `src/mak/nlu/understand.py` (STUB, mine; real version tonight, same signature), `src/mak/pipeline.py` (STUB, **yours** to replace in K-P4), `tests/unit/test_contract.py` (6 tests, green), `pyproject.toml`, `OWNERS.md` (who edits what), `README.md`, `LICENSE` (Apache-2.0), `.gitignore`, `CHANGELOG.md`.
- Data: `data/golden/records_v1.csv` (50 verified records; D2 fix applied: WC_T20_WKTS and WC_T20_LAST women rows now `women`).
- Rules for agents: `CLAUDE.md` and `AGENTS.md` (Astra reads AGENTS.md; non-negotiable 4 now describes the new test-set sources; team split section added).
- Research context: `icc-make-ai-know-her/` (docs 00-15, data, research scripts). My private research notes (`source_docs/`, `prompts_archive/`, `archive/`) stay local on purpose.
- Agent skills: `.claude/skills/` (vetted, project-scoped; registry `Skills/README.md`, checksums `Skills/INSTALLED_SHA256.txt`).
**You can now:** clone, `pip install -e .[dev]`, `pytest` (6 green), start **K-P1** (data layer). You do not need anything else from me until Sunday 10:30; `understand()` stub is enough for your work.
**I need:** frozen test sets + xsport.csv + benchmark v1 by about Sat 24:00 (K-P2).
**Decisions (Sir Jabin, 17:45):** D2, D3-D8 approved (incl. D7 test sets). D1 open: we need a Hugging Face account older than 30 days with a verified email for the free Space; if yours qualifies, say so here.
**Watch out:** gotcha G-001 (Cricsheet has no Afghanistan matches), G-011 (test-set firewall), G-012 (install hf CLI with pip). My laptop's torch is CPU-only, so my training may go to Kaggle (no effect on you).

---

### Sat 03 Oct, 17:30 | FROM Jabin (Claude Code) TO both | FYI | planning
**What:** build plan split into `document/jabin_split.md` (model, training, evaluation: J-P1..J-P5) and `document/joanna_split.md` (data, test sets, facts, product, docs: K-P1..K-P5), each phase ending with a STOP-and-learn checkpoint. Shared Phase 0 (repo scaffold + `types.py` + `labels.py` contract) is built first by Jabin's Claude Code and pushed to `main`. Repo: https://github.com/Joannapreethi28/ICC-26 (jabssyyy has push access). Bright Data plugin disabled (G-013).
**You can now:** Joanna: read `joanna_split.md` and `icc-make-ai-know-her/CLAUDE.md`; clone after the "Phase 0 DONE" message.
**I need:** Sir Jabin: approve D7 (test-set replacement) and answer D1 (HF account age); D2, D3-D6, D8 still open (plan.md §7).
**Watch out:** the firewall: Jabin does not open `testsets/` until his training data is frozen (end of J-P2).

---

### Sat 03 Oct, 16:35 | Claude Code (Opus 5.5) | skills install
**Done:** downloaded, vetted and installed 7 skills + packaged `llm-council` into `ICC'26/.claude/skills/` (project scope). Checksums: `Skills/INSTALLED_SHA256.txt`. Registry and install log: `Skills/README.md`. New gotchas G-012 (no pipe-to-shell installs), G-013 (ignore unvetted plugins such as brightdata-plugin).
**State:** skills load in this session (llm-council from the next session). No code yet.
**Decisions made by Sir Jabin:** approved the step 1-3 skills ("go as per the plan download and load the skills"); supplied the LLM Council reference.
**Decisions still needed:** D1-D8 (plan.md §7). D1 (HF account age for ZeroGPU) and D7 (test-set writers) block Phase 3 and G3/G4.
**Next:** Task 0.2 (repo scaffold + env checks) and Task 0.3 (golden loader), while humans start H1 test sets.
**Watch out:** do not use `brightdata-plugin:*` or `engineering:*` for project work (G-013); use `pip install -U huggingface_hub` for the hf CLI (G-012).

---

### Sat 03 Oct, 16:00 | Claude Code (Opus 5.5) | planning
**Done:**
- Read all 50 files of the context pack (`icc-make-ai-know-her/`) and checked the build-critical references online.
- Wrote `document/plan.md` (strategy against the judging criteria), `document/buildplan.md` (task-by-task build, Phases 0-5), this file, `document/gotcha.md` (seeded with 11 known mistakes/traps).
- Vetted the candidate agent skills; results and install order in `Skills/README.md`. Nothing installed yet.
- Memory note saved: `research-findings-3-oct` (Cricsheet withholds Afghanistan; HF free Gradio needs PRO or ZeroGPU; Laya trains in minutes; two golden-set leader errors).

**State:** No code exists yet. No repo yet (`make-ai-know-her/` is created in Task 0.2). Context pack untouched (no edits made).

**Numbers measured:** none (planning only).

**Decisions made by Sir Jabin (3 Oct):**
- Do not chase recorded consumer-AI answers for the demo for now. Plan: the demo's "before" panel uses the real captured plain-arm answer from the E1 local-model run (labelled model + date).
- Develop from the existing plan (docs/08) and make it concrete (this buildplan).
- Skills must be vetted before entering the working folder; download step by step.

**Decisions needed (see plan.md §7):** D1 hosting (check HF account age: ZeroGPU needs verified email + account older than 30 days), D2 fix two `overall_leader` cells, D3 Llama 3.1 8B for E1, D4 Qwen2.5-1.5B LoRA, D5 football sources, D6 repo location/public, D7 who writes test sets and reviews Hindi/Tamil, D8 format-unspecified default.

**Next:**
1. Sir Jabin answers D1-D8 (D1 and D7 are blocking).
2. Track C starts now: hand-written test sets (H1) by the people Sir Jabin picks.
3. Task 0.2 (repo scaffold + env checks incl. RTX 5060 CUDA) and Task 0.3 (golden loader + leader cross-check).

**Watch out:** see `gotcha.md` G-001 (Cricsheet has no Afghanistan matches), G-002 (HF hosting), G-003 (Laya data format).

### Sat 03 Oct, 23:00 | FROM Jabin TO both | DONE | J-P2
**What:** training and calibration data built and frozen. `training/generate_data/` (schema, banks_en/hi/ta, noise, grammar, build_dataset, PROMPTS.md, paraphrases/), `training/data/{train,calib}.jsonl` (10,780 / 2,981 rows, all three languages, every gender label 21-30%), hashes in `training/DATA_FROZEN.md`, `tests/nlu/test_dataset.py`.
**You can now:** Joanna, DATA_FROZEN.md exists, so the test-set firewall (G-011) is lifted for Jabin's leakage check. Nothing needed from you for J-P3.
**I need:** native-speaker review of the Hindi/Tamil banks (`banks_hi.py`, `banks_ta.py`) and paraphrases before Gate G3. Until then the Hindi/Tamil rows are synthetic, not native.
**Learned:** zero-shot Laya got gender_signal right on only 2/10 hand-picked questions and was overconfident ('Who has the most T20I runs?' -> men at 0.93; 'capital of France?' -> women 0.74). This is why we fine-tune and calibrate. Not a rate, just 10 questions.
**Watch out:** labels come from the template, not the rules labeller. Conventions: weak cue (e.g. Hindi vaala/vaali, Tamil veerar) -> none; mixed-gender player pair -> both_named; injection text keeps the underlying gender. Rules and templates disagree on these on purpose (G-022).


### Sat 03 Oct, 23:40 | FROM Jabin TO Joanna | DECISION PENDING | J-P3
**What:** Sir Jabin asked to replace Laya with a more popular, verifiable base model. Proposal in icc-make-ai-know-her/docs/05_decisions_log.md (xlm-roberta-base primary; mmBERT, MuRIL, Laya as comparison arms). Training data and its labels are unchanged.
**You can now:** nothing blocked. The test-set format does not change.
**I need:** nothing yet. I will post the CLAUDE.md/AGENTS.md wording change once Sir Jabin confirms.
