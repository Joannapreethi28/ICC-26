import csv
import json

import duckdb

from mak.registry.people import build_registry, derive_gender, export_registry


def test_roster_categories_ids_aliases_and_cached_labels(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "people.csv").write_text(
        "identifier,name,unique_name,key_cricinfo,key_pulse,key_opta\n"
        "s,SM Mandhana,SM Mandhana,597806,100,200\n"
        "x,Collision,Collision,,,\n"
        "u,Official,Official,,,\n", encoding="utf-8")
    (raw / "names.csv").write_text("identifier,name\ns,Smriti Mandhana\n", encoding="utf-8")
    cache = tmp_path / "labels.csv"
    with cache.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["cricinfo_id", "qid", "hi", "ta", "en", "status"])
        writer.writeheader()
        # Contract fixture from the build plan; actual downloaded cache is verified separately.
        writer.writerow({"cricinfo_id": "597806", "qid": "Q16224802", "hi": "स्मृति मंधाना",
                         "ta": "ஸ்மிருதி மந்தனா", "en": "Smriti Mandhana", "status": "found"})
    db = tmp_path / "registry.duckdb"
    with duckdb.connect(str(db)) as conn:
        conn.execute("CREATE TABLE match_players(match_id VARCHAR, team VARCHAR, person_id VARCHAR, gender VARCHAR)")
        conn.execute("INSERT INTO match_players VALUES ('1','India','s','women'), ('1','India','x','women'), ('2','India','x','men')")
    build_registry(raw, db, cache_path=cache)
    assert derive_gender("s", db) == "women"
    assert derive_gender("x", db) is None
    assert derive_gender("u", db) is None
    assert derive_gender("missing", db) is None
    with duckdb.connect(str(db), read_only=True) as conn:
        assert conn.execute("select pulse_id, opta_id, wikidata_qid, label_hi, label_ta from people where person_id='s'").fetchone() == (
            "100", "200", "Q16224802", "स्मृति मंधाना", "ஸ்மிருதி மந்தனா"
        )
        aliases = conn.execute("select aliases from people where person_id='s'").fetchone()[0]
        assert "Smriti Mandhana" in json.loads(aliases)
        assert conn.execute("select gender from teams_i18n order by gender").fetchall() == [("men",), ("women",)]
    export_registry(db, tmp_path / "export")
    rows = list(csv.DictReader((tmp_path / "export/people.csv").open(encoding="utf-8")))
    assert len(rows) == 3
    assert rows[1]["gender"] == ""  # Unknown remains unknown in the portable export.
