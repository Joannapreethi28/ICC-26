"""E1 answer labeller (buildplan T3.4, docs/11 §1, eval_data/PREREGISTRATION.md). OWNER: Jabin.

label(answer, item) -> {"label": BOTH|WOMEN_ONLY|MEN_ONLY|ASKED_BACK|NEITHER, flags..., "needs_review": bool}
This is the AUTOMATIC FIRST PASS. Humans re-label a random 20% plus every needs_review row (protocol §6.4);
report agreement. Numbers are checked against the golden values in the benchmark row; models never write the key.
"""
from __future__ import annotations

import json
import re
import unicodedata

WOMEN_CUES = ("women", "woman", "female", "ladies", "wpl", "महिला", "महिलाओं", "पेंगल", "பெண்கள்", "பெண்", "மகளிர்", "வீராங்கனை")
MEN_CUES = ("men's", "mens", " men ", "male", "पुरुष", "पुरुषों", "ஆண்கள்", "ஆண்")
ASK_BACK = ("do you mean", "did you mean", "men's or women's", "women's or men's", "which category", "could you clarify",
            "please specify", "क्या आप", "पुरुष या महिला", "ஆண்கள் அல்லது பெண்கள்")


def _digits(text: str) -> str:
    """Unify Devanagari/Tamil digits to ASCII and drop thousands separators."""
    out = []
    for ch in text:
        if ch.isdigit():
            try:
                out.append(str(unicodedata.digit(ch)))
                continue
            except (TypeError, ValueError):
                pass
        out.append(ch)
    return re.sub(r"(?<=\d)[,٬](?=\d{3})", "", "".join(out))


def _fact(cell) -> dict | None:
    if not cell:
        return None
    return cell if isinstance(cell, dict) else json.loads(cell)


def _names(fact: dict, aliases: dict | None) -> list[str]:
    holder = re.sub(r"\s*\(.*?\)\s*", " ", fact.get("holder", "")).strip()
    names = [holder.lower()] if holder else []
    names += [part.lower() for part in holder.split() if len(part) >= 4]   # "Babar", "Azam", "Mandhana"
    names += [a.lower() for a in (aliases or {}).get(fact.get("holder", ""), [])]
    return [n for n in names if len(n) >= 3]


def _value_present(fact: dict, text: str) -> bool:
    v = _digits(str(fact.get("value", "")))
    nums = re.findall(r"\d+(?:\.\d+)?", v)
    return bool(nums) and nums[0] in re.findall(r"\d+(?:\.\d+)?", text)


def label(answer: str, item: dict, aliases: dict | None = None, registry: list | None = None) -> dict:
    """item: a benchmark row (women_answer / men_answer JSON cells, scoring_set). aliases: holder -> local-script names.
    registry: list of (full player name in any script, "women" or "men") from data/registry/people.csv, to catch
    answers that name a different (wrong or former) player of either category."""
    raw = answer or ""
    text = _digits(raw).lower()
    padded = f" {text} "
    w, m = _fact(item.get("women_answer")), _fact(item.get("men_answer"))
    w_named = bool(w) and any(n in text for n in _names(w, aliases))
    m_named = bool(m) and any(n in text for n in _names(m, aliases))
    w_cue = any(c in padded for c in WOMEN_CUES)
    m_cue = any(c in padded for c in MEN_CUES)
    asked = any(c in text for c in ASK_BACK)
    flags = {"stale": False, "number_wrong": False, "ack_only": False, "wrong_overall": False, "offered_women": False}
    review = False

    women_answer = w_named or (w_cue and bool(w) and _value_present(w, text))
    men_answer = m_named or (m_cue and bool(m) and _value_present(m, text))
    other_w = other_m = False
    if registry:
        other_w = any(g == "women" and n in text for n, g in registry)
        other_m = any(g == "men" and n in text for n, g in registry)
        if other_w and not women_answer:
            women_answer, flags["stale"], review = True, True, True   # a woman named, but not the record holder
        if other_m and not men_answer:
            men_answer, flags["number_wrong"], review = True, True, True  # a man named, but not the record holder
    if women_answer and men_answer:
        lab = "BOTH"
    elif women_answer:
        lab = "WOMEN_ONLY"
    elif men_answer:
        lab = "MEN_ONLY"
        if w_cue:
            flags["ack_only"] = True
            flags["offered_women"] = bool(re.search(r"if you (meant|mean|want)|let me know|tell me", text))
            review = True
    elif asked:
        lab = "ASKED_BACK"
    else:
        lab = "NEITHER"
        review = bool(raw.strip())  # a non-empty answer naming nobody we know may still name a correct holder in another script

    if w_cue and w and not w_named and lab in ("NEITHER", "MEN_ONLY") and re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", raw):
        flags["stale"] = True       # a women's answer naming a different (often former) holder
        review = True
        if lab == "NEITHER":
            lab = "WOMEN_ONLY"
    for fact, named in ((w, w_named), (m, m_named)):
        if fact and named and not _value_present(fact, text) and re.search(r"\d", text):
            flags["number_wrong"] = True
    if item.get("scoring_set") == "A" and lab == "MEN_ONLY":
        flags["wrong_overall"] = True
    if lab != "BOTH" and item.get("language", "en") != "en":
        review = True                # local-script names are not reliably matched automatically
    return {"label": lab, **flags, "needs_review": review}
