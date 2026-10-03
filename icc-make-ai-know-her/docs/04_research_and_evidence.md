# 04. Research and evidence

Legend: **[V2]** verified against two sources, **[V1]** one source, **[VERIFIED-DOC]** page fetched and the claim found in it on 3 Oct 2026, **[MEM]** from memory / not re-checked, **[UNVERIFIED]**.
Full URL list: `docs/13_references.md`. Scripts used: `docs/14_scripts_index.md`.

## 1. Academic evidence
**Biester, "Sports and Women's Sports: Gender Bias in Text Generation with Olympic Data", NAACL 2025 (short).** arXiv 2502.04218; https://aclanthology.org/2025.naacl-short.17/ [VERIFIED-DOC]
- 338 parallel men's/women's Olympic team events (1988-2021); the same question asked with gender stated and left out.
- Models: GPT-4o-mini, GPT-4o, Llama 3.1 8B/70B, Mistral NeMo/Large (generated Sept 2024).
- Finding 1: no significant knowledge gap. Finding 2: when gender was not stated, models tended to give only the men's result, explicitly or implicitly; most showed significant implicit bias.
- Nuance: the effect **reversed for gymnastics** (favoured women). So bias is not uniform across sports. Do not generalise beyond what the paper shows.
- Nobody (as far as we found) has published a cricket-specific test.
**Kalhor & Bahrak, Persian multilingual gender-bias paper, WiNLP 2025** https://aclanthology.org/2025.winlp-main.3/ [VERIFIED-DOC]: sports show rigid bias; supplementary only, not the same task.

## 2. Industry validation
**Google, "How we're making it easier to find results on women's sports"** [VERIFIED-DOC]: uses the "India cricket captain" example of a gender-ambiguous query; lists gendered languages including Hindi (also Spanish, German per the master doc). Shows the problem is recognised in Search. Google's fix is Search-only.

## 3. ICC alignment [VERIFIED-DOC unless noted]
- **ICC 100% Cricket:** aim of 250 million incremental fans by 2032 and building female cricketing heroes. (The URL https://www.icc-cricket.com/100percentcricket returned 404 for the sandbox; the page exists at https://icc-cricket.com/100percentcricket/what-is-100percent-cricket.)
- **ICC-Google partnership for women's cricket**, 29 Aug 2025 (women-only), Android/Gemini/Pixel/Google Pay; goal of making the women's game more visible.
- **Gemini = ICC's Official AI Fan Companion** for the Men's T20 World Cup 2026 (ICC release, Feb 2026) with an "Explore Cricket" tab. Natural integration point.
- **ICC digital partner Pulselive** runs ICC digital properties [UNVERIFIED currency: the source is an old (circa 2015-17) vendor page]. Cricsheet's register carries Pulse IDs, so moving to ICC's official data later may be an ID-mapping task. Confirm before saying this in the pitch.
- **CWC 2025:** 5.2B video views, 279M social interactions, 8.5M unique ICC site/app visitors; final reached 185M JioHotstar users, matching the men's 2024 T20 WC final. Proof that demand exists.
- **ICC strategy PDFs** cited in the master doc are actually **Annual Report 2022-23** (hcueaghytzn8htllwelt.pdf) and **Annual Report 2021-22** (bisel0ksrxtscf16t2wu.pdf), not "strategy" documents; content (the "Profile" area: visibility, perception, awareness; build female heroes) is accurate.

## 4. AI usage context
- **Pew (US only), 17 Jun 2026:** 61% of US adults 18-29 use ChatGPT; 54% use chatbots to search for information [VERIFIED-DOC]. US data; do not generalise.
- **India (from search results; URLs not saved; re-verify before use) [UNVERIFIED]:** Sensor Tower, May 2026 monthly users: ChatGPT ~330M, Gemini ~229M, Claude ~72M, Perplexity ~29M. StatCounter June 2026 India chatbot share: ChatGPT 78%, Gemini 9.65%, Perplexity 5.07%, Claude 4.07%, Copilot 3.19%; ChatGPT ~84% of mobile.
- Target markets chosen by Sir Jabin: India, England, Australia, New Zealand.

## 5. Women's-sport growth (context) [VERIFIED-DOC]
Deloitte: women's elite sports revenue to reach US$3B in 2026. Nielsen: 46B minutes viewed in the US in 2025 (+71% since 2022); women's football to 800M+ fans by 2030.

## 6. Pilot observations (NOT rates; label them "pilot")
1. **Sir Jabin's own test (3 Oct):** asked Gemini, ChatGPT and Claude "who is the top T20I run scorer"; each said Babar Azam and did not mention Smriti Mandhana. Exact wording, model versions, search on/off, logged-in state and time were not recorded. One question only.
2. **Claude-in-Chrome pilot (3 Oct, dropped):** the agent captured A01-A04 word for word on ChatGPT, Gemini and Google AI Overview (12 answers; Copilot skipped; A06 in flight; helper-written ChatGPT records were moved to a separate unverified file and excluded). **The results file was not shared with the assistant that wrote this pack, so those answers are unseen here.** If Sir Jabin adds it to the folder, score it under `docs/11_evaluation_protocol.md` and quote only as a pilot (n=12). Note: the A03 ground truth in the old question bank is stale (see section 9). A screenshot showed ChatGPT test account "Test User (Free)" with the composer tagged "Create image" (an agent mis-click) and a chat titled "T20I Top Run Scorer" in Recents.
3. **Source-page audit (3 Oct), real data, `data/wiki_audit.json`:** English-Wikipedia pageviews Sep 2025-Aug 2026 [VERIFIED by API]:
| Page | 12-month views |
|---|---|
| List of Twenty20 International records (no gender in title) | 324,077 |
| List of women's Twenty20 International records | 28,307 (11.4x fewer) |
| List of One Day International cricket records | 314,930 |
| List of women's ODI cricket records | 150,969 (2.1x fewer) |
| Cricket World Cup / Women's Cricket World Cup | 2,252,198 / 2,858,656 (counter-evidence: events draw interest; the gap is in evergreen record pages) |
The unqualified T20I records page is men-only; its lead caption names Babar Azam and Rashid Khan; Mandhana and Bates appear 0 times (women's records only via a hatnote). Other pages seen in search results state the default openly (a cricket-stats explainer answers "Who has the most runs in T20I cricket?" with Babar Azam; exam-prep sites call Zimbabwe's 344 the highest T20I total). URLs for those two were not saved. **Limit:** this shows the *sources* are men-default; it does not show what each assistant answers.

## 7. Verified record facts
See `data/records_v1.csv` and `docs/10_data_and_records.md`. Headline: women hold the overall T20I lead in runs, team total, best bowling and matches; men lead wickets and highest score; men lead all seven ODI categories.

## 8. Prior art (honest) [VERIFIED-DOC that the repos exist]
| Project | What it is | Note |
|---|---|---|
| CricketStudio MCP (i-m-arul) | 57 tools; IPL/MLC/WPL from Cricsheet; built by a Chennai developer | 17 occurrences of "women" on its repo page |
| Duckworth MCP (ankitksr) | DuckDB ball-by-ball stats, records, insights | men's + women's Cricsheet |
| mcp-cricket (asaraog) | win-probability model, 22k-match archive, live scores | |
| TigZig women's cricket DB/API/MCP | women's data added Sep 2026 | proves "women's cricket MCP" alone isn't novel |
| SportScore MCP (backspace-me) | multi-sport scores via a free API | no women's mentions |
| Stats Perform / Opta | commercial women's-sports data and AI | data, not the decision layer |
Conclusion: an MCP server for cricket data is **not** novel. Our novelty = (1) the first measured test of men-default behaviour in cricket, (2) the gender-ambiguity policy as a reusable layer with provenance, (3) a trained small multilingual classifier (en/hi/ta) that runs free, (4) the three-arm proof.

## 9. Corrections to earlier claims (do not repeat the old values)
| Old claim | Correct (3 Oct 2026) |
|---|---|
| Mandhana 4,788 | 4,867 after the Asian Games final, 22 Sep 2026 (4,788 was her total on 20 Sep) |
| Best T20I bowling: Rohmalia 7/0 (Indonesia, 2024); men's best 7/8 Syazrul Idrus | Laura Cardoso (Brazil women) 9/4, 9 Apr 2026 (best in either gender); men's best Sonam Yeshey (Bhutan) 8/7, 26 Dec 2025 |
| Deepti Sharma 166 T20I wickets | 189 (152 at end 2025 + 37 in 2026) |
| Rashid Khan 193 | 197 (196 on 15 Sep) |
| Women's World Cup most wickets: Jhulan Goswami 43 | Marizanne Kapp 44 [V1] |
| Men's ODI centuries: Tendulkar 49 leads | Virat Kohli 55 (27 Sep 2026) |
| Discussion doc: "ICC strategy PDF" | It is the ICC Annual Report 2022-23; the other is 2021-22 |
`archive/findings_v0_CONTAINS_STALE_NUMBERS.md`, `data/question_bank.csv` (A03 markers, B-set numbers) and `archive/plan_v1_PARTLY_SUPERSEDED.md` still contain old values.

## 10. Source check of the master doc (3 Oct 2026): 20 of 22 verified, 2 mislabelled, 0 wrong
Verified: NAACL paper; Google blog; ICC Mandhana milestone page (4,788/4,758 on 20 Sep); Babar 4,596 (Cricketsky); ICC-Google partnership; CWC25 digital and final figures; Pew; Deloitte; Nielsen (two); Persian paper; Cricsheet counts (22,983 / 4,667 / 611 women's ODIs / 2,171 women's T20Is); TigZig, CricketStudio, Duckworth, mcp-cricket, SportScore, Stats Perform exist as described. Mislabelled: the two ICC PDFs (above). "9,000 participants" is not verifiable and the doc says so. Strengths adopted from the master doc: the fairness policy, gender-insensitive controls with an Unnecessary Intervention Rate, a CLARIFY label, "the policy is the product", the sport-adapter architecture. Weaknesses found: the >=95% target is near-circular on supported queries; the before/after comparison must be same-model with/without; Cricsheet totals may differ from official; the assistant list was US-based.

## 11. Evidence we must NOT claim
- A cross-assistant rate (we have a pilot of ~12 answers at most).
- That AI "suppresses" women's cricket or "doesn't know" women's cricket (the research says defaults, not missing knowledge).
- That all current assistants fail (newer ones with web search may do better; time-sensitive).
- Any "29% -> 97%"-style numbers (illustrative only in the master doc, section 29).
- Global usage percentages from US survey data.
- That women hold the records "in general" (men lead ODIs and several T20I categories).

## 12. Reusable audience/market evidence from earlier passes (context, not central)
From `source_docs/handoff_icc_hackathon_2_oct.md` section 5: WPL 2026 57% first-time viewers; BBC-Kantar 2026 survey; Women's T20 WC 2026 ad volumes (India matches +58%); ICC/GoBubble 2024 abuse trial (~18.1% of 1.5M comments harmful or bot). Use only if a slide needs extra context.
