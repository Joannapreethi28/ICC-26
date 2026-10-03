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
| 4 | Frozen test sets + xsport.csv | Joanna → Jabin | Sat 23:30 | pending |
| 5 | Benchmark v1 + PREREGISTRATION | Joanna → Jabin | Sat 23:30 | pending |
| 6 | `LayaHead` + weights | Jabin → Joanna | Sun 10:30 | pending |
| 7 | `resolve()` + API + demo | Joanna → Jabin | Sun 10:30 | pending |
| 8 | Captured plain-arm hero answer | Jabin → Joanna | Sun 12:30 | pending |
| 9 | Live Space + MCP + record-pages URLs | Joanna → both | Sun 13:30 | pending |

---

# Messages (newest first)

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
