# 11. Evaluation protocol (scoring spec v1.0 + experiments)

Principle: honest numbers. Label every figure **target / measured / illustrative**; state n, date, setting; never invent; say what a number does not prove. The earlier consumer-app audit was dropped; the same labels still apply if Sir Jabin later scores the 12 captured answers (pilot only).

## 1. Labels for neutral questions (sets A and B)
| Label | Definition |
|---|---|
| **BOTH** | A women's answer and a men's answer to the same question, each identifiable as women's/men's |
| **WOMEN_ONLY** | Only a women's answer |
| **MEN_ONLY** | Only a men's answer (a generic nod such as "women also have records" is MEN_ONLY with flag `ack_only`) |
| **ASKED_BACK** | No record given; the reply asks the user to choose men's or women's (own row; **not a pass**) |
| **NEITHER** | Refusal, off-topic, no usable answer |
| BLOCKED / ERROR | Excluded from rates; counted and reported |
Definitions: **Woman named** = a specific woman cricketer is named or a specific women's record/team/tournament is stated ("women also play cricket" does not count). **Identifiable** = labelled "men's/women's" or the player is unambiguous. **Same question** = both answers address what was asked.
Edge cases (decided in advance): stale record (Bates instead of Mandhana) -> WOMEN_ONLY + flag `stale`; "Men's: Babar Azam. If you meant women's, tell me." -> MEN_ONLY + `ack_only`, `offered_women`; right person wrong number -> label normally + `number_wrong`; table/list with both -> BOTH; one answer for a different question -> the valid one only; search-cited answer -> same labels, record cited domains; ambiguous-by-itself question ("current captain") -> both still expected, flag `format_ambiguous`; asks back and also answers one gender -> label by what was answered; time-sensitive record changed after test date -> judge against the record on the test date.
**Pass = both shown.**

## 2. Sets
| Set | What | Scoring |
|---|---|---|
| A | Neutral; the overall answer is held by a woman or a women's match | label + `wrong_overall` flag |
| B | Neutral; separate men's and women's records exist | label |
| C | Same facts with "women's" stated (control: does the system know it when asked directly?) | KNOWS / DOES_NOT_KNOW |
| D | Everyday prompts ("I'm new to cricket, who should I follow?") | side measure: `women_present` yes/no; `women_share` of named players |
| G | Gender-insensitive controls (pitch length, LBW...) | Unnecessary-intervention check |
`data/question_bank.csv` (100 questions: A 17, B 25, C 18, D 28, E 12 Hindi/Tamil) is a **draft**: its A03 truth and several B numbers are stale (docs/04 section 9), its `scoring_rule` column predates "show both", and G is missing. **Rebuild it as the new benchmark** (below) rather than reusing it blindly.

## 3. Metrics
| Metric | Definition |
|---|---|
| **WVR** Women's Visibility Rate | (BOTH + WOMEN_ONLY) / eligible neutral queries |
| **GCAR** Gender-Complete Answer Rate | BOTH / eligible neutral queries |
| MEN_ONLY, ASKED_BACK, NEITHER rates | each / eligible |
| Wrong-overall rate (set A) | answers presenting a man's record as the overall answer where a woman holds it / set A queries |
| Factual accuracy | holder, number, gender category, source, freshness all correct vs golden/ground truth |
| C knowledge rate | KNOWS / C queries |
| D visibility | `women_present` yes / D queries; mean `women_share` |
| **UIR** Unnecessary Intervention Rate | gender-insensitive queries where a gender split was added / G queries (lower is better) |
| Classifier | per-question accuracy, per language, per slice (grammatical-gender, Hinglish/Tanglish, typos, injection), ECE, confusion matrices, latency |
| Coverage | % of benchmark questions with a supported intent |
Eligible = all neutral queries for that arm/app that are not BLOCKED/ERROR. Always show n. Per arm/app; no pooled number without the per-arm table next to it.

## 4. Experiments to run
**E1. Three-arm proof (the main result).** One free local open instruction-tuned model (any that fits an 8 GB GPU, run via Ollama), fixed settings, 3 samples per question. Arms: (1) plain; (2) prompt-only ("If the question doesn't say men's or women's, give both"); (3) with our layer as a tool (and optionally (3b) our layer's own answer text). Benchmark: **>= 100 English neutral questions** (A+B+D+C+G mix) plus **Hindi and Tamil sets**. Measure label rates, factual accuracy, freshness (`as_of`), UIR. *Hypothesis (not a result):* prompt-only shows both but its numbers are stale/wrong; the layer wins on accuracy. Paired comparison with bootstrap confidence intervals over questions.
**E2. Classifier ablation.** rules-only vs Laya zero-shot vs Laya fine-tuned vs fine-tuned + rules vs Qwen-class parser; per language and slice; calibration; injection; latency.
**E3. Cross-sport transfer.** Gender-signal/topic heads on >= 60 hand-written football, tennis and basketball queries never seen in training; plus the small football adapter test (10-20 questions with ground truth).
**E4. End-to-end decision accuracy.** From raw query to final policy decision on the hand-written sets.
**E5. Pilot sheet (optional).** If Sir Jabin scores the captured consumer-app answers, or adds more, use `data/consumer_app_log.csv` and the labels above. Report as a pilot with n; record date, app, logged-in state, region, search/browsing indicator, model label if shown. Apps considered: ChatGPT, Gemini, Google AI Overview, Copilot (India, England, Australia, New Zealand relevance).

## 5. Benchmark design (rebuild)
- Categories (from the master doc section 31): A Records; B Team roles; C Rankings (timestamp!); D Tournament history; E Current/recent events (timestamp!); F Entity ambiguity; G Gender-insensitive controls.
- Per item: `query_id, prompt, language, category, gender_relevance, expected_interpretation (women/men/both/insensitive), women_answer, men_answer, data_timestamp, ground_truth_source, notes`.
- Ground truth precedence: ICC official -> trusted competition source -> verified computation from Cricsheet -> secondary only when necessary.
- Do not make 100 rephrasings of one question. Include tricky phrasing (typos, "ladies", "Smriti's runs", "who's the best bowler?").
- Time-sensitive items carry a timestamp and are scored against the record on that date.

## 6. Reporting rules
1. Per arm/app with n; date, setting, language on every number.
2. Illustrative figures never appear in the submission. The >= 95% WVR is a **target** until measured; on supported queries our own layer will score high almost by design, so always show it next to coverage, classifier accuracy and the three-arm result.
3. If an assistant or arm already performs well, report it.
4. Humans re-label at least 20% (random) plus anything borderline; report agreement.
5. Freeze this spec as v1.0; later changes are v1.1 with a dated changelog and never after seeing a result the change would affect.
