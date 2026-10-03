"""Player identities and competition categories derived from match rosters.

Wikidata P21 is never used to guess a competition category. Missing or conflicting
roster evidence stays NULL. Cricsheet IDs remain strings, including leading zeroes.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import json
import logging
from pathlib import Path

import duckdb
import pandas as pd

from mak.config import DATA, DB_PATH, I18N_DIR
from mak.types import Gender

LOG = logging.getLogger(__name__)
PEOPLE_COLUMNS = ("person_id", "name", "unique_name", "gender", "cricinfo_id", "pulse_id", "opta_id",
                  "wikidata_qid", "label_hi", "label_ta", "aliases", "label_en", "match_count")


def read_csv(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict], fields: tuple | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    with partial.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    partial.replace(path)


def derive_gender(person_id: str, db_path: Path = DB_PATH) -> Gender | None:
    with duckdb.connect(str(db_path), read_only=True) as conn:
        genders = {r[0] for r in conn.execute("SELECT DISTINCT gender FROM match_players WHERE person_id=?", [person_id]).fetchall()}
    return next(iter(genders)) if len(genders) == 1 and genders <= {"women", "men"} else None


def build_registry(raw_dir: Path, db_path: Path = DB_PATH, *, cache_path: Path | None = None) -> dict[str, int]:
    labels_path = cache_path or I18N_DIR / "wikidata_players.csv"
    labels = {r["cricinfo_id"]: r for r in read_csv(labels_path)} if labels_path.exists() else {}
    aliases = defaultdict(set)
    for row in read_csv(Path(raw_dir) / "names.csv"):
        aliases[row["identifier"]].add(row["name"])
    raw_people = read_csv(Path(raw_dir) / "people.csv")
    with duckdb.connect(str(db_path)) as conn:
        rosters = conn.execute("SELECT person_id, list(DISTINCT gender), count(DISTINCT match_id) FROM match_players GROUP BY person_id").fetchall()
        categories = {pid: (gender[0] if len(gender) == 1 else None, count) for pid, gender, count in rosters}
        for pid, gender, _ in rosters:
            if len(gender) > 1:
                LOG.warning("Conflicting competition categories for %s: %s", pid, gender)
        rows, seen = [], set()
        for person in raw_people:
            pid = person["identifier"]
            if not pid or pid in seen:
                raise ValueError(f"Missing or duplicate person identifier: {pid}")
            seen.add(pid)
            cricinfo = person.get("key_cricinfo") or None
            label = labels.get(cricinfo, {})
            if label.get("status") not in (None, "found"):
                label = {}
            names = aliases[pid] | {person["name"], person["unique_name"]}
            names.update(label[key] for key in ("en", "hi", "ta") if label.get(key))
            gender, count = categories.get(pid, (None, 0))
            rows.append(dict(zip(PEOPLE_COLUMNS, (
                pid, person["name"], person["unique_name"], gender, cricinfo,
                person.get("key_pulse") or None, person.get("key_opta") or None,
                label.get("qid") or None, label.get("hi") or None, label.get("ta") or None,
                json.dumps(sorted(names), ensure_ascii=False), label.get("en") or None, count,
            ))))
        missing = set(categories) - seen
        if missing:
            raise ValueError(f"Roster IDs missing from people.csv: {sorted(missing)[:10]}")
        frame = pd.DataFrame(rows, columns=PEOPLE_COLUMNS)
        conn.register("registry_rows", frame)
        conn.execute("BEGIN")
        try:
            conn.execute("""CREATE OR REPLACE TABLE people (
                person_id VARCHAR PRIMARY KEY, name VARCHAR, unique_name VARCHAR, gender VARCHAR,
                cricinfo_id VARCHAR, pulse_id VARCHAR, opta_id VARCHAR, wikidata_qid VARCHAR,
                label_hi VARCHAR, label_ta VARCHAR, aliases VARCHAR, label_en VARCHAR, match_count INTEGER)""")
            conn.execute("INSERT INTO people SELECT * FROM registry_rows")
            conn.execute("""CREATE OR REPLACE TABLE teams_i18n AS
                SELECT DISTINCT team, gender, NULL::VARCHAR label_hi, NULL::VARCHAR label_ta,
                                NULL::VARCHAR wikidata_qid
                FROM match_players ORDER BY team, gender""")
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        teams = conn.execute("SELECT count(*) FROM teams_i18n").fetchone()[0]
    return {"people": len(rows), "teams_i18n": teams}


def export_registry(db_path: Path = DB_PATH, output_dir: Path = DATA / "registry") -> dict[str, int]:
    counts = {}
    with duckdb.connect(str(db_path), read_only=True) as conn:
        for table, order in (("people", "person_id"), ("teams_i18n", "team, gender")):
            result = conn.execute(f"SELECT * FROM {table} ORDER BY {order}")
            fields = [col[0] for col in result.description]
            rows = [dict(zip(fields, row)) for row in result.fetchall()]
            write_csv(Path(output_dir) / f"{table}.csv", rows, fields)
            counts[table] = len(rows)
    return counts
