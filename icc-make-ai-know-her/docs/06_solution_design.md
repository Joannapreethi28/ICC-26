# 06. Solution design (approved by Sir Jabin, 3 Oct 2026)

Analogy for beginners: a well-run **library**. The stacks hold everything (database), a receptionist reads your request slip (the classifier), a fixed rule decides which shelves to bring (the policy), a clerk fetches the books (the lookup) and writes a receipt (the answer with sources and date).

## 1. Policy (deterministic, in code)
| Case | Detected by | Response |
|---|---|---|
| Explicit women's | "women's", "woman", "female", "ladies", "WT20I", "Women's World Cup", Hindi/Tamil equivalents, grammatical-gender cues, a known woman player's name | Women's answer only |
| Explicit men's | "men's", "male", "Men's World Cup", equivalents, a known man player's name | Men's answer only |
| Both named | "men's and women's" | Both |
| **Neutral** (stats question, gender changes the answer, none given) | supported intent, no gender signal | **Both, side by side, each labelled**; add an "overall leader" note when one holder tops both lists |
| Gender-insensitive | no stats intent ("How long is a pitch?", "What is LBW?") | `no_intervention`: say nothing; the host AI answers normally |
| Unsupported stats question | looks like a stats question; intent not in catalogue and not computable | `unsupported`: say nothing, count in coverage; never invent |
| Unsure about gender | low classifier confidence | treat as neutral: show both (fail-safe) |
Answer format (neutral):
```
Women's T20Is: Smriti Mandhana, 4,867 runs (as of 22 Sep 2026)
Men's T20Is: Babar Azam, 4,596 runs (as of 1 Oct 2026)
Overall: Mandhana leads both lists. Sources: ICC, Cricsheet. Ask for "women's" or "men's" to narrow.
```
"Asked back" ("do you mean men's or women's?") is NOT used by our layer; when we measure other assistants it is its own row and not a pass.

## 2. The phases, each with its attack and the best decision
**Phase 0: Data (built once, free).** *What:* a database of every international T20I and ODI (men's and women's) from Cricsheet, plus a player/team registry with gender and Hindi/Tamil names from Wikidata. The 50 checked records are the **answer key**, not the live data. *Analogy:* Cricsheet is the full library; the 50 rows are the reference shelf used to catch mistakes. *Attack:* Cricsheet withholds some matches (161 T20Is) and lags, so totals may differ from official numbers; hand-typed rows don't scale. *Best decision:* compute any record/stat from the database for coverage; use the golden set to test and to override headline records; label computed answers "computed from Cricsheet, as of [date]"; flag when computed != golden.

**Phase 1: Understand the question.** *What:* turn a messy sentence into labels: gender signal, topic (cricket stat / general / other sport / non-sport), stat family, stat, format. *Analogy:* reception desk ticking boxes on your slip. *Example:* "who's the top scorer in T20s?" -> gender none; cricket stat; career record; most runs; T20I. *Attack:* rules alone break on messy, typo-ridden or Hindi/Tamil phrasing; a model alone can be confidently wrong; Laya is near chance untrained; one-step classification collapses with many labels. *Best decision:* **fine-tune laya-multilingual (free, 322M, runs on CPU)** with a two-level hierarchy (family, then stat), calibrated by temperature scaling; **rules override** it (an explicit "women's"/"महिला"/"மகளிர்" always means women); player names are **looked up** (name -> player -> gender from which Cricsheet files they appear in), never guessed; low confidence -> show both. Rules-only is kept as a **baseline measurement**, not an exit. Qwen-class small-model LoRA parser is a comparison arm.

**Phase 2: Decide.** *What:* the if-then in section 1. *Analogy:* a traffic light, no judgment. *Attack:* could show both when the user plainly meant one, or add a split to questions that don't need one. *Best decision:* keep it in code, never a model, so behaviour is guaranteed and testable; intervene only when gender changes the answer; measure Unnecessary Intervention Rate.

**Phase 3: Fetch.** *What:* turn labels into a database lookup. *Analogy:* a vending machine with fixed buttons, not a free-form order. *Attack:* letting an AI write SQL freely covers more questions but can be silently wrong. *Best decision:* a catalogue of fixed, parameterised query templates (docs/07 section 5); anything unmatched = `unsupported`.

**Phase 4: Answer.** *What:* write the reply with both records, the overall leader, source and date, in the question's language. *Analogy:* a receipt. *Attack:* an AI phrasing the answer could change a number. *Best decision:* fill-in templates (English, Hindi, Tamil); no model writes a number. A host assistant may reword the text but numbers arrive as data.

**Phase 5: Prove it.** One free local open model answers the same questions three ways: (1) plain, (2) told "show both genders", (3) with our layer. Measure both-shown rate and factual accuracy, per language. *Hypothesis (not a result):* prompt-only shows both but gets numbers stale or wrong; the layer wins on accuracy and freshness. Also: classifier ablation (rules-only vs trained), per-language accuracy and calibration, cross-sport transfer, unnecessary-intervention control. Details: docs/11.

## 3. How an AI app actually gets our answer (delivery)
ChatGPT will not call our tool by itself. Four entry points:
1. **MCP tool** (Gradio `mcp_server=True` on a free Hugging Face Space): AI apps and agents add it with one URL.
2. **Open REST API**: for the ICC app or partners (e.g. Gemini fan companion).
3. **Demo page**: fans/judges; the same Space.
4. **Crawlable record pages** with structured data (JSON-LD), showing both records per question, so search-grounded AI reads complete answers. This repairs the men-only source pages we found and needs nobody's permission.

## 4. Cross-sport (bonus)
The gender-signal head is sport-agnostic. Test it on football, tennis and basketball queries unseen in training (transfer result), and add a small football adapter (same engine, different source) to demonstrate the adapter interface. Cricket remains the full prototype.

## 5. Multilingual (required: English, Hindi, Tamil)
- Hypothesis to test: **grammatical gender is itself an explicit signal**. Tamil வீராங்கனை (woman sportsperson) vs வீரர் (male/default); Hindi feminine forms like "विकेट लेने वाली गेंदबाज़" vs "वाला". A model trained only on keywords would miss these; the training and test sets must include them.
- Answer templates in all three languages; player/team names from Wikidata labels (Mandhana = स्मृति मंधाना / ஸ்மிருதி மந்தனா).
- Laya's untrained Tamil is weak (card: 0.250 on a hard zero-shot benchmark; Hindi 0.387), so Tamil needs its own substantial training set and test results, reported per language. Claim only what the held-out test supports.

## 6. Mapping to the judging criteria
| Criterion (weight) | What we show |
|---|---|
| Innovation (25%) | First measured test of men-default behaviour in cricket; a decision layer rather than another database; fail-safe "show both"; positioning slide vs MCP servers (data only), Google's fix (closed, Search only) and prompting (no verified facts) |
| Technical (20%) | Working UI + API + MCP; trained multilingual classifier with calibration; verified database with provenance; architecture, model, data and benchmark cards; open repository; sport-adapter interface |
| Impact on women (20%) | Women's Visibility Rate before/after; incidental discovery of women's records; symmetric fairness policy with unnecessary-intervention rate reported |
| Value to fans & ecosystem (15%) | Complete, correct answers for fans; drop-in for ICC app and Gemini companion; exposure for women players for sponsors/broadcasters; free tool for developers |
| Sustainability & inclusivity (10%) | Free and open (Apache-2.0 model, open data); small model on CPU instead of a large model per question; English/Hindi/Tamil, each tested; a woman owns/leads technical work (SJ decides how) |
| Presentation (10%) | 3-minute story: real screenshot (AI says Babar) -> same question through the layer (Mandhana leads both lists) -> numbers -> ICC pilot |
| Bonus | Women-led team; cross-sport transfer test + adapter; pilot-ready (one API call, free hosting, IDs that map to ICC's platform, pilot plan with targets) |

## 7. Attacks and prepared answers
| Attack | Answer |
|---|---|
| "AI already fixed this." | Pilot screenshots (three assistants named Babar); source-page audit; our fix doesn't depend on anyone's model update; newer assistants may do better and the benchmark is timestamped so we say so |
| "Just prompt it to mention women." | The three-arm test measures exactly that; prompting can't supply verified current numbers |
| "You're biasing toward women." | Symmetric policy; explicit questions untouched; UIR reported; gender-insensitive questions untouched |
| "Cluttered answers." | Three lines, only when gender changes the answer |
| "Tiny coverage / why a database when Opta exists?" | Database computes answers from open data; source-agnostic (swap in ICC/Opta later); unsupported stays silent; coverage published |
| "Cricket MCP servers already exist." | They provide data; none decides gender ambiguity; we measure the gap and ship the policy |
| "Why would a normal user install an MCP server?" | They won't: four entry points; record pages and ICC/partner embedding need no user action |
| "A small model can be confidently wrong." | Rules override, name lookups, calibration, fail-safe to both; claims limited to tested languages; injection tests |
| "Stale numbers." | As-of dates, golden set, refresh job, discrepancy flags; six records changed within weeks, which is the point |
| "Licences." | Cricsheet (ODC Attribution; credit required), Wikidata (CC0), Laya (Apache-2.0) |
| "How do you prove impact?" | WVR/GCAR/accuracy/UIR before vs after on a published benchmark; a pilot plan with ICC |

## 8. What changed versus the master discussion doc
- Multilingual moves from "later" to **required** (SJ decision; also a judging criterion).
- A trained classifier is **required** (the master doc allowed rules or LLM router).
- Facts come from a computed database plus a golden set, not hand-typed rows alone.
- Added: crawlable record pages, three-arm proof, grammatical-gender hypothesis, free hosting plan.
- Kept: fairness principle, controls and UIR, CLARIFY-as-own-row in measurement, adapter architecture, "the policy is the product".
