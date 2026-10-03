import csv

import pytest

from mak.config import GOLDEN_PATH
from mak.records.golden import audit_golden, golden_index, load_golden


def test_all_fifty_records_have_provenance_and_form_gender_pairs():
    facts = load_golden()
    assert len(facts) == 50
    index = golden_index()
    assert len(index) == 50
    assert len({f.intent_id for f in facts}) == 25
    for fact in facts:
        assert fact.trust == "verified"
        assert fact.as_of and fact.holder and fact.value and fact.sources
        assert all(source.startswith("https://") for source in fact.sources)
        assert (fact.intent_id, "women") in index
        assert (fact.intent_id, "men") in index
    mandhana = index["T20I_RUNS", "women"]
    assert (mandhana.holder, mandhana.country, mandhana.value, mandhana.unit) == (
        "Smriti Mandhana", "India", "4,867", "runs"
    )
    assert index["WC_ODI_LAST", "women"].holder == "India (first title)"


def write_rows(tmp_path, mutate):
    with GOLDEN_PATH.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields, rows = reader.fieldnames, list(reader)
    mutate(rows)
    path = tmp_path / "records.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_unverified_record_is_excluded(tmp_path):
    path = write_rows(tmp_path, lambda rows: rows[0].update(verification="unverified"))
    with pytest.warns(UserWarning, match="unverified"):
        facts = load_golden(path)
    assert len(facts) == 49
    assert not any(f.intent_id == "T20I_RUNS" and f.gender == "women" for f in facts)


@pytest.mark.parametrize("change", [
    {"as_of": "2026-02-31"}, {"source_1": ""}, {"value": ""},
    {"gender": "female"}, {"overall_leader": "unknown"},
])
def test_invalid_record_fails_with_row_context(tmp_path, change):
    path = write_rows(tmp_path, lambda rows: rows[0].update(change))
    with pytest.raises(ValueError, match="row 2"):
        load_golden(path)


def test_duplicate_key_is_rejected(tmp_path):
    path = write_rows(tmp_path, lambda rows: rows.append(rows[0].copy()))
    with pytest.raises(ValueError, match="duplicate"):
        load_golden(path)


def test_audit_does_not_count_repeated_url_as_two_sources():
    issues = audit_golden()
    duplicates = [r for r in issues if r["issue"] == "V2 has fewer than two distinct URLs"]
    assert {r["intent_id"] for r in duplicates} == {
        "WC_T20_LAST", "WC_T20_TITLES", "WC_T20_RUNS", "WC_T20_WKTS"
    }
