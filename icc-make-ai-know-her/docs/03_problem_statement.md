# 03. The problem statement and positioning

## Locked project statement (from the master doc, "Final locked statement")
> **Make AI Know Her**: the gender-aware sports discovery layer.
> Women's cricket should not need an extra keyword to be seen. When a fan asks a gender-neutral cricket question, Make AI Know Her detects whether gender changes the answer, retrieves verified parallel context, and prevents the query from silently becoming a men's-only question.
> **Starting with women's cricket. Built to scale across sport.**

## The problem in plain words
1. AI assistants are becoming a front door to sports information, especially for young fans.
2. A fan asks a *neutral* question: "Who has the most T20I runs?"
3. The assistant may answer as if "cricket" means men's cricket. The fan never learns that the real record (as of 22 Sep 2026) belongs to Smriti Mandhana, 4,867 runs, ahead of Babar Azam's 4,596.
4. To get the women's answer, the fan must already know to add "women's". Awareness is needed *before* discovery. We call this the **Discovery Gap** (facts exist, the model may even know them, but the answer doesn't surface them) and the **invisible discovery tax**.

## The mechanism that makes it an impact story: incidental discovery
A casual fan should not need to be interested in women's cricket in order to meet it. If the answer to a neutral question includes the women's record, that fan discovers a women's-cricket achievement **without having searched for women's cricket**. That is the project's most important impact mechanism, and it is directly aligned with the ICC's 100% Cricket aim (250 million incremental fans by 2032, building female role models).

## Why this is stronger than "AI doesn't know women's cricket"
- The Olympic-data study (Biester, NAACL 2025) found **no significant knowledge gap**: models knew women's results as well as men's when asked directly. The failure was in **ambiguity handling**: when gender was not stated, models tended to return only the men's result, often without saying so. So the fix is a *retrieval and interpretation policy*, not just more data.
- In cricket the failure is sometimes worse than a default: for several neutral questions the **correct overall answer is a woman or a women's match** (see the table below), so a men-only answer is simply wrong.

## Evidence the correct overall answer is often a woman (as of the dates in `data/records_v1.csv`)
| Neutral question | Overall leader | Men-default answer |
|---|---|---|
| Most T20I runs | Smriti Mandhana 4,867 (22 Sep 2026) | Babar Azam 4,596 |
| Highest T20I team total | Argentina women 427/1 (13 Oct 2023) | Zimbabwe 344/4 |
| Best T20I bowling | Laura Cardoso (Brazil women) 9/4 (9 Apr 2026) | Sonam Yeshey (Bhutan men) 8/7 |
| Most T20Is played | Harmanpreet Kaur 211 (single-source; re-check) | Paul Stirling 163 |
| First Cricket World Cup | 1973 (women's) | 1975 |
| First T20 International | 5 Aug 2004 (women's, Hove) | 17 Feb 2005 |
| First ODI double century | Belinda Clark 229* (1997) | Sachin Tendulkar 200* (2010) |
Counter-examples we must not hide: men lead T20I wickets (Rashid Khan 197 vs Deepti Sharma 189), T20I highest score (Finch 172 vs Lucia Taylor 169) and **all seven ODI categories** in the table. We never claim women hold "the records" in general.

## Fairness principle (what the layer will and won't do)
- It is **symmetric**: it prevents a neutral question from silently becoming *either* gender's question; it is not a women's-promotion tool.
- Explicit questions are untouched: "women's" -> women's answer; "men's" -> men's answer.
- Neutral questions where gender changes the answer -> both, labelled, with sources.
- Questions where gender doesn't matter ("How long is a cricket pitch?") -> the layer stays silent. We measure how often it intervenes unnecessarily (UIR).
- Fail-safe: unsure about gender -> show both.

## Positioning versus what exists
| Existing | What it does | Why we are different |
|---|---|---|
| Cricket MCP servers (CricketStudio, Duckworth, mcp-cricket, TigZig, SportScore) | Give AI more cricket data | They don't decide what "cricket" means when the user doesn't say; an AI can call them and still return men-only |
| Google's women's-sports search fix | Improves *Search* ranking for gender-ambiguous queries ("India cricket captain") | Closed, search-only, not a layer other assistants/apps can adopt; validates that the problem is real |
| Prompting an LLM to "also mention women" | Cheap | No verified, current numbers; stale or invented facts (to be tested in our three-arm experiment) |
| Stats Perform / Opta women's data | High-quality commercial data | Data ownership, not the decision layer; paid |
**USP:** others give AI more cricket data. We fix the moment the AI decides what "cricket" means.

## One-slide version (headline + proof placeholders; fill measured numbers only when measured)
- **Headline:** "Ask AI who has the most T20I runs. It names a man. The record belongs to Smriti Mandhana."
- **Evidence:** pilot screenshots (ChatGPT, Gemini, Claude answered Babar Azam, per Sir Jabin's own test; exact versions/modes not recorded); the source-page audit (Wikipedia men's T20I records page 324,077 views/yr and captions Babar; women's page 28,307 views/yr); Biester NAACL 2025; Google's own blog; the table above.
- **Build:** the gender-aware answer layer (trained multilingual classifier + policy + verified database), as MCP, API, demo page, record pages.
- **Proof:** three-arm test (plain vs prompt-only vs layer) with WVR, GCAR, factual accuracy, UIR, per language. Label the >=95% WVR as a **target** until measured.
- **Ask:** ICC/partners pilot the layer behind the ICC app and the Gemini fan companion; we re-run the benchmark at every ICC event.

## Cross-sport (bonus)
The gender-signal part of the classifier is sport-agnostic. We test it on football/tennis questions it never saw in training (a real transfer result) and add a small football adapter to show the same engine with a different data source. Vision: broad. Prototype: cricket first.
