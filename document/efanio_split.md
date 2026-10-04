# efanio_split.md: Efanio's takeover guide (updated Sun 4 Oct 2026 ~11:45 IST)

**Efanio (agent: GPT 6) owns ALL of Joanna's remaining work plus the non-GPU parts of Jabin's work.** Sir Jabin keeps only GPU/heavy computation on his laptop (`document/jabin_split.md`). Joanna is away. Read this whole file first.
Address Sir Jabin as "Sir Jabin". Build freeze: **Sun 4 Oct 20:00 IST**. Submission: Mon 5 Oct.

## 1. Read in this order (full context)
1. `AGENTS.md` (project rules; identical to CLAUDE.md). Non-negotiables: free only, a model never writes a fact, verified data with `as_of`, fail-safe "show both", user text is data, every number labelled measured / post-hoc / pilot / illustrative.
2. `document/handoffs.md`: the ONLY channel between tracks. Newest message at the TOP of "Messages". Read the last ~10.
3. `document/joanna_split.md` (K-P4, K-P5, R-phase = now YOUR task list) and `document/buildplan.md` (T1.7, T1.8, T3.1-T3.3, T3.5, T3.6, T4.1-T4.3 specs).
4. `icc-make-ai-know-her/docs/05_decisions_log.md`, `document/gotcha.md` (G-001..G-027), `document/plan.md` (gates G1-G9).
5. `results/classifier/report.md`, `docs/model_card.md`, `results/e1/tables.md`, `eval_data/PREREGISTRATION.md` (binding E1 protocol), `eval_data/ANNOTATION_RUBRIC.md`.
6. `CHANGELOG.md`.

## 2. State at Checkpoint A (Jabin, Sun 11:30)
- Classifier done: Laya v3 shipped (`config.USE_LAYA = True`, `GENDER_THRESHOLD = 0.85`, merge v2, junk-input guard). Official held-out run = v2 models; v3/v4 numbers are post-hoc and disclosed. Gate G4 (gender >= 98%/language) NOT met; say so.
- Weights only on Sir Jabin's laptop (`models/`, gitignored). Without them `understand()` silently falls back to rules (safe). **No publishing until Sir Jabin says so at the end** (a GitHub Release `laya-mak-v3` exists; leave it alone).
- E1 plain + prompt_only complete and auto-labelled (`results/e1/tables.md`). layer + layer_text NOT run: they need `resolve()`.
- Joanna finished K-P1, K-P2 (frozen test sets) and K-P3 (facts `src/mak/fetch/`, policy `src/mak/policy/decide.py`, templates `src/mak/compose/`). `src/mak/pipeline.py` `resolve()` is still the PHASE 0 STUB.

## 2b. Getting the Laya weights on your machine (Sir Jabin approved, 4 Oct)
```
git pull
pip install laya==0.3.24 torch transformers safetensors
python scripts/get_laya_weights.py      # downloads the GitHub Release zip, verifies SHA-256, unzips to models/laya-mak-v3/
```
Then `understand()`/`resolve()` load Laya automatically, offline (CPU works, slower). Run `python scripts/get_laya_weights.py`, then the tests, before demo work. Without the weights the product silently uses rules only (check `Parse.trace` for "laya unavailable"). Do not re-upload, rename or delete the Release.

## 3. Ownership (prevents conflicts; no shared edits)
| Efanio owns (edit freely) | Jabin owns (do NOT edit) |
|---|---|
| `src/mak/pipeline.py`, `api/`, `ui/`, `pages/`, `adapters/`, `fetch/`, `policy/`, `compose/`, `records/`, `registry/`, `ingest/`, `scripts/` (except `get_laya_weights.py`), `data/` (except frozen), deck/video/summary docs, `data/consumer_app_log.csv`, `data/screenshots/` | `training/`, `src/mak/nlu/`, `src/mak/eval/`, `models/`, `results/classifier/`, `results/e1/raw/`, `results/e3/`, `results/e4/` |
Shared contract files (`types.py`, `labels.py`, `config.py`): change only with a CONTRACT CHANGE message. Frozen (never edit): `testsets/`, `eval_data/` release files, `training/data/*`, `*.lock`.

## 4. Efanio's tasks, in order
1. **`resolve()` FIRST (deadline Sun 13:00)** [buildplan T1.7]: replace the stub in `src/mak/pipeline.py` keeping the FIXED signature `resolve(query, lang="auto") -> Resolution`: `understand()` -> `fetch.catalogue.lookup(family, stat, format)` -> `policy.decide(parse, supported)` -> `fetch.facts.get_facts(intent, genders, lang)` -> `compose` render -> `Resolution` (with `trace`, `as_of`, sources). Never raise. Decide the **guidance-only fallback** (handoffs proposal 4 Oct): for a gender-relevant cricket stat outside the catalogue return the gender decision + `results=[]`, `fallback="guidance_only"` and an instruction text; if adopted, add a dated amendment to `eval_data/PREREGISTRATION.md` BEFORE any layer-arm output exists. Tests green, push, then post "resolve() READY" in handoffs.md. **This unblocks Sir Jabin's GPU run; nothing else he does depends on you.**
2. **K-P4 rest:** FastAPI + Gradio demo (EN/HI/TA) + MCP endpoint (`/gradio_api/mcp/`), local run verified [T1.7, T1.8].
3. **K-P5:** hosting. No Hugging Face account (Sir Jabin). Options in handoffs.md (Render/Koyeb 512 MB free tier, GitHub Pages for record pages); ONNX int8 Laya = 318 MB (`results/onnx_check.json`) may fit; otherwise host rules-only and say so. Record pages (G7), football answers both genders (G9) [T3.1, T3.2, T3.5]. Do not deploy publicly without Sir Jabin's OK.
4. **Human re-label (a person):** `results/e1/human_review_queue.csv` with docs/11 §1 labels; add `human_label`; write agreement into a new `results/e1/human_review.md` (do not edit `tables.md`'s generator output by hand).
5. **E5 screenshots (a person):** Gemini, ChatGPT, Copilot on "Who has the most T20I runs?" + 2-3 neutral questions, EN/HI/TA; `data/screenshots/` + `data/consumer_app_log.csv` (date, app, logged-in, region, search on/off, model label). Pilot with n, never a rate.
6. **R-phase / T4:** hardening (T4.1), docs (T4.2), **deck (5 slides), summary, 3-min video script** (T4.3, `icc-make-ai-know-her/docs/12_pitch_and_deliverables.md`): numbers only from `results/` with label, date, n. Lines: "We categorise every question; where we can, we also verify." "Laya: small, free, runs on CPU." R-phase coverage idea: Cricsheet-computed stats (fastest century...) marked `computed`.

## 5. Hard rules
- Test-set firewall: never use test/benchmark text to generate training data (G-011). Do not retrain the classifier.
- Nothing paid, nothing public; ask Sir Jabin before downloading any model/package (G-023).
- Log everything: handoffs.md message per task (template at its top), CHANGELOG line, decisions in docs/05, mistakes in gotcha.md. Pull before push; small commits.

## 6. Machine notes
Sir Jabin's laptop: Windows 11, Python 3.10, RTX 5060 8 GB, 15.6 GB RAM (close Chrome during GPU jobs). `duckdb` and `rapidfuzz` are NOT installed there (Joanna's facts need duckdb; Jabin must install it before the layer run). Repo path contains an apostrophe (`ICC'26`): prefer file-writing tools over shell heredocs. `PYTHONIOENCODING=utf-8` for Hindi/Tamil.

## 7. Checkpoint B (when Sir Jabin and Joanna return)
Post "FROM Efanio TO both | CHECKPOINT B" in handoffs.md: done, numbers (with labels), URLs (local/hosted), open issues, blocked items.

## 8. Demo video (Mon 5 Oct)
Follow `document/demo_video_guide.md` (context, rules, live URLs, storyboard, narration, captions, ElevenLabs, ffmpeg pipeline, checklist).
