"""Load the team's reviewed snapshot, preserving values, dates and source URLs.

V1 and V2 are the team's existing verification tiers, not a claim that this
loader independently rechecked the web. audit_golden exposes evidence caveats.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
import re
from urllib.parse import urlsplit
import warnings

from mak.config import GOLDEN_PATH
from mak.records.leader import KIND
from mak.types import Fact, Leader

_REQUIRED = {"intent_id", "gender", "format", "holder", "value", "context", "as_of",
             "source_1", "source_2", "verification", "overall_leader"}
_UNITS = {"RUNS": "runs", "WKTS": "wickets", "HS": "score", "TEAM": "total",
          "BBI": "figures", "MATCHES": "matches", "100S": "centuries", "TITLES": "titles"}


def _sources(row: dict) -> tuple[str, ...]:
    # A space introduces the team's source annotation; URLs themselves are encoded.
    urls = [row[key].strip().split(" ", 1)[0] for key in ("source_1", "source_2") if row[key].strip()]
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Invalid source URL: {url!r}")
    return tuple(dict.fromkeys(urls))


def _rows(path: Path):
    with Path(path).open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = _REQUIRED - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing golden columns: {sorted(missing)}")
        yield from enumerate(reader, 2)


def _load(path: Path) -> tuple[list[Fact], dict[str, Leader]]:
    facts, leaders, seen = [], {}, set()
    for line, row in _rows(path):
        try:
            if not re.match(r"^V[12](?:\s|$)", row["verification"] or ""):
                warnings.warn(f"Skipping unverified golden row {line}: {row['intent_id']}", stacklevel=3)
                continue
            for key in ("intent_id", "gender", "format", "holder", "value", "as_of", "source_1"):
                if not row.get(key, "").strip():
                    raise ValueError(f"Missing {key}")
            intent, gender = row["intent_id"], row["gender"]
            if intent not in KIND or gender not in {"women", "men"}:
                raise ValueError("Unknown intent or gender")
            key = intent, gender
            if key in seen:
                raise ValueError(f"duplicate key {key}")
            as_of = row["as_of"]
            if re.fullmatch(r"\d{4}", as_of):
                date(int(as_of), 1, 1)
            elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of):
                date.fromisoformat(as_of)
            else:
                raise ValueError("as_of must be an ISO date or year")
            leader = row["overall_leader"]
            if leader not in {"women", "men", "none"} or (intent in leaders and leaders[intent] != leader):
                raise ValueError("Invalid or inconsistent overall_leader")
            holder, country = row["holder"], None
            match = re.fullmatch(r"(.+) \(([^()]+)\)", holder)
            if match and "title" not in match[2].casefold():
                holder, country = match[1], match[2]
            sources = _sources(row)
            facts.append(Fact(
                intent_id=intent, gender=gender, format=row["format"], holder=holder,
                holder_local=None, country=country, value=row["value"],
                unit="score" if intent == "FIRST_ODI_200" else _UNITS.get(intent.rsplit("_", 1)[-1], "year"),
                context=row["context"], as_of=as_of, trust="verified", sources=sources,
            ))
            seen.add(key)
            leaders[intent] = leader
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError(f"{path}: row {line}: {exc}") from exc
    return facts, leaders


def load_golden(path: Path = GOLDEN_PATH) -> list[Fact]:
    return _load(path)[0]


def golden_index(path: Path = GOLDEN_PATH) -> dict[tuple[str, str], Fact]:
    return {(fact.intent_id, fact.gender): fact for fact in load_golden(path)}


def audit_golden(path: Path = GOLDEN_PATH) -> list[dict[str, str]]:
    issues = []
    for _, row in _rows(path):
        count = len(_sources(row))
        issue = None
        if row["verification"].startswith("V2") and count < 2:
            issue = "V2 has fewer than two distinct URLs"
        elif row["verification"].startswith("V1"):
            issue = "Single-source record; recheck before demo"
        if issue:
            issues.append({"intent_id": row["intent_id"], "gender": row["gender"], "issue": issue})
    return issues


GOLDEN_LEADER: dict[str, Leader] = _load(GOLDEN_PATH)[1]
