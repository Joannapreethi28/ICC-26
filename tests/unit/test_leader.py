from dataclasses import replace

import pytest

from mak.records.golden import GOLDEN_LEADER, golden_index
from mak.records.leader import compute_leader


@pytest.mark.parametrize("intent_id", sorted(GOLDEN_LEADER))
def test_all_declared_leaders_match_comparison(intent_id):
    index = golden_index()
    assert compute_leader(intent_id, index[intent_id, "women"], index[intent_id, "men"]) == GOLDEN_LEADER[intent_id]


@pytest.mark.parametrize("intent,women,men,expected", [
    ("ODI_HS", "232*", "232", "none"),
    ("T20I_TEAM", "427/1", "344/4", "women"),
    ("T20I_BBI", "9/4", "8/7", "women"),
    ("T20I_BBI", "5/10", "5/11", "women"),
    ("T20I_BBI", "5/10", "5/10", "none"),
])
def test_cricket_number_ordering(intent, women, men, expected):
    index = golden_index()
    assert compute_leader(intent, replace(index[intent, "women"], value=women),
                          replace(index[intent, "men"], value=men)) == expected
