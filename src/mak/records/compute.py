"""Deterministic statistics over the available Cricsheet snapshot.

These are records *within covered matches*, never certified all-time records.
SQL is fixed by the catalogue; user values are bound parameters. Super overs
are excluded. Dismissals are aggregated separately to avoid multiplying runs.
"""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
from pathlib import Path

import duckdb

from mak.config import DB_PATH
from mak.types import Entity, Fact, Gender

SUFFIXES = ('RUNS', 'WKTS', 'HS', 'TEAM', 'BBI', 'MATCHES', '100S', '50S', '6S',
            'AVG', 'SR', 'ECON', 'LOWEST', 'WIN_RUNS', 'WIN_WKTS', 'CHASE', 'MOST_WINS')
COMPUTABLE = frozenset(f'{fmt}_{stat}' for fmt in ('T20I', 'ODI') for stat in SUFFIXES)


def _rows(conn, sql, params=None):
    result = conn.execute(sql, params or [])
    columns = [c[0] for c in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]


def _prepare(conn, gender, fmt):
    conn.execute('CREATE TEMP TABLE m AS SELECT * FROM matches WHERE gender=? AND match_type=?', [gender, fmt])
    conn.execute('CREATE TEMP TABLE i AS SELECT i.* FROM innings i JOIN m USING(match_id) WHERE NOT super_over')
    conn.execute('CREATE TEMP TABLE d AS SELECT d.* FROM deliveries d JOIN i USING(match_id, innings_no)')
    conn.execute('''CREATE TEMP TABLE w AS SELECT w.*, d.bowler_id FROM wickets w
        JOIN d USING(match_id, innings_no, "over", ball)''')
    # Include a non-striker run out without facing a ball in the dismissal denominator.
    conn.execute('''CREATE TEMP TABLE bat AS
        WITH players AS (
            SELECT match_id, innings_no, batter_id person_id FROM d
            UNION SELECT match_id, innings_no, non_striker_id FROM d
            UNION SELECT match_id, innings_no, player_out_id FROM w
        ), totals AS (
            SELECT match_id, innings_no, batter_id person_id, sum(runs_batter) runs,
                   sum(batter_ball::INT) balls,
                   sum((runs_batter=6 AND NOT non_boundary)::INT) sixes
            FROM d GROUP BY ALL
        ), dismissals AS (
            SELECT DISTINCT match_id, innings_no, player_out_id person_id FROM w
            WHERE wicket_kind NOT IN ('retired hurt', 'obstructing the field (not out)')
        ) SELECT p.*, coalesce(t.runs,0) runs, coalesce(t.balls,0) balls,
            coalesce(t.sixes,0) sixes, (o.person_id IS NOT NULL)::INT outs
        FROM players p LEFT JOIN totals t USING(match_id, innings_no, person_id)
        LEFT JOIN dismissals o USING(match_id, innings_no, person_id)''')
    conn.execute('''CREATE TEMP TABLE bowl AS
        WITH totals AS (
            SELECT match_id, innings_no, bowler_id person_id,
                sum(runs_bowler) runs, sum(legal_ball::INT) balls FROM d GROUP BY ALL
        ), dismissals AS (
            SELECT match_id, innings_no, bowler_id person_id, count(*) wickets
            FROM w WHERE credited_to_bowler GROUP BY ALL
        ) SELECT t.*, coalesce(wickets,0) wickets FROM totals t
        LEFT JOIN dismissals USING(match_id, innings_no, person_id)''')


def _identity(conn, person_id):
    roster = conn.execute('''SELECT min(name), string_agg(DISTINCT team, ', ' ORDER BY team)
        FROM match_players JOIN m USING(match_id) WHERE person_id=?''', [person_id]).fetchone()
    name, country = roster
    ids = {'cricsheet': person_id}
    if 'people' in {r[0] for r in conn.execute('SHOW TABLES').fetchall()}:
        rows = _rows(conn, 'SELECT * FROM people WHERE person_id=?', [person_id])
        if rows:
            row = rows[0]
            name = row.get('label_en') or row['name']
            for source, column in (('cricinfo', 'cricinfo_id'), ('pulse', 'pulse_id'), ('wikidata', 'wikidata_qid')):
                if row.get(column):
                    ids[source] = row[column]
    return name or person_id, country, ids


def _record(conn, intent, gender, rows, value, unit, context=''):
    """Rows contain all equal leaders; don't silently pick one joint holder."""
    if not rows:
        return None
    start, latest, count = conn.execute('SELECT min(date), max(date), count(*) FROM m').fetchone()
    names, countries, all_ids = [], [], []
    for row in rows:
        if row.get('person_id'):
            name, country, ids = _identity(conn, row['person_id'])
        else:
            name, country, ids = row['holder'], None, {}
        if name not in names:
            names.append(name)
        if country and country not in countries:
            countries.append(country)
        all_ids.append(ids)
    coverage = f'Covered Cricsheet matches only: {start} to {latest}; {count} matches; incomplete career coverage.'
    if gender == 'men':
        coverage += ' Afghanistan matches are withheld by Cricsheet.'
    if len(names) > 1:
        context += ' Joint record in covered matches.'
    if rows[0].get('match_id'):
        match_ids = sorted({r['match_id'] for r in rows})
        context += ' Match IDs: ' + ', '.join(match_ids) + '.'
    return Fact(intent, gender, intent.split('_')[0], ' / '.join(names), None,
                ', '.join(countries) or None, value, unit, (coverage + ' ' + context).strip(),
                str(latest), 'computed', ('Cricsheet',), all_ids[0] if len(names) == 1 else {})


def _batting(conn, fmt, gender):
    records = []
    for suffix, expr, unit, qualification in (
        ('RUNS', 'sum(runs)', 'runs', ''),
        ('100S', 'sum((runs>=100)::INT)', 'centuries', ''),
        ('50S', 'sum((runs>=50 AND runs<100)::INT)', 'fifties', ''),
        ('6S', 'sum(sixes)', 'sixes', ''),
        ('AVG', 'sum(runs)*1.0/nullif(sum(outs),0)', 'average', 'HAVING sum(runs)>=1000 AND sum(outs)>0'),
        ('SR', '100.0*sum(runs)/nullif(sum(balls),0)', 'strike_rate', 'HAVING sum(runs)>=1000 AND sum(balls)>0'),
    ):
        rows = _rows(conn, f'''WITH scores AS (SELECT person_id, {expr} score FROM bat
            GROUP BY person_id {qualification})
            SELECT * FROM scores WHERE score>0 AND score=(SELECT max(score) FROM scores) ORDER BY person_id''')
        if rows:
            value = f"{rows[0]['score']:.2f}" if suffix in ('AVG', 'SR') else str(int(rows[0]['score']))
            context = 'Qualification: at least 1000 runs in covered matches.' if qualification else ''
            if suffix == 'AVG':
                context += ' Runs divided by dismissals; excludes retired hurt.'
            records.append(_record(conn, f'{fmt}_{suffix}', gender, rows, value, unit, context))
    rows = _rows(conn, 'SELECT * FROM bat WHERE runs=(SELECT max(runs) FROM bat) ORDER BY person_id, match_id')
    if rows:
        # A star is meaningful only if all tied best innings were unbeaten.
        value = str(int(rows[0]['runs'])) + ('*' if all(not r['outs'] for r in rows) else '')
        records.append(_record(conn, f'{fmt}_HS', gender, rows, value, 'score'))
    return records


def _bowling(conn, fmt, gender):
    records = []
    rows = _rows(conn, '''WITH scores AS (SELECT person_id, sum(wickets) score FROM bowl GROUP BY person_id)
        SELECT * FROM scores WHERE score>0 AND score=(SELECT max(score) FROM scores) ORDER BY person_id''')
    if rows:
        records.append(_record(conn, f'{fmt}_WKTS', gender, rows, str(int(rows[0]['score'])), 'wickets'))
    rows = _rows(conn, '''SELECT * FROM bowl WHERE wickets>0
        QUALIFY dense_rank() OVER(ORDER BY wickets DESC, runs)=1 ORDER BY person_id, match_id''')
    if rows:
        records.append(_record(conn, f'{fmt}_BBI', gender, rows,
                               f"{rows[0]['wickets']}/{rows[0]['runs']}", 'figures'))
    rows = _rows(conn, '''WITH scores AS (
        SELECT person_id, 6.0*sum(runs)/sum(balls) score FROM bowl GROUP BY person_id HAVING sum(balls)>=1000
        ) SELECT * FROM scores WHERE score=(SELECT min(score) FROM scores) ORDER BY person_id''')
    if rows:
        records.append(_record(conn, f'{fmt}_ECON', gender, rows, f"{rows[0]['score']:.2f}", 'economy',
            'Qualification: at least 1000 legal balls in covered matches; runs per six legal balls; byes/leg-byes/penalties excluded.'))
    return records


def _appearances(conn, fmt, gender):
    rows = _rows(conn, '''WITH counts AS (SELECT person_id, count(DISTINCT match_id) score
        FROM match_players JOIN m USING(match_id) GROUP BY person_id)
        SELECT * FROM counts WHERE score=(SELECT max(score) FROM counts) ORDER BY person_id''')
    if rows:
        return [_record(conn, f'{fmt}_MATCHES', gender, rows, str(rows[0]['score']), 'matches',
                        'Roster appearances in supplied match files; includes recorded no-results.')]
    return []


def _teams(conn, fmt, gender):
    records = []
    rows = _rows(conn, '''SELECT team holder, match_id, runs, wickets FROM i WHERE NOT forfeited
        AND runs=(SELECT max(runs) FROM i WHERE NOT forfeited) ORDER BY team, match_id''')
    if rows:
        records.append(_record(conn, f'{fmt}_TEAM', gender, rows, _scorelines(rows), 'total'))
    for suffix, condition, order, context in (
        ('LOWEST', 'i.wickets>=10 AND NOT i.forfeited', 'runs',
         'Lowest all-out total only; partial, forfeited and unfinished innings excluded.'),
        ('CHASE', "i.team=m.winner AND m.outcome_method IS NULL AND NOT i.forfeited "
         "AND i.innings_no=(SELECT max(j.innings_no) FROM i j WHERE j.match_id=i.match_id) "
         "AND (SELECT count(*) FROM i j WHERE j.match_id=i.match_id)>=2 "
         "AND m.result_type='wickets'", 'runs DESC',
         'Highest winning second-innings total; revised-target/method-adjusted matches excluded.'),
    ):
        rows = _rows(conn, f'''SELECT i.team holder, i.match_id, i.runs, i.wickets FROM i
            JOIN m USING(match_id) WHERE {condition}
            QUALIFY dense_rank() OVER(ORDER BY {order})=1 ORDER BY holder, match_id''')
        if rows:
            records.append(_record(conn, f'{fmt}_{suffix}', gender, rows, _scorelines(rows), 'total', context))
    for suffix, margin, unit in (('WIN_RUNS', 'runs', 'runs'), ('WIN_WKTS', 'wickets', 'wickets')):
        rows = _rows(conn, '''SELECT winner holder, match_id, result_margin score FROM m
            WHERE result_type=? AND winner IS NOT NULL AND result_margin IS NOT NULL
            QUALIFY dense_rank() OVER(ORDER BY result_margin DESC)=1 ORDER BY holder, match_id''', [margin])
        if rows:
            records.append(_record(conn, f'{fmt}_{suffix}', gender, rows, str(rows[0]['score']), unit,
                                   'Recorded match outcome margin, including method-adjusted outcomes.'))
    rows = _rows(conn, '''WITH counts AS (SELECT winner holder, count(*) score FROM m
        WHERE winner IS NOT NULL GROUP BY winner)
        SELECT * FROM counts WHERE score=(SELECT max(score) FROM counts) ORDER BY holder''')
    if rows:
        records.append(_record(conn, f'{fmt}_MOST_WINS', gender, rows, str(rows[0]['score']), 'wins',
            'Outright wins recorded in outcome.winner; tied-match eliminators are not added.'))
    return records


def _scorelines(rows):
    return ' = '.join(dict.fromkeys(f"{r['runs']}/{r['wickets']}" for r in rows))


@lru_cache(maxsize=12)
def _snapshot(path, modified, size, gender, fmt):
    with duckdb.connect(path, read_only=True) as conn:
        _prepare(conn, gender, fmt)
        if not conn.execute('SELECT count(*) FROM m').fetchone()[0]:
            return ()
        return tuple(_batting(conn, fmt, gender) + _bowling(conn, fmt, gender)
                     + _appearances(conn, fmt, gender) + _teams(conn, fmt, gender))


def compute(intent_id: str, gender: Gender, *, db_path: Path = DB_PATH) -> Fact | None:
    """Return a record from this snapshot, or None when unavailable/unsupported.

    The optional path is useful for offline scorecard tests. Cache keys include
    file timestamp and size, so a refreshed database never reuses old totals.
    """
    if intent_id not in COMPUTABLE or gender not in ('women', 'men'):
        return None
    path = Path(db_path)
    if not path.is_file():
        return None
    stat = path.stat()
    facts = _snapshot(str(path.resolve()), stat.st_mtime_ns, stat.st_size, gender, intent_id.split('_')[0])
    fact = next((f for f in facts if f.intent_id == intent_id), None)
    return replace(fact, ids=dict(fact.ids)) if fact else None


@lru_cache(maxsize=128)
def _entity_snapshot(path, modified, size, intent, gender, entity):
    fmt, suffix = intent.split('_', 1)
    with duckdb.connect(path, read_only=True) as conn:
        _prepare(conn, gender, fmt)
        latest = conn.execute('SELECT max(date) FROM m').fetchone()[0]
        if latest is None:
            return None
        if suffix == 'PLAYER_LINE':
            matches = conn.execute('''SELECT count(DISTINCT match_id) FROM match_players
                JOIN m USING(match_id) WHERE person_id=?''', [entity.entity_id]).fetchone()[0]
            if not matches:
                return None
            runs = conn.execute('SELECT coalesce(sum(runs),0) FROM bat WHERE person_id=?', [entity.entity_id]).fetchone()[0]
            wickets = conn.execute('SELECT coalesce(sum(wickets),0) FROM bowl WHERE person_id=?', [entity.entity_id]).fetchone()[0]
            return _record(conn, intent, gender, [{'person_id': entity.entity_id}],
                f'{matches} / {runs} / {wickets}', 'career_line',
                f'Order: roster matches / batting runs / bowler wickets. data_lag: {latest}.')
        rows = _rows(conn, '''SELECT * FROM m WHERE team1=? OR team2=?
            QUALIFY date=max(date) OVER() ORDER BY match_id''', [entity.entity_id, entity.entity_id])
        if len(rows) != 1:
            # Match dates have no start time: do not invent an ordering on the same day.
            return None
        match = rows[0]
        if match['winner']:
            value = f"{match['winner']} won"
            if match['result_margin'] is not None and match['result_type'] in ('runs', 'wickets'):
                value += f" by {match['result_margin']} {match['result_type']}"
        elif match['result_type'] in ('tie', 'no result', 'draw'):
            value = match['result_type']
            if match['eliminator']:
                value += f"; eliminator winner: {match['eliminator']}"
        else:
            return None
        context = f"{match['team1']} vs {match['team2']}; match date: {match['date']}; data_lag: {latest}."
        if match['outcome_method']:
            context += f" Method: {match['outcome_method']}."
        return _record(conn, intent, gender, [{'holder': entity.name, 'match_id': match['match_id']}],
                       value, 'result', context)


def compute_entity(intent_id: str, gender: Gender, entity: Entity, *, db_path: Path = DB_PATH) -> Fact | None:
    """Covered player totals or a team's latest supplied match, never a live result."""
    if gender not in ('women', 'men') or intent_id not in {
        f'{fmt}_{suffix}' for fmt in ('T20I', 'ODI') for suffix in ('PLAYER_LINE', 'LAST_RESULT')
    }:
        return None
    if intent_id.endswith('PLAYER_LINE'):
        if entity.kind != 'player' or entity.gender != gender or entity.entity_id.startswith('ambiguous:'):
            return None
    elif entity.kind != 'team':
        return None
    path = Path(db_path)
    if not path.is_file():
        return None
    stat = path.stat()
    fact = _entity_snapshot(str(path.resolve()), stat.st_mtime_ns, stat.st_size, intent_id, gender, entity)
    return replace(fact, ids=dict(fact.ids)) if fact else None
