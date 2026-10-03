# plan.md: the strategy to win (Make AI Know Her)

Written Sat 3 Oct 2026, 15:30 IST. Build freeze Sun 4 Oct 20:00 IST (about 28 hours away). Submit Mon 5 Oct.
Companion files: `buildplan.md` (the task-by-task build), `handoffs.md` (session state), `gotcha.md` (mistakes and lessons).
Source of truth for facts and rules: `../icc-make-ai-know-her/` (CLAUDE.md, docs 00-15). This file does not repeat them; it decides how we win with them.

Status words used below: **LOCKED** = Sir Jabin decided. **PROPOSED** = needs Sir Jabin's yes/no. **TARGET** = a goal, not a result.

---

## 1. The goal in one line

Ship a working, free, multilingual gender-aware answer layer **and** the measured proof that it fixes the men-default, packaged so a judge understands it in 3 minutes and an ICC engineer could pilot it on Monday.

## 2. The winning thesis (what the judges must walk away believing)

1. **The problem is real and specific to cricket.** For several neutral questions the overall record is a woman's (Mandhana's T20I runs, Argentina's 427/1, Cardoso's 9/4, the 1973 World Cup). A men-only answer is not just incomplete, it is wrong.
2. **Prompting is not the fix.** Our three-arm test on the same free model shows what "just tell it to mention women" gets wrong (stale or invented numbers), and what our layer gets right (verified, dated, sourced).
3. **The product is a decision, not a database.** A fixed, symmetric policy in plain code, fed by a small trained multilingual model that only picks categories. No model ever writes a number.
4. **It works in English, Hindi and Tamil**, each with its own measured accuracy, including the grammatical-gender cues (वाली, வீராங்கனை) that keyword rules miss.
5. **It is ready for ICC.** One URL (MCP), one API call, record pages that fix the men-only sources, open benchmark that ICC can re-run at every event, IDs that map to ICC's own platform (Cricsheet `key_pulse`).

## 3. Criteria → what the judges will actually see

| Criterion (weight) | The evidence we put in front of them | Where it is built |
|---|---|---|
| Innovation & Creativity (25%) | (a) First measured cricket test of men-default answers (three-arm result). (b) The decision layer itself, with a fail-safe "show both". (c) Grammatical gender as a detection signal in Hindi/Tamil (measured slice). (d) Record pages that repair the sources AI reads. Positioning slide: MCP servers = data; Google = closed, Search-only; prompting = no verified facts | buildplan Phases 1-3 |
| Technical Feasibility & Execution (20%) | Live demo + REST API + MCP tool; trained and calibrated Laya with per-language accuracy, ECE and latency; rules-only and Qwen baselines; reconciliation report (golden vs computed); model/data/benchmark cards; tests; open repo | Phases 1-4 |
| Impact on Women in Sport (20%) | Women's Visibility Rate and Gender-Complete Answer Rate per arm (plain vs prompt-only vs layer), with n and intervals; incidental-discovery story; symmetric policy; Unnecessary Intervention Rate reported | Phase 3 (T3.3, T3.4) |
| Value to Fans, Athletes & Ecosystem (15%) | Fans: complete answers without the magic word. ICC/Gemini: drop-in tool. Developers: free MCP/API + open benchmark. Sponsors/broadcasters: women's players surfaced at moments of casual discovery | Demo + deck slide 5 |
| Sustainability & Inclusivity (10%) | Free and open end to end; 322M model on CPU (measured latency); English/Hindi/Tamil each tested; accessibility pass; team representation (Sir Jabin decides how roles are shown) | T2.5, T4.1 |
| Presentation & Storytelling (10%) | 3-minute video with one hero question carried end to end (section 5); 5-slide deck where every number is dated and labelled measured/target | T4.3 |
| Bonus: cross-sport | Gender/topic heads tested on unseen football/tennis/basketball questions + a football adapter answering through the same policy | T3.5 |
| Bonus: pilot-readiness | Hosted endpoint, one-call integration, IDs mapped to ICC Pulse, a 4-week pilot plan with metrics and success targets | T3.1, deck slide 5 |
| Bonus: women-led | Sir Jabin decides; we only make sure the docs and video can show it truthfully | T4.3 |

## 4. The proof package (the part most teams will not have)

Ranked by persuasive power. All numbers are **TARGET/hypothesis until measured**; never put an unmeasured number on a slide.

1. **E1 three-arm test (headline).** Same free local model (PROPOSED: Llama 3.1 8B Instruct, the same family Biester tested in NAACL 2025, so our cricket result sits next to the published Olympic result), 3 samples per question, ≥100 English neutral/control questions + Hindi and Tamil sets. Arms: (1) plain, (2) prompt-only "if gender is not stated give both", (3) with our layer's JSON as tool context, (3b) our layer's own text. Report GCAR, WVR, factual accuracy, freshness, UIR, per arm, paired bootstrap 95% intervals. Hypothesis: prompt-only raises "both shown" but stays stale (a model trained before Sep 2026 cannot know Mandhana 4,867, Cardoso 9/4 or Australia's 2026 title); the layer wins on accuracy. If the hypothesis fails, we report that.
2. **E2 classifier ablation.** Rules-only vs Laya zero-shot vs Laya fine-tuned vs fine-tuned + rules (shipped) vs Qwen LoRA parser; per language and slice (grammatical gender, romanised, typos, injection); ECE; CPU latency.
3. **E4 end-to-end decision accuracy** on the hand-written sets (what the policy finally receives).
4. **E3 cross-sport transfer** on ≥60 hand-written unseen-sport questions + 10-20 football ground-truth questions.
5. **Reconciliation report:** where Cricsheet-computed records differ from the verified golden set, and why (e.g. Cricsheet withholds all Afghanistan matches, so Rashid Khan's 197 cannot be computed; see gotcha G-001).

Honesty rules that make the proof credible: always show coverage, classifier accuracy and the three-arm result next to our own WVR (our layer scores high on supported queries by design); freeze the scoring spec before the first run; save every raw output.

## 5. The hero demo (Presentation 10%, and the spine of the video)

One question carried through every surface, then four contrast shots:
1. "Who has the most T20I runs?" → the **plain local model's real captured answer** (from the E1 plain arm, labelled with model name and date; this replaces consumer-app screenshots, per Sir Jabin's 3 Oct decision) → the same question through Make AI Know Her: both records, sources, as-of dates, "Overall: Mandhana leads both lists", decision trace.
2. Same question in **Hindi** and **Tamil** (answer in that language, names from Wikidata labels).
3. "women's most T20I runs" → untouched, women only (shows symmetry).
4. "How long is a cricket pitch?" → silent (no unnecessary intervention).
5. "Who has the most T20I maiden overs?" → honest "not supported" (builds trust).
6. An AI client calling the MCP tool (MCP Inspector or the E1 harness), then the record page with JSON-LD.
7. The proof slide numbers (measured only).

## 6. Strategy decisions that make the plan strong (and why)

| # | Decision | Why |
|---|---|---|
| S1 | **Vertical slice first:** by Sat night the whole chain (question → rules → policy → facts → answer → API → Gradio) works for the 25 golden intents in English, then we widen (Laya, Hindi/Tamil depth, computed stats, adapters) | There is always a submittable product; every later piece plugs into a working spine. This is ordering, not a cut line: everything in docs/08 still gets built |
| S2 | **Three tracks run in parallel from hour one:** (A) code spine, (B) training data + Laya, (C) human-written test sets | Track C cannot be done by AI (it would leak into training and invalidate the accuracy claims). It is the true critical path |
| S3 | **Rules are the override and the baseline; Laya is the generaliser** | Explicit cues ("women's", महिला, மகளிர்) are guaranteed by code; Laya earns its place on messy, romanised and grammatical-gender phrasing, which E2 measures |
| S4 | **Golden set wins for headline records; computed rows are labelled "computed from Cricsheet, as of …"** | Cricsheet withholds Afghanistan matches and lags; we never silently overwrite verified rows |
| S5 | **Injection-suspected queries fail safe to "both"** | Showing both never hides anyone, so an attacker cannot use injected text to make a neutral question one-gender (and the policy stays symmetric) |
| S6 | **Format not stated ("who has the most wickets?") → both genders for T20I and ODI, labelled** (PROPOSED default) | We refuse to invent a gender; we also should not silently invent a format. Four labelled lines, flagged `format_unspecified` |
| S7 | **One Gradio app = demo + MCP + API**; record pages as a separate static site | One deploy for the live parts; static pages are free to host anywhere |
| S8 | **Pre-register E1** (questions, prompts, arms, scoring) in the repo before the run | Judges and reviewers can see we did not tune after seeing results |

## 7. Decisions (status 3 Oct 17:45: D2, D3, D4, D5, D6, D7, D8 APPROVED by Sir Jabin; D1 pending: finding an HF account older than 30 days)

| ID | Decision | My recommendation | Blocks |
|---|---|---|---|
| D1 | Hosting. Free HF accounts can no longer run Gradio on free CPU; the free route is a **ZeroGPU Gradio Space** (needs verified email and an account older than 30 days; we keep the model on CPU with a no-op `@spaces.GPU` function, so no GPU quota is used) + a **static Space** for record pages | Check your HF account age now. If eligible: ZeroGPU + static Space. If not: a teammate's eligible account, else run locally for the video and host record pages statically | T3.1, T3.2 |
| D2 | Fix two wrong `overall_leader` cells in `records_v1.csv` (WC_T20_WKTS women row → women; WC_T20_LAST women row → women) and the docs/10 table | Yes, fix; a code cross-check test will guard it | T0.3 |
| D3 | Three-arm model: Llama 3.1 8B Instruct via Ollama (~5 GB download; RTX 5060 8 GB) | Yes (literature continuity). Optional second model (Qwen3 8B) only if time | T3.4 |
| D4 | Qwen comparison parser: Qwen2.5-1.5B-Instruct + LoRA | Yes (fits 8 GB locally or Kaggle T4) | T2.4 |
| D5 | Football ground truth from Wikipedia/Wikidata lists, only rows verified with two sources and an as-of date | Yes; StatsBomb only if its licence and women's coverage check out | T3.5 |
| D6 | Where the code lives: new repo `ICC'26/make-ai-know-her/` (git), context pack stays read-only; public GitHub repo at the end | Yes; making it public is your call (outward-facing) | T0.2, T4.2 |
| D7 | Test sets. **Sir Jabin, 3 Oct: hand-written test sets are not possible.** PROPOSED replacement (needs approval because it amends CLAUDE.md non-negotiable 4): (1) REAL-EN: about 600 cricket-related real Google search queries from NQ-open (CC BY-SA 3.0); (2) REAL-NATIVE: native-speaker-written Hindi (12) and Tamil (39) cricket prompts from the Aya dataset (Apache-2.0); (3) REAL-TRANSLATED: the real English queries translated to Hindi/Tamil by IndicTrans2 (open, MIT); (4) HELD-OUT-GENERATED slices (grammatical gender, romanised, injection) written by a different model family than the training generator. Labels: two independent annotators (a held-out open LLM + Claude), disagreements adjudicated and flagged; rules are never a labeller (avoids inflating the rules baseline); optional 15-min human spot-check of 50 labels | Approve the replacement | G3, G4, E2, E4 |
| D8 | Format-unspecified default (S6) | Approve S6 | T1.6 |

## 8. Schedule (IST)

| Window | Track A: code spine | Track B: model | Track C: humans |
|---|---|---|---|
| Sat 15:30-17:00 | Phase 0: decisions, repo, env, golden loader | Read Laya API locally, GPU check | Start writing test sets (H1) |
| Sat 17:00-23:30 | Phase 1: Cricsheet → DuckDB, registry, facts, rules NLU, policy, composer, API, Gradio (walking skeleton) | T2.1 training-data generator (EN first, then HI/TA) | Test sets; native review of lexicons |
| Sat 23:30-Sun 09:00 | Computed stats, reconciliation report | T2.2 Laya fine-tune (minutes per run), T2.3 calibration/eval, T2.4 Qwen arm (can run while people sleep) | Sleep; freeze test sets before first eval |
| Sun 09:00-15:00 | Phase 3: Space + MCP deploy, record pages, benchmark v1, E1 three-arm run (about 2 h background), cross-sport adapter | T2.5 integrate Laya + rules, CPU latency | Human 20% re-label of E1 outputs |
| Sun 15:00-20:00 | Phase 4: hardening, docs and cards, results regeneration | Model card | Deck, summary, video recording |
| **Sun 15:00** | **Whole tool done** (Sir Jabin, 3 Oct); refinement 15:00-20:00 | | |
| **Sun 20:00** | **Build freeze** (bug fixes only) | | |
| Mon 5 Oct | Re-verify dynamic records (Mandhana, Babar, Deepti, Rashid, Kohli, Harmanpreet, Kapp), final checks, submit. Confirm exact deadline time/timezone first thing | | |

## 9. Quality gates (from docs/08; a failed gate is fixed or reported, never silently weakened)

G1 data loads and reconciles · G2 all 50 golden rows returned by templates · G3 rules-only baseline measured · G4 gender ≥98%/language end to end, stat/format ≥90 EN / ≥85 HI / ≥80 TA, ECE ≤0.05, beats rules on messy slices (TARGETS) · G5 all policy cases tested incl. injection, mixed gender, surname · G6 hosted Space answers EN/HI/TA and an MCP client calls the tool · G7 record pages validate with both records · G8 one command regenerates all results · G9 football answers both genders with sources.

## 10. Risk register (top 8)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Hand-written test sets late → no honest accuracy numbers | High | Start now (Track C); minimum viable sizes are the docs/09 numbers; freeze before eval |
| HF account not eligible for ZeroGPU | Medium | Decide D1 now; fallback = local demo for video + static pages |
| Laya misses G4 on Tamil | Medium | More targeted Tamil data, hierarchy, calibration; report "Tamil: X%" honestly |
| RTX 5060 (Blackwell) needs a CUDA 12.8+ PyTorch build | Medium | Check in Phase 0; Kaggle 2×T4 fallback (notebook trains in ~4-6 min) |
| E1 run time (≈1,500 generations) | Medium | Start by Sun 11:00, run in background, checkpoint per question |
| Records change before submission | Medium | `as_of` everywhere; Monday re-verification task |
| Scope vs 28 hours | High | Vertical slice first (S1), parallel tracks (S2), strict gate order |
| Judges see our own score as circular | Medium | Lead with three-arm accuracy and the prompt-only comparison, never WVR alone |

## 11. What we will not claim

No cross-assistant rates (no consumer-app data). No "AI is biased/sexist/suppresses". No "women hold the records" (men lead all seven ODI categories and several T20I ones). No untested language. No illustrative numbers (the 29% → 97% examples are banned). No global percentages from US survey data. Full list: docs/04 §11, docs/12 §5.

## 12. Skills (agent tooling)

Vetting results and the step-by-step install order are in `../Skills/README.md`. Nothing enters `.claude/skills/` until it passes vetting and Sir Jabin approves it.
