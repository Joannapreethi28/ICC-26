"""Cricsheet JSON -> DuckDB, retaining extras, dismissals and coverage metadata.

Only international T20/ODI inputs are accepted. Staging CSVs keep memory bounded;
the previous database is replaced only after an entire build succeeds.
"""
from __future__ import annotations

from contextlib import ExitStack
import csv
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile

import duckdb

from mak.config import DB_PATH

SCHEMA = {
    "matches": "match_id VARCHAR, gender VARCHAR, match_type VARCHAR, event VARCHAR, season VARCHAR, date DATE, team1 VARCHAR, team2 VARCHAR, venue VARCHAR, winner VARCHAR, result_margin INTEGER, result_type VARCHAR, team_type VARCHAR, balls_per_over INTEGER, outcome_method VARCHAR, eliminator VARCHAR, source_url VARCHAR, data_version VARCHAR",
    "innings": "match_id VARCHAR, innings_no INTEGER, team VARCHAR, runs INTEGER, wickets INTEGER, legal_balls INTEGER, super_over BOOLEAN, penalty_pre INTEGER, penalty_post INTEGER, declared BOOLEAN, forfeited BOOLEAN, target_runs INTEGER, target_overs DOUBLE",
    "deliveries": 'match_id VARCHAR, innings_no INTEGER, "over" INTEGER, ball INTEGER, batter_id VARCHAR, bowler_id VARCHAR, runs_batter INTEGER, runs_extras INTEGER, runs_total INTEGER, extras_type VARCHAR, wicket_kind VARCHAR, player_out_id VARCHAR, non_striker_id VARCHAR, wides INTEGER, noballs INTEGER, byes INTEGER, legbyes INTEGER, penalty INTEGER, legal_ball BOOLEAN, batter_ball BOOLEAN, runs_bowler INTEGER, non_boundary BOOLEAN',
    "match_players": "match_id VARCHAR, team VARCHAR, person_id VARCHAR, gender VARCHAR, name VARCHAR",
    "wickets": 'match_id VARCHAR, innings_no INTEGER, "over" INTEGER, ball INTEGER, wicket_no INTEGER, wicket_kind VARCHAR, player_out_id VARCHAR, credited_to_bowler BOOLEAN',
}
BOWLER_WICKETS = {"bowled", "caught", "caught and bowled", "lbw", "stumped", "hit wicket"}
NOT_OUT = {"retired hurt", "obstructing the field (not out)"}


def _inputs(raw_dir: Path):
    for path in sorted(raw_dir.glob("*.zip")):
        with zipfile.ZipFile(path) as archive:
            for name in sorted(archive.namelist()):
                if name.endswith(".json"):
                    yield Path(name).stem, archive.read(name), f"https://cricsheet.org/downloads/{path.name}#{name}"
    for path in sorted(raw_dir.glob("*.json")):
        if path.stem.isdigit():
            yield path.stem, path.read_bytes(), "https://cricsheet.org/downloads/"


def _write_match(match_id: str, data: dict, writers: dict, source_url: str) -> None:
    info = data["info"]
    gender = {"female": "women", "male": "men"}[info["gender"]]
    fmt = {"T20": "T20I", "IT20": "T20I", "T20I": "T20I", "ODI": "ODI"}.get(info["match_type"])
    if info.get("team_type") != "international" or fmt is None:
        raise ValueError("Expected an international T20I or ODI match")
    registry = info["registry"]["people"]
    team1, team2 = info["teams"]
    outcome = info.get("outcome", {})
    margin = outcome.get("by", {})
    result_type = next(iter(margin), outcome.get("result", "unknown"))
    writers["matches"].writerow([
        match_id, gender, fmt, info.get("event", {}).get("name"), str(info.get("season", "")),
        info["dates"][0], team1, team2, info.get("venue"), outcome.get("winner"),
        margin.get(result_type), result_type, info["team_type"], info.get("balls_per_over", 6),
        outcome.get("method"), outcome.get("eliminator", outcome.get("bowl_out")),
        source_url, data["meta"]["data_version"],
    ])
    # Registry contains officials too; derive categories exclusively from actual rosters.
    for team, names in info["players"].items():
        for name in dict.fromkeys(names):
            writers["match_players"].writerow([match_id, team, registry[name], gender, name])
    for innings_no, innings in enumerate(data.get("innings", []), 1):
        penalties = innings.get("penalty_runs", {})
        pre, post = penalties.get("pre", 0), penalties.get("post", 0)
        total, outs, legal = pre + post, 0, 0
        for over in innings.get("overs", []):
            for ball, delivery in enumerate(over["deliveries"], 1):
                runs, extras = delivery["runs"], delivery.get("extras", {})
                if runs["batter"] + runs["extras"] != runs["total"]:
                    raise ValueError("Delivery runs do not reconcile")
                wides, noballs, byes, legbyes, penalty = [extras.get(key, 0) for key in ("wides", "noballs", "byes", "legbyes", "penalty")]
                is_legal = not (wides or noballs)
                wickets = delivery.get("wickets", [])
                first = wickets[0] if wickets else {}
                writers["deliveries"].writerow([
                    match_id, innings_no, over["over"], ball, registry[delivery["batter"]],
                    registry[delivery["bowler"]], runs["batter"], runs["extras"], runs["total"],
                    "|".join(sorted(extras)), first.get("kind"), registry.get(first.get("player_out")),
                    registry[delivery["non_striker"]], wides, noballs, byes, legbyes, penalty,
                    is_legal, not bool(wides), runs["total"] - byes - legbyes - penalty,
                    runs.get("non_boundary", False),
                ])
                for wicket_no, wicket in enumerate(wickets, 1):
                    kind = wicket["kind"]
                    writers["wickets"].writerow([match_id, innings_no, over["over"], ball,
                        wicket_no, kind, registry[wicket["player_out"]], kind in BOWLER_WICKETS])
                    outs += kind not in NOT_OUT
                total += runs["total"]
                legal += is_legal
        target = innings.get("target", {})
        writers["innings"].writerow([
            match_id, innings_no, innings["team"], total, outs, legal,
            innings.get("super_over", False), pre, post, innings.get("declared", False),
            innings.get("forfeited", False), target.get("runs"), target.get("overs"),
        ])


def build_db(raw_dir: Path, db_path: Path = DB_PATH) -> dict[str, int]:
    raw_dir, db_path = Path(raw_dir), Path(db_path)
    if not raw_dir.is_dir():
        raise FileNotFoundError(raw_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="mak-build-", dir=db_path.parent) as temp:
        stage = Path(temp)
        with ExitStack() as stack:
            writers = {}
            for table, schema in SCHEMA.items():
                fh = stack.enter_context((stage / f"{table}.csv").open("w", encoding="utf-8", newline=""))
                writers[table] = csv.writer(fh)
                writers[table].writerow([col.strip().split()[0].strip('"') for col in schema.split(",")])
            seen = {}
            for match_id, payload, source_url in _inputs(raw_dir):
                digest = hashlib.sha256(payload).hexdigest()
                if match_id in seen:
                    if seen[match_id] != digest:
                        raise ValueError(f"Conflicting duplicate match {match_id}")
                    continue
                try:
                    _write_match(match_id, json.loads(payload), writers, source_url)
                except (KeyError, ValueError, TypeError) as exc:
                    raise ValueError(f"Invalid Cricsheet match {match_id}: {exc}") from exc
                seen[match_id] = digest
                if len(seen) % 500 == 0:
                    print(f"Parsed {len(seen)} matches", flush=True)
            if not seen:
                raise ValueError("No Cricsheet matches found; refusing to replace database")
        built = stage / "mak.duckdb"
        with duckdb.connect(str(built)) as conn:
            for table, schema in SCHEMA.items():
                conn.execute(f"CREATE TABLE {table} ({schema})")
                conn.execute(f"INSERT INTO {table} SELECT * FROM read_csv(?, header=true, all_varchar=true)",
                             [str(stage / f"{table}.csv")])
            conn.execute("CREATE UNIQUE INDEX match_identity ON matches(match_id)")
            conn.execute("CREATE INDEX roster_person ON match_players(person_id)")
            conn.execute('CREATE UNIQUE INDEX delivery_identity ON deliveries(match_id, innings_no, "over", ball)')
            counts = {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in SCHEMA}
            conn.execute("CHECKPOINT")
        built.replace(db_path)
    return counts


def coverage(db_path: Path = DB_PATH) -> list[dict]:
    with duckdb.connect(str(db_path), read_only=True) as conn:
        rows = conn.execute("""SELECT gender, match_type, count(*), min(date)::VARCHAR, max(date)::VARCHAR
                               FROM matches GROUP BY gender, match_type ORDER BY gender, match_type""").fetchall()
    return [dict(zip(("gender", "match_type", "matches", "first_date", "last_date"), row)) for row in rows]
