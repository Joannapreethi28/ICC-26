"""Query -> Resolution (buildplan T1.7). Built by Jabin on Sir Jabin's instruction (4 Oct) to unblock E1; owner now Efanio.

Chain: understand() -> catalogue.lookup() -> policy.decide() -> fetch.get_facts() -> compose.render().
The signature below is FIXED (shared contract). Never raises: any failure returns a safe 'unsupported' Resolution.
A model never writes a fact: numbers come only from get_facts (golden/verified first, computed as covered-data).

Guidance-only fallback (proposal 4 Oct, docs/05): a gender-relevant cricket stat outside the catalogue keeps
decision='unsupported' (so E4 and the E1 preregistration are unchanged) but sets fallback='guidance_only' and an
answer_text telling the assistant to give women's and men's answers, clearly labelled, numbers unverified.
"""
from __future__ import annotations

import time
from functools import lru_cache
from typing import Literal

from mak import config
from mak.compose.render import render
from mak.fetch.catalogue import lookup
from mak.fetch.facts import get_facts
from mak.nlu.understand import understand
from mak.policy.decide import DECISION_TO_GENDERS, decide
from mak.types import Lang, Resolution

GUIDANCE = {
    "en": "This tool has no verified record for this question. If the answer depends on gender, give both the women's and "
          "the men's answer, clearly labelled, and say the numbers are not verified by this tool.",
    "hi": "इस प्रश्न के लिए इस टूल के पास कोई सत्यापित रिकॉर्ड नहीं है। यदि उत्तर लिंग पर निर्भर करता है, तो महिला और पुरुष "
          "दोनों के उत्तर स्पष्ट लेबल के साथ दें, और बताएं कि ये आंकड़े इस टूल द्वारा सत्यापित नहीं हैं।",
    "ta": "இந்தக் கேள்விக்கு இந்தக் கருவியிடம் சரிபார்க்கப்பட்ட பதிவு இல்லை. பதில் பாலினத்தைப் பொறுத்தது என்றால், பெண்கள் மற்றும் "
          "ஆண்கள் இருவரின் பதில்களையும் தெளிவாகக் குறிப்பிட்டுத் தரவும்; இந்த எண்கள் இந்தக் கருவியால் சரிபார்க்கப்படவில்லை என்றும் கூறவும்.",
}


@lru_cache(maxsize=1)
def _leaders() -> dict:
    from mak.records.golden import _load
    return _load(config.GOLDEN_PATH)[1]


def _entities(query: str) -> dict:
    """gender -> the single unambiguous entity of that gender named in the query (player_stat intents)."""
    try:
        from mak.nlu.entities import resolve_entities
        by: dict[str, list] = {}
        for e in resolve_entities(query):
            if e.gender in ("women", "men"):
                by.setdefault(e.gender, []).append(e)
        return {g: v[0] for g, v in by.items() if len(v) == 1}
    except Exception:  # noqa: BLE001 - missing registry/rapidfuzz -> no entity facts, never a crash
        return {}


def resolve(query: str, lang: Lang | Literal["auto"] = "auto") -> Resolution:
    """Answer a sports question with the gender-aware policy."""
    t0 = time.perf_counter()
    text = query if isinstance(query, str) else ""
    try:
        p = understand(text, None if lang == "auto" else lang)
        trace = list(p.trace)
        intents = lookup(p.family, p.stat, p.format) if p.topic == "cricket_stat" else []
        decision, ptrace = decide(p, bool(intents))
        trace += ptrace
        genders = DECISION_TO_GENDERS[decision]
        facts, fallback, answer = [], None, ""
        if genders:
            ents = _entities(text) if any(i.endswith("_PLAYER_LINE") for i in intents) else {}
            for intent in intents:
                for g in genders:
                    if intent.endswith(("_PLAYER_LINE", "_LAST_RESULT")):
                        e = ents.get(g)
                        if e is None:
                            trace.append(f"facts: {intent}/{g}: no unambiguous {g} entity named; skipped")
                            continue
                        facts += get_facts(intent, (g,), p.lang, entity=e)
                    else:
                        facts += get_facts(intent, (g,), p.lang)
            leader = _leaders().get(intents[0], "none") if len(intents) == 1 else "none"
            answer = render(decision, facts, p.lang, leader if leader in ("women", "men") else "none",
                            fmt_unspecified=(p.format in (None, "unspecified")))
            if not facts:
                fallback = "no_verified_facts"
                trace.append("facts: none found for the supported intent(s); nothing invented")
        elif decision == "unsupported" and p.topic == "cricket_stat":
            fallback = "guidance_only"
            answer = GUIDANCE.get(p.lang, GUIDANCE["en"])
            trace.append("fallback: guidance_only (gender policy without verified facts)")
        overall = "none"
        if len(facts) == 2 and {f.gender for f in facts} == {"women", "men"} and len(intents) == 1:
            overall = _leaders().get(intents[0], "none")
        return Resolution(
            decision=decision, language=p.lang, sport="cricket" if p.topic.startswith("cricket") else "other",
            intent=intents[0] if intents else None, format=p.format, gender_relevant=p.topic == "cricket_stat",
            trace=trace, confidence={"gender": p.gender_conf}, fallback=fallback, results=facts,
            overall_leader=overall if overall in ("women", "men") else "none", answer_text=answer,
            latency_ms=(time.perf_counter() - t0) * 1000,
        )
    except Exception as exc:  # noqa: BLE001 - the contract says never raise
        return Resolution(
            decision="unsupported", language=(lang if lang in ("en", "hi", "ta") else "en"), sport="cricket", intent=None,
            format=None, gender_relevant=False, trace=[f"pipeline: internal error {type(exc).__name__}; safe unsupported"],
            confidence={}, fallback="error", results=[], overall_leader="none", answer_text="",
            latency_ms=(time.perf_counter() - t0) * 1000,
        )
