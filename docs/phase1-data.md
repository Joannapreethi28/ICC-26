# K-P1 data layer

Owner: Joanna. Shared dataclasses and Jabin's NLU files are unchanged. The entity
resolver is independent; integrating it into `resolve()` belongs to K-P4.

## Reproduce

```powershell
python -m pip install -e ".[dev]"
python scripts/download_data.py --build --labels
python -m pytest -q
```

The downloader prints server-reported sizes before downloading, limits the new
download to 900 MiB, validates ZIP/CSV contents, records SHA-256 and retrieval
timestamps, and skips existing valid files. A failed/empty ingest preserves the
previous database. Delete only the specific cached input when intentionally
refreshing it. Tests use small local fixtures and committed CSV snapshots, without
network access or the full database.

`data/raw/` and `data/processed/mak.duckdb` are ignored by Git. They are rebuilt
locally. A full build of the snapshot below downloaded **43.48 MiB**. The committed
`data/registry/build_manifest.json` identifies the exact six source inputs.

## Measured coverage, 3 October 2026

| Competition | Matches | Earliest included | Latest included |
|---|---:|---|---|
| Women's T20I | 2,171 | 2009-06-18 | 2026-09-17 |
| Women's ODI | 611 | 2007-01-22 | 2026-09-06 |
| Men's T20I | 3,558 | 2005-02-17 | 2026-09-17 |
| Men's ODI | 2,576 | 2002-06-27 | 2026-09-15 |

The database contains 8,916 matches, 17,783 innings, 2,982,599 delivery events,
118,359 dismissal entries and 196,288 roster entries. The registry has 18,554
people and 201 team/category combinations. These are observed coverage counts,
not complete international-career totals. No classifier accuracy is claimed.

## Files Jabin can consume immediately

- `data/registry/people.csv`: `person_id`, Cricsheet `name`/`unique_name`, competition
  `gender`, `cricinfo_id`, `pulse_id`, `opta_id`, `wikidata_qid`, `label_hi`,
  `label_ta`, JSON-encoded `aliases`, `label_en`, `match_count`.
- `data/registry/teams_i18n.csv`: team, gender, Hindi/Tamil names and Wikidata ID.
- `data/i18n/entities_{hi,ta}.csv`: portable native names, source and retrieval
  time; `fallback=True` explicitly marks English fallback. Historical golden
  players absent from Cricsheet may have `cricinfo:<id>` identifiers here.
- `data/i18n/wikidata_players.csv`, `wikidata_teams.csv`, `golden_players.csv`:
  reproducible lookup caches, including missing/ambiguous results.
- `data/i18n/coverage.json`: measured translation coverage and any golden holders
  that could not be linked confidently. Never invent a missing translation.

Training code must treat an empty `gender` as unknown. Derivation uses only
`info.players` roster membership, joined to `info.registry.people`; that registry
also contains officials. Four real IDs occur in both competition categories and
are deliberately left unknown: `26a8b2fe`, `5597338d`, `3a54c25b`, `f6ba97c6`.
This detects conflicting source assignments; it does not assert why they exist.
Wikidata P21 is cached as source metadata and never overrides competition category.

Example cross-checks: Smriti Mandhana `5d2eda89` -> women, Virat Kohli `ba607b88`
-> men, Rohit Sharma `740742ef` -> men. Mandhana maps to `Q16224802`,
Hindi `स्मृति मंधाना`, Tamil `ஸ்மிருதி மந்தனா`.

The final label lookup requested 1,012 ESPNcricinfo IDs, all 27 distinct golden
player holders, and all 112 team names in this database. It found 860 Wikidata
player identities. The 1,125 exported entities per language contain 829 native
Hindi labels and 510 native Tamil labels; the remaining 296/615 entries explicitly
fall back to English. Ninety-five team names have native labels in each language.
Name-only golden lookup remains ambiguous for Rashid Khan and Rohit Sharma, and
unmatched for Sonam Yeshey; distinct source IDs for the homonyms remain available
in the registry. Lucia Taylor has a unique Cricsheet identity but no Wikidata
label in this lookup. These gaps are recorded, not guessed.

Validation: **131 tests passed in 4.02 seconds** on Python 3.11.9. The full database
was rebuilt from the downloaded archives after the final code fixes. Package
versions, table counts and checked player IDs are in `data/registry/validation.json`.
The code review found no spec violations; the duplicate golden-fallback reporting
issue was fixed and covered by a regression test.

## Public interfaces

```python
from mak.records.golden import load_golden, golden_index, GOLDEN_LEADER, audit_golden
from mak.records.leader import compute_leader
from mak.ingest.cricsheet import build_db, coverage
from mak.registry.people import build_registry, derive_gender, export_registry
from mak.registry.wikidata import fetch_labels, populate_labels
from mak.nlu.entities import resolve_entities
```

`resolve_entities()` reads the portable registry, so Jabin need not download the
database. Full names, source aliases, Hindi/Tamil labels and conservative typo
matching are supported. Shared country names and surnames retain `gender=None`.
The plan's two explicit shorthand examples, **Kohli** and **Mandhana**, are reviewed
exceptions tied to their ESPNcricinfo IDs. Other unique surnames do not automatically
become gender overrides. Name resolution itself does not make a policy decision.

## Database details needed by K-P3

The four planned tables are present: `matches`, `innings`, `deliveries`,
`match_players`. The additional `wickets` table preserves multiple dismissal
entries on one delivery without double-counting runs. Use it for dismissal stats;
`deliveries.wicket_kind`/`player_out_id` retain only the first entry for compatibility.

- `matches.match_type` normalises international T20/IT20 to `T20I`; club formats
  are rejected. `balls_per_over`, outcome method, eliminator, source archive URL
  and source schema version are retained.
- `innings` retains super-over flags, pre/post penalty runs, target, declared and
  forfeited flags. Filter `super_over=false` for standard career calculations.
- `deliveries` separates wides, no-balls, byes, leg-byes and penalties. `ball` is
  the delivery event's ordinal within the over, including illegal deliveries.
  `legal_ball` excludes wides/no-balls. `batter_ball` excludes wides. `runs_bowler`
  excludes byes, leg-byes and penalty extras. `non_boundary` preserves overthrows.
- `wickets.credited_to_bowler` excludes run-outs and other non-bowler dismissals;
  retired hurt does not increment innings wickets.

Cricsheet withholds Afghanistan men's matches. It also lacks early parts of many
careers, especially women's ODIs before 2007 and T20Is before 2009. Rashid Khan's
career wickets and many historic totals therefore cannot be established from this
snapshot. Golden headline records take priority; K-P3 must explain discrepancies.

## Golden evidence caveat

All 50 existing golden rows load, and their 25 leader comparisons agree with the
CSV after the team's D2 correction. This verifies parsing and comparison, not a
fresh independent verification of every cricket fact. Unknown verification tiers
are excluded; malformed verified rows and duplicate keys fail clearly.

`audit_golden()` flags the 25 V1 single-source rows and four V2 rows whose two URLs
are identical: women's `WC_T20_LAST`, `WC_T20_TITLES`, `WC_T20_RUNS`, `WC_T20_WKTS`.
URLs are deduplicated when constructing Facts. Original values and verification
labels remain intact for the planned final evidence review.

## Sources and attribution

- [Cricsheet downloads](https://cricsheet.org/downloads/),
  [JSON specification](https://cricsheet.org/format/json/),
  [coverage](https://cricsheet.org/coverage/),
  [withheld matches](https://cricsheet.org/withheld-matches).
- [Cricsheet Register](https://cricsheet.org/register/): the registry and derived
  identity/category exports use [ODC-BY 1.0](https://opendatacommons.org/licenses/by/1-0/).
  Attribute Cricsheet. The match ZIPs inspected contain README notices but no
  explicit licence file; do not generalise the Register licence to every archive.
- [Wikidata structured data](https://www.wikidata.org/wiki/Wikidata:Licensing)
  uses CC0. Player lookup uses P2697; team labels are country labels shared across
  competition categories. Unavailable or ambiguous labels fall back to English.
