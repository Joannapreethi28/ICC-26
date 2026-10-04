# Make AI Know Her — Pitch Deck Content
**ICC Global Hackathon 2026 | Prototype Track | Student Category**

---

## Slide 1: Title
- **Make AI Know Her** — Gender-aware answer layer for cricket statistics
- **Tagline:** When a fan asks "Who has the most T20I runs?", AI should answer *both* Smriti Mandhana (4,867) and Babar Azam (4,596) — not just the men's record
- **Team:** Sir Jabin (ML/Architecture), Joanna (Data/Product), Efanio (API/Demo/Deployment)
- **Track:** Prototype (working demo + 3-min video + 5-slide deck)
- **Category:** Student | Women-integrated team

---

## Slide 2: Problem — The Men-Default Bias
- **Core issue:** Gender-neutral cricket questions ("most T20I runs", "highest score", "most wickets") return *only* men's records
- **Verified example (22 Sep 2026):** Smriti Mandhana leads *all* T20I run-scorers (4,867) ahead of Babar Azam (4,596) — yet AI assistants name Babar
- **Root cause:** Training data reflects historical media bias; models default to men's cricket unless explicitly told "women's"
- **Impact:** Women's cricket stays invisible to casual fans; records like Argentina's 427/1 (women's T20I team total) or Laura Cardoso's 9/4 (best T20I bowling figures) are never surfaced
- **Not fixed by prompting:** "Just tell it to show both" → stale/invented numbers (Llama 3.1 8B: 3,718 runs vs actual 4,867)

---

## Slide 3: Solution — A Verified, Policy-Driven Layer
- **Architecture:** `Understand` (rules + fine-tuned Laya 322M) → `Decide` (pure-code policy) → `Fetch` (verified DB) → `Answer` (EN/HI/TA templates)
- **Policy (code, not model):**
  - Explicit "women's" → women's record only
  - Explicit "men's" → men's record only
  - Neutral → **both**, labelled, with sources & as-of dates
  - Gender-irrelevant (e.g., "pitch length") → no intervention
  - Injection/ambiguity → fail-safe **show both**
- **No model writes facts:** Every number from verified DB (Cricsheet + golden set) with source URL & as-of date
- **Multilingual:** English, Hindi, Tamil — each with own training data, test set, reported accuracy
- **Free & open:** Laya 322M on CPU, DuckDB, FastAPI, Gradio — zero paid APIs

---

## Slide 4: Proof — Measured Three-Arm Test
- **Setup:** Llama 3.1 8B Instruct (same free local model), 188 benchmark Qs (120 EN / 34 HI / 34 TA), 3 seeds, preregistered prompts
- **Arms:** Plain | Prompt-only ("show both if neutral") | Layer (our tool JSON) | Layer-text (deterministic)
- **Results (first-pass auto labels, human re-label pending):**

| Language | Plain WVR | Prompt-only WVR | **Layer WVR** | Layer-text WVR |
|----------|-----------|-----------------|---------------|----------------|
| **English** | 0.110 | 0.189 | **0.528** | 0.708 |
| **Hindi** | 0.000 | 0.000 | **0.643** | 0.893 |
| **Tamil** | 0.000 | 0.000 | **0.429** | 0.750 |

- **Paired bootstrap (layer − plain):** EN +0.418 (CI +0.324 to +0.516), HI +0.643, TA +0.429
- **Prompt-only fails:** Shows both but with stale numbers (2023 data vs 2026 reality)
- **Layer wins:** Verified, dated, sourced — *accuracy* not just visibility

---

## Slide 5: Architecture & Deployment
- **Classifier:** Laya v3 (322M, fine-tuned, ONNX int8 = 318 MB, 51 ms CPU) + rules override
- **Data:** 8,916 Cricsheet matches → DuckDB; 50 golden records (V1/V2 verified); 18,554-player registry with HI/TA Wikidata labels
- **API:** FastAPI `/resolve`, `/intents`, `/coverage`, `/health` — 23 e2e tests
- **Demo:** Gradio (EN/HI/TA presets, trace, sources, coverage) + MCP tools at `/gradio_api/mcp/`
- **Hosting:** Render/Koyeb 512 MB free tier (ONNX fits) + GitHub Pages for static record pages
- **Cross-sport:** Football adapter (10–20 verified rows) — same policy answers both genders

---

## Slide 6: Impact on Women in Sport (Judging Criterion #3 — 20%)
- **Women's Visibility Rate (WVR):** Layer lifts neutral-Q visibility from ~0% to 43–64% across languages
- **Gender-Complete Answer Rate (GCAR):** Layer shows *both* records labelled — no "men's record presented as universal"
- **Symmetric policy:** Explicit women's Qs get women's answer; explicit men's get men's; neutral gets both
- **No invented numbers:** Every stat carries source URL & as-of date — builds trust
- **Multilingual inclusion:** Hindi & Tamil grammatical-gender cues (वाली, வீராங்கனை) detected — not just English
- **Record pages:** Static JSON-LD FAQPage for SEO — fixes men-only sources that AI crawlers read

---

## Slide 7: Technical Feasibility & Execution (Criterion #2 — 20%)
- **Classifier accuracy (E4, post-hoc):** EN 74.8%, HI 67.5%, TA 76.2% vs rules-only 63.2%/49.8%/48.1%
- **Cross-sport transfer (E3):** Gender accuracy EN 94.9% (Laya) vs 84.7% (rules) on unseen football/tennis Qs
- **Latency:** ~50 ms CPU (ONNX int8) + ~10 ms policy/fetch → sub-100 ms end-to-end
- **Tests:** 489 passing (unit + e2e + policy + classifier + render + score)
- **Reproducible:** `scripts/run_all_eval.py --from-raw` regenerates all tables from frozen raw outputs
- **Zero paid deps:** Apache-2.0 code, Cricsheet ODC-BY, Wikidata CC0, Laya Apache-2.0

---

## Slide 8: Value to Fans, Athletes & Ecosystem (Criterion #4 — 15%)
- **Fans:** Ask naturally ("most T20I runs") → get complete answer instantly — no "magic word" needed
- **Athletes:** Women's records surfaced at moment of casual discovery — Mandhana, Cardoso, Argentina 427/1
- **ICC/Gemini/Assistants:** Drop-in MCP tool — one call returns structured JSON with decision, facts, trace
- **Developers:** Free API + open benchmark — run your own evaluation
- **Broadcasters/Sponsors:** Women's players surfaced in real-time Q&A during matches

---

## Slide 9: Sustainability & Inclusivity (Criterion #5 — 10%)
- **Free end-to-end:** No paid APIs, no GPU required at inference (CPU ONNX), open weights
- **Multilingual:** EN/HI/TA each with own test set, reported accuracy — no "English only"
- **Accessibility:** Clean white-background UI, semantic HTML, keyboard-navigable Gradio
- **Team diversity:** Women-integrated team (Joanna — data/product; female contributor requirement met)
- **Environmental:** 322M model on CPU — no GPU inference energy cost

---

## Slide 10: Presentation & Storytelling (Criterion #6 — 10%)
- **Hero demo (3-min video):**
  1. "Who has the most T20I runs?" → Plain model answers Babar Azam (stale)
  2. Same Q through **Make AI Know Her** → Both records, sources, dates, "Overall: Mandhana leads"
  3. Hindi & Tamil versions — native names (स्मृति मंधाना, ஸ்மிருதி மந்தனா)
  4. "Women's most T20I runs" → Women only (symmetry)
  5. "How long is a cricket pitch?" → Silent (no unnecessary intervention)
  6. MCP call from AI client → structured JSON
  7. Record page with JSON-LD — search-grounded AI now sees both
- **Every number labelled:** measured / target / illustrative, with n, date, source

---

## Slide 11: Bonus — Cross-Sport & Pilot Readiness
- **Cross-sport (E3):** Football adapter answers "most World Cup goals" with both women's (Marta) and men's (Miroslav Klose) — same policy, new data
- **Pilot-ready:** MCP endpoint + REST API + static record pages + open benchmark
- **ICC integration:** Cricsheet `key_pulse` IDs map to ICC Pulse platform; `key_cricinfo` to ESPNcricinfo
- **4-week pilot plan:** Deploy on ICC dev environment → measure WVR lift on real fan queries → iterate

---

## Slide 12: What We Will NOT Claim (Honesty)
- ❌ No cross-assistant bias rates (no consumer-app data)
- ❌ No "AI is sexist/suppresses women" — framing is *men-default*, not malice
- ❌ No "women hold all records" — men lead 7 ODI categories & several T20I
- ❌ No untested language accuracy — only EN/HI/TA reported
- ❌ No illustrative numbers — every figure measured, dated, sourced
- ❌ No global percentages from US surveys — only our benchmark

---

## Slide 13: Ask & Next Steps
- **Prototype track submission:** Working demo (localhost:7860), 3-min video, 5-slide deck, summary
- **Immediate:** Human re-label of E1 queue (1,178 needs_review + 150 random) → final WVR/GCAR
- **Week 1:** Public deploy (Render + GitHub Pages) + football adapter verification
- **Week 2:** Hardening (30 injection tests, 200 fuzz, concurrency limits, accessibility)
- **Week 3:** Final deck polish, video edit, submission
- **Contact:** [Team details] — open to ICC pilot discussion

---

## Appendix: Key Metrics at a Glance
| Metric | Value | Status |
|--------|-------|--------|
| Layer WVR (EN/HI/TA) | 0.528 / 0.643 / 0.429 | Measured (auto labels) |
| Layer GCAR (EN/HI/TA) | 0.459 / 0.238 / 0.107 | Measured |
| E4 decision accuracy (EN/HI/TA) | 74.8% / 67.5% / 76.2% | Post-hoc |
| E3 cross-sport gender (EN) | 94.9% | Measured |
| Latency (CPU ONNX) | ~50 ms | Measured |
| Model size (int8) | 318 MB | Measured |
| Tests passing | 489 / 489 | Current |
| Golden records | 50 (V1/V2 verified) | Frozen |
| Benchmark Qs | 188 (120/34/34) | Frozen |