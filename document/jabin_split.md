# jabin_split.md: Sir Jabin's track (model, training, evaluation)

Owner: Sir Jabin, with Claude Code. Partner track: `joanna_split.md` (Joanna + Astra). Specs per task: `buildplan.md` (IDs in brackets). Strategy: `plan.md`. Channel: `handoffs.md` only.

**Deadline:** whole tool done **before Sun 4 Oct 15:00 IST** (Sir Jabin). Refinement 15:00-20:00, freeze 20:00.

**Your job in one line:** turn any question (en/hi/ta, messy, romanised, adversarial) into correct labels with a trained, calibrated model, and prove what the whole system achieves.

**Phase rhythm:** build → "done when" check → **STOP and learn** (15 min, answer the questions in your handoff message) → merge to `main` → post handoff → next phase.

---

## LIVE STATUS (updated Mon 05 Oct, 09:24 IST; newest state only; a new session starts HERE)

**Deadline: 23:59 IST Mon 5 Oct (Sir Jabin).** **Phase: REFINEMENT, small tweaks only (Sir Jabin: deck is ready).** Then push and hand over: teammates do the video, the hosting decision (HF via a >30-day account / Modal / laptop; decided at the end) and submission. Sir Jabin checks ChatGPT at the end.
**Jabin track: complete** (Laya v3 shipped, official + post-hoc evals, E1 all arms, E3/E4, resolve(), report, model card). Keep: `video/raw/` (real screen captures) and `video/voice/` (Bella clips) for the team's edit. ffmpeg uninstalled; temp files cleaned.
Live demo/MCP (URL since 05 Oct 09:22): https://85007419db81af9060.gradio.live , MCP https://85007419db81af9060.gradio.live/gradio_api/mcp/ (server PID 31892, started with `PYTHONPATH=src`; older 924d7… and 277143… URLs are DEAD). check_mcp.py passed en/hi/ta + catalogue at 09:23. **Is it on?** Open `<URL>/gradio_api/mcp/schema`; a tool list means on.
Logo: `logo/logo_for_mcp.png` (Sir Jabin's). `logo/logo_mcp_128.png` = icon to upload in ChatGPT's connector form (ChatGPT does NOT take it from the server automatically). The server also sends it as MCP `serverInfo.icons` (verified in `initialize`) for clients that read it; demo tab favicon = `logo/favicon.png`.
Cross-sport (E3): official run 4 Oct (gender en 0.949 vs rules 0.847, topic en 0.797; n=59, only 1 ta row). Post-hoc re-run 5 Oct with current code (other-sport keep rule): gender en 0.949, topic en 0.932 (`results/e3/report_posthoc_20261005.md`, POST-HOC).

**Pre-submission MCP check (run on Sir Jabin's laptop before Efanio records/submits):**
1. Server up: port 7862 listening (`scripts/serve_demo.py --share`), trained Laya loaded (trace shows "laya:", not "laya unavailable").
2. `python scripts/check_mcp.py <PUBLIC_URL>/gradio_api/mcp/` prints "trained Laya, both records, sources and dates OK" for en/hi/ta and "Catalogue OK".
3. ChatGPT plugin "Make AI Know Her" points to the SAME public URL and has `logo/logo_mcp_128.png` as its icon (Settings -> Apps & Connectors; a restart changes the gradio.live URL: recreate the plugin if so).
4. `python -m pytest tests -q` green (490 passed on 5 Oct 01:00; needs duckdb, rapidfuzz, gradio[mcp]).
5. Laptop stays on, plugged in, online while judges might use the link (temporary share link, not permanent hosting).
Open: ChatGPT re-point + icon (Sir Jabin, at the end); small deck tweaks (Sir Jabin); video, hosting decision, submission (teammates). Model weights are public: GitHub Release `laya-mak-v3` (Apache-2.0, release notes = model card).

## How we stay independent of each other

| Interface | Owner | Fixed in Phase 0 as | Until the real one lands, the other side uses |
|---|---|---|---|
| `understand(text, lang=None, use_laya=None) -> Parse` | Jabin | signature + a small English keyword stub | Joanna: the stub (enough for the 25 golden intents in English) |
| `labels.py` label sets | shared | final list | both |
| Test sets (`testsets/*.csv`) | Joanna | column format in `labels.py` docstring | Jabin: his own calibration split for dev numbers; final numbers on Joanna's frozen sets |
| Laya weights | Jabin | `config.LAYA_MODEL_ID` (HF Hub repo id), `config.USE_LAYA=False` | Joanna: rules only; flips the flag when weights are on the Hub |
| `resolve(query, lang) -> Resolution` | Joanna | signature + stub returning golden facts | Jabin: the stub to build and test the E1 runner; the real run after Joanna's K-P4 merge |
| Entity lookup (player/team → gender) | Joanna | `pipeline.py` applies it after `understand()` | Jabin: not needed (`understand()` = text → labels only) |

Only two real meeting points: **Sat ~24:00** (Joanna's frozen test sets, for your Sunday evaluation) and **Sun ~10:30** (your weights on the Hub ↔ Joanna's real `resolve()` for E1/E4).

---

## Phase 0: shared contract (built and pushed by Jabin's Claude Code, Sat 18:00-18:45)

- [x] Repo = this folder; remote `https://github.com/Joannapreethi28/ICC-26.git`; scaffold [T0.2]; `types.py`, `labels.py`, `config.py`, stubs for `understand()` and `resolve()`, `OWNERS.md`, `pyproject.toml`, `.gitignore`, `pytest` green; golden CSV copied with the D2 fix.
- [x] Pushed as `jabssyyy` (no AI co-author). Handoff "Phase 0 DONE".

## J-P1: rules baseline + language detection (Sat 18:45-21:00) [x] DONE Sat 17:00 (code); learn questions pending

- [x] `data/lexicons/{en,hi,ta}.yaml` (strong vs weak gender cues, stat/format phrases, injection markers), `src/mak/nlu/lang.py`, `src/mak/nlu/rules.py`, real `understand(use_laya=False)` replacing the stub (same signature) [T1.5, minus entities which are Joanna's].
- [x] Tests: the 14 rule cases + 3 injection cases in buildplan T1.5 (the two entity cases move to Joanna's pipeline tests) + Review Focus 1-2.

**Done when:** `python -c "from mak.nlu.understand import understand as u; print(u('அதிக விக்கெட்டுகள் எடுத்த வீராங்கனை யார்?'))"` → lang ta, women, wickets; NLU tests green; merged; handoff "real understand() on main".

**STOP and learn:** (1) Run 10 questions of your own; which do rules miss and why? (2) Why is வீரர் weak but வீராங்கனை strong? (3) Why does injection go to "show both" instead of a block? (4) Write 3 questions where you expect Laya to beat rules; keep them for J-P4.

## J-P2: Laya hands-on + training data (Sat 21:00-24:00)

- [x] 20 min hands-on: `pip install laya`, load `convaiinnovations/laya-multilingual`, zero-shot our typed questions on 10 queries; note the (bad, overconfident) probabilities.
- [x] Read `laya.common.build_sequence`, `render_options` and the repo notebook for the gold format (gotcha G-003).
- [x] `training/generate_data/{schema,grammar,noise,build_dataset}.py`, `paraphrases/{en,hi,ta}.jsonl` (Claude dev-time; prompts in `PROMPTS.md`) [T2.1]. Sizes: 8-12k train, hi ≥3k, ta ≥3k; calibration ≈1k/lang by template family.
- [x] Freeze: hashes in `training/DATA_FROZEN.md`. Only after this may you open `testsets/`; run the leakage test (0 overlaps required).

**Done when:** per-language/label counts balanced (each gender label ≥15%), leakage test green, merged.

**STOP and learn:** (1) What does Laya output and why can't it hallucinate a number? (2) Why family-then-stat instead of one 40-option question? (3) Read 5 Tamil rows: what looks synthetic? (4) Why calibration data from different template families?

## J-P3: fine-tune + calibrate (Sun 00:00-02:00)

- [x] Tell the team the job (≈650 MB download; minutes of training). RTX 5060 if CUDA works, else Kaggle 2×T4 [T2.2]. Log to `results/training_log.md`. (done: local RTX 5060)
- [x] Temperatures per (question, option count) on `calib.jsonl`; fit `GENDER_THRESHOLD` for ≥98% accepted-gender accuracy; CONTRACT CHANGE message if `config.py` changes [T2.3]. (done: buckets on calib; threshold 0.85 from the calib grid; docs/05)
- [x] Start Qwen2.5-1.5B LoRA (skill `trl-training`) in the background [T2.4]. (done: Qwen2.5-1.5B LoRA v2 trained, arm e)

**Done when:** `models/laya-mak-v1/` saved; ECE before/after printed; Qwen job running.

**STOP and learn:** (1) Loss curve: overfitting? (2) What did temperature scaling change and what not? (3) Why fit the threshold on calibration data, never on test?

## J-P4: honest evaluation + integration + publish weights (Sun 08:00-10:30)

- [x] `src/mak/eval/classifier_eval.py`: rules-only (Gate G3), Laya zero-shot, fine-tuned, fine-tuned + rules (shipped), Qwen, on Joanna's frozen sets; per language, slice and source; Wilson intervals; ECE; confident errors; option-order sensitivity [T2.3, T2.4]. (done: results/classifier/report.md; ONNX latency in results/onnx_check.json)
- [x] `src/mak/nlu/laya_head.py` + `understand(use_laya=True)`: rule override, calibrated gating, two-step hierarchy [T2.5]. ONNX + CPU p50/p95 if feasible. (done: Laya v3 shipped, USE_LAYA=True)
- [x] Push weights to the HF Hub (skill `hf-cli`, CLI via pip) and set `config.LAYA_MODEL_ID`; CONTRACT CHANGE message "Laya on Hub, flip USE_LAYA". (changed: no HF account (SJ); GitHub Release laya-mak-v3 + scripts/get_laya_weights.py; publish decision at the end)

**Done when:** `results/classifier/report.md` complete with n and intervals; Gate G4 checked (misses reported); weights on the Hub.

**STOP and learn:** (1) Does fine-tuned beat rules on messy slices, and by how much with what interval? (2) 5 confident errors: data, label or model limit? (3) Weakest language and the one data fix that would help most? (4) What does our ECE mean for an API user?

## J-P5: the proof (Sun 10:30-14:30)

- [x] Tell the team: `ollama pull llama3.1:8b-instruct-q4_K_M` (≈4.9 GB) and ≈1,500 generations (~1.5-2 h, background). Build `eval/arms.py`, `eval/score.py`, `eval/stats.py` against the `resolve()` stub first (scorer tests from T3.4), then run on the real `resolve()` with Joanna's `eval_data/benchmark_v1.csv` and `PREREGISTRATION.md` [T3.4]. (done: E1 all arms complete, results/e1/tables.md; human re-label pending, Efanio)
- [x] E4: raw query → real `resolve()` → decision accuracy on the frozen sets [T2.5]. E3: gender/topic heads on `testsets/xsport.csv` [T3.5]. (done: results/e4/, results/e3/)
- [x] `docs/model_card.md`; post the captured plain-arm hero answer for the demo's "before" panel. (model card done; hero "before" answer: pick one from results/e1/raw/plain.jsonl, Efanio for the demo)

**Done when:** `results/e1/tables.md`, `results/e3/`, `results/e4/` exist, each number labelled measured + date + model; model card merged; handoff "proof DONE".

**STOP and learn:** (1) The one honest sentence for the proof slide? (2) Did prompt-only show both, and were its numbers right? Show one stale answer. (3) Two things the results do NOT prove (for `docs/limits.md`).

## After 15:00: refinement (both): see `joanna_split.md` R-phase.
