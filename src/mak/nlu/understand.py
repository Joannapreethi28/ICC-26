"""Question -> labels. OWNER: Jabin. The signature below is FIXED (shared contract).

Rules always run. With use_laya=True the fine-tuned Laya head is added and merged (merge policy v1, below);
if Laya is missing or errors, the rules result is returned with a trace note (never raises, never blocks an answer).

Merge policy v1 (the J-P4 ablation measures rules-only vs this; change it only with evidence):
  * gender: an explicit rules cue (gender_conf 1.0) is an override. Otherwise Laya's calibrated gender signal is accepted
    only if its probability >= config.GENDER_THRESHOLD; below that the question is treated as neutral ("none") so BOTH
    records are shown (fail-safe). An injection marker always keeps gender "none".
  * topic/family/stat: a lexicon stat match from the rules is kept (high precision); otherwise Laya's top label is used
    when its probability >= LABEL_MIN_PROB. Format: rules value unless it is "unspecified".
"""
from __future__ import annotations

from dataclasses import replace

from mak import config, labels
from mak.nlu.lang import detect_lang
from mak.nlu.rules import rules_parse
from mak.types import Lang, Parse

LABEL_MIN_PROB = 0.5
# "v1": a rules lexicon stat match beats Laya on topic/family/stat. "v2": a confident Laya label (>= LABEL_MIN_PROB)
# beats the rules on topic/family/stat. Gender handling is identical in both. Chosen by the dev ablation BEFORE test.
MERGE_POLICY = "v1"


def understand(text: str, lang: Lang | None = None, use_laya: bool | None = None) -> Parse:
    """Turn a question into labels. `lang=None` means detect it. `use_laya=None` follows config.USE_LAYA."""
    try:
        query = text if isinstance(text, str) else ""
        resolved_lang: Lang = lang or detect_lang(query)
        parse = rules_parse(query, resolved_lang)
        if config.USE_LAYA if use_laya is None else use_laya:
            parse = _add_laya(query, parse)
        return parse
    except Exception as exc:  # noqa: BLE001 - the pipeline must always get a Parse
        return Parse(lang=lang or "en", gender_signal="none", gender_conf=0.0, topic="non_sport",
                     family=None, stat=None, format=None,
                     trace=(f"understand: internal error {type(exc).__name__}; neutral fail-safe parse",))


def _with_note(parse: Parse, note: str) -> Parse:
    return replace(parse, trace=parse.trace + (note,))


def _add_laya(query: str, parse: Parse) -> Parse:
    try:
        from mak.nlu.laya_head import LayaHead
        pred = LayaHead.load().predict(query)
    except Exception as exc:  # noqa: BLE001 - degrade to rules, say so in the trace
        return _with_note(parse, f"laya unavailable ({type(exc).__name__}: {str(exc)[:80]}); rules-only result")
    return merge(parse, pred)


def merge(parse: Parse, pred: dict[str, tuple[str, float]], policy: str | None = None) -> Parse:
    """pred = {question: (label, calibrated probability)} from any backend (LayaHead.predict)."""
    trace = list(parse.trace)

    signal, conf = parse.gender_signal, parse.gender_conf
    if parse.injection_suspected:
        trace.append("laya: gender ignored (injection marker)")
    elif parse.gender_conf >= 1.0:
        trace.append("laya: explicit rules cue kept as override")
    else:
        g, p = pred["gender_signal"]
        if g in ("women", "men", "both_named") and p >= config.GENDER_THRESHOLD:
            signal, conf = g, p
            trace.append(f"laya: gender {g} p={p:.2f} >= threshold {config.GENDER_THRESHOLD}")
        else:
            signal, conf = "none", (p if g == "none" else 0.0)
            trace.append(f"laya: gender {g} p={p:.2f} below threshold or neutral; treated as neutral (show both)")

    topic, family, stat, fmt = parse.topic, parse.family, parse.stat, parse.format
    rules_found_stat = parse.topic == "cricket_stat" and parse.family not in (None, "other_stat")
    if (policy or MERGE_POLICY) == "v2":
        rules_found_stat = False
    if not rules_found_stat:
        t, tp = pred["topic"]
        if tp >= LABEL_MIN_PROB:
            topic = t
            trace.append(f"laya: topic {t} p={tp:.2f}")
        if topic == "cricket_stat":
            f, fp = pred["family"]
            if fp >= LABEL_MIN_PROB:
                family = f
                s, sp = pred.get("stat", (None, 0.0))
                stat = s if (s and sp >= LABEL_MIN_PROB and s in labels.STATS.get(f, ())) else (parse.stat if parse.family == f else None)
                trace.append(f"laya: family {f} p={fp:.2f}, stat {stat}")
            elif family is None:
                family, stat = "other_stat", "other"
        else:
            family = stat = fmt = None
    if topic == "cricket_stat" and fmt in (None, "unspecified"):
        f, fp = pred["format"]
        fmt = f if fp >= LABEL_MIN_PROB else (fmt or "unspecified")
    return replace(parse, gender_signal=signal, gender_conf=conf, topic=topic, family=family, stat=stat, format=fmt,
                   trace=tuple(trace))