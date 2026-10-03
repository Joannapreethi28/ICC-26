"""Explicit Wikidata identifiers and native labels, with a resumable CSV cache.

Missing translations are left blank; consumers fall back to English. This module
does not translate names, infer sex from names, or use P21 for match categories.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
import time

import duckdb
import requests

from mak.config import DB_PATH, I18N_DIR
from mak.records.golden import golden_index
from mak.registry.people import read_csv, write_csv

ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "MakeAIKnowHer/0.1 (https://github.com/Joannapreethi28/ICC-26)"
PREFIX = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""
LABELS = """OPTIONAL { ?item rdfs:label ?en FILTER(LANG(?en) = "en") }
OPTIONAL { ?item rdfs:label ?hi FILTER(LANG(?hi) = "hi") }
OPTIONAL { ?item rdfs:label ?ta FILTER(LANG(?ta) = "ta") }
"""
FIELDS = ("cricinfo_id", "qid", "P21", "en", "hi", "ta", "status", "source", "fetched_at")
LOG = logging.getLogger(__name__)


def _query(query: str, session, attempts: int) -> list[dict]:
    for attempt in range(attempts):
        try:
            response = session.get(ENDPOINT, params={"query": PREFIX + query, "format": "json"},
                                   headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"},
                                   timeout=45)
            response.raise_for_status()
            return response.json()["results"]["bindings"]
        except requests.RequestException:
            if attempt + 1 == attempts:
                raise
            time.sleep(2 ** attempt)
    raise ValueError("attempts must be positive")


def _value(row: dict, key: str) -> str:
    return row.get(key, {}).get("value", "")


def fetch_labels(cricinfo_ids: list[str], *, cache_path: Path = I18N_DIR / "wikidata_players.csv",
                 session=None, attempts: int = 3) -> dict[str, dict]:
    ids = sorted(set(str(value) for value in cricinfo_ids))
    if any(not re.fullmatch(r"\d+", value) for value in ids):
        raise ValueError("ESPNcricinfo identifiers must be numeric strings")
    cache = {r["cricinfo_id"]: r for r in read_csv(cache_path)} if cache_path.exists() else {}
    pending = [value for value in ids if value not in cache]
    session = session or requests.Session()
    for start in range(0, len(pending), 200):
        batch = pending[start:start + 200]
        values = " ".join(json.dumps(value) for value in batch)
        query = "SELECT ?id ?item ?sex ?en ?hi ?ta WHERE { VALUES ?id { " + values + " } "
        query += "?item wdt:P2697 ?id. OPTIONAL { ?item wdt:P21 ?sex } " + LABELS + " }"
        bindings = _query(query, session, attempts)
        grouped = defaultdict(list)
        for row in bindings:
            grouped[_value(row, "id")].append(row)
        for value in batch:
            hits = grouped[value]
            qids = {_value(row, "item").rsplit("/", 1)[-1] for row in hits}
            status = "found" if len(qids) == 1 else "missing" if not qids else "ambiguous"
            qid = next(iter(qids)) if status == "found" else ""
            row = {"cricinfo_id": value, "qid": qid, "P21": "", "en": "", "hi": "", "ta": "",
                   "status": status, "source": f"https://www.wikidata.org/wiki/{qid}" if qid else ENDPOINT,
                   "fetched_at": datetime.now(timezone.utc).isoformat()}
            if status == "found":
                for lang in ("en", "hi", "ta"):
                    labels = {_value(hit, lang) for hit in hits} - {""}
                    if len(labels) == 1:
                        row[lang] = next(iter(labels))
                row["P21"] = "|".join(sorted({_value(hit, "sex").rsplit("/", 1)[-1] for hit in hits} - {""}))
            cache[value] = row
        write_csv(cache_path, [cache[key] for key in sorted(cache)], FIELDS)
        print(f"Wikidata players: checked {min(start + 200, len(pending))}/{len(pending)} new IDs", flush=True)
    return {value: cache[value] for value in ids}


def fetch_team_labels(teams: list[str], cache_path: Path = I18N_DIR / "wikidata_teams.csv", *, session=None) -> dict:
    fields = ("team", "qid", "hi", "ta", "status", "source", "fetched_at")
    cache = {r["team"]: r for r in read_csv(cache_path)} if cache_path.exists() else {}
    pending = sorted(set(teams) - cache.keys())
    session = session or requests.Session()
    for start in range(0, len(pending), 50):
        batch = pending[start:start + 50]
        values = " ".join(f"({json.dumps(team)} {json.dumps(team)}@en)" for team in batch)
        query = "SELECT DISTINCT ?requested ?item ?hi ?ta WHERE { VALUES (?requested ?name) { " + values + " } "
        query += "?item (rdfs:label|skos:altLabel) ?name . ?item wdt:P31/wdt:P279* wd:Q6256 . " + LABELS + " }"
        grouped = defaultdict(list)
        for row in _query(query, session, 3):
            grouped[_value(row, "requested")].append(row)
        for team in batch:
            hits = grouped[team]
            qids = {_value(hit, "item").rsplit("/", 1)[-1] for hit in hits}
            qid = next(iter(qids)) if len(qids) == 1 else ""
            row = dict.fromkeys(fields, "")
            row.update(team=team, qid=qid, status="found" if qid else "missing" if not qids else "ambiguous",
                       source=f"https://www.wikidata.org/wiki/{qid}" if qid else ENDPOINT,
                       fetched_at=datetime.now(timezone.utc).isoformat())
            if qid:
                for lang in ("hi", "ta"):
                    labels = {_value(hit, lang) for hit in hits} - {""}
                    row[lang] = next(iter(labels)) if len(labels) == 1 else ""
            cache[team] = row
        write_csv(cache_path, [cache[key] for key in sorted(cache)], fields)
        print(f"Wikidata teams: checked {min(start + 50, len(pending))}/{len(pending)} new names", flush=True)
    return {team: cache[team] for team in teams}


def fetch_golden_ids(holders: list[str], cache_path: Path = I18N_DIR / "golden_players.csv", *, session=None) -> dict:
    """Try every full golden-holder name, including players outside Cricsheet coverage.

    Name lookup only chooses candidates for P2697 fetching. Ambiguous identity matches
    are rejected; no match-derived category is assigned to a missing registry entry.
    """
    fields = ("holder", "cricinfo_id", "qid", "status", "source", "fetched_at")
    cache = {r["holder"]: r for r in read_csv(cache_path)} if cache_path.exists() else {}
    pending = sorted(set(holders) - cache.keys())
    if pending:
        values = " ".join(f"({json.dumps(name)} {json.dumps(name)}@en)" for name in pending)
        query = "SELECT DISTINCT ?requested ?item ?id WHERE { VALUES (?requested ?name) { " + values + " } "
        query += "?item (rdfs:label|skos:altLabel) ?name . ?item wdt:P2697 ?id . }"
        grouped = defaultdict(list)
        for hit in _query(query, session or requests.Session(), 3):
            grouped[_value(hit, "requested")].append(hit)
        for name in pending:
            pairs = {(_value(hit, "id"), _value(hit, "item").rsplit("/", 1)[-1]) for hit in grouped[name]}
            cricinfo, qid = next(iter(pairs)) if len(pairs) == 1 else ("", "")
            cache[name] = {"holder": name, "cricinfo_id": cricinfo, "qid": qid,
                           "status": "found" if qid else "missing" if not pairs else "ambiguous",
                           "source": f"https://www.wikidata.org/wiki/{qid}" if qid else ENDPOINT,
                           "fetched_at": datetime.now(timezone.utc).isoformat()}
        write_csv(cache_path, [cache[name] for name in sorted(cache)], fields)
    return {name: cache[name] for name in holders}


def populate_labels(db_path: Path = DB_PATH, output_dir: Path = I18N_DIR) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path), read_only=True) as conn:
        people = conn.execute("SELECT person_id, name, aliases, cricinfo_id FROM people").fetchall()
        ranked = conn.execute("""SELECT cricinfo_id FROM people WHERE gender IS NOT NULL AND cricinfo_id IS NOT NULL
            QUALIFY row_number() OVER (PARTITION BY gender ORDER BY match_count DESC, person_id) <= 500""").fetchall()
        teams = [r[0] for r in conn.execute("SELECT DISTINCT team FROM teams_i18n ORDER BY team").fetchall()]
    ids = {r[0] for r in ranked}
    holder_names = sorted({fact.holder for fact in golden_index().values() if fact.country})
    golden_ids = fetch_golden_ids(holder_names, output_dir / "golden_players.csv")
    ids.update(row["cricinfo_id"] for row in golden_ids.values() if row["cricinfo_id"])
    holders = {name.casefold() for name in holder_names}
    registry_candidates = defaultdict(set)
    for _, name, aliases, cricinfo in people:
        hits = ({name.casefold()} | {alias.casefold() for alias in json.loads(aliases)}) & holders
        if hits and cricinfo:
            ids.add(cricinfo)
            for holder in hits:
                registry_candidates[holder].add(cricinfo)
    labels = fetch_labels(sorted(ids), cache_path=output_dir / "wikidata_players.csv")
    # The name-based query may be missing an English label while the Register has
    # a unique full alias. Preserve the original query cache; reconcile separately.
    reconciled = {}
    for holder, identity in golden_ids.items():
        candidates = registry_candidates[holder.casefold()]
        if identity["status"] == "found":
            reconciled[holder] = identity
        elif len(candidates) == 1:
            cricinfo = next(iter(candidates))
            label = labels[cricinfo]
            reconciled[holder] = {**identity, "cricinfo_id": cricinfo, "qid": label["qid"],
                                  "status": "found", "source": "https://cricsheet.org/register/"}
        else:
            reconciled[holder] = identity
    team_labels = fetch_team_labels(teams, cache_path=output_dir / "wikidata_teams.csv")
    exports = {lang: [] for lang in ("hi", "ta")}
    exported_ids = set()
    with duckdb.connect(str(db_path)) as conn:
        conn.execute("BEGIN")
        try:
            for pid, name, aliases, cricinfo in people:
                label = labels.get(cricinfo)
                if not label:
                    continue
                exported_ids.add(cricinfo)
                names = set(json.loads(aliases)) | {label[key] for key in ("en", "hi", "ta") if label.get(key)}
                conn.execute("""UPDATE people SET wikidata_qid=?, label_hi=?, label_ta=?, label_en=?, aliases=? WHERE person_id=?""",
                             [label["qid"] or None, label["hi"] or None, label["ta"] or None,
                              label["en"] or None, json.dumps(sorted(names), ensure_ascii=False), pid])
                for lang in exports:
                    exports[lang].append({"entity_id": pid, "kind": "player", "name": label["en"] or name,
                        "label": label[lang] or label["en"] or name, "fallback": not bool(label[lang]),
                        "wikidata_qid": label["qid"], "source": label["source"], "fetched_at": label["fetched_at"]})
            for team, label in team_labels.items():
                conn.execute("UPDATE teams_i18n SET label_hi=?, label_ta=?, wikidata_qid=? WHERE team=?",
                             [label["hi"] or None, label["ta"] or None, label["qid"] or None, team])
                for lang in exports:
                    exports[lang].append({"entity_id": team, "kind": "team", "name": team,
                        "label": label[lang] or team, "fallback": not bool(label[lang]), "wikidata_qid": label["qid"],
                        "source": label["source"], "fetched_at": label["fetched_at"]})
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    for holder, identity in reconciled.items():
        cricinfo = identity["cricinfo_id"]
        if cricinfo and cricinfo in exported_ids:
            continue
        if not cricinfo and registry_candidates[holder.casefold()]:
            # Existing homonyms are already exported with their distinct IDs. An
            # extra same-name row would obscure those identities in downstream joins.
            continue
        label = labels.get(cricinfo, {})
        for lang in exports:
            exports[lang].append({"entity_id": "cricinfo:" + cricinfo if cricinfo else "golden:" + holder,
                "kind": "player", "name": holder, "label": label.get(lang) or holder,
                "fallback": not bool(label.get(lang)), "wikidata_qid": label.get("qid", ""),
                "source": label.get("source") or identity["source"],
                "fetched_at": label.get("fetched_at") or identity["fetched_at"]})
    fields = ("entity_id", "kind", "name", "label", "fallback", "wikidata_qid", "source", "fetched_at")
    for lang, rows in exports.items():
        write_csv(output_dir / f"entities_{lang}.csv", rows, fields)
    report = {"requested_player_ids": len(ids),
              "golden_holders_requested": len(holder_names),
              "golden_holders_not_mapped": sorted(name for name, row in reconciled.items() if row["status"] != "found"),
              "golden_holders_without_wikidata": sorted(name for name, row in reconciled.items() if not row["qid"]),
              "players_found": sum(row["status"] == "found" for row in labels.values()),
              "teams_requested": len(teams),
              "labels": {lang: {"native": sum(not r["fallback"] for r in rows),
                                "english_fallback": sum(r["fallback"] for r in rows),
                                "teams_native": sum(r["kind"] == "team" and not r["fallback"] for r in rows)}
                         for lang, rows in exports.items()}}
    (output_dir / "coverage.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LOG.info("Label coverage: %s", report)
    return report


if __name__ == "__main__":
    import argparse
    from mak.registry.people import export_registry
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", type=Path, default=DB_PATH)
    args = parser.parse_args()
    print(json.dumps(populate_labels(args.db_path), indent=2, ensure_ascii=False))
    export_registry(args.db_path)
