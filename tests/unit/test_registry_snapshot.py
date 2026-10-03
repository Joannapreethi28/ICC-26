"""Checks the portable production snapshot, without a database or network."""
import csv
import json
import shutil

import duckdb

from mak.config import DATA, I18N_DIR
from mak.nlu.entities import resolve_entities
from mak.registry.wikidata import populate_labels


def test_committed_mandhana_identity_and_native_labels():
    with (DATA / "registry/people.csv").open(encoding="utf-8", newline="") as fh:
        mandhana = next(r for r in csv.DictReader(fh) if r["cricinfo_id"] == "597806")
    assert mandhana["gender"] == "women"
    assert mandhana["wikidata_qid"] == "Q16224802"
    assert mandhana["label_hi"] == "स्मृति मंधाना"
    assert mandhana["label_ta"] == "ஸ்மிருதி மந்தனா"
    assert {e.gender for e in resolve_entities("Kohli vs Mandhana T20I runs")} == {"women", "men"}
    assert all(e.gender is None for e in resolve_entities("Sharma wickets"))


def test_cached_translations_are_dated_sourced_and_fallbacks_explicit():
    for lang in ("hi", "ta"):
        with (I18N_DIR / f"entities_{lang}.csv").open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) >= 1000
        assert all(r["source"] and r["fetched_at"] and r["label"] for r in rows)
        assert sum(r["kind"] == "team" and r["fallback"] == "False" for r in rows) >= 20
    report = json.loads((I18N_DIR / "coverage.json").read_text(encoding="utf-8"))
    assert report["golden_holders_requested"] >= 20


def test_refresh_reconciles_unique_aliases_without_duplicate_fallbacks(tmp_path, monkeypatch):
    import requests

    def no_network(*args, **kwargs):
        raise AssertionError("All snapshot lookups should be cached")

    monkeypatch.setattr(requests.Session, "get", no_network)
    for name in ("wikidata_players.csv", "wikidata_teams.csv", "golden_players.csv"):
        shutil.copyfile(I18N_DIR / name, tmp_path / name)
    db = tmp_path / "registry.duckdb"
    with duckdb.connect(str(db)) as conn:
        for table in ("people", "teams_i18n"):
            conn.execute(f"CREATE TABLE {table} AS SELECT * FROM read_csv(?, header=true, all_varchar=true)",
                         [str(DATA / "registry" / f"{table}.csv")])
        conn.execute("ALTER TABLE people ALTER match_count TYPE INTEGER")
    report = populate_labels(db, tmp_path)
    assert "Sachin Tendulkar" not in report["golden_holders_not_mapped"]
    assert "Lucia Taylor" not in report["golden_holders_not_mapped"]
    assert "Rashid Khan" in report["golden_holders_not_mapped"]  # Real distinct identities.
    with (tmp_path / "entities_hi.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert not any(r["entity_id"] == "golden:Sachin Tendulkar" for r in rows)
    assert not any(r["entity_id"] == "golden:Rashid Khan" for r in rows)
