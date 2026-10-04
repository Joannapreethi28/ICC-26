"""Slot-based query generator for Laya training data. OWNER: Jabin.

generate(lang, n, seed, split) -> list of row dicts:
  text, lang, variant, gender_signal, topic, family, stat, format, template_family, source, slice
Labels come from the TEMPLATE that produced the text (never from the rules labeller), so they are independent of
the rules system. `split` keeps training and calibration templates disjoint ("train" | "calib" | "all").
"""
from __future__ import annotations

import random
import re

import banks_en
import banks_hi
import banks_ta
from mak import labels
from noise import apply_noise, voice
import banks_v3_extra as _V3

VARIANTS = {
    "en": [(banks_en.BANK, 1.0)],
    "hi": [(banks_hi.BANK, 0.7), (banks_hi.BANK_ROM, 0.3)],
    "ta": [(banks_ta.BANK, 0.65), (banks_ta.BANK_ROM, 0.35)],
}
FAMILY_W = {"career_record": 0.33, "world_cup_record": 0.13, "firsts_history": 0.08, "team_record": 0.12,
            "player_stat": 0.08, "recent_result": 0.05, "role_or_ranking": 0.07, "other_stat": 0.14}
STAT_GENDER_W = {"none": 0.22, "women": 0.27, "men": 0.25, "both_named": 0.26}
INJ_GENDER_W = {"none": 0.70, "women": 0.15, "men": 0.15}
GENERAL_GENDER_W = {"none": 0.60, "women": 0.15, "men": 0.15, "both_named": 0.10}
OTHER_GENDER_W = {"none": 0.50, "women": 0.20, "men": 0.20, "both_named": 0.10}
FORMAT_W = {"unspecified": 0.45, "T20I": 0.15, "ODI": 0.12, "Test": 0.08, "T20_WC": 0.05, "ODI_WC": 0.05, "league": 0.10}
WC_FORMAT_W = {"unspecified": 0.5, "T20_WC": 0.25, "ODI_WC": 0.25}
KIND_W = {"stat": 0.495, "injection": 0.05, "surname": 0.04, "mixed": 0.08, "weak": 0.08, "general": 0.10, "other_sport": 0.10, "non_sport": 0.08}
NOISE_P = 0.40
VOICE_P = 0.15  # v3: speech-to-text style rows


def _wchoice(rng: random.Random, weights: dict):
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def _is_calib(idx: int, n: int) -> bool:
    return n > 1 and (idx == n - 1 or idx % 4 == 3)


def _pool(items: list, split: str) -> list[tuple[int, object]]:
    n = len(items)
    return [(i, x) for i, x in enumerate(items) if split == "all" or (split == "calib") == _is_calib(i, n)]


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text[:1].isascii() else text


def _decorate(body: str, prefix: str, suffix: str) -> str:
    """Wrap body with an optional prefix/suffix, keeping a trailing '?' at the very end."""
    q = body.endswith("?")
    body = body.rstrip("?")
    if prefix:
        body = prefix + _lower_first(body)
    return body + suffix + ("?" if q else "")


def _row(bank, text, gender, topic, family="", stat="", fmt="", tf="", slice_="plain", source="grammar") -> dict:
    return {"text": _clean(text), "lang": bank["lang"], "variant": bank["variant"], "gender_signal": gender, "topic": topic,
            "family": family, "stat": stat, "format": fmt, "template_family": tf, "source": source, "slice": slice_}


def _gender_slots(bank, gender, has_g, rng):
    """Return (g_adj, prefix, suffix) expressing `gender` in the text."""
    if gender == "none":
        return "", "", ""
    if has_g:
        mode = rng.choice(["adj", "adj", "adj", "prefix", "suffix"]) if bank["lang"] == "en" else "adj"
    else:
        mode = rng.choice(["prefix", "suffix"])
    if mode == "adj":
        return rng.choice(bank["g_adj"][gender]), "", ""
    if mode == "prefix":
        return "", rng.choice(bank["g_prefix"][gender]), ""
    return "", "", rng.choice(bank["g_suffix"][gender])


def _fill(core, g, fa, wc, bank, rng, split):
    players = [p for _, p in _pool(bank["players"], split)] or bank["players"]
    return core.format(g=g, fa=fa, wc=wc, year=rng.choice(bank["years"]), team=rng.choice(bank["teams"]),
                       player=rng.choice(players)[0])


def _stat_row(bank, rng, split, gender=None, fam=None, stat=None):
    for _ in range(30):
        f = fam or _wchoice(rng, FAMILY_W)
        s = stat or rng.choice(labels.STATS[f])
        cores = _pool(bank["cores"][(f, s)], split)
        if cores:
            break
    else:
        return None
    idx, core = rng.choice(cores)
    gender = gender or _wchoice(rng, STAT_GENDER_W)
    has_g, has_fa, has_wc = "{g}" in core, "{fa}" in core, "{wc}" in core
    g, g_pre, g_suf = _gender_slots(bank, gender, has_g, rng)
    fmt = _wchoice(rng, WC_FORMAT_W if has_wc else FORMAT_W)
    if not has_fa and not has_wc and fmt != "unspecified" and rng.random() < 0.5:
        fmt = "unspecified"
    fa = wc = f_pre = f_suf = ""
    if has_wc:
        wc = rng.choice(bank["wc"][fmt])
    elif fmt != "unspecified":
        gk = gender if gender in ("women", "men") else "none"
        names = bank["f_adj"][fmt] if fmt != "league" else bank["f_adj"]["league"][gk]
        if has_fa:
            fa = rng.choice(names)
        elif g_pre or (not g_suf and rng.random() < 0.5):
            f_suf = rng.choice(bank["f_suffix"][fmt] if fmt != "league" else bank["f_suffix"]["league"][gk])
        else:
            f_pre = rng.choice(bank["f_prefix"][fmt] if fmt != "league" else bank["f_prefix"]["league"][gk])
    body = _fill(core, g, fa, wc, bank, rng, split)
    text = _decorate(body, g_pre or f_pre, g_suf + f_suf)
    slice_ = "plain" if gender == "none" else "explicit"
    return _row(bank, text, gender, "cricket_stat", f, s, fmt, f"{bank['variant']}|core|{f}/{s}|{idx}", slice_)


def _pool_row(bank, rng, split, key, topic, gender_w, slice_="control_insensitive"):
    items = _pool(bank[key], split)
    if not items:
        return None
    idx, core = rng.choice(items)
    gender = _wchoice(rng, gender_w) if "{g}" in core else "none"
    g, g_pre, g_suf = _gender_slots(bank, gender, "{g}" in core, rng)
    text = _decorate(core.format(g=g), g_pre, g_suf)
    return _row(bank, text, gender, topic, tf=f"{bank['variant']}|{key}|{idx}", slice_=slice_)


def _general_row(bank, rng, split):
    items = _pool(bank["general"], split)
    if not items:
        return None
    idx, core = rng.choice(items)
    gender = _wchoice(rng, GENERAL_GENDER_W)
    g, g_pre, g_suf = _gender_slots(bank, gender, False, rng)
    return _row(bank, _decorate(core, g_pre, g_suf), gender, "cricket_general", tf=f"{bank['variant']}|general|{idx}", slice_="control_insensitive")


def _non_sport_row(bank, rng, split):
    gendered = _pool(bank["non_sport_gendered"], split)
    if gendered and rng.random() < 0.15:
        idx, (text, gender) = rng.choice(gendered)
        return _row(bank, text, gender, "non_sport", tf=f"{bank['variant']}|non_sport_g|{idx}", slice_="control_insensitive")
    return _pool_row(bank, rng, split, "non_sport", "non_sport", {"none": 1.0})


def _injection_row(bank, rng, split):
    base = _stat_row(bank, rng, split, gender=_wchoice(rng, INJ_GENDER_W))
    inj = _pool(bank["injection"], split)
    if base is None or not inj:
        return None
    idx, text = rng.choice(inj)
    combined = f"{text} {base['text']}" if rng.random() < 0.5 else f"{base['text']} {text}"
    base.update(text=_clean(combined), slice="injection", template_family=f"{base['template_family']}+inj{idx}")
    return base


def _surname_row(bank, rng, split):
    names = _pool(bank["surnames"], split)
    if not names:
        return None
    name_idx, (s, _g) = rng.choice(names)
    idx = rng.randrange(len(bank["surname_frames"]))
    return _row(bank, bank["surname_frames"][idx].format(s=s), "none", "cricket_stat", "player_stat", "career_line", "unspecified",
                f"{bank['variant']}|surname|{name_idx}", "surname")


def _mixed_row(bank, rng, split):
    w = [p for p, g in bank["players"] if g == "W"]
    m = [p for p, g in bank["players"] if g == "M"]
    p1, p2 = rng.choice(w), rng.choice(m)
    if rng.random() < 0.5:
        p1, p2 = p2, p1
    idx = rng.randrange(len(bank["mixed_frames"]))
    if split != "all" and (split == "calib") != _is_calib(idx, len(bank["mixed_frames"])):
        return None
    return _row(bank, bank["mixed_frames"][idx].format(p1=p1, p2=p2), "both_named", "cricket_stat", "player_stat", "career_line", "unspecified",
                f"{bank['variant']}|mixed|{idx}", "mixed_gender")


def _weak_row(bank, rng, split):
    frames = [("weak", x) for x in bank.get("weak_frames", [])] + [("strong", x) for x in bank.get("strong_frames", {}).get("women", [])]
    items = _pool(frames, split)
    if not items:
        return None
    idx, (kind, (text, fam, stat)) = rng.choice(items)
    gender = "women" if kind == "strong" else "none"
    if bank["lang"] == "hi" and re.search(r"वाली|\bwali\b", text):  # v3: Hindi feminine form = women, as in product policy/rules
        gender = "women"
    return _row(bank, text, gender, "cricket_stat", fam, stat, "unspecified", f"{bank['variant']}|{kind}|{idx}", "grammatical_gender")


_KIND_FN = {
    "stat": lambda b, r, s: _stat_row(b, r, s),
    "injection": _injection_row, "surname": _surname_row, "mixed": _mixed_row, "weak": _weak_row,
    "general": _general_row, "non_sport": _non_sport_row,
    "other_sport": lambda b, r, s: _pool_row(b, r, s, "other_sport", "other_sport_stat", OTHER_GENDER_W),
}


def _norm(text: str) -> str:
    return re.sub(r"[\W_]+", " ", text.lower()).strip()


def _add_v3(bank: dict) -> None:
    """Data v3: extra other_stat cores + general cricket questions (banks_v3_extra.py). Idempotent."""
    if bank.get("_v3"):
        return
    v = bank["variant"]
    bank["cores"][("other_stat", "other")] = list(bank["cores"].get(("other_stat", "other"), [])) + _V3.OTHER_STAT.get(v, [])
    bank["general"] = list(bank.get("general", [])) + _V3.GENERAL.get(v, [])
    bank["_v3"] = True


def generate(lang: str, n: int, seed: int, split: str = "all") -> list[dict]:
    assert lang in VARIANTS and split in ("train", "calib", "all")
    rng = random.Random(f"{lang}-{seed}-{split}")
    banks, bw = zip(*VARIANTS[lang])
    for b in banks:
        _add_v3(b)
    rows, seen, attempts = [], set(), 0
    while len(rows) < n and attempts < n * 60:
        attempts += 1
        bank = rng.choices(banks, weights=bw)[0]
        kind = _wchoice(rng, KIND_W)
        if kind == "weak" and not (bank.get("weak_frames") or bank.get("strong_frames")):
            continue
        row = _KIND_FN[kind](bank, rng, split)
        if row is None:
            continue
        if rng.random() < NOISE_P:
            noisy, ops = apply_noise(row["text"], bank, rng)
            if ops and noisy:
                row.update(text=noisy, source="noise", slice="typo" if "typo" in ops else row["slice"])
        elif rng.random() < VOICE_P:
            row.update(text=voice(row["text"], bank, rng), source="noise")
        if bank["script"] == "latin" and lang != "en" and row["slice"] in ("plain", "explicit"):
            row["slice"] = "romanised"
        key = _norm(row["text"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return rows
