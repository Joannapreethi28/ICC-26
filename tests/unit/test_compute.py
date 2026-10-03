"""Small synthetic scorecards with hand-counted expectations, never record evidence."""
import json

import pytest
import duckdb

from mak.ingest.cricsheet import build_db
from mak.records.compute import compute
from mak.types import Entity


def delivery(runs=0, *, extras=None, wickets=None, batter='Alice', bowler='Beth'):
    extras = extras or {}
    result = {'batter': batter, 'non_striker': 'Anne', 'bowler': bowler,
              'runs': {'batter': runs, 'extras': sum(extras.values()), 'total': runs + sum(extras.values())}}
    if extras:
        result['extras'] = extras
    if wickets:
        result['wickets'] = [{'player_out': name, 'kind': kind} for name, kind in wickets]
    return result


@pytest.fixture
def scorecards(tmp_path):
    raw = tmp_path / 'raw'
    raw.mkdir()
    matches = [
        [delivery(4), delivery(extras={'wides': 2}), delivery(6, extras={'noballs': 1}),
         delivery(extras={'legbyes': 1}, wickets=[('Anne', 'run out')]),
         delivery(wickets=[('Alice', 'caught')])],
        [delivery(1), delivery(wickets=[('Alice', 'bowled')])],
    ]
    for i, balls in enumerate(matches, 1):
        match = {'meta': {'data_version': '1.1.0'}, 'info': {
            'gender': 'female', 'match_type': 'T20', 'team_type': 'international',
            'dates': [f'2024-01-0{i}'], 'teams': ['Alpha', 'Beta'], 'balls_per_over': 6,
            'players': {'Alpha': ['Alice', 'Anne'], 'Beta': ['Beth']},
            'registry': {'people': {'Alice': 'a', 'Anne': 'b', 'Beth': 'c'}},
            'outcome': {'winner': 'Alpha', 'by': {'runs': i}},
        }, 'innings': [
            {'team': 'Alpha', 'overs': [{'over': 0, 'deliveries': balls}],
             'penalty_runs': {'pre': 5}},
            {'team': 'Alpha', 'super_over': True, 'overs': [{'over': 0, 'deliveries': [delivery(6)]}]},
        ]}
        (raw / f'{i}.json').write_text(json.dumps(match), encoding='utf-8')
    path = tmp_path / 'db.duckdb'
    build_db(raw, path)
    return path


def test_counting_from_scorecards(scorecards):
    def record(intent):
        return compute(intent, 'women', db_path=scorecards)
    runs = record('T20I_RUNS')
    assert (runs.holder, runs.value, runs.trust, runs.as_of) == ('Alice', '11', 'computed', '2024-01-02')
    assert runs.sources == ('Cricsheet',)
    assert record('T20I_WKTS').value == '2'  # run-out does not belong to the bowler
    assert record('T20I_BBI').value == '1/1'  # same wickets, fewer conceded runs
    assert record('T20I_TEAM').value == '19/2'  # penalties and every extra included
    assert record('T20I_HS').value == '10'
    assert record('T20I_6S').value == '1'
    assert record('T20I_MATCHES').value == '2'
    assert compute('T20I_RUNS', 'men', db_path=scorecards) is None
    assert compute('WC_T20_RUNS', 'women', db_path=scorecards) is None


def test_team_records_and_incomplete_chases(scorecards):
    with duckdb.connect(str(scorecards)) as conn:
        conn.execute("UPDATE innings SET wickets=10 WHERE match_id='2' AND NOT super_over")
        conn.execute("INSERT INTO innings VALUES ('1',3,'Beta',20,3,15,false,0,0,false,false,20,20)")
        conn.execute("UPDATE matches SET winner='Beta', result_type='wickets', result_margin=7 WHERE match_id='1'")
    assert compute('T20I_LOWEST', 'women', db_path=scorecards).value == '6/10'
    assert compute('T20I_WIN_RUNS', 'women', db_path=scorecards).value == '2'
    assert compute('T20I_WIN_WKTS', 'women', db_path=scorecards).value == '7'
    assert compute('T20I_CHASE', 'women', db_path=scorecards).value == '20/3'
    wins = compute('T20I_MOST_WINS', 'women', db_path=scorecards)
    assert (wins.value, wins.holder) == ('1', 'Alpha / Beta')
    with duckdb.connect(str(scorecards)) as conn:
        conn.execute("UPDATE matches SET outcome_method='D/L' WHERE match_id='1'")
    assert compute('T20I_CHASE', 'women', db_path=scorecards) is None


def test_player_line_and_last_result_require_resolved_entities(scorecards):
    from mak.records.compute import compute_entity
    alice = Entity('a', 'Alice', 'player', 'women', 100)
    line = compute_entity('T20I_PLAYER_LINE', 'women', alice, db_path=scorecards)
    assert (line.holder, line.value) == ('Alice', '2 / 11 / 0')
    assert 'data_lag: 2024-01-02' in line.context
    assert compute_entity('T20I_PLAYER_LINE', 'men', alice, db_path=scorecards) is None
    unknown = Entity('ambiguous:Alice', 'Alice', 'player', None, 100)
    assert compute_entity('T20I_PLAYER_LINE', 'women', unknown, db_path=scorecards) is None
    team = Entity('Alpha', 'Alpha', 'team', None, 100)
    result = compute_entity('T20I_LAST_RESULT', 'women', team, db_path=scorecards)
    assert result.value == 'Alpha won by 2 runs'
    assert '2024-01-02' in result.context


def test_qualifications_notouts_and_nonboundary_sixes(scorecards):
    assert compute('T20I_AVG', 'women', db_path=scorecards) is None
    assert compute('T20I_ECON', 'women', db_path=scorecards) is None
    with duckdb.connect(str(scorecards)) as conn:
        # Extend the second synthetic innings: 1000 singles, no extra dismissals.
        conn.execute('''INSERT INTO deliveries
            SELECT '2',1,10+(n//6)::INT,(n%6+1)::INT,'a','c',1,0,1,'',NULL,NULL,'b',
                   0,0,0,0,0,true,true,1,false FROM range(1000) t(n)''')
        conn.execute("UPDATE deliveries SET non_boundary=true WHERE runs_batter=6")
    assert compute('T20I_AVG', 'women', db_path=scorecards).value == '505.50'  # 1011 / two outs
    assert compute('T20I_SR', 'women', db_path=scorecards).value == '100.50'  # 1011 / 1006 faced
    assert compute('T20I_ECON', 'women', db_path=scorecards).value == '6.05'  # 1014 / 1005 legal * 6
    assert compute('T20I_6S', 'women', db_path=scorecards) is None
    assert '1000' in compute('T20I_AVG', 'women', db_path=scorecards).context


def test_centuries_and_fifties_are_disjoint(scorecards):
    with duckdb.connect(str(scorecards)) as conn:
        # The first innings becomes 100 and the second 50, each built from singles.
        for match_id, count in [('1', 90), ('2', 49)]:
            conn.execute('''INSERT INTO deliveries
                SELECT ?,1,10+(n//6)::INT,(n%6+1)::INT,'a','c',1,0,1,'',NULL,NULL,'b',
                       0,0,0,0,0,true,true,1,false FROM range(?) t(n)''', [match_id, count])
    assert compute('T20I_100S', 'women', db_path=scorecards).value == '1'
    assert compute('T20I_50S', 'women', db_path=scorecards).value == '1'


def test_entity_to_policy_to_facts_flow_and_shared_team_names(scorecards):
    from mak.fetch.catalogue import lookup
    from mak.fetch.facts import get_facts
    from mak.policy.decide import DECISION_TO_GENDERS, decide
    from mak.types import Parse
    # This tests the Phase 3 seams. Applying registry overrides inside resolve()
    # remains K-P4; here the already-resolved parse comes from that contract.
    alice = Entity('a', 'Alice', 'player', 'women', 100)
    p = Parse('en', 'women', 1, 'cricket_stat', 'player_stat', 'career_line', 'T20I', (alice,))
    [intent] = lookup(p.family, p.stat, p.format)
    decision, _ = decide(p, supported=True)
    assert decision == 'explicit_women'
    [fact] = get_facts(intent, DECISION_TO_GENDERS[decision], entity=alice, db_path=scorecards)
    assert fact.holder == 'Alice' and fact.trust == 'computed'
    # Reuse the second source match as a men's match to exercise neutral teams.
    with duckdb.connect(str(scorecards)) as conn:
        conn.execute("UPDATE matches SET gender='men' WHERE match_id='2'")
        conn.execute("UPDATE match_players SET gender='men' WHERE match_id='2'")
    team = Entity('Alpha', 'Alpha', 'team', None, 100)
    p = Parse('en', 'none', 1, 'cricket_stat', 'recent_result', 'last_result', 'T20I', (team,))
    [intent] = lookup(p.family, p.stat, p.format)
    decision, _ = decide(p, supported=True)
    assert decision == 'ambiguous_both'
    facts = get_facts(intent, DECISION_TO_GENDERS[decision], entity=team, db_path=scorecards)
    assert [f.gender for f in facts] == ['women', 'men']
    assert [f.value for f in facts] == ['Alpha won by 1 runs', 'Alpha won by 2 runs']


def test_retired_hurt_is_not_a_dismissal_and_unknown_results_stay_missing(scorecards):
    from mak.records.compute import compute_entity
    with duckdb.connect(str(scorecards)) as conn:
        conn.execute("UPDATE wickets SET wicket_kind='retired hurt', credited_to_bowler=false WHERE player_out_id='a'")
        conn.execute("UPDATE matches SET winner=NULL, result_type='unknown' WHERE match_id='2'")
    assert compute('T20I_HS', 'women', db_path=scorecards).value == '10*'
    assert compute('T20I_WKTS', 'women', db_path=scorecards) is None
    assert compute_entity('T20I_LAST_RESULT', 'women', Entity('Alpha', 'Alpha', 'team', None, 100), db_path=scorecards) is None
