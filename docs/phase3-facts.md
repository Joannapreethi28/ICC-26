# Phase 3: facts, policy and answers

K-P3 implements buildplan T1.3, T1.4 and T1.6. The catalogue, computations,
golden-first facts, category policy and English/Hindi/Tamil templates run offline.
The public pipeline, API, UI and deployment are K-P4/K-P5 work.

## Interfaces

```python
from mak.fetch.catalogue import lookup
from mak.fetch.facts import get_facts
from mak.policy.decide import decide, DECISION_TO_GENDERS
from mak.compose.render import render
from mak.records.leader import compute_leader
from mak.types import Parse

parsed = Parse("en", "none", 1.0, "cricket_stat", "career_record", "runs", "T20I")
intents = lookup(parsed.family, parsed.stat, parsed.format)
decision, trace = decide(parsed, supported=bool(intents))
facts = get_facts(intents[0], DECISION_TO_GENDERS[decision], parsed.lang)
leader = compute_leader(intents[0], *facts)  # women, then men; both present
answer = render(decision, facts, parsed.lang, leader, False)
```

The catalogue has 50 intent IDs: 34 computable records, 12 World Cup/history
intents served from the golden table, and four entity-driven intents. The golden
table covers 25 intents / 50 category rows; 13 of those intents also compute.
`lookup(..., "unspecified")` expands only to T20I and ODI. Unsupported Test,
league, historical-edition and arbitrary-filter queries must stay unsupported
upstream; a closed label match is not proof that every constraint in a question
can be answered. Frozen evaluation data is unchanged.

`get_facts(intent_id, genders, lang="en", *, entity=None, db_path=DB_PATH)` keeps
the original three positional arguments. Player lines and latest results require
the optional `Entity`. For several named players, call once per resolved player.
No entity or an ambiguous player returns no fact; it never substitutes a global
record. Players must have the requested registry category. Shared teams remain
neutral. K-P4 applies registry category overrides to `Parse` before `decide()`.

`compute(intent_id, gender, *, db_path=DB_PATH)` returns a computed Fact or None.
`compute_entity` provides covered player totals / a team's latest available
match. Missing databases do not create empty database files. Golden-only answers
and native labels still work without a local database. Computed caches include
the database path, modification timestamp and size; regenerate after a refresh.
Returned `ids` dictionaries are copied so callers cannot mutate cached facts.

## Counting rules and limits

- Batting runs exclude extras; totals include extras and innings penalty runs.
  Wickets come from the separate dismissal table; run-outs and retired hurt do
  not count toward bowler wickets. Super overs are excluded from every statistic.
- Best bowling sorts wickets descending, then runs conceded ascending. Runs
  conceded exclude byes, leg-byes and penalty extras. Sixes exclude non-boundary
  six-run events. Fifties are innings from 50 through 99; centuries are at least
  100. Highest scores retain the not-out star when every tied highest innings
  was unbeaten. All joint holders are retained, ordered deterministically.
- Batting average uses runs / dismissals, excluding retired hurt; zero-dismissal
  averages are absent. Strike rate uses runs per 100 balls faced. Both require
  at least 1000 runs within available matches. Economy uses runs per six legal
  balls, requires at least 1000 legal balls, and compares lower values as better.
- Matches mean roster appearances in supplied files, including recorded
  no-results. They are not claimed to reproduce official complete career counts.
- Lowest total is explicitly **all-out innings only** (at least ten wickets).
  Highest chase is the winning second-innings total in a wickets win, excluding
  method-adjusted matches. Victory margins use supplied outcome margins,
  including adjusted matches. Most wins counts `outcome.winner`; tied-match
  eliminators are not added. These definitions appear in each Fact's context.
- Player-line values are `matches / runs / wickets`, with translated field
  labels. Latest results mean the latest **available** team match. They include
  match date, snapshot date and `data_lag`; no current/live-result claim. If a
  team has multiple matches on the latest date, no ordering is invented.
- Every computed Fact has `trust="computed"`, `sources=("Cricsheet",)`, its
  category/format's latest available match date and an incomplete-coverage note.
  Computed records are available-match maxima/minima, not certified all-time
  headlines. Names and IDs come from the registry; untranslated labels fall
  back to English.

Source definitions checked against the official
[Cricsheet JSON documentation](https://cricsheet.org/format/json/) and
[downloads coverage](https://cricsheet.org/downloads/). The calculation thresholds
and supported scope are project conventions from buildplan T1.3.

## Golden precedence and reconciliation

`get_facts` preserves every verified golden value, date, source, context and
holder exactly. When covered-data values or holders differ, `computed_delta`
contains a descriptive comparison; it does not replace the headline. The
reconciliation report's numeric `delta` is computed minus golden for scalar
records only. A difference between leaders is not necessarily a same-player
difference.

Rebuild locally with `python -m mak.records.reconcile`.
[The measured report](../results/reconciliation.md) lists every computable golden
row. `explained` indicates a known coverage issue, not a match-by-match accounting
of every missing run. The Sonam Yeshey / S Yeshi identity remains flagged even
though bowling figures agree. Golden-source caveats from K-P1 remain: some V1
records have one source and four V2 rows repeat a URL. No fresh factual
certification is claimed by passing loader or equality tests.

## Policy and multilingual output

Gender-insensitive/non-sport questions receive no intervention; unsupported
questions receive no invented answer; supported injection queries show both.
Explicit categories require confidence at or above the configured threshold;
invalid/NaN confidence fails safe. Neutral and explicitly both-category queries
show both. The function is pure and records a trace.

The renderer enforces the decision again, reports missing categories, and only
shows an overall comparison for a complete pair of the same intent/format when
the supplied leader agrees with deterministic comparison. No-format career
queries produce T20I + ODI, two categories each, without a cross-format leader.
Templates ship in the built wheel and escape markup in Fact fields.

Statistical numbers are inserted from `Fact.value`. Dates, format labels,
source URLs, context and coverage comparison are sourced metadata and can also
contain digits. The numeric guard checks those against the corresponding Fact
fields; requiring dates to occur inside the record value would contradict the
required dated answer. No model generates a record, number, source or date.

[Saved headline outputs](phase3-examples.md) show all three languages. Labels,
units and standard answer sentences are translated. Source context/country
fields and recent-result text retain source English; missing native names fall
back to English. Astra self-reviewed the templates. **Native-speaker review is
still pending**, so Gate G5's human wording-review substep is not claimed passed.

## Validation and reproduction

Run `python -m pytest tests/golden tests/policy tests/unit -q`, then the full
`python -m pytest -q`. Tests use small synthetic scorecards for counting edge
cases, exact golden equality for all 50 rows, exhaustive policy combinations,
and sourced-value rendering in all three languages. Component tests do not
measure classifier accuracy or the answer benchmark.

`python eval_data/tools/build_release.py --check` checks the unchanged K-P2
freeze. A local wheel build with `pip wheel --no-build-isolation --no-deps
--no-index .` confirms offline packaging; Jinja2 3.1.6 / MarkupSafe 3.0.4 were
already downloaded for the earlier translation environment and reused locally.
No new model or network package download was needed.
