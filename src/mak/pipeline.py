"""Query -> Resolution. OWNER: Joanna.

PHASE 0 STUB: returns a correctly typed Resolution with no facts so Jabin can build the E1 runner now.
Joanna replaces the body in K-P4 (buildplan T1.7). The signature below is FIXED.
"""
from __future__ import annotations

import time
from typing import Literal

from mak.nlu.understand import understand
from mak.types import Lang, Resolution


def resolve(query: str, lang: Lang | Literal["auto"] = "auto") -> Resolution:
    """Answer a sports question with the gender-aware policy. Stub: labels only, no facts."""
    t0 = time.perf_counter()
    p = understand(query, None if lang == "auto" else lang)
    return Resolution(
        decision="unsupported", language=p.lang, sport="cricket", intent=None, format=p.format,
        gender_relevant=p.topic == "cricket_stat", trace=list(p.trace) + ["pipeline: PHASE 0 STUB"],
        confidence={"gender": p.gender_conf}, fallback="stub", results=[], overall_leader="none",
        answer_text="", latency_ms=(time.perf_counter() - t0) * 1000,
    )
