# 00. Start here

## One-paragraph summary
AI assistants are becoming the front door to sports information. When a fan asks a neutral cricket question, the assistant can silently treat it as a men's question, so women's cricket is invisible unless the fan already knows to say "women's". **Make AI Know Her** is a free, open layer that detects when gender matters and wasn't specified, and answers with **both** the men's and women's records, each labelled, with a source and a date. A small fine-tuned multilingual model (Laya) understands the question in English, Hindi and Tamil; plain code applies the policy; a verified database supplies every number. We prove the effect with a measured three-condition test, and ship it as an MCP tool, an API, a demo page and crawlable record pages.

## Status as of Sat 3 Oct 2026
| Item | State |
|---|---|
| Problem statement | Locked (docs/03) |
| Evidence | Gathered and source-checked (docs/04); a live baseline across consumer apps was attempted and DROPPED; only pilot observations exist |
| Records table | `data/records_v1.csv`, 50 rows, 25 two-source verified, 25 single-source (docs/10) |
| Solution design | Approved by Sir Jabin (docs/06, docs/07) |
| Build | Not started. Plan in docs/08, model plan in docs/09 |
| Deadline | Entry Mon 5 Oct 2026 (confirm exact time and timezone on the Ignyte page). Build stops Sun 4 Oct 8 pm; Monday = buffer + submission |

## Glossary (for a beginner)
| Term | Meaning |
|---|---|
| T20I / ODI | Men's or women's international cricket in the 20-over / 50-over format |
| Cricsheet | Free open ball-by-ball cricket data (men's and women's matches); our main data source |
| Wikidata | Free structured database behind Wikipedia; gives player IDs, gender and Hindi/Tamil names |
| Neutral question | A cricket stats question that doesn't say men's or women's ("Who has the most T20I runs?") |
| Discovery gap | The facts exist and the AI may know them, but the answer doesn't surface women's cricket unless asked |
| Incidental discovery | A fan meets women's cricket without having searched for it, because the answer included it |
| MCP | Model Context Protocol: a standard way for AI apps to call outside tools |
| API | A web address software can call to get an answer |
| Laya | A free open "decision model" (Apache-2.0) that picks from multiple-choice options and reports calibrated confidence; it must be fine-tuned to be useful |
| Fine-tuning | Training a pre-trained model further on our own labelled examples |
| Calibration (ECE) | Whether "90% confident" really means right 90% of the time; ECE is the error in that |
| Rules override | Plain keyword rules that overrule the model (e.g. the word "women's" always means women) |
| Fail-safe | When unsure, show both genders |
| WVR | Women's Visibility Rate: share of eligible neutral questions where the answer surfaces the women's result |
| GCAR | Gender-Complete Answer Rate: share where BOTH men's and women's results are shown |
| UIR | Unnecessary Intervention Rate: how often we add a gender split where gender doesn't matter (lower is better) |
| Golden set | The checked records (`records_v1.csv`) used as the answer key, not as the live data |
| As-of date | The date a record was true; records change |
| Three-arm test | Same free local AI model answering (1) plain, (2) with a "show both" prompt, (3) with our layer |

## Folder map
See `README.md` at the root. Reading order is in `CLAUDE.md`.

## The one sentence to remember
The product is **the gender-ambiguity policy** (a decision), not a cricket database and not "an MCP server". Others already ship cricket data and cricket MCP servers; nobody ships the step that stops a neutral question silently becoming a men's question.
