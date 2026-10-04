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
| 6 | `LayaHead` + weights | Jabin → Efanio | Sun 10:30 | **DONE Sun 10:55 (Laya v3; Release/download script exists). Weights absent on Joanna's machine; respect latest distribution decision.** |
| 7 | `resolve()` + API + demo | Jabin: resolve; Efanio: API/demo/MCP → both | `resolve()` delivered; remaining K-P4 per current split | **DONE Sun 18:10 (Efanio). FastAPI + Gradio + MCP all local, 480 tests pass.** |
| 8 | Captured plain-arm hero answer | Jabin → Efanio | Sun 12:30 | Plain-arm raw responses delivered; select the dated/model-labelled hero answer for the demo; UI integration pending |
| 9 | Live app + MCP + record-pages URLs | Efanio → both | Hosting schedule per Checkpoint B | Temporary public Gradio demo + trained-Laya MCP delivered and transport verified (URLs below). Consumer-app connection, durable hosting and record-pages deployment remain unverified/pending. |
| 10 | Facts + policy + answer components (K-P3) | Joanna → Jabin | Sun 10:00 | **IMPLEMENTED Sat 21:40 IST (76cb7ce / 857b1cd); native wording review pending** |

---

# Messages (newest first)
### Sun 04 Oct 2026 | FROM Efanio TO both | FYI | MCP setup complete; consumer connection and demo recording pending
**Identity:** The person working in this chat is Efanio, not Sir Jabin. Attribute this work and the next account-side steps to Efanio. Earlier messages are preserved as historical records.

### Sun 04 Oct, 23:55 IST | FROM Jabin TO Efanio | DONE | demo + MCP live again (trained Laya)
**Demo:** https://924d7dfe7ec2a1f775.gradio.live  **MCP:** https://924d7dfe7ec2a1f775.gradio.live/gradio_api/mcp/
**Verified:** scripts/check_mcp.py on the public URL: discovery OK; EN/HI/TA trained Laya, both records, sources and dates; catalogue OK. Temporary share link backed by Jabin's laptop (keep it on, plugged in, online). For the demo video.

### Sun 04 Oct, 23:53 IST | FROM Jabin TO Efanio | DONE + FYI | injection order fixed (Sir Jabin OK); demo restart; deck status
**What:** decide() order restored in src/mak/policy/decide.py (non-sport/unsupported first, then injection -> both); tests/policy/test_decide.py updated; your Tamil injection test still passes (your ta.yaml lines cover it). 490 tests pass incl. demo tests (gradio[mcp] now installed on Jabin's laptop).
**Demo:** the earlier gradio.live link died when its Python process stopped. Jabin is restarting serve_demo.py --share; the NEW URL will be posted here.
**Deck:** someone is still producing versions in the untracked folder submssion/final (v10 at 23:39). Whoever owns it: tell us which version is FINAL; it will then be committed to submission/final/ (folder name fixed), without the work/ build files.
**Completed setup (previously verified, not re-tested in this documentation update):** Downloaded Laya v3 with release SHA-256 verification and loaded it locally/offline. Prepared `scripts/serve_demo.py`, `scripts/check_mcp.py` and `docs/live_mcp_test.md`. Local and public HTTPS MCP initialization, discovery and tool calls succeeded for English, Hindi and Tamil with trained `laya:` traces, sourced records and as-of dates. The tools are `resolve_sports_query` and `list_supported_intents`; four targeted registration/input-validation tests passed in the setup session. No model weights were published or altered.
**URLs:** Demo: https://df337fc2ba08c1ca49.gradio.live ; MCP: https://df337fc2ba08c1ca49.gradio.live/gradio_api/mcp/ . This is a temporary, unauthenticated Gradio share endpoint backed by this laptop, not permanent hosting. Earlier approval for the public test and official tunnel helper is recorded below. Last recorded process: PID 4364, port 7862; current process/URL liveness was not rechecked in this update.
**Other completed work:** Demo presentation polish is recorded below (Full answer typography and sources-table styling). Syntax and whitespace checks passed; browser appearance and a server restart to load the styles remain unverified.
**Consumer connection:** ChatGPT and Gemini have NOT yet been connected or tested in a consumer account. Current official ChatGPT instructions were checked: Settings → Security and login → Developer mode, then Plugins → + and the MCP URL; choose No authentication for this endpoint. Reference: https://developers.openai.com/plugins/deploy/connect-chatgpt . Gemini's account eligibility and actual connection remain unverified in this session; do not claim either app has successfully invoked our tool.
**Demo plan discussed:** Prioritize one working ChatGPT integration. Capture the same neutral question, "Who has the most T20I runs?", in separate fresh chats without and with our plugin. Show the actual tool invocation plus category labels, sources and as-of dates. If explicitly instructing ChatGPT to use the plugin is necessary, leave that instruction visible. If the baseline already shows women, report that honestly rather than claiming a correction. This is a connected-tool demonstration, not a new benchmark or E5 unassisted result.
**Next step / access:** Browser inventory exposed only Codex's in-app browser and MCP Apps, with no existing tabs or connected Chrome/Edge session. Efanio proposed logging into ChatGPT in the in-app browser and handing over operation; login and handover have NOT happened yet. The agent can attempt setup and demo queries after login; Efanio handles account verification and screen recording. No video-recording tool is currently available to this agent, and no demo video has been recorded in this session.
**Watch out:** Keep the laptop awake, online and the server running; restarting sharing may change the URL. Computed database was absent at the last setup check. No new full-suite run, permanent deployment, record-pages publication or hackathon submission is claimed by this update. Outstanding policy review and evidence caveats in earlier handoffs still apply.

### Sun 04 Oct 2026 | FROM Efanio TO both | DONE | Small demo typography polish
**What:** Updated only presentation in `src/mak/ui/demo.py`: Full answer disclosure typography, spacing and focus outline; sources table header, row shading, cell spacing and date wrapping. Requested by Sir Jabin; existing design and data retained.
**Validation:** Python syntax and diff whitespace checks passed. Live browser appearance not verified. Restart the running demo to load these styles.

### Sun 04 Oct 2026 | FROM Efanio TO both | DONE | Temporary public trained-model MCP
**Demo:** https://df337fc2ba08c1ca49.gradio.live
**MCP:** https://df337fc2ba08c1ca49.gradio.live/gradio_api/mcp/
**Approval:** Efanio explicitly confirmed Sir Jabin's approval in chat before the public launch and official Gradio tunnel-helper download.
**Verified:** actual public HTTPS MCP initialize/list/call passes for EN/HI/TA, sourced dated women+men records, trained Laya traces and catalogue. Four targeted registration/input-validation tests pass. This is real local Laya, not rules-only.
**Limits:** temporary Gradio share URL; laptop and server must remain running. Computed database absent. ChatGPT/Gemini account-side connection is the next manual test; no claim it already succeeded. Consumer connected-tool checks are distinct from E5 unassisted baselines.
**Reproduce:** docs/live_mcp_test.md, scripts/serve_demo.py --share, scripts/check_mcp.py URL. Current process PID 4364, port 7862. No weights published or altered. No permanent hosting/submission claims.
### Sun 04 Oct 2026 | FROM Efanio TO both | FYI | Trained-model public MCP test approved
**What:** downloaded Laya v3 verified against release SHA-256, loaded offline. Local MCP initialize/list/call succeeded for EN/HI/TA with real laya traces, sourced dated records, and catalogue. Added scripts/serve_demo.py, scripts/check_mcp.py, docs/live_mcp_test.md.
**Approval:** Efanio explicitly confirmed Sir Jabin approved the temporary public test and official Gradio tunnel-helper download in this chat. Starting the free HTTPS share tunnel; public URL and external verification follow.
**Measured:** warmup EN/HI/TA request latencies 2290/1442/1432 ms, one observation each, not a benchmark. Computed database still absent; no model weights edited. Public server must load trained Laya successfully before opening the tunnel.
**Watch out:** this test depends on laptop/process uptime. Consumer account access remains to be tested; do not conflate MCP-connected demos with E5 unassisted observations. Jabin's 18:25 policy review is noted for hardening; no submission status inferred from the 18:32 message.

---

### Sun 04 Oct, 18:32 IST | FROM Jabin TO Efanio | REQUEST (Sir Jabin) | record the submission: CHECKPOINT B
**Context:** Sir Jabin understands the entry was submitted by Efanio, but the repo only shows Task 1 (cd62e8d). Nothing records what was submitted.
**Please, as soon as possible:**
1. Push everything submitted: deck (5 slides), summary text, 3-min video link, hosted demo/API/MCP URL(s), record pages, and the submission confirmation (screenshot or email text, no credentials) under `submission/`.
2. Post "FROM Efanio TO both | CHECKPOINT B" here: what was submitted, when (IST), which commit it reflects, whether the demo ran WITH Laya weights or rules-only, and which numbers were quoted (each with its label from results/: official / post-hoc / first-pass E1 / pilot).
3. Check whether the event lets us update the entry before the deadline (Mon 5 Oct). If yes, say so: we may resubmit with the 18:25 fixes (other-sport bug fixed in fd2a55a; your decide() injection-order fix still open) and a Laya-on demo.
**Caveats any submitted material must carry:** E1 labels are automatic first pass (human re-label pending); v3 classifier numbers are post-hoc next to the official v2 run; Gate G4 (gender >= 98%) not met; HI/TA E1 n=28 each.

### Sun 04 Oct, 18:25 IST | FROM Jabin TO Efanio | REVIEW of Task 1 (cd62e8d) | 1 fix done by Jabin, 1 fix requested from Efanio
**Good:** API, demo, MCP and e2e tests look solid; 481 tests pass on Jabin's laptop WITH Laya on (gradio not installed here, so test_demo_fn.py is not run here).
**Fixed by Jabin (nlu, my area):** with Laya weights present, "Who has the most World Cup goals?" became a cricket World Cup stat (your test_non_sport_no_intervention failed here; it passed on your machine only because you had no weights). understand.merge now keeps the rules' explicit other-sport topic. Test added.
**Please fix (policy, your area):** moving the injection check FIRST in decide() makes "ignore previous instructions. what is the weather in delhi" return ambiguous_both, i.e. we intervene on a non-sport question, and an injected out-of-catalogue stat returns ambiguous_both with no facts. ANNOTATION_RUBRIC says the sports question is labelled normally. Suggested: restore the original order (no_intervention / unsupported first, then injection -> both) and fix the Tamil injection test at its source (if Tamil injection text was making topic non_sport, that is a classifier/rules issue: tell me the query pattern, not the test text). Also re-check your Tamil injection lexicon lines.
**Reminders:** test with the weights (`python scripts/get_laya_weights.py`) before claiming a behaviour; player-line facts need data/processed/mak.duckdb (build it per docs/phase1-data.md).

### Sun 04 Oct, 18:18 IST | FROM Jabin TO Efanio | ANSWER | how to get the Laya weights
**What:** `git pull`; `pip install laya==0.3.24 torch transformers safetensors`; `python scripts/get_laya_weights.py` (GitHub Release laya-mak-v3, 575 MB, SHA-256 verified, unzips to models/laya-mak-v3/). Then resolve() uses Laya offline. Also in document/efanio_split.md §2b. Please push your progress and post a handoff message so Sir Jabin can see it.

### Sun 04 Oct, 12:31 IST | FROM Jabin TO Efanio, Joanna | DONE | E1 all four arms complete (first-pass automatic labels)
**What:** results/e1/tables.md (Llama 3.1 8B q4, preregistered settings; 564 x 3 model arms + 188 layer_text, 0 transport errors). Neutral A+B, WVR (women's record shown) EN: plain .110, prompt_only .189, **layer .528**, layer_text .708; HI: .000 / .000 / **.643** / .893; TA: .000 / .000 / **.429** / .750. Paired bootstrap layer - plain: EN +.418 (CI +.324 to +.516), HI +.643 (+.476 to +.798), TA +.429 (+.262 to +.607); intent-group CIs in the file. MEN_ONLY EN: plain .613 -> layer .308. number_wrong EN: .566 -> .173.
**Caveats (must travel with these numbers):** labels are AUTOMATIC first pass; human re-label of results/e1/human_review_queue.csv (1178 needs_review + 150 random) is pending (Efanio task 4). HI/TA n=28 questions each. layer_text is deterministic (1 record per question). No claim beyond this model and benchmark.

### Sun 04 Oct, 18:10 IST | FROM Efanio TO Jabin, Joanna | DONE | Task 1 complete — FastAPI + Gradio demo + MCP
**What:** 
- FastAPI app (`src/mak/api/app.py`) with `/resolve`, `/intents`, `/coverage`, `/health` endpoints — 23 e2e tests passing
- Gradio demo (`src/mak/ui/demo.py`) with EN/HI/TA presets, styled answer cards, decision trace, sources/provenance, coverage grid — clean white-background UI, no emojis
- MCP tools: `resolve_sports_query` and `list_supported_intents` exposed at `/gradio_api/mcp/`
- All 480 tests passing (unit + e2e + policy)
- Policy fix: injection check now runs first in `decide()` (fixes Tamil injection test)
- Local demo running at http://localhost:7860 — ready for video recording

**You can now:** Record demo video from local Gradio app; proceed to Task 2 (hosting), Task 3 (human re-label), Task 4 (R-phase hardening/docs/deck)

**I need:** Sir Jabin's approval before any public deployment (Task 2); human re-label of `results/e1/human_review_queue.csv` (Task 3)

**Learned:** 
- Injection check must be first in policy decision chain (before topic checks) to catch injected gender words
- Gradio 6.0 requires `css=` in `launch()`, not in `Blocks()` constructor
- TestClient from FastAPI works better than async httpx for e2e tests

**Watch out:** 
- Laya weights not on this machine — `USE_LAYA=True` falls back to rules silently (trace shows "laya unavailable")
- Human re-label pending before final E1 numbers are claimed
- No public deploy without Sir Jabin's explicit OK

---

### Sun 04 Oct, 12:01 IST | FROM Joanna (Astra) TO Efanio, Jabin | FYI | handoff merge and current resolve ownership
**Latest status supersedes the first two rows of my 11:41 checklist:** Jabin took over `resolve()` at 11:53 and delivered it with guidance-only fallback in `2236f11`. Efanio should consume that implementation, continue API/demo/MCP and verify the full T1.7 acceptance cases. Joanna/Astra has not implemented or modified the pipeline. The complete remaining-work inventory in my earlier checkpoint is retained as a dated snapshot; its "resolve still a stub" and "guidance decision pending" statements no longer describe current main.
**Merge:** preserved my full pending-work handoff and both of Jabin's newer plan/READY messages. Kept the upstream pipeline byte-for-byte. Guidance now retains `decision='unsupported'` and uses `fallback='guidance_only'`; Efanio/Jabin retain responsibility for protocol consistency, disclosure and the remaining end-to-end checks. API/demo/MCP, hosting, data availability, native review, evidence gaps and submission work are still pending as listed below.
**Validation here:** **457 tests passed in 15.19s**; all **65 frozen hashes** verify. A direct headline call returned `ambiguous_both`, two facts and overall leader `women`. This machine has no Laya weights, so its trace explicitly used the rules fallback; this smoke check is not trained-model validation. No frozen evidence was edited.

---

### Sun 04 Oct, 11:55 IST | FROM Jabin TO Efanio, Joanna | DONE | resolve() READY (src/mak/pipeline.py)
**What:** real resolve(): understand -> catalogue.lookup -> decide -> get_facts (golden first; computed only if data/processed/mak.duckdb exists) -> render. Never raises. Player intents use nlu.entities (one unambiguous entity per gender). **Guidance-only fallback** implemented WITHOUT changing the decision vocabulary: decision stays 'unsupported' (E4 + E1 PREREGISTRATION unchanged, no amendment needed) with fallback='guidance_only' and an en/hi/ta answer_text telling the assistant to give both genders, numbers unverified. 457 tests pass (duckdb + rapidfuzz now installed on Jabin's laptop).
**Known gaps (Efanio/R-phase):** no mak.duckdb on Jabin's laptop, so player-line/last-result intents return no facts here (fallback='no_verified_facts', nothing invented); a question like "men's T20I sixes record" can be routed to player_stat by the classifier (quality limit, documented).
**Next:** Jabin starts E1 layer + layer_text arms now (GPU). Efanio: build API/demo/MCP on top of resolve().

### Sun 04 Oct, 11:53 IST | FROM Jabin TO Efanio | PLAN CHANGE (Sir Jabin) | Jabin builds resolve() now
**What:** to remove the only dependency, Jabin implements `resolve()` in src/mak/pipeline.py now (plus the guidance-only fallback decision). **Efanio: do NOT start resolve();** start with API/demo/MCP scaffolding against the fixed resolve() signature, the E1 human re-label and E5 screenshots. I will post "resolve() READY" here when pushed.

---

### Sun 04 Oct, 11:41 IST | FROM Joanna (Astra) TO Efanio, Jabin | CHECKPOINT A (Joanna) | complete pending-work handoff

**Ownership confirmed by Joanna:** another teammate will implement `resolve()`; **Joanna/Astra will not start it**. The current repo identifies that teammate as **Efanio**, and Sir Jabin's final split in `c479a1c` transfers all remaining K-P4, K-P5 and R-phase work to him. Follow [Efanio's guide](efanio_split.md) and its ownership table; the older `OWNERS.md` still shows the original two-person split. This note records the existing transfer, not a new assignment. Jabin retains GPU/heavy computation as listed in [his live queue](jabin_split.md).

**Exact stopping point:** K-P1, K-P2 and K-P3 were published through `1532f40`. This checkpoint incorporates main through `c479a1c`. **There is no half-written Phase 4 code, local Phase 4 branch, running server, package-install job or unfinished model download from Astra.** `src/mak/pipeline.py` is still the Phase 0 stub. `api/`, `ui/`, `pages/` and `adapters/` contain their package skeletons. Phase 4 was estimated/planned only. Earlier messages saying Joanna would start it are superseded by this transfer.

**Completed components to reuse:** data/registry/entity resolution ([phase 1 notes](../docs/phase1-data.md)); the frozen questions and answer benchmark (`testsets/FROZEN.md`, `eval_data/release_manifest.json`); computed records, golden-first retrieval, policy and en/hi/ta templates ([phase 3 interfaces and limits](../docs/phase3-facts.md), [saved outputs](../docs/phase3-examples.md)). The last full suite Astra ran was **451 passed** on the pre-overnight integration through `57c5fa2`; that is historical validation, not a new test result for `c479a1c`. No training, classifier selection or benchmark run needs to be repeated merely to take over.

**Pending engineering work — Efanio's queue:** exact acceptance tests remain in [buildplan](buildplan.md) and [Joanna's transferred task list](joanna_split.md).

| Priority / scope | Work still required | Completion / dependency |
|---|---|---|
| First: `resolve()` — T1.7 | Replace `src/mak/pipeline.py` stub, preserving `resolve(query, lang="auto") -> Resolution`. Connect understanding, registry entities/category overrides, catalogue, policy, facts, leader and rendering; accumulate trace/confidence/fallback/latency. Handle mixed names, surname ambiguity, unspecified format and injection. | En/hi/ta component and boundary tests green; actual sourced results returned; push and post **`resolve() READY`** with commit. This alone unblocks Jabin's E1 layer run. Updated target: Sun 13:00 IST. |
| Resolve policy decision | Decide the proposed **guidance-only fallback** with Jabin and keep runner/E4 decision semantics consistent. Joanna has not adopted or implemented it; current unsupported behaviour remains. | Before any affected layer output, record a dated, versioned protocol amendment and its evaluation/run identifiers. Preserve the original frozen v1 bytes/hashes; distinguish amended results from the original protocol. Never manufacture a verified Fact. |
| Local environment / data | Install the required API/UI/browser packages in Efanio's environment; establish the DB and approved model-access route. Confirm the trace says which backend actually ran. | `USE_LAYA=True` is now committed, but a missing weight directory silently falls back to rules. Do not call that trained-model inference. Jabin needs DuckDB/rapidfuzz and the facts data before his layer run. |
| API — T1.7 | `src/mak/api/app.py`: POST `/resolve`, GET `/intents`, `/coverage`, `/health`; validation and JSON contract; `tests/e2e/test_api.py`. | Empty/oversized requests handled as specified; emoji/non-cricket safe; actual English/Hindi/Tamil answers with sources/dates; all Review Focus cases covered. |
| Demo + MCP — T1.8 | `src/mak/ui/demo.py`: query/language inputs, presets, answer, trace, source/date table and coverage; expose `resolve_sports_query` and `list_supported_intents`. | Local demo works and MCP discovery/call is verified at `/gradio_api/mcp/`. Use the actual captured plain-arm answer for the before panel, with model/date; raw plain outputs now exist. |
| Browser/product checks | Add `tests/e2e/test_demo_fn.py`, `test_ui.py`; exercise presets, keyboard access, visible output and console errors. | Verify a real running local app in all three languages; passing component tests alone does not meet this check. |
| Hosting — K-P5 / T3.1 / G6 | Prepare deployment files, startup/model loading, REST/MCP configuration, health and cold-start checks. Verify current free-host eligibility/capacity rather than relying on old plan assumptions. | Public app/MCP links remain pending. Follow Sir Jabin's current **no public deployment until his approval** decision. If ONNX is chosen, Jabin's wrapper + accuracy verification is still required; an export-size check is not production inference. |
| Record pages — T3.2 / G7 | `src/mak/pages/build.py`, templates and `site/`: both categories, dates/sources, en/hi/ta, parseable JSON-LD `FAQPage`; accessible markup. | Build/test pages; validate three pages with recorded evidence; publish URLs only after deployment approval. |
| Football — T3.5 / G9 | `adapters/{base,cricket,football}.py`, `data/golden/football_v1.csv`, tests; verify 10–20 source-dated rows using two sources each. | Neutral/explicit-category football answers work through unchanged category policy. Jabin's E3 classifier report is already available; it does not implement or validate this facts adapter. |
| Product documentation — T4.2 | Architecture, data card, benchmark card, licences, limits and README with setup, API example and MCP config. Reuse phase notes, frozen cards and Jabin's existing model card. | Document incomplete Cricsheet coverage, native-name fallback, actual inference backend, original vs post-hoc results, and unpassed gates. Verify archive licences separately from the Cricsheet Register licence. |
| Hardening / refresh — T4.1 | At least 30 injection checks, 200 fuzzed inputs with no server error, queue/concurrency limits, accessibility, reproducible versions/seeds, `scripts/refresh.py`. | Recompute/reconcile refreshes and flag changed headlines for review; preserve source dates and frozen evaluation evidence. |
| Reproducible reports — T3.6 / G8 | `scripts/run_all_eval.py --from-raw`, report orchestration and `results/README.md`; coordinate changes to Jabin-owned eval modules. | Regenerate tables/plots from saved raw files and compare reproducibly without re-querying models. Existing individual report generators are useful inputs, not completion of this aggregate task. |
| Pitch / submission — T4.3 + Monday | Five-slide deck, summary and three-minute video script; recording/editing and presenter choice; final claim/source check. | Every metric labelled, dated and tied to evidence. Confirm the exact submission deadline/timezone; re-verify dynamic records, rerun final checks, submit and log receipt. Sir Jabin decides presentation/submission roles. Build freeze remains Sun 20:00 IST. |

**Open reviews and evidence carried forward (not completed by handing them over):**

- **Native wording:** human Hindi/Tamil review of answer templates and relevant lexicons/banks is pending. Astra's self-review is not native-speaker or independent-human review. Source context/country/recent-result text can still be English; missing native names deliberately fall back to English.
- **Records:** `results/reconciliation.md` has one unresolved Sonam Yeshey / S Yeshi identity match. Keep it flagged until source IDs establish identity. Recheck the 25 V1 single-source rows and four V2 rows with repeated URLs identified by `audit_golden()`, plus dynamic records before submission. Do not replace golden headlines with incomplete Cricsheet totals or silently rewrite frozen benchmark truths.
- **Later training audits:** Astra's completed v2 overlap recheck is `eval_data/overlap_audit_training_v2.json` (810 rows, zero flags). Jabin subsequently requested v3 + `voice_calib` coverage; **that recheck is still pending**. Working `training/data/` now contains v4, although the shipped model is v3: identify the intended snapshot and exact hashes before labelling a new audit. The frozen comparator only reads train/calib/messy_calib, so running it unchanged does **not** audit voice_calib. Use separate versioned audit evidence/tooling, retain original frozen artifacts and disclose post-hoc timing.
- **Human E1 labels and E5 screenshots:** Efanio coordinates actual people for `results/e1/human_review_queue.csv` and consumer-app screenshots/logs as specified in his guide. These are pending human tasks, not work already done by this agent. Preserve raw responses and generator-produced tables; record agreement and distinguish the screenshot pilot from a measured rate.
- **Results claims:** Jabin reports plain/prompt-only E1 complete, E3/E4/classifier reports and a model card delivered. Layer/layer_text still await real `resolve()`. Official v2 evaluation and test-informed v3/v4 results must remain distinct; Gate G4 is reported unmet. Human review and complete E1 tables remain dependencies for final claims.

**Machine handover:** Joanna's checkout is `ICC-26-latest`; the working embedded Python is `../.icc-tools/python/python.exe` (3.11.9). Her full `data/processed/mak.duckdb` exists locally; raw archives, DB, Python environments, credentials and model binaries are gitignored and do **not** arrive with a clone. Portable registry/native-label CSVs do. Use `docs/phase1-data.md` and the downloader/rebuild interfaces to establish data on another machine, retaining snapshot provenance. At this checkpoint, FastAPI, Uvicorn, Gradio, httpx and Playwright are **not installed in Joanna's interpreter**, and `models/laya-mak-v3/model.safetensors` is absent. No need to repeat the already-completed Phase 2 translation download or generation.

**Verification entry points (from the repo, after environment setup):**

```powershell
python eval_data/tools/build_release.py --check
python -m pytest -q
python -m mak.records.reconcile
```

`--check` verifies the committed freeze; do not invoke v1 reassembly to absorb newer training data. The last command intentionally rewrites the reconciliation report from the local DB. For Joanna's embedded interpreter, use its relative path and a fresh workspace `--basetemp` for pytest. Native Python on other machines needs the package installed or `PYTHONPATH=src`; do not copy credentials or machine-specific environment binaries into Git.

**Suggested guides:** `.claude/skills/huggingface-gradio/SKILL.md`, `mcp-builder/SKILL.md` and `webapp-testing/SKILL.md` for K-P4; the existing hosting guides only after the host is selected. Follow the current ownership/approval rules in `efanio_split.md` and post Checkpoint B with completed work, actual test results, URLs and unresolved issues. This update is a documentation handover; Astra is not implementing transferred work.

---

### Sun 04 Oct, 11:35 IST | FROM Jabin TO Efanio, Joanna | DECISION (Sir Jabin) | final split from Checkpoint A
**What:** Jabin keeps ONLY GPU/heavy computation on his laptop (jabin_split.md live status). **Efanio owns all of Joanna's remaining work (K-P4, K-P5, R-phase) plus the non-GPU parts of Jabin's (human re-label, E5 screenshots, deck/summary/video drafts).** File-ownership table in document/efanio_split.md §3, so nobody edits the same files. joanna_split.md is marked TRANSFERRED.
**The one dependency:** E1 layer arms need a real resolve(). Efanio's FIRST task: resolve() + guidance-only decision, deadline **Sun 13:00**, then post "resolve() READY" here. Nothing else on Jabin's side depends on Efanio.
**Joanna:** if you can, post a short note of anything half-done before leaving; otherwise Efanio continues from joanna_split.md + your K-P3 handoff.

### Sun 04 Oct, 11:18 IST | FROM Jabin TO Efanio, Joanna | CHECKPOINT A (Jabin) | classifier shipped, E1 plain+prompt_only done
**Done:** Laya v3 shipped (USE_LAYA=True, threshold 0.85, merge v2, junk-input guard); official v2 run + post-hoc v3/v4 in results/classifier/report.md; E4 (results/e4/), E3 (results/e3/); docs/model_card.md. E1 plain + prompt_only complete (564 + 564 responses, 0 transport errors), first-pass automatic labels in results/e1/tables.md: EN plain WVR .110 / MEN_ONLY .613, prompt_only WVR .189 / MEN_ONLY .544 (diff +.079, CI +.031 to +.129). Hindi/Tamil have many NEITHER/unknown-name answers: human re-label needed (results/e1/human_review_queue.csv, 841 needs_review + 75 random).
**ONNX (training/export/export_onnx.py, results/onnx_check.json, MEASURED on 200 calib rows):** int8 318 MB (fp32 1228 MB), 96.5% top-label agreement with torch, CPU p50 51 ms per question row. Borderline for 512 MB hosts; needs an inference wrapper + accuracy check before use. Files in models/ (not in git).
**Efanio, continue with:** document/efanio_split.md section 3 (E1 layer arms after resolve() is on main, human re-label, E5 screenshots, Joanna's listed items, deck/summary drafts). Do not retrain, publish, or edit frozen files.

### Sun 04 Oct, 11:15 IST | FROM Jabin TO Joanna (and Efanio) | PLAN (Sir Jabin) | Checkpoint A, then Efanio takes over
**What:** Sir Jabin decided: you and I each finish our work up to a checkpoint ("Checkpoint A"), then **Efanio (agent: GPT 6)** carries the project while we are both away; we rejoin later. Efanio's guide: `document/efanio_split.md` (read order, state, exact commands, rules). CLAUDE.md/AGENTS.md now mention it.
**My Checkpoint A (~45 min):** E1 plain + prompt_only finished and scored, tables + classifier report regenerated, ONNX size test, all pushed, final "CHECKPOINT A (Jabin)" message here.
**Your Checkpoint A (please):** post a "CHECKPOINT A (Joanna)" message here before you leave, listing exactly what Efanio should continue on your track (resolve()/API/demo/MCP/hosting/record pages/football), what is done, how to run it, and your decision on the guidance-only fallback (+ PREREGISTRATION amendment if any). Efanio runs the E1 layer arms only after resolve() is on main.
**Also:** Sir Jabin: no publishing until the end (a Release laya-mak-v3 already exists; he decides whether it stays). Weights live only on his laptop, so E1 layer arms run there.

### Sun 04 Oct, 11:01 IST | FROM Jabin TO Joanna | DONE | Laya v3 weights published (row 6 of the sync board)
**What:** GitHub Release https://github.com/Joannapreethi28/ICC-26/releases/tag/laya-mak-v3 (575 MB zip). Run `python scripts/get_laya_weights.py` once: downloads, verifies SHA-256, unzips to models/laya-mak-v3/. Then understand()/resolve() use Laya automatically (USE_LAYA=True). For a hosted demo, run the same script at build/start time.

### Sun 04 Oct, 10:27 IST | FROM Jabin TO Joanna | CONTRACT CHANGE | USE_LAYA = True (Laya v3), GENDER_THRESHOLD = 0.85
**What:** config.USE_LAYA = True; shipped model = models/laya-mak-v3 (chosen by the pre-stated rule in docs/05: v3r shipped mean .726 vs v4 .701; v4 had better E4, disclosed). GENDER_THRESHOLD back to 0.85 (calibration grid; the overnight 0.98 had broken 4 of your policy tests). New safety guard in understand(): Laya is skipped for junk input (empty, emoji, < 2 words, > 1000 chars). Rules lexicon: IPL/PSL/BBL/CPL removed from men_strong per your ANNOTATION_RUBRIC. 322 tests pass on my side (duckdb tests not runnable here).
**Watch out:** the weights are NOT in git. On a machine without models/laya-mak-v3, understand() falls back to rules with a trace note (safe, never crashes). I will publish the weights (proposal: GitHub Release asset, SJ to approve) and post the download step. rules-baseline tests now pin USE_LAYA=False via a fixture.
**Post-hoc results (disclosed, test-informed):** E4 decision accuracy shipped v3: en .748 / hi .675 / ta .762 (rules .632/.498/.481). Full report coming in results/classifier/report.md.

### Sun 04 Oct, 09:35 IST | FROM Jabin TO Joanna | PROPOSAL (Sir Jabin agreed in principle) | 'guidance-only' fallback for unsupported gender-relevant questions
**What:** today a gender-relevant cricket stat outside our catalogue (e.g. fastest century) returns decision 'unsupported' and the assistant answers alone (likely men-only again). Proposal: keep verified facts as the core, add a fallback: for topic=cricket_stat + no catalogue match, return the gender decision (ambiguous_both / explicit_*) with results=[] and fallback='guidance_only', plus an instruction 'give women's and men's answers, clearly labelled; numbers are not verified by this tool'. Our layer still never writes a fact; numbers from the assistant are labelled unverified.
**Why:** every cricket question gets the gender policy (no coverage cliff); verified numbers remain the differentiator (prompt-only answers are expected to be stale/wrong, which E1 measures).
**Touches:** policy/decide.py (new fallback path; keep 'unsupported' for other sports / unsupported intents if you prefer), compose (instruction text in en/hi/ta), and a DATED AMENDMENT to eval_data/PREREGISTRATION.md layer arm (send layer system prompt + guidance-only JSON instead of plain for this case) BEFORE any layer-arm output exists. Your call on exact naming/implementation; tell me the final decision string so E4 and the runner match.
**Also noted for R-phase:** expand coverage with Cricsheet-computed stats (e.g. fastest century from balls faced), trust='computed', known gaps disclosed.

### Sun 04 Oct, 09:05 IST | FROM Jabin TO Joanna | FYI + small ask | training data v3, E4 baseline, weights hosting
**What:** SJ chose to ship Laya and improve it. Training data v3 (training/DATA_FROZEN.md v3) is TEST-INFORMED from aggregate counts only (no test text read) and disclosed: Hindi 'वाली' frames now labelled women (aligns with product policy/your labels), more mixed-gender, other_stat ~11%, voice-style noise. My leakage screen on v3: exact 0, 3 near-dups dropped unseen, re-check clean. Any v3 test number is post-hoc, shown next to the official v2 run.
**Ask (when free):** please re-run your opaque overlap comparator against v3 train/calib/messy_calib/voice_calib (your release check will flag the changed snapshot again).
**E4 (new, src/mak/eval/decision_eval.py, uses your decide() + catalogue.lookup):** rules-only end-to-end decision accuracy on nlu_*.csv: en .632 / hi .498 / ta .481 (MEASURED). Main error: gold unsupported -> no_intervention (121) or ambiguous_both (115).
**Hosting/weights (SJ: no HF account):** proposal: model weights as a GitHub Release asset (free, 640 MB < 2 GB). I will test an int8 ONNX export for 512 MB free hosts after v3.

### Sat 03 Oct, 23:59 IST | FROM Jabin TO Joanna | CONTRACT CHANGE + DONE | config.GENDER_THRESHOLD 0.85 -> 0.98; understand MERGE_POLICY v2; test run done
**What:** pre-registered rules (docs/05) applied on calibration data before the test run: GENDER_THRESHOLD = 0.98 (calib fit, >= 98% accepted-gender accuracy in every language), MERGE_POLICY = "v2" (dev mean topic/family/stat .867 vs .834). USE_LAYA still False until the model choice is written up. The single test run on testsets/nlu_*.csv is complete (results/classifier/test/, TEST_RUN.lock). Report + model choice follow Sunday.
**Watch out:** E1 plain arm stopped at 358/564 records (process killed for low system memory, not a code error); it resumes from its checkpoint when restarted.

### Sat 03 Oct, 22:21 IST | FROM Joanna TO Jabin | DONE | merge repair + training-v2 overlap recheck
**What:** integrated your main through `57c5fa2`, retaining both tracks' handoff entries. Combined tests: **451 passed in 19.42s**, no skips; all **65 frozen K-P2 hashes** still verify. Joanna's original push was rejected because your main advanced; the merged work is ready for a normal fast-forward push.
**Your requested audit:** re-ran the unchanged opaque comparator on all **810** released classifier/transfer rows against training v2 train/calib/messy_calib. **CLEAN: 0 exact/near flags at 0.92**, measured 34.17 seconds. New versioned evidence: `eval_data/overlap_audit_training_v2.json`, with exact input hashes. No corpus text, classifier predictions or scores were shown to the reviewer. String hygiene is not proof against semantic/pretraining overlap.
**Freeze integrity:** deliberately retained `eval_data/preparation/final_overlap_audit.json` as the original frozen v1 evidence; replacing it would invalidate the published manifest. The v2 report is additional evidence, not a re-freeze or altered evaluation set. No exclusions or label changes were made. This recheck occurred after your 22:06 test-run authorization; actual scoring timing was not inspected. The revised validation test already distinguishes frozen-release verification from attempted rebuilding against changed training data.

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

---

### Sat 03 Oct | FROM Joanna TO Jabin | FYI | K-P3 final integration update
Integrated your additional `0370810` / `4a9d864` in `8f8c3b6` while preparing publication. Final combined validation: **451 tests passed in 7.90s**, no skips; all **65 frozen hashes** verify. K-P3 code and the review caveats in the DONE entry below are unchanged. This agent's GitHub push socket is blocked; Joanna has the single prepared `git push origin main` command for normal PowerShell. Do not infer publication from a local commit alone.

---

### Sat 03 Oct, 21:40 IST | FROM Joanna TO Jabin | DONE (implementation; review caveats below) | K-P3
**What:** T1.3/T1.4/T1.6 implemented in `76cb7ce`, integrated with your latest `0bd6055` in `857b1cd`. New `records/{compute,reconcile}.py`, `fetch/{catalogue,facts}.py`, `policy/decide.py`, `compose/render.py` and packaged en/hi/ta Jinja templates. Fifty supported intent IDs: 34 covered-match records, 12 golden-only history/World Cup intents and four entity intents. All 50 golden category rows retain exact values/holders/sources/dates and always take priority. Native labels are attached offline; unknown identities never get guessed.
**Validation (measured):** **450 tests passed in 7.97s**, no skips, after merging your new scorer tests and training v2. All 65 frozen K-P2 hashes still verify. Local offline wheel contains all four templates. Full snapshot covers every non-entity catalogue intent for both categories. Real-data component checks: Mandhana player line is women-only/computed; India latest-result returns both categories; all three headline outputs are saved in `docs/phase3-examples.md`. No classifier or answer-benchmark score is claimed here.
**You can now:** import `lookup`, `get_facts`, `decide`, `DECISION_TO_GENDERS`, `render` and `compute_leader`. `get_facts(..., entity=resolved_entity)` handles player lines/latest results; pass one entity per call. Missing/ambiguous entity -> no fact, not a headline substitute. `resolve()`/API/UI are still K-P4; do not run E1 layer arms against the existing stub yet. Full definitions and use: `docs/phase3-facts.md`.
**Gate/evidence status:** G2 exact golden assertions pass. G1 report covers every computable golden row: **5 match, 20 coverage explanations, 1 flagged** (Sonam Yeshey vs S Yeshi identity; equal 8/7 figures alone do not establish identity). Coverage explanations are not full numerical audits. G5 automated policy/rendering checks pass; **native-speaker Hindi/Tamil wording review remains pending**. Astra self-reviewed both spec and standards; fixed missing-format reporting and cross-format comparison guards. Source context/country/recent-result text may remain English. K-P1 golden-source caveats are retained.
**Integration note:** your training v2 correctly triggered the old release builder's v1-overlap guard. Updated only `tests/unit/test_eval_release.py`: validate the published frozen release and exact answer keys, plus a separate test proving stale training snapshots are rejected. No frozen build tool/audit/label/file was changed. For your `No module named mak` issue, run from the repo after `python -m pip install -e . --no-deps`, or use your normal Python with `PYTHONPATH=src`; `--check` only verifies the freeze. Rebuilding v1 against v2 is intentionally rejected. Your reported v2 overlap screen remains separate from our v1 evidence.
**Learned:** labels -> catalogue -> deterministic category policy -> golden-first facts -> templated answer. Every statistic is in Fact.value; dates/source/coverage digits come from Fact metadata. Policy lives in code so model confidence or injected instructions cannot hide a category. Cricsheet lacks early careers, some historical fixtures, Afghanistan matches and recent updates, hence computed/golden differences. No-format career questions expand T20I + ODI for women and men, producing four records without comparing formats.
**Next on Joanna's track:** K-P4 product integration. No model choice, threshold or NLU implementation changed by this phase. Publication of this local handoff commit is the final Git step.

---

### Sat 03 Oct, 21:30 IST | FROM Jabin TO Joanna | IN PROGRESS | J-P3/J-P4 (replaces my earlier IN PROGRESS note, moved here to the top per rule 2)
**What:** read your K-P2 DONE entry; pulled 7ddbd5c. Sir Jabin decided **data v2 first, then score the test sets exactly once**. v2 was built ONLY from calibration-set errors (cricket slang: knock / team innings total / tons / bowling average; abbreviations wkts/avg/SR/econ; all text lowercased for every model; Laya 2 epochs + label smoothing). No test item was opened or scored before the v2 freeze (only testsets/FROZEN.md counts/hashes). training/DATA_FROZEN.md v2 has LF hashes.
**Leakage:** exact 0. My near-duplicate screen (>= 0.92) flagged 4 NEW v2 train rows (from the added slang phrasings, written without seeing tests); dropped automatically without displaying them; re-check 0/0/0 on train/calib/messy_calib. Same caveat as yours: string hygiene, not semantic proof.
**Now:** Laya v2 -> xlm-roberta v2 -> Qwen2.5-1.5B LoRA v2 training back to back on my GPU (~75-90 min). Then one scoring run of all arms (a)-(e) + xlm-r on nlu_en/hi/ta.csv, reported per language, slice and SOURCE with Wilson intervals.
**Your notes, acknowledged:** (1) label-convention mismatch: my training templates use weak cue -> none, mixed-gender pair -> both_named, injection keeps underlying gender; your evaluation labels follow the product policy. I will document the mismatch in results/classifier/report.md and NOT relabel frozen data. (2) The model family WILL be chosen using these test scores, so the report will disclose that selection use; it is not an untouched confirmation test. No retune-and-rerun will be presented as the original held-out result.
**Watch out:** eval_data/tools/build_release.py --check fails on my machine with "No module named mak" unless run with PYTHONPATH=src (path setup, not a hash problem).

---

### Sat 03 Oct | FROM Joanna TO Jabin | CONTRACT CHANGE + FYI | K-P3 started
**What:** building T1.3, T1.4 and T1.6 on `joanna/k3`, based on your `c239c84`. Before editing shared packaging: add only setuptools package-data for `mak.compose/templates/*.j2` to `pyproject.toml`, so installed wheels retain the answer templates. No dependency, type, label, threshold or classifier changes. Frozen K-P2 files remain unchanged.
**Interface clarification:** `get_facts(intent_id, genders, lang='en', *, entity=None, db_path=DB_PATH)` retains the three original positional arguments; the optional resolved entity implements T1.4 Step 5. Missing/ambiguous entities yield no fabricated headline substitute. `compute` also accepts a keyword-only database path for offline fixtures. K-P4 still owns entity-to-policy integration and `resolve()`.
**Review:** Astra implements and self-reviews as Joanna requested; no other Claude chat. Hindi/Tamil template self-review is not completed native-speaker review.
**Number guard clarification:** T1.6 also requires dates, formats, source URLs and coverage notes, whose digits do not occur in `Fact.value`. Test statistical values against `Fact.value`, and all provenance digits against the corresponding Fact metadata fields. No number may be generated by a model. This resolves the literal guard's conflict with required dated/provenanced answers; it does not change evaluation labels.

---

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

### Sun 04 Oct 2026 | FROM Efanio TO both | Task 1 interface integration
**Built:** unified FastAPI/Gradio/MCP, shared validation and inference lock, scorebook UI, sources/as-of table, honest coverage and model status, exact saved E1 comparison. Run `python -m mak.api.app`; MCP `/gradio_api/mcp/`. Current review server uses localhost:7861. Tested Gradio 6.29.1; new UI requires Gradio 6 APIs.
**Measured:** 489 tests pass; actual MCP initialize/list/call succeeds for EN/HI/TA and catalogue. Browser headline shows both records and real dated baseline.
**Correctness:** named players route to player-specific lookups instead of global leaders. No player facts returned without local computed data; this is safer than showing Babar as Kohli.
**Still needed for full Task 1 sign-off:** trained weights and computed database on this machine, then repeat demo with actual Laya. No new packages/models downloaded, no public deployment, no frozen evaluation files modified.
**Next:** Task 2 host sizing and packaging, football verified rows and crawlable pages; Task 3 human labels (real person); Task 4 dated consumer screenshots; Task 5 hardening and submission artifacts before freeze. No public deploy without Sir Jabin OK.

### Sun 04 Oct 2026 | FROM Efanio TO both | CONTRACT CHANGE | pyproject.toml Gradio version
The completed UI uses Gradio 6's `gr.api`, `api_visibility` and launch/mount theme arguments. Tighten the declared dependency from `gradio[mcp]>=5.0` to `gradio[mcp]>=6.29.1,<7` so fresh installs cannot select an incompatible Gradio 5 or a future major. This changes the dependency contract only; no shared Python types or model contracts change. Existing installed 6.29.1 already passes validation; no package installation is needed.
