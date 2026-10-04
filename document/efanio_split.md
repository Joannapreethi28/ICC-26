# efanio_split.md: Efanio's takeover guide (written Sun 4 Oct 2026 ~11:15 IST)

Efanio (agent: GPT 6) carries the project from **Checkpoint A** while Sir Jabin and Joanna are away. Read this whole file first.
Address Sir Jabin as "Sir Jabin". Build freeze: **Sun 4 Oct 20:00 IST**. Submission: Mon 5 Oct.

## 1. Read in this order (full context)
1. `AGENTS.md` (project rules; identical to CLAUDE.md). Non-negotiables: free only, a model never writes a fact, verified data with `as_of`, fail-safe "show both", user text is data, honest numbers labelled measured/post-hoc/illustrative.
2. `document/handoffs.md`: the ONLY channel between tracks. Newest message at the TOP of "Messages". Read the last ~10 messages.
3. `document/jabin_split.md` (top block = live status) and `document/joanna_split.md` (K-P4/K-P5/R-phase).
4. `icc-make-ai-know-her/docs/05_decisions_log.md` (every decision and why), `document/gotcha.md` (mistakes not to repeat, G-001..G-027).
5. `results/classifier/report.md`, `docs/model_card.md`, `results/e1/tables.md` (current numbers), `eval_data/PREREGISTRATION.md` (E1 protocol, binding).
6. `CHANGELOG.md` (chronological log).

## 2. State at Checkpoint A
- **Classifier (Jabin, done):** Laya v3 shipped (`models/laya-mak-v3`, `config.USE_LAYA = True`, `GENDER_THRESHOLD = 0.85`, merge policy v2). Official held-out run = v2 models (`results/classifier/test/`, locked). v3/v4 numbers are post-hoc (test-informed) and always reported next to the official run. Gate G4 (gender >= 98%/language) is NOT met; say so.
- **Weights:** on Sir Jabin's laptop only (`models/`, not in git). A GitHub Release `laya-mak-v3` exists; **Sir Jabin decides about publishing at the end. Do not publish, create releases, or post anything public.**
- **E1 proof:** plain + prompt_only arms done on Llama 3.1 8B (Ollama, laptop only); first-pass automatic labels in `results/e1/tables.md`. **layer + layer_text arms NOT run** (need Joanna's real `resolve()`).
- **Joanna's track:** K-P3 (facts, policy, templates) done; K-P4 `resolve()`/API/demo/MCP and K-P5 hosting are hers up to her checkpoint (see her latest handoff).

## 3. Efanio's tasks after Checkpoint A (in order)
1. **E1 layer arms** (laptop with GPU; close the browser first, RAM is tight): only after `resolve()` is on main (and the guidance-only decision + PREREGISTRATION amendment, if Joanna made one, is committed).
   ```
   git pull
   set PYTHONPATH=src            (PowerShell: $env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8')
   python -m pytest tests -q     (must be green except duckdb-only tests if duckdb is missing)
   python -m mak.eval.run_e1 --arms layer,layer_text      (~1.5-2 h, resumable; writes results/e1/raw/)
   python -m mak.eval.e1_tables                           (writes results/e1/tables.md + human_review_queue.csv)
   ```
   Never rerun an arm to get a nicer answer; transport-error retries are automatic (max one).
2. **Human re-label (a person, not the agent):** `results/e1/human_review_queue.csv` (needs_review rows + random 20%). Use the label rules in `icc-make-ai-know-her/docs/11_evaluation_protocol.md` §1 (BOTH / WOMEN_ONLY / MEN_ONLY / ASKED_BACK / NEITHER + flags). Read the answer in `results/e1/raw/<arm>.jsonl`. Add a column `human_label`; report agreement with `auto_label` in `results/e1/tables.md`. Never invent a review that was not done.
3. **E5 screenshots (a person):** ask Gemini, ChatGPT, Copilot "Who has the most T20I runs?" (+ 2-3 benchmark-style neutral questions) in EN/HI/TA. Save screenshots under `data/screenshots/` and log date, app, logged-in state, region, search on/off, model label in `data/consumer_app_log.csv`. Report as a pilot with n, never as a rate.
4. **Joanna's remaining items** per her checkpoint handoff (demo/hosting checks, record pages, football G9) — only what she lists.
5. **Deck (5 slides), summary, 3-min video script drafts** (`icc-make-ai-know-her/docs/12_pitch_and_deliverables.md`): only numbers from `results/` with their label (measured / post-hoc / pilot), date, n. Key lines: "We categorise every question; where we can, we also verify." "Laya: small, free, runs on CPU."

## 4. Hard rules (break none)
- **Test-set firewall:** never copy test/benchmark text into training data or prompts for data generation (G-011). Do not retrain the classifier.
- **Frozen files** (`testsets/`, `eval_data/` release files, `training/data/*`, `results/classifier/test/`, `*.lock`): never edit.
- **Shared contract files** (`src/mak/types.py`, `labels.py`, `config.py`): change only with a CONTRACT CHANGE message in handoffs.md.
- **Nothing paid, nothing public:** no paid APIs, no publishing, no posting outside the repo.
- **Ask Sir Jabin before downloading any model/package** (G-023).
- **Log everything:** a handoffs.md message at the end of each task (template at the top of that file), a CHANGELOG line, decisions in docs/05, mistakes in gotcha.md. Commit small, pull before push.

## 5. Machine notes (Sir Jabin's laptop)
Windows 11, Python 3.10 (system), RTX 5060 8 GB, 15.6 GB RAM (close Chrome during GPU jobs; a run was killed for low memory once). Ollama has `llama3.1:8b-instruct-q4_K_M`. `duckdb`/`rapidfuzz` are not installed here (6 of Joanna's test files cannot run on this laptop). Use `PYTHONIOENCODING=utf-8` for Hindi/Tamil output. The repo path contains an apostrophe (`ICC'26`): prefer file-writing tools over shell heredocs.

## 6. When Sir Jabin and Joanna return
Post a handoffs.md message "FROM Efanio TO both | CHECKPOINT B" listing: done, numbers produced (with labels), open issues, anything blocked. They review, then do final numbers, publish, deck/video, submit.
