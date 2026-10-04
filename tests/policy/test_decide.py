from dataclasses import replace
from itertools import product

import pytest

from mak.policy.decide import DECISION_TO_GENDERS, decide
from mak.types import Parse


@pytest.mark.parametrize('topic,supported,injection,signal,confidence', list(product(
    ('cricket_general', 'non_sport', 'cricket_stat', 'other_sport_stat'),
    (False, True), (False, True), ('women', 'men', 'both_named', 'none'), (0.5, 0.85, 1.0))))
def test_policy_precedence_and_purity(topic, supported, injection, signal, confidence):
    p = Parse('en', signal, confidence, topic, 'career_record', 'runs', 'T20I',
              injection_suspected=injection)
    before = replace(p)
    result, trace = decide(p, supported)
    if topic in ('cricket_general', 'non_sport'):
        expected = 'no_intervention'
    elif not supported:
        expected = 'unsupported'
    elif injection or (signal in ('women', 'men') and confidence < 0.85):
        expected = 'ambiguous_both'
    else:
        expected = {'women': 'explicit_women', 'men': 'explicit_men',
                    'both_named': 'both_named', 'none': 'ambiguous_both'}[signal]
    assert result == expected
    assert trace
    assert decide(p, supported) == (result, trace)
    assert p == before
    assert DECISION_TO_GENDERS[result] == {
        'explicit_women': ('women',), 'explicit_men': ('men',),
        'ambiguous_both': ('women', 'men'), 'both_named': ('women', 'men'),
        'no_intervention': (), 'unsupported': (),
    }[expected]
