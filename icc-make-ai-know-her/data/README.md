# data/

| File | What | Status |
|---|---|---|
| `records_v1.csv` | The golden set: 50 verified records (25 intents x men's/women's) with sources, as-of dates and verification level | **Use this.** Re-verify dynamic rows before the demo |
| `question_bank.csv` | Draft 100-question benchmark (sets A, B, C, D, E) | **Partly stale**: A03 truth and several B numbers are outdated; its scoring rule predates "show both"; no gender-insensitive (G) set. Rebuild per docs/11 |
| `consumer_app_log.csv` | Empty sheet for logging answers from consumer apps (30 core questions) | Optional (the Chrome audit was dropped) |
| `wiki_audit.json` | Raw output of the Wikipedia pageview/lead audit (3 Oct 2026) | Real data; see docs/04 section 6 |
