"""Phase 0 contract tests: the shared types, labels and the two fixed signatures."""
import csv
import dataclasses

import pytest

from mak import config, labels
from mak.nlu.understand import understand
from mak.pipeline import resolve
from mak.types import Fact, Parse, Resolution


def test_parse_is_frozen():
    p = Parse(lang="en", gender_signal="none", gender_conf=0.0, topic="cricket_stat",
              family="career_record", stat="runs", format="T20I")
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.lang = "hi"  # type: ignore[misc]


def test_fact_ids_default_empty():
    f = Fact(intent_id="T20I_RUNS", gender="women", format="T20I", holder="Smriti Mandhana",
             holder_local=None, country="India", value="4,867", unit="runs", context="", as_of="2026-09-22",
             trust="verified", sources=("x",))
    assert f.ids == {}


def test_label_sets_are_closed_and_consistent():
    assert set(labels.STATS) == set(labels.FAMILY)
    assert "none" in labels.GENDER_SIGNAL and "unspecified" in labels.FORMAT
    assert labels.TESTSET_COLUMNS[0] == "id" and "source" in labels.TESTSET_COLUMNS


def test_understand_signature_and_type():
    p = understand("Who has the most T20I runs?")
    assert isinstance(p, Parse)
    assert (p.gender_signal, p.family, p.stat, p.format) == ("none", "career_record", "runs", "T20I")
    assert understand("most women's T20I runs").gender_signal == "women"
    assert understand("").topic == "non_sport"


def test_resolve_signature_and_type():
    r = resolve("Who has the most T20I runs?")
    assert isinstance(r, Resolution)
    assert r.language == "en"


def test_golden_csv_present_with_d2_fix():
    rows = list(csv.DictReader(open(config.GOLDEN_PATH, encoding="utf-8")))
    assert len(rows) == 50
    leader = {(r["intent_id"], r["gender"]): r["overall_leader"] for r in rows}
    assert leader[("WC_T20_WKTS", "women")] == "women"
    assert leader[("WC_T20_LAST", "women")] == "women"
