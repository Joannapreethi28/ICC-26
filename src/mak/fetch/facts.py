"""Golden-first retrieval and offline identity labels; no model or network."""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
import json
from pathlib import Path

from mak.config import DATA, DB_PATH, GOLDEN_PATH
from mak.records.compute import compute, compute_entity
from mak.records.golden import golden_index
from mak.registry.people import read_csv
from mak.types import Entity, Fact, Gender, Lang


@lru_cache(maxsize=2)
def _golden(path, version):
    return golden_index(Path(path))


@lru_cache(maxsize=4)
def _identities(directory, versions):
    root = Path(directory)
    people, labels = {}, {}
    people_path = root / 'registry/people.csv'
    if people_path.exists():
        for row in read_csv(people_path):
            names = set(json.loads(row.get('aliases') or '[]')) | {row['name'], row.get('label_en', '')}
            for name in names:
                if name:
                    people.setdefault(name.casefold(), []).append(row)
    for lang in ('hi', 'ta'):
        path = root / f'i18n/entities_{lang}.csv'
        if path.exists():
            for row in read_csv(path):
                labels.setdefault((lang, row['name'].casefold()), []).append(row)
    return people, labels


def localize(fact: Fact, lang: Lang) -> Fact:
    if lang not in ('en', 'hi', 'ta'):
        raise ValueError(f'Unsupported language: {lang}')
    paths = [DATA / 'registry/people.csv', DATA / 'i18n/entities_hi.csv', DATA / 'i18n/entities_ta.csv']
    versions = tuple(p.stat().st_mtime_ns if p.exists() else 0 for p in paths)
    people, labels = _identities(str(DATA), versions)
    ids, local = dict(fact.ids), None
    candidates = people.get(fact.holder.casefold(), [])
    if ids.get('cricsheet'):
        candidates = [r for r in candidates if r['person_id'] == ids['cricsheet']]
    else:
        candidates = [r for r in candidates if not r.get('gender') or r['gender'] == fact.gender]
    # Full-name collisions remain unresolved; never attach another person's IDs.
    unique = {r['person_id']: r for r in candidates}
    if len(unique) == 1:
        row = next(iter(unique.values()))
        ids['cricsheet'] = row['person_id']
        for key, column in (('cricinfo', 'cricinfo_id'), ('pulse', 'pulse_id'), ('wikidata', 'wikidata_qid')):
            if row.get(column):
                ids[key] = row[column]
        if lang != 'en':
            local = row.get(f'label_{lang}') or None
    if lang != 'en' and not local:
        candidates = labels.get((lang, fact.holder.casefold()), [])
        values = {r['label'] for r in candidates if r.get('fallback', '').casefold() == 'false'}
        if len(values) == 1:
            local = next(iter(values))
    return replace(fact, holder_local=local, ids=ids)


def get_facts(intent_id: str, genders: tuple[Gender, ...], lang: Lang = 'en', *,
              entity: Entity | None = None, db_path: Path = DB_PATH) -> list[Fact]:
    """Golden values win; entity intents require one unambiguous resolved entity.

    K-P4 may call once per named player. Empty results mean missing coverage,
    not permission to substitute a headline or guess an identity.
    """
    if lang not in ('en', 'hi', 'ta'):
        raise ValueError(f'Unsupported language: {lang}')
    index = _golden(str(GOLDEN_PATH), GOLDEN_PATH.stat().st_mtime_ns)
    results = []
    for gender in dict.fromkeys(genders):
        if gender not in ('women', 'men'):
            raise ValueError(f'Unsupported category: {gender}')
        if intent_id.endswith(('_PLAYER_LINE', '_LAST_RESULT')):
            fact = compute_entity(intent_id, gender, entity, db_path=db_path) if entity else None
        else:
            golden = index.get((intent_id, gender))
            computed = compute(intent_id, gender, db_path=db_path)
            fact = golden or computed
            if golden and computed and (golden.value != computed.value or golden.holder != computed.holder):
                fact = replace(golden, computed_delta=(
                    f'Covered-data record: {computed.holder}, {computed.value}; through {computed.as_of}. '
                    'Values or holder names differ; verified headline retained.'
                ))
        if fact:
            results.append(localize(fact, lang))
    return results
