# 15. Corrections, open risks and things to verify

## A. Known stale or wrong items still sitting in the files
| File | Problem |
|---|---|
| `archive/findings_v0_CONTAINS_STALE_NUMBERS.md` | Mandhana 4,788, Rohmalia 7/0 as best bowling, Deepti 166, Rashid 193, old men's best 7/8 |
| `data/question_bank.csv`, `scripts/build_bank.py` | A03 truth and markers (7/0, Rohmalia), several B-set numbers from memory, `scoring_rule` predates "show both", no gender-insensitive (G) set |
| `archive/plan_v1_PARTLY_SUPERSEDED.md` | Part 3 prompt superseded; spec Part 2 superseded by docs/11 |
| `archive/build_spec_v1_SUPERSEDED_by_docs_08.md` | Assumed Jev optional, 25 intents hand-typed, cut line, Chrome-era scope |
| `source_docs/discussion_make_ai_know_her_master.md` | Mandhana 4,788; "ICC strategy" PDFs are annual reports; multilingual marked "later" (now required); illustrative numbers in section 29 |
| `source_docs/context-2-icc_AUDIENCE_CURVE_SUPERSEDED.md` | Entire Audience Curve problem is rejected; only event facts used |

## B. Things to verify before the submission (Mon 5 Oct at the latest)
1. **Exact deadline time and timezone** on the Ignyte page; participant count (~9,000 is team-reported).
2. **Dynamic records** (Mandhana, Babar, Deepti, Rashid, Kohli, Harmanpreet matches, Kapp) re-checked on the day.
3. **V1 rows** in `records_v1.csv` (25 rows): corroborate with a second source or leave out of the demo.
4. First-edition winners (1973, 1975, 2007, 2009) and Belinda Clark's 229* on ESPNcricinfo.
5. **India chatbot usage figures** (Sensor Tower, StatCounter): find and save the URLs or drop the numbers.
6. **Pulselive** as ICC's current digital partner; the source is old.
7. **Cricsheet licence** wording (ODC-BY vs ODbL) and the exact download zip names.
8. **Hugging Face free Space limits** (CPU/RAM/sleep) and whether Gradio MCP + a ~322M model fit and respond fast enough.
9. **Laya's real fine-tuned accuracy** on our task, especially Tamil (unknown until measured).
10. Football/other-sport free data sources and their licences (StatsBomb open data is a candidate, unverified).
11. Hindi and Tamil lexicons, templates and test sets reviewed by native speakers.

## C. Risks
| Risk | Mitigation |
|---|---|
| Laya underperforms (especially Tamil) | More targeted data; hierarchy; calibration; Qwen-class parser comparison; report honestly |
| Cricsheet computed values differ from official | Golden set wins for headline records; reconciliation report; label computed answers |
| Records change before demo | `as_of` everywhere; re-verify Mon morning |
| Free hosting too slow | ONNX/quantisation, caching, smaller max length; pre-warm before the demo |
| Newer assistants already show both | The benchmark is timestamped; report it; the three-arm proof still shows value (accuracy, freshness, provenance) |
| Judges see our own score as circular | Always show coverage, classifier accuracy, three-arm result, UIR together; label target vs measured |
| Prompt injection via queries | Overrides in code; injection test set; model outputs categories only |
| Scope too large for the time | Gate-driven order in docs/08; freeze Sun 8 pm; Monday is buffer only |

## D. Mistakes made earlier in this research (so they are not repeated)
- Quoted records without as-of dates; several changed within weeks (docs/04 section 9).
- Over-sold the Claude-in-Chrome audit as a time-saver; it was unreliable and was dropped.
- Proposed paid Jev as an optional classifier step before the free-only rule was stated.
- Started the audit design before locking the scoring rule ("show both"), causing rework.
