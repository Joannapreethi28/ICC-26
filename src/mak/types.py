"""Shared data types for Make AI Know Her. SHARED CONTRACT: change only with a CONTRACT CHANGE message in document/handoffs.md."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Lang = Literal["en", "hi", "ta"]
Gender = Literal["women", "men"]
GenderSignal = Literal["women", "men", "both_named", "none"]
Topic = Literal["cricket_stat", "cricket_general", "other_sport_stat", "non_sport"]
Family = Literal["career_record", "world_cup_record", "firsts_history", "team_record",
                 "player_stat", "recent_result", "role_or_ranking", "other_stat"]
Format = Literal["T20I", "ODI", "Test", "T20_WC", "ODI_WC", "league", "unspecified"]
Decision = Literal["ambiguous_both", "explicit_women", "explicit_men", "both_named",
                   "no_intervention", "unsupported"]
Trust = Literal["verified", "computed"]
Leader = Literal["women", "men", "none"]


@dataclass(frozen=True)
class Entity:
    entity_id: str            # Cricsheet identifier or team name
    name: str
    kind: Literal["player", "team"]
    gender: Gender | None     # None = ambiguous (surname-only, shared team name)
    score: float              # fuzzy-match score 0-100


@dataclass(frozen=True)
class Parse:
    lang: Lang
    gender_signal: GenderSignal
    gender_conf: float                    # 0-1 after calibration; rules override = 1.0
    topic: Topic
    family: Family | None
    stat: str | None
    format: Format | None
    entities: tuple[Entity, ...] = ()
    injection_suspected: bool = False
    trace: tuple[str, ...] = ()


@dataclass(frozen=True)
class Fact:
    intent_id: str
    gender: Gender
    format: str
    holder: str
    holder_local: str | None              # hi/ta label when lang != en
    country: str | None
    value: str
    unit: str
    context: str
    as_of: str                            # ISO date (or year for old records)
    trust: Trust
    sources: tuple[str, ...]
    ids: dict[str, str] = field(default_factory=dict)   # cricsheet, cricinfo, pulse, wikidata
    computed_delta: str | None = None


@dataclass
class Resolution:
    decision: Decision
    language: Lang
    sport: str
    intent: str | None
    format: str | None
    gender_relevant: bool
    trace: list[str]
    confidence: dict[str, float]
    fallback: str | None
    results: list[Fact]
    overall_leader: Leader
    answer_text: str
    latency_ms: float
