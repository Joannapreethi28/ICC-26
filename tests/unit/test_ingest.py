import json
from pathlib import Path
import zipfile

import duckdb
import pytest

from mak.ingest.cricsheet import build_db, coverage


@pytest.fixture
def match():
    # Synthetic schema fixture, deliberately not a real match or a record source.
    return {"meta": {"data_version": "1.1.0"}, "info": {
        "gender": "female", "match_type": "T20", "team_type": "international",
        "dates": ["2024-01-01"], "teams": ["Team A", "Team B"], "season": "2024",
        "players": {"Team A": ["A Batter", "A Partner"], "Team B": ["B Bowler"]},
        "registry": {"people": {"A Batter": "a", "A Partner": "b", "B Bowler": "c", "Umpire": "u"}},
        "outcome": {"winner": "Team A", "by": {"runs": 1}}, "balls_per_over": 6,
    }, "innings": [{"team": "Team A", "overs": [{"over": 0, "deliveries": [
        {"batter": "A Batter", "non_striker": "A Partner", "bowler": "B Bowler",
         "runs": {"batter": 4, "extras": 0, "total": 4}},
        {"batter": "A Batter", "non_striker": "A Partner", "bowler": "B Bowler",
         "runs": {"batter": 0, "extras": 2, "total": 2}, "extras": {"wides": 2}},
        {"batter": "A Batter", "non_striker": "A Partner", "bowler": "B Bowler",
         "runs": {"batter": 2, "extras": 1, "total": 3}, "extras": {"noballs": 1}},
        {"batter": "A Batter", "non_striker": "A Partner", "bowler": "B Bowler",
         "runs": {"batter": 0, "extras": 1, "total": 1}, "extras": {"legbyes": 1},
         "wickets": [{"player_out": "A Partner", "kind": "run out"}]},
    ]}]}]}


def raw_match(tmp_path, match, match_id="1"):
    raw = tmp_path / "raw"
    raw.mkdir(exist_ok=True)
    (raw / f"{match_id}.json").write_text(json.dumps(match), encoding="utf-8")
    return raw


def test_ingest_preserves_runs_legal_balls_ids_and_roster_only(tmp_path, match):
    raw, db = raw_match(tmp_path, match), tmp_path / "mak.duckdb"
    counts = build_db(raw, db)
    assert counts == {"matches": 1, "innings": 1, "deliveries": 4, "match_players": 3, "wickets": 1}
    with duckdb.connect(str(db), read_only=True) as conn:
        assert conn.execute("select gender, match_type from matches").fetchone() == ("women", "T20I")
        assert conn.execute("select runs, wickets, legal_balls from innings").fetchone() == (10, 1, 2)
        assert conn.execute("select person_id from match_players order by person_id").fetchall() == [("a",), ("b",), ("c",)]
        assert conn.execute("select sum(runs_batter), sum(runs_bowler), sum(batter_ball) from deliveries").fetchone() == (6, 9, 3)
        assert conn.execute("select credited_to_bowler from wickets").fetchone() == (False,)
    assert coverage(db)[0]["matches"] == 1


def test_super_over_penalties_and_multiple_wickets_survive(tmp_path, match):
    innings = match["innings"][0]
    innings["super_over"] = True
    innings["penalty_runs"] = {"pre": 5, "post": 5}
    innings["overs"][0]["deliveries"][-1]["wickets"].append({"player_out": "A Batter", "kind": "retired hurt"})
    db = tmp_path / "mak.duckdb"
    build_db(raw_match(tmp_path, match), db)
    with duckdb.connect(str(db), read_only=True) as conn:
        assert conn.execute("select runs, wickets, super_over from innings").fetchone() == (20, 1, True)
        assert conn.execute("select count(*) from wickets").fetchone() == (2,)
        assert conn.execute("select sum(runs_total) from deliveries").fetchone() == (10,)


def test_bad_input_preserves_previous_database(tmp_path, match):
    raw, db = raw_match(tmp_path, match), tmp_path / "mak.duckdb"
    build_db(raw, db)
    match["info"]["registry"]["people"].pop("A Batter")
    raw_match(tmp_path, match)
    with pytest.raises(ValueError, match="1"):
        build_db(raw, db)
    assert coverage(db)[0]["matches"] == 1


def test_club_match_does_not_become_an_international(tmp_path, match):
    match["info"]["team_type"] = "club"
    with pytest.raises(ValueError, match="international"):
        build_db(raw_match(tmp_path, match), tmp_path / "mak.duckdb")


def test_trimmed_real_cricsheet_files(tmp_path):
    db = tmp_path / "real.duckdb"
    build_db(Path(__file__).parents[1] / "fixtures/cricsheet", db)
    with duckdb.connect(str(db), read_only=True) as conn:
        assert conn.execute("SELECT match_id, gender, match_type FROM matches ORDER BY match_id").fetchall() == [
            ("1000887", "men", "ODI"), ("1043989", "women", "T20I")]
        assert conn.execute("SELECT match_id, runs, legal_balls FROM innings ORDER BY match_id").fetchall() == [
            ("1000887", 1, 6), ("1043989", 3, 6)]


def test_duplicate_zip_member_does_not_double_count(tmp_path, match):
    raw = raw_match(tmp_path, match)
    with zipfile.ZipFile(raw / "sample.zip", "w") as archive:
        archive.write(raw / "1.json", "1.json")
    counts = build_db(raw, tmp_path / "deduplicated.duckdb")
    assert counts["matches"] == 1
    assert counts["deliveries"] == 4
