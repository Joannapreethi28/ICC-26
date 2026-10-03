# 12. Pitch, demo and deliverables

All numbers must be dated and sourced; measured results are filled in only after the experiments run. Placeholders are written `[MEASURED: ...]`.

## 1. Deck (max 5 slides)
1. **Problem.** Real screenshot of an AI answering "Who has the most T20I runs?" with a man (only screenshots we actually captured; never fabricate). Beside it: Smriti Mandhana 4,867 vs Babar Azam 4,596 (as of 22 Sep 2026). Line: "To find her, a fan must already know to ask for her."
2. **Why it matters.** Discovery gap and incidental discovery; Biester NAACL 2025 (defaults, not missing knowledge); Google's own admission ("India cricket captain"); source-page audit (324,077 vs 28,307 views); ICC 100% Cricket (250M incremental fans by 2032); ICC-Google; Gemini as the ICC's AI fan companion.
3. **Solution.** The layer: understand (trained multilingual Laya + rules) -> decide (fixed policy) -> fetch (verified database) -> answer (both, sourced, dated). One example in English, Hindi and Tamil. Delivery: MCP, API, demo, record pages. Free and open.
4. **Proof.** `[MEASURED: three-arm results: WVR/GCAR/accuracy per arm]`, `[MEASURED: classifier accuracy per language and calibration]`, `[MEASURED: UIR]`, `[MEASURED: cross-sport transfer]`. Label the >= 95% as target unless measured. State limits.
5. **Impact and pilot.** Women's visibility at the moment of discovery; value to fans, ICC, sponsors, developers; sustainability (free, small model, CPU, three languages); cross-sport roadmap; pilot plan with ICC/Google (what to measure, how long, success targets); women-led team note (Sir Jabin decides how to present roles).

## 2. Three-minute video script (Prototype track max 3 min)
| Time | Content |
|---|---|
| 0:00-0:20 | Hook: ask an AI "Who has the most T20I runs?" (use captured real answer). "It named a man. The record is Smriti Mandhana's." |
| 0:20-0:50 | The discovery gap; one line each on the research and the ICC aim |
| 0:50-1:50 | Live demo: same question through Make AI Know Her -> both records with sources and date -> show the decision trace -> same question in Hindi and Tamil -> an explicit women's question (untouched) -> a gender-insensitive question (silent) -> an unsupported question (honest "not supported") -> an AI app calling the MCP tool |
| 1:50-2:25 | Proof: three arms (plain, prompt-only, layer), per-language accuracy, unnecessary-intervention rate, cross-sport transfer. Say plainly what the numbers do and don't show |
| 2:25-3:00 | Impact and the pilot ask to ICC/partners; free and open; "a fan shouldn't need an extra keyword to find women's cricket" |

## 3. Summary (draft for the submission form; edit once numbers exist)
"AI assistants are becoming the front door to sports information, but when a fan asks a gender-neutral cricket question they can silently answer as if it were about men's cricket. For example, the T20I run record belongs to Smriti Mandhana (4,867 runs as of 22 Sep 2026), yet AI answers name Babar Azam (4,596). Make AI Know Her is a free, open, multilingual layer (English, Hindi, Tamil) that detects when gender matters and isn't specified, and returns both the men's and women's records with sources and dates. A small fine-tuned Laya model understands the question; a fixed policy decides what to show; a verified database supplies every number, so no model writes a fact. It ships as an MCP tool, an open API, a demo and crawlable record pages, and we measure its effect with a published benchmark `[MEASURED: ...]`."

## 4. Demo flow rules
- Left column of the comparison shows only real captured answers (app, date). If no capture exists for a typed query, show "not captured".
- Show the decision trace (why it decided what it decided) and the as-of dates.
- Show one failure honestly (an unsupported question) to build trust.

## 5. Language to use / avoid
Use: "defaults to men's when gender isn't specified"; "discovery gap"; "incidental discovery"; "show both"; "verified, dated, sourced"; "target" vs "measured"; "pilot observation".
Avoid: "AI is sexist/biased against women" (overclaims; the research shows defaults); "AI doesn't know women's cricket" or "suppresses" (knowledge exists); "fixes bias"; any global percentage; "first ever"/"guaranteed"; presenting illustrative numbers; claiming languages we didn't test; "women hold the records" without the qualifier that men lead ODIs and several T20I categories.

## 6. Why it appeals to each stakeholder (one line each)
- **ICC:** serves the 100% Cricket aim (visibility, new fans, female role models) at the exact point where fans now ask AI; pilot-ready behind the ICC app and the Gemini fan companion; maps to ICC's Pulse IDs via the register.
- **Google / AI platforms:** a source-grounded, symmetric fix for gender-ambiguous sports queries that generalises beyond Search; open and free to adopt.
- **Developers:** one URL (MCP) or one API call; open data, open model, open benchmark.
- **Sponsors/broadcasters:** more women's-cricket exposure at moments of casual discovery.
- **Fans:** correct, complete answers without needing to know the magic word.

## 7. Ethics and fairness note (include in docs)
Symmetric policy; explicit questions unchanged; UIR reported; fail-safe both; no personal data collected; sources credited (Cricsheet, Wikidata, Wikipedia); limits and untested languages stated.
