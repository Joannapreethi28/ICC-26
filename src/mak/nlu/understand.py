"""Question -> labels. OWNER: Jabin. The signature below is FIXED (shared contract).

J-P1: rules only (lexicons + language detection). J-P4 adds the fine-tuned Laya head behind use_laya=True;
the rules stay as the explicit-cue override and as the baseline measurement.
Never raises: any internal failure degrades to a neutral, non-intervening parse.
"""
from __future__ import annotations

from mak import config
from mak.nlu.lang import detect_lang
from mak.nlu.rules import rules_parse
from mak.types import Lang, Parse


def understand(text: str, lang: Lang | None = None, use_laya: bool | None = None) -> Parse:
    """Turn a question into labels. `lang=None` means detect it. `use_laya=None` follows config.USE_LAYA."""
    try:
        query = text if isinstance(text, str) else ""
        resolved_lang: Lang = lang or detect_lang(query)
        parse = rules_parse(query, resolved_lang)
        if (config.USE_LAYA if use_laya is None else use_laya):
            parse = _with_note(parse, "laya requested but not available yet: rules-only result")
        return parse
    except Exception as exc:  # noqa: BLE001 - the pipeline must always get a Parse
        return Parse(lang=lang or "en", gender_signal="none", gender_conf=0.0, topic="non_sport",
                     family=None, stat=None, format=None,
                     trace=(f"understand: internal error {type(exc).__name__}; neutral fail-safe parse",))


def _with_note(parse: Parse, note: str) -> Parse:
    from dataclasses import replace
    return replace(parse, trace=parse.trace + (note,))
