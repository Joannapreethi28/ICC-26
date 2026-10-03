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
