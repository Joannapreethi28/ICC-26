"""Conservative registry lookup; ambiguous names never supply a gender override.

The plan explicitly requires Kohli/Mandhana shorthand. Those two reviewed aliases
are tied to source IDs. Every other surname-only match keeps gender=None, even
when our incomplete international-match snapshot currently contains one player.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import json
from pathlib import Path
import unicodedata

from rapidfuzz import fuzz, process

from mak.config import DATA
from mak.registry.people import read_csv
from mak.types import Entity

# Explicit product examples; IDs from Cricsheet Register.
_REVIEWED_SHORT_NAMES = {"kohli": "253802", "mandhana": "597806"}


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text).casefold()
    return " ".join("".join(c if unicodedata.category(c)[0] in "LMN" else " " for c in text).split())


@lru_cache(maxsize=4)
def _load(directory: str, people_version: int, teams_version: int):
    path = Path(directory)
    entries, aliases, surnames = {}, defaultdict(set), defaultdict(set)
    for row in read_csv(path / "people.csv"):
        # Officials and players absent from our rosters cannot create a category override.
        if int(row.get("match_count") or 0) == 0:
            continue
        pid = row["person_id"]
        gender = row.get("gender") if row.get("gender") in {"women", "men"} else None
        entries[pid] = (row.get("label_en") or row["name"], "player", gender)
        names = set(json.loads(row.get("aliases") or "[]")) | {row["name"]}
        for name in names:
            normal = _normalise(name)
            if not normal:
                continue
            tokens = normal.split()
            if len(tokens) > 1:
                aliases[normal].add(pid)
                surnames[tokens[-1]].add(pid)
            else:
                surnames[normal].add(pid)
        for alias, cricinfo in _REVIEWED_SHORT_NAMES.items():
            if row.get("cricinfo_id") == cricinfo:
                aliases[alias].add(pid)
    teams_path = path / "teams_i18n.csv"
    if teams_path.exists():
        for row in read_csv(teams_path):
            key = "team:" + row["team"]
            # A country query is neutral regardless of coverage of this database snapshot.
            entries[key] = (row["team"], "team", None)
            for name in (row["team"], row.get("label_hi"), row.get("label_ta")):
                if name:
                    aliases[_normalise(name)].add(key)
    by_length = defaultdict(list)
    for alias in aliases:
        if len(alias.split()) > 1 and len(alias) >= 7:
            by_length[len(alias.split())].append(alias)
    return entries, aliases, surnames, by_length


def resolve_entities(text: str, *, registry_dir: Path = DATA / "registry") -> tuple[Entity, ...]:
    if not isinstance(text, str) or not text.strip():
        return ()
    registry_dir = Path(registry_dir)
    people_path, teams_path = registry_dir / "people.csv", registry_dir / "teams_i18n.csv"
    if not people_path.exists():
        return ()
    entries, aliases, surnames, by_length = _load(
        str(registry_dir.resolve()), people_path.stat().st_mtime_ns,
        teams_path.stat().st_mtime_ns if teams_path.exists() else 0,
    )
    tokens = _normalise(text[:5000]).split()[:128]
    hits = []
    for start in range(len(tokens)):
        for size in range(1, min(6, len(tokens) - start) + 1):
            phrase = " ".join(tokens[start:start + size])
            if phrase in aliases:
                hits.append((start, start + size, 100.0, phrase, aliases[phrase]))
            elif size >= 2 and len(phrase) >= 7:
                # Equal token counts AND character similarity prevent token_set_ratio's
                # substring=100 behaviour from turning a surname into a full-name match.
                candidates = process.extract(phrase, by_length[size], scorer=fuzz.ratio, score_cutoff=90, limit=2)
                if candidates and (len(candidates) == 1 or candidates[0][1] > candidates[1][1] + 3):
                    alias, score, _ = candidates[0]
                    if fuzz.token_set_ratio(phrase, alias) >= 90:
                        hits.append((start, start + size, score, phrase, aliases[alias]))
    occupied, found, seen = set(), [], set()
    # Prefer exact matches, then longest names, before considering overlaps.
    for start, end, score, phrase, ids in sorted(hits, key=lambda h: (-h[2], -(h[1] - h[0]), h[0])):
        positions = set(range(start, end))
        if positions & occupied:
            continue
        occupied |= positions
        if len(ids) != 1:
            found.append((start, Entity("ambiguous:" + phrase, phrase, "player", None, score)))
            continue
        pid = next(iter(ids))
        if pid in seen:
            continue
        seen.add(pid)
        name, kind, gender = entries[pid]
        found.append((start, Entity(pid.removeprefix("team:"), name, kind, gender, score)))
    for index, token in enumerate(tokens):
        if index not in occupied and token in surnames and len(token) >= 3:
            key = "ambiguous:" + token
            if key not in seen:
                seen.add(key)
                found.append((index, Entity(key, token, "player", None, 100.0)))
    return tuple(entity for _, entity in sorted(found, key=lambda pair: pair[0]))
