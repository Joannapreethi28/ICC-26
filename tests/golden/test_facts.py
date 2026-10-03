from pathlib import Path

import pytest

from mak.fetch.catalogue import CATALOGUE, lookup
from mak.fetch.facts import get_facts
from mak.records.golden import load_golden
from mak.types import Entity


@pytest.mark.parametrize('expected', load_golden(), ids=lambda f: f'{f.intent_id}-{f.gender}')
def test_all_golden_facts_win_exactly(expected):
    [actual] = get_facts(expected.intent_id, (expected.gender,))
    for field in ('value', 'holder', 'country', 'context', 'as_of', 'sources', 'trust', 'unit'):
        assert getattr(actual, field) == getattr(expected, field)


def test_catalogue_expansion_and_unknowns():
    assert lookup('career_record', 'runs', 'unspecified') == ['T20I_RUNS', 'ODI_RUNS']
    assert lookup('career_record', 'maiden_overs', 'T20I') == []
    assert lookup('career_record', 'runs', 'Test') == []
    assert lookup('world_cup_record', 'first_edition', 'unspecified') == []
    assert lookup(None, 'runs', 'T20I') == []
    assert len(CATALOGUE) == 50


def test_verified_names_are_localized_offline_even_without_database(tmp_path):
    missing = tmp_path / 'missing.duckdb'
    [hi] = get_facts('T20I_RUNS', ('women',), 'hi', db_path=missing)
    [ta] = get_facts('T20I_RUNS', ('women',), 'ta', db_path=missing)
    assert hi.holder_local == 'स्मृति मंधाना'
    assert ta.holder_local == 'ஸ்மிருதி மந்தனா'
    assert hi.ids['cricinfo'] == '597806'
    assert not missing.exists()
    assert get_facts('T20I_6S', ('women',), db_path=missing) == []
    assert get_facts('ODI_PLAYER_LINE', ('women',), db_path=missing) == []


def test_entity_queries_do_not_fall_back_to_headline():
    unknown = Entity('ambiguous:Sharma', 'Sharma', 'player', None, 100)
    assert get_facts('T20I_PLAYER_LINE', ('men',), entity=unknown) == []
    assert get_facts('T20I_LAST_RESULT', ('women', 'men')) == []


def test_golden_results_are_independent_values():
    first = get_facts('T20I_RUNS', ('women',))[0]
    first.ids['cricinfo'] = 'corrupted'
    assert get_facts('T20I_RUNS', ('women',))[0].ids['cricinfo'] == '597806'
