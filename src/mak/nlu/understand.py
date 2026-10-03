"""Question -> labels. OWNER: Jabin.

PHASE 0 STUB: a tiny English keyword parser so Joanna's pipeline can be built and tested now.
Jabin replaces the body in J-P1 (rules) and J-P4 (Laya). The signature below is FIXED.
"""
from __future__ import annotations

import re

from mak.types import Lang, Parse

_STAT_WORDS = {
    "runs": ("career_record", "runs"),
    "wickets": ("career_record", "wickets"),
    "highest score": ("career_record", "highest_score"),
    "team total": ("career_record", "team_total"),
    "best bowling": ("career_record", "best_bowling"),
    "matches": ("career_record", "matches"),
    "centuries": ("career_record", "centuries"),
}
_CRICKET_GENERAL = ("pitch", "lbw", "powerplay", "how many players")


def understand(text: str, lang: Lang | None = None, use_laya: bool | None = None) -> Parse:
    """Turn a question into labels. Stub: English keywords only, never raises."""
    t = (text or "").lower()
    if re.search(r"\b(women|woman|female|ladies)('s)?\b", t) and re.search(r"\bmen('s)?\b", t):
        signal, conf = "both_named", 1.0
    elif re.search(r"\b(women|woman|female|ladies)('s)?\b", t):
        signal, conf = "women", 1.0
    elif re.search(r"\b(men|male)('s)?\b", t):
        signal, conf = "men", 1.0
    else:
        signal, conf = "none", 0.0
    fmt = "T20I" if re.search(r"t20", t) else "ODI" if re.search(r"\bodi|one.day", t) else "unspecified"
    family = stat = None
    for word, (fam, st) in _STAT_WORDS.items():
        if word in t:
            family, stat = fam, st
            break
    if family:
        topic = "cricket_stat"
    elif any(w in t for w in _CRICKET_GENERAL) or "cricket" in t:
        topic = "cricket_general"
    else:
        topic = "non_sport"
    return Parse(lang=lang or "en", gender_signal=signal, gender_conf=conf, topic=topic,
                 family=family, stat=stat, format=fmt if family else None,
                 trace=("understand: PHASE 0 STUB (English keywords only)",))
