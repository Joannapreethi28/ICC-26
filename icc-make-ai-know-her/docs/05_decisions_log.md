# 05. Decisions log (chronological) and what was dropped

Dates are 2-3 Oct 2026. "SJ" = Sir Jabin.

## 2 Oct
- Earlier directions (Audience Curve, Spotlight, etc.) rejected (docs/02). Candidate problem statements were drawn from the "Winning Problem Statements" research pass.
- SJ chose **"Make AI know her (knowledge layer)"**: an open API + MCP server for women's cricket (Cricsheet + Wikidata, multilingual labels) so any AI answers correctly. Prior evidence: AI assistants biased toward men's results in an Olympic study. To settle: run ~100 ambiguous cricket questions across assistants.

## 3 Oct (this chat)
1. **Refinement brief:** make it focused and punchy for one slide, ICC-facing; validate on popular (not newest) consumer LLMs; save the data. Research done: the Olympic paper (arXiv 2502.04218), usage data, ICC-Google partnership, prior art.
2. **Attempts to test assistants from the sandbox failed:** keyless LLM endpoints (Pollinations, DuckDuckGo AI chat, OpenRouter) unusable without keys or behind bot-checks (`scripts/probe_free_llm_endpoints.sh`). Claude in Chrome was not connected at first.
3. **Source-page audit** (Wikipedia pageviews and content) produced real data (docs/04 section 6).
4. **Question bank (100) and runner** built (`data/question_bank.csv`, `scripts/build_bank.py`, `scripts/run_audit.py`). Sets: A neutral-with-woman-holder, B neutral-with-separate-records, C explicit-women controls, D everyday prompts, E Hindi/Tamil. **Now partly stale** (ground truth for A03 and some B items; scoring rule predates "show both").
5. **SJ rule (locked): neutral cricket question -> show both men's and women's records, labelled.** Scoring consequence: pass = both shown; men-only = fail; women-only = incomplete.
6. **Claude-in-Chrome audit plan** went through versions (`prompts_archive/`): v1 plan, v2 (flags not labels, checkpoints), v2.1 (user handles logins, strict privacy), v2.2 (reads project context), v3 relaxed (SJ: too many restrictions), v3.1 parallel+auto, v3.2 composer check (after the agent sent a ChatGPT question in "Create image" mode). **Outcome: the extension kept returning "tab not in Claude's tab group" on about half the calls and re-grouped tabs between steps; the agent stopped after A01-A04 on three apps and could not safely continue. SJ dropped the plan** ("we already have enough sources and findings"; "we know the current system gives biased answers, then what"). Lesson: I over-sold its reliability as a time-saver. The captured 12 answers (if SJ keeps them) are a pilot only.
7. **SJ's discussion/research master doc read and source-checked** (docs/04 section 10). SJ confirmed he wrote it.
8. **Locked scoring decisions:** "asked back" is its own row and not a pass; everyday prompts included as a side measure; test assistants India/England/Australia/NZ-relevant: ChatGPT, Gemini, Google AI Overview, Copilot; target markets India, England, Australia, NZ.
9. **Deadline plan:** SJ committed both days; build stops **Sun 4 Oct 8 pm**; Mon 5 Oct buffer only. (The Ignyte page exact time/timezone still to be confirmed.)
10. **Records table compiled** (`data/records_v1.csv`, 50 rows) with source and as-of date per row; **several earlier facts were stale and corrected** (docs/04 section 9).
11. **Architecture iterations:** v1 rules + optional Jev -> **Jev dropped** (paid, no free tier; SJ: everything must be free) -> v2 trained Laya + rules + database-computed facts -> v3 four bands (built once / every question / where it shows up / proof) adding crawlable record pages and a three-arm proof.
12. **Why not only 50 rows:** SJ challenged this. Answer adopted: the 50 rows are the **answer key/golden set**; coverage comes from a database computed from Cricsheet; unsupported questions stay silent; coverage is published.
13. **Final approvals (SJ):** solution v3 approved; **no work-splitting by the assistant**; **no cut line**: MUST/SHOULD/NICE all get built; **Laya (or Qwen-class) must be trained well**; **Tamil must be included** to show multilinguality. Rules-only stays only as a baseline measurement.
14. SJ asked for this context pack to carry every reference, script and decision to Claude Code / GPT 6.

## 3 Oct (planning session, Claude Code)
15. **SJ:** do not chase recorded consumer-AI answers for the demo for now. Proposed replacement: the demo's "before" panel shows the real captured plain-arm answer from the E1 local-model run (labelled model + date).
16. **SJ:** build from docs/08, made concrete in `../document/buildplan.md` (strategy in `../document/plan.md`; session state in `handoffs.md`; mistakes in `gotcha.md`).
17. **SJ:** agent skills must be vetted (owner, licence, contents, scripts, free-only) before entering the working folder; installed step by step, project-scoped. Registry: `../Skills/README.md`.
18. Open decisions D1-D8 listed in `../document/plan.md` section 7 (hosting, two golden-set fixes, E1 model, Qwen arm, football sources, repo location, test-set writers, format-unspecified default).

19. **SJ (3 Oct, 17:45):** D2 approved and applied (two `overall_leader` cells fixed). D7 approved: test sets come from real queries + native-speaker prompts + translations + held-out-generator slices (CLAUDE.md non-negotiable 4 amended). D3-D6 and D8 approved as recommended in `../document/plan.md` §7 (Llama 3.1 8B for E1; Qwen2.5-1.5B LoRA arm; football facts only with two sources; code at the repo root of https://github.com/Joannapreethi28/ICC-26; format-unspecified -> T20I + ODI, both genders). D1 pending (SJ is finding an HF account older than 30 days).
20. **SJ:** team split: Jabin = model/training/evaluation; Joanna (agent Astra) = data/test sets/facts/product/docs. Minimise dependencies; whole tool done before Sun 4 Oct 15:00 IST, then refinement until the 20:00 freeze. Bright Data plugin removed (paid). Commits from Jabin's machine as `jabssyyy`, no AI co-author.

## Dropped / killed (do not revive without new evidence)
| Item | Why |
|---|---|
| Jev as the classifier | Paid, no free tier; project must be free |
| Claude-in-Chrome consumer-app audit | Tool unreliable (tab-group errors), time sink; SJ judged evidence sufficient |
| Rules-only as the end state | SJ requires a trained model; rules-only is a baseline |
| "Women's-only MCP server" framing | Not novel; the policy is the product |
| Promoting women over men / always showing women | Reverse-bias risk; policy is symmetric |
| Global percentage claims | No defensible denominator |

## Open decisions (none blocking the build)
- Which free local LLM to use for the three-arm test (any open instruct model that fits an 8 GB GPU).
- Exact free hosting split (Hugging Face Space for demo+MCP+API; static pages host for record pages).
- Whether to also use ICC official data later (production path; not for the hackathon).

## J-P2 data decisions (3 Oct, Jabin)
- Generated data goes to `training/data/` and its tests to `tests/nlu/`.
- Labelling conventions: weak gender cue -> none; mixed-gender player pair -> both_named; injection keeps the underlying gender; labels come from the template, never the rules labeller.
- Calibration uses template families disjoint from training, so calibration measures unseen phrasings.
- Sizes: train 3,600 per language, calib about 1,000 per language, seed 20261003. Hindi/Tamil banks are synthetic until native-speaker review (before G3).

## Classifier base model: proposal to replace Laya (3 Oct 2026, Jabin; PROPOSAL until Sir Jabin confirms)
Trigger: Sir Jabin asked for a more popular, verifiable model. HF numbers pulled by API on 3 Oct 2026 (downloads are the last 30 days): xlm-roberta-base 16.0M downloads / 927 likes / MIT / Meta, 2022; mdeberta-v3-base 5.8M / 243 / MIT; multilingual-e5-base 7.2M / 391; xlm-roberta-large 2.7M / 538; mBERT 1.7M / 607; google/muril-base-cased 52k / 66 / Apache-2.0 (Google, Indian languages); jhu-clsp/mmBERT-base 376k / 259 / MIT (JHU, ICML 2026 poster; this is Laya's backbone); laya-multilingual 0 / 358 / Apache-2.0 (created 19 Sep 2026, vendor: Convai Innovations, founder named on its own site, third-party listings exist but no independent track record).
Proposal: fine-tune standard encoders with ordinary classification heads (one head per question: gender_signal, topic, family, format, stat_*) on the frozen data. Primary: xlm-roberta-base (most used, best provenance). Comparison arms trained on the identical data: mmBERT-base, MuRIL, and Laya if time allows. The winner is chosen by the held-out per-language test results, not by popularity. Qwen-class LoRA stays as the other comparison arm.
Why: removes dependence on an unverified vendor and a typed-decision wrapper; the data format (labels per question) is unchanged. Cost: we lose Laya's pretrained calibrated decision head, so we calibrate ourselves (temperature scaling on calib.jsonl).
Conflict: CLAUDE.md non-negotiable 3 names Laya or Qwen-class; edit CLAUDE.md and AGENTS.md only after Sir Jabin confirms.

### Correction (3 Oct 2026, Jabin): the '0 downloads' signal is likely a counting artefact
Both Laya repos report 0 downloads (30-day and all-time) while having 358 and 5,042 likes. Neither repo has a root `config.json` (the encoder config is in `encoder/`), and Hugging Face counts downloads from requests to specific files, so the counter probably never increments for this layout. This is an inference, not verified with Hugging Face. So 0 downloads is NOT evidence against Laya; likes show real attention, though likes can be gamed. The safety audit (docs/09) found nothing wrong. Revised proposal: do NOT drop Laya. Fine-tune Laya AND xlm-roberta-base (plus mmBERT-base and MuRIL if time allows) on the identical frozen data; choose by held-out per-language results. This stays inside CLAUDE.md non-negotiable 3 (Laya or Qwen-class), so no edit to CLAUDE.md is needed unless the winner is not Laya.

### Data v2 before test scoring (3 Oct 2026 ~21:30 IST, SJ decided)
Context: v1 Laya and xlm-roberta were trained and checked on the calibration set only. Calibration errors showed (a) four cricket phrasings that existed only in calibration templates (knock, team innings total, tons, bowling average: 83 of 89 English career-stat errors), (b) ALL-CAPS text hiding gender cues and 'wkts' breaking stats (G-026), (c) saturated confidences (temperatures 3.2-5.0).
Options shown to SJ: v2 first then test once / score v1 now / no v2. **SJ chose "v2 first, then test once".**
v2: English slang phrasings in train and calib positions; 'abbrev' noise op; all text lowercased for every arm at train + inference; Laya 2 epochs + label smoothing 0.05 (CE only). Hindi/Tamil banks unchanged (no native review). Frozen in training/DATA_FROZEN.md v2; leakage screen dropped 4 near-duplicate train rows unseen.
Disclosure (Joanna's K-P2 note): the winning model family will be selected using the frozen test scores, so that run is a selection run, not an untouched confirmation test; the report says so. No retune-and-rerun is presented as the original held-out result.

### Test scoring before Joanna's overlap re-audit (3 Oct 2026 ~22:15 IST, SJ decided)
Neither SJ nor Joanna is available before Sun 10:30. SJ chose to run the single test scoring tonight on the basis of Jabin's own v2 leakage screen (0 exact, 0 near >= 0.92 after dropping 4 unseen rows). Order: GENDER_THRESHOLD + merge policy fixed on calibration data first, then one test run (TEST_RUN.lock). If Joanna's re-audit later flags rows, they are excluded and disclosed as post-hoc; the run is not repeated.

### Pre-test decision rules (fixed 3 Oct ~22:30 IST, before any result): GENDER_THRESHOLD = calib fit (none found -> 0.85); merge v2 only if it beats v1 by >= 0.005 mean topic/family/stat accuracy on calib+messy; outcome in results/calibration/pre_test_decision.json; CONTRACT CHANGE posted after. Laya v2 calib: en .959/hi .970/ta .943; ta gender .969 (13/31 errors are injection rows the pipeline forces neutral; real misses: veeranganai x6, mixed pairs x3).

### 'Guidance-only' fallback (4 Oct, SJ agreed in principle; Joanna implements/decides naming)
Gender-relevant cricket stat questions outside the catalogue get the gender decision + instruction with no facts (results=[], fallback=guidance_only) instead of a bare 'unsupported'. Verified facts stay the core value. Requires a dated PREREGISTRATION amendment before layer-arm outputs exist. R-phase: expand coverage via Cricsheet-computed stats.

### GENDER_THRESHOLD back to 0.85 (4 Oct, Laya v3)
Calibration grid for v3 (rows without rules cue/injection): accepted gender accuracy 100% for every t in 0.50-0.95 in all languages; accept rate ~12-13%; 0 accepted above 0.95 (v3 confidences top out ~0.95-0.96). 0.50 rejected (breaks fail-safe tests, non-negotiable 7). 0.85 = original contract value, same calibration outcome as 0.90, keeps Joanna's policy tests green (the overnight 0.98 had broken 4 of them and disabled Laya's gender). Chosen on calibration data only.
