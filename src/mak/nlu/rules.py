"""Rules baseline: lexicon patterns -> labels. OWNER: Jabin.

This is both the deterministic override layer next to the fine-tuned Laya model and the 'rules-only' arm of the
classifier ablation. It never raises and never writes a fact: it only picks categories.
Gender cues are STRONG (explicit, gender_conf = 1.0) or WEAK (trace only, never an override).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

import yaml

from mak import config
from mak.types import Lang, Parse

MAX_CHARS = 20_000
_DEV, _TAM = "ऀ-ॿ", "஀-௿"
_YEAR = r"(?:19|20)\d\d"
_ALL_LANGS: tuple[Lang, ...] = ("en", "hi", "ta")


def normalise(text: str) -> str:
    return unicodedata.normalize("NFC", text or "").replace("’", "'").replace("‘", "'")


def _wrap(pattern: str) -> re.Pattern[str]:
    p = normalise(pattern)
    if re.search(f"[{_DEV}]", p):
        body = f"(?<![{_DEV}])(?:{p})(?![{_DEV}])"
    elif re.search(f"[{_TAM}]", p):
        body = f"(?<![{_TAM}])(?:{p})"
    else:
        body = rf"\b(?:{p})\b"
    return re.compile(body, re.IGNORECASE)


def _compile(patterns: list[str]) -> tuple[re.Pattern[str], ...]:
    return tuple(_wrap(p) for p in patterns)


def _first(patterns: tuple[re.Pattern[str], ...], text: str) -> str | None:
    for pat in patterns:
        m = pat.search(text)
        if m:
            return m.group(0)
    return None


@dataclass(frozen=True)
class _Entry:
    family: str
    stat: str
    groups: tuple[tuple[re.Pattern[str], ...], ...]


@dataclass(frozen=True)
class _Lexicon:
    women_strong: tuple[re.Pattern[str], ...]
    men_strong: tuple[re.Pattern[str], ...]
    women_weak: tuple[re.Pattern[str], ...]
    men_weak: tuple[re.Pattern[str], ...]
    formats: dict[str, tuple[re.Pattern[str], ...]]
    world_cup: tuple[re.Pattern[str], ...]
    cricket: tuple[re.Pattern[str], ...]
    other_sport: tuple[re.Pattern[str], ...]
    stat_question: tuple[re.Pattern[str], ...]
    stats: tuple[_Entry, ...]
    injection: tuple[re.Pattern[str], ...]


def _load_raw(lang: str) -> dict:
    with open(config.LEXICON_DIR / f"{lang}.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _union(raws: list[dict], key: str) -> list[str]:
    return [p for raw in raws for p in raw.get(key, [])]


@lru_cache(maxsize=None)
def _lexicon(langs: tuple[Lang, ...]) -> _Lexicon:
    """Combined lexicon for a query language (its own lexicon first, English always included for code-mixing)."""
    raws = [_load_raw(lg) for lg in langs]
    tokens = {"@world_cup": _union(raws, "world_cup"), "@cricket": _union(raws, "cricket"), "@year": [_YEAR]}
    entries: list[_Entry] = []
    for raw in raws:
        for e in raw.get("stats", []):
            groups = []
            for group in e["all"]:
                expanded: list[str] = []
                for item in group:
                    expanded.extend(tokens.get(item, [item]))
                groups.append(_compile(expanded))
            entries.append(_Entry(e["family"], e["stat"], tuple(groups)))
    formats: dict[str, list[str]] = {}
    for raw in raws:
        for name, pats in raw.get("format", {}).items():
            formats.setdefault(name, []).extend(pats)
    return _Lexicon(
        women_strong=_compile([p for r in raws for p in r["gender"]["women_strong"]]),
        men_strong=_compile([p for r in raws for p in r["gender"]["men_strong"]]),
        women_weak=_compile([p for r in raws for p in r["gender"]["women_weak"]]),
        men_weak=_compile([p for r in raws for p in r["gender"]["men_weak"]]),
        formats={k: _compile(v) for k, v in formats.items()},
        world_cup=_compile(tokens["@world_cup"]),
        cricket=_compile(tokens["@cricket"]),
        other_sport=_compile(_union(raws, "other_sport")),
        stat_question=_compile(_union(raws, "stat_question")),
        stats=tuple(entries),
        injection=_compile(_union(raws, "injection")),
    )


def _search_all(langs: tuple[Lang, ...] | None = None) -> _Lexicon:
    return _lexicon(langs or _ALL_LANGS)


def detect_injection(text: str) -> bool:
    """True when the text looks like it is trying to instruct the system (any supported language)."""
    t = normalise(text)[:MAX_CHARS]
    return _first(_search_all().injection, t) is not None


def _lexicon_for(lang: Lang) -> _Lexicon:
    return _lexicon((lang,) if lang == "en" else (lang, "en"))


def rules_parse(text: str, lang: Lang) -> Parse:
    """Parse a question with lexicon rules only. gender_conf is 1.0 when an explicit cue fired, else 0.0."""
    t = normalise(text)[:MAX_CHARS]
    lex = _lexicon_for(lang)
    trace: list[str] = [f"rules: lang={lang}"]

    injection = _first(_search_all().injection, t)
    if injection:
        trace.append(f"injection marker: {injection!r}; user text treated as data, gender cues ignored (fail-safe)")

    w_strong, m_strong = _first(lex.women_strong, t), _first(lex.men_strong, t)
    for label, cue in (("women", _first(lex.women_weak, t)), ("men", _first(lex.men_weak, t))):
        if cue:
            trace.append(f"weak cue: {cue} (hints {label}, never an override)")
    if injection:
        signal, conf = "none", 0.0
    elif w_strong and m_strong:
        signal, conf = "both_named", 1.0
        trace.append(f"gender: both named ({w_strong!r}, {m_strong!r})")
    elif w_strong:
        signal, conf = "women", 1.0
        trace.append(f"gender: women cue {w_strong!r}")
    elif m_strong:
        signal, conf = "men", 1.0
        trace.append(f"gender: men cue {m_strong!r}")
    else:
        signal, conf = "none", 0.0
        trace.append("gender: no explicit cue")

    cricket = _first(lex.cricket, t) is not None
    other = _first(lex.other_sport, t) is not None
    stat_q = _first(lex.stat_question, t) is not None
    wc = _first(lex.world_cup, t) is not None

    league = _first(lex.formats.get("league", ()), t)
    matched = [f for f in ("T20I", "ODI", "Test") if _first(lex.formats.get(f, ()), t)]
    if league:
        fmt = "league"
    elif len(matched) == 1:
        fmt = matched[0]
        if wc and fmt in ("T20I", "ODI"):
            fmt = "T20_WC" if fmt == "T20I" else "ODI_WC"
    else:
        fmt = "unspecified"
        if len(matched) > 1:
            trace.append(f"format: several formats named {matched}; left unspecified")

    family = stat = None
    if other and not cricket:
        topic = "other_sport_stat" if stat_q else "non_sport"
    else:
        for entry in lex.stats:
            if all(_first(group, t) for group in entry.groups):
                family, stat = entry.family, entry.stat
                break
        if family:
            topic = "cricket_stat"
        elif cricket and stat_q:
            topic, family, stat = "cricket_stat", "other_stat", "other"
        elif cricket:
            topic = "cricket_general"
        else:
            topic = "non_sport"
    if topic == "cricket_stat":
        trace.append(f"topic: cricket_stat {family}/{stat}, format {fmt}")
    else:
        trace.append(f"topic: {topic}")

    return Parse(lang=lang, gender_signal=signal, gender_conf=conf, topic=topic, family=family, stat=stat,
                 format=fmt if topic == "cricket_stat" else None, injection_suspected=bool(injection),
                 trace=tuple(trace))
