# 10. Data sources and the records table

## 1. Sources
| Source | Use | Licence / terms | Notes |
|---|---|---|---|
| **Cricsheet** https://cricsheet.org/downloads/ | Ball-by-ball men's and women's matches; compute records and stats | Open Data Commons **Attribution** (register page states ODC-BY: http://opendatacommons.org/licenses/by/1.0/); credit Cricsheet. (An earlier note says sources disagree between ODC-BY and ODbL; re-check the page and credit Cricsheet either way.) | Downloads page lists about 22,983 matches, 4,667 women's, 611 women's ODIs, 2,171 women's T20Is (verified 3 Oct). **Some T20Is are withheld (about 161)**, and data lags live matches. Match JSON has `info.gender`, `info.match_type`, `info.registry.people`. |
| **Cricsheet register** https://cricsheet.org/register/ | `people.csv`, `names.csv`: ID mapping | same licence | Columns include `key_cricinfo`, `key_cricketarchive`, `key_opta`, `key_pulse`, etc. Pulse = ICC's digital partner platform, useful for a later move to official data. |
| **Wikidata** | Entity resolution, gender (P21), ESPNcricinfo player ID (P2697), Hindi/Tamil labels | CC0 | Example: Smriti Mandhana = Q16224802; hi: स्मृति मंधाना; ta: ஸ்மிருதி மந்தனா; P21 female (Q6581072); P2697 = 597806 |
| **Wikipedia records lists** | The golden set's primary source for men's and women's records side by side | CC BY-SA (attribute if reused) | Fetched 3 Oct 2026 (page edit dates are in `records_v1.csv`); cross-checked against news/ICC where possible |
| Official/other | ICC news, Guinness World Records, Cricinfo-derived news, ICC reports | per site | Used for corroboration; never copied wholesale |
| Future/production | ICC feeds, Opta, other licensed providers | licensed | The architecture is source-agnostic; this is the pilot path, not part of the hackathon build |

## 2. The golden set: `data/records_v1.csv` (50 rows, 25 intents x 2 genders)
Columns: `intent_id, intent, format, gender, holder, value, context, as_of, source_1, source_2, verification, overall_leader, note`.
- **Verification levels:** **V2** = two independent sources agree (25 rows); **V1** = one source (25 rows; "re-check before demo"). V1 rows are mostly long-standing records (e.g. Tendulkar's 18,426) but include dynamic ones (T20I matches played; Lanning's ODI centuries; World Cup runs and wickets).
- `as_of` is the date the value was true (event date or source edit date). **Records are dynamic**; re-verify before the demo and again on Mon 5 Oct.
- `overall_leader` records who tops the combined list for that stat (blank/none where the two are different events).
- Not in the set: current captains, rankings (dynamic; need a verified free source), Tests, leagues.

| intent_id | women | men | overall leader | verification (w / m) |
|---|---|---|---|---|
| T20I_RUNS | Smriti Mandhana (India) 4,867 | Babar Azam (Pakistan) 4,596 | women | V2 / V2 |
| T20I_WKTS | Deepti Sharma (India) 189 | Rashid Khan (Afghanistan) 197 | men | V2 / V2 |
| T20I_HS | Lucia Taylor (Argentina) 169 | Aaron Finch (Australia) 172 | men | V2 / V2 |
| T20I_TEAM | Argentina 427/1 | Zimbabwe 344/4 | women | V2 / V2 |
| T20I_BBI | Laura Cardoso (Brazil) 9/4 | Sonam Yeshey (Bhutan) 8/7 | women | V2 / V2 |
| T20I_MATCHES | Harmanpreet Kaur (India) 211 | Paul Stirling (Ireland) 163 | women | V1 / V1 |
| ODI_RUNS | Mithali Raj (India) 7,805 | Sachin Tendulkar (India) 18,426 | men | V1 / V2 |
| ODI_WKTS | Jhulan Goswami (India) 255 | Muttiah Muralitharan (Sri Lanka) 534 | men | V2 / V1 |
| ODI_HS | Amelia Kerr (New Zealand) 232* | Rohit Sharma (India) 264 | men | V1 / V1 |
| ODI_TEAM | New Zealand 491/4 | England 498/4 | men | V1 / V1 |
| ODI_BBI | Sajjida Shah (Pakistan) 7/4 | Chaminda Vaas (Sri Lanka) 8/19 | men | V1 / V1 |
| ODI_MATCHES | Mithali Raj (India) 232 | Sachin Tendulkar (India) 463 | men | V1 / V1 |
| ODI_100S | Meg Lanning (Australia) 15 | Virat Kohli (India) 55 | men | V1 / V2 |
| WC_ODI_FIRST | 1973, England won by England | 1975, England won by West Indies | women | V2 / V1 |
| WC_T20_FIRST | 2009, England won by England | 2007, South Africa won by India | men | V2 / V1 |
| WC_ODI_LAST | India (first title) 2025, India/Sri Lanka | Australia (6th title) 2023, India | women | V2 / V1 |
| WC_T20_LAST | Australia (7th title) 2026, England and Wales | India (3rd title) 2026, India/Sri Lanka | women (most recent) | V2 / V2 |
| WC_ODI_TITLES | Australia 7 | Australia 6 | women | V1 / V1 |
| WC_T20_TITLES | Australia 7 | India 3 | women | V2 / V2 |
| WC_ODI_RUNS | Debbie Hockley (New Zealand) 1,501 | Sachin Tendulkar (India) 2,278 | men | V1 / V1 |
| WC_T20_RUNS | Suzie Bates (New Zealand) 1,254 | Virat Kohli (India) 1,292 | men | V2 / V1 |
| WC_ODI_WKTS | Marizanne Kapp (South Africa) 44 | Glenn McGrath (Australia) 71 | men | V1 / V1 |
| WC_T20_WKTS | Shabnim Ismail (South Africa) 51 | Shakib Al Hasan (Bangladesh) 50 | women | V2 / V1 |
| FIRST_T20I | England v New Zealand, Hove 2004-08-05 | Australia v New Zealand, Eden Park, Auckland 2005-02-17 | women | V2 / V2 |
| FIRST_ODI_200 | Belinda Clark (Australia) 229* | Sachin Tendulkar (India) 200* | women | V2 / V1 |

## 3. Notes on specific rows (read before trusting them)
- **T20I_RUNS women: Mandhana 4,867 (22 Sep 2026).** ICC reported 4,788 on 20 Sep (passed Bates' 4,758); she scored 79 in the Asian Games final on 22 Sep. Wikipedia lists 4,867 (edit 26 Sep).
- **T20I_BBI women: Laura Cardoso 9/4 (Brazil v Lesotho, Gaborone, 9 Apr 2026)**: best in either gender; supersedes Rohmalia 7/0. Men's best: Sonam Yeshey 8/7 (Bhutan v Myanmar, 26 Dec 2025).
- **T20I_WKTS:** Deepti 189 = 152 at end of 2025 + 37 in 2026 (myKhel, 22 Sep). Rashid 197 (Cricinfo via NewsBytes had 196 on 15 Sep; Wikipedia 197 on 1 Oct).
- **T20I_TEAM:** Argentina 427/1 v Chile, 13 Oct 2023 (Chile bowled 64 no-balls); Austria 322/7 (Jun 2026) is second on the men's list behind Zimbabwe 344/4.
- **ODI_100S men: Kohli 55** (27 Sep 2026).
- **WC_ODI_WKTS women: Kapp 44** passes Goswami 43 (V1; dynamic).
- **Winners of first editions** (West Indies 1975, England 1973, India 2007, England 2009) are from the general record/infoboxes (V1/V2 mix; check before demo).
- **First ODI double century:** Belinda Clark 229* v Denmark, Mumbai, 16 Dec 1997 (Wikipedia women's list + a news source); men's: Sachin Tendulkar 200* v South Africa, Gwalior, 24 Feb 2010 (Wikipedia progression table).

## 4. Reconciling golden vs computed (build task)
For each golden row that Cricsheet can compute (career runs/wickets, highest score, team totals, matches, centuries), compute from the database and store the delta. Expected: small differences from withheld matches and timing. Policy: golden wins for headline records; a difference above a tolerance is flagged in the UI/API (`trust: verified, computed_delta: ...`) and listed in the reconciliation report. Never silently overwrite.

## 5. Refresh
Nightly job: re-download Cricsheet, recompute, compare with golden, flag changes; a human re-verifies changed headline records before the golden set is updated. Always carry `as_of`.

## 6. How the golden set was produced (for provenance)
Wikipedia record tables were fetched by `scripts/wikipedia_records_extract.py` (3 Oct 2026); dynamic items were corroborated by web searches against news/ICC pages (Mandhana, Cardoso, Deepti, Rashid, Kohli); the CSV itself was written by an inline Python script (one `add(...)` call per row; no separate script file). The CSV's `source_1`/`source_2` columns are the provenance record.

## 7. Fix log
- 2026-10-03 (Sir Jabin, D2): `overall_leader` corrected to `women` in the women rows of WC_T20_WKTS (51 > 50) and WC_T20_LAST (July 2026 final is the most recent); the table above updated. Guarded by `tests/unit/test_leader.py`.
