"""Noise for training queries: typos, casing, dropped question marks, SMS spelling, filler words. OWNER: Jabin.

Noise never changes a label. Typos touch only Latin-script tokens of 5+ letters and keep the first letter, so the
meaning stays recoverable (a native reader would still know the word). Hindi/Tamil script is never corrupted.
"""
from __future__ import annotations

import random
import re

_SMS = {
    "en": {"please": "pls", "thanks": "thx", "who": "who", "tell me": "tell me", "which": "wich", "the": "da", "you": "u"},
    "hi_rom": {"kya": "kya", "mein": "me", "aur": "or", "zyada": "jyada", "sabse": "sbse", "kaun": "kon", "kisne": "kisne", "hai": "h", "hain": "h", "batao": "btao"},
    "ta_rom": {"yaaru": "yaru", "evlo": "evvlo", "adhiga": "athiga", "enna": "ena", "sollunga": "solunga", "-la": "la", "eduthavanga": "eduthavnga"},
}
_QMARKS = ("?", "।", ".")
# Gender cue words are never typo'd: a corrupted cue would make the label unrecoverable (label noise, not realism).
_PROTECT = {"women", "womens", "men", "mens", "female", "male", "mahila", "purush", "pengal", "aangal", "magalir", "aadavar",
            "mahilaon", "purushon", "veeranganai"}


def _typo_word(w: str, rng: random.Random) -> str:
    if len(w) < 5 or not w.isascii() or not w.isalpha():
        return w
    i = rng.randrange(1, len(w) - 1)
    op = rng.choice(("swap", "drop", "dup", "sub"))
    if op == "swap":
        return w[:i] + w[i + 1] + w[i] + w[i + 2:]
    if op == "drop":
        return w[:i] + w[i + 1:]
    if op == "dup":
        return w[:i] + w[i] + w[i:]
    near = {"a": "s", "e": "r", "i": "o", "o": "p", "n": "m", "s": "d", "r": "t", "t": "y", "u": "i", "l": "k", "m": "n"}
    return w[:i] + near.get(w[i].lower(), w[i]) + w[i + 1:]


def add_typos(text: str, rng: random.Random, rate: float = 0.25) -> tuple[str, bool]:
    parts = re.split(r"(\s+)", text)
    changed = False
    out = []
    for p in parts:
        core = p.strip("?,.!:;()'\"")
        if core and rng.random() < rate and len(core) >= 5 and core.isascii() and core.isalpha() and core.lower() not in _PROTECT:
            new = _typo_word(core, rng)
            if new != core:
                p = p.replace(core, new, 1)
                changed = True
        out.append(p)
    return "".join(out), changed


def sms_spelling(text: str, variant: str, rng: random.Random) -> tuple[str, bool]:
    changed = False
    for src, dst in _SMS.get(variant, {}).items():
        pat = re.escape(src) if src.startswith("-") else r"\b" + re.escape(src) + r"\b"
        if src != dst and re.search(pat, text, flags=re.I) and rng.random() < 0.6:
            text = re.sub(pat, dst, text, flags=re.I)
            changed = True
    return text, changed


def recase(text: str, rng: random.Random) -> tuple[str, bool]:
    mode = rng.choice(("lower", "upper", "title"))
    new = {"lower": text.lower(), "upper": text.upper(), "title": " ".join(w.capitalize() for w in text.split(" "))}[mode]
    return new, new != text


def drop_qmark(text: str) -> tuple[str, bool]:
    t = text.rstrip()
    if t and t[-1] in _QMARKS:
        return t[:-1].rstrip(), True
    return text, False


def add_filler(text: str, bank: dict, rng: random.Random) -> tuple[str, bool]:
    if rng.random() < 0.6:
        pre = rng.choice(bank["fillers_prefix"])
        return pre + text[0].lower() + text[1:] if text[:1].isascii() else pre + text, True
    return text.rstrip("?।. ") + rng.choice(bank["fillers_suffix"]), True


def apply_noise(text: str, bank: dict, rng: random.Random) -> tuple[str, list[str]]:
    """Apply 1-3 random noise operations; returns (noisy text, names of operations applied)."""
    variant, applied = bank["variant"], []
    ops = ["typo", "case", "qmark", "sms", "filler"]
    rng.shuffle(ops)
    for op in ops[: rng.choice((1, 1, 2, 3))]:
        if op == "typo" and bank["script"] == "latin":
            text, ok = add_typos(text, rng)
        elif op == "case" and bank["script"] == "latin":
            text, ok = recase(text, rng)
        elif op == "qmark":
            text, ok = drop_qmark(text)
        elif op == "sms" and bank["script"] == "latin":
            text, ok = sms_spelling(text, variant, rng)
        elif op == "filler":
            text, ok = add_filler(text, bank, rng)
        else:
            ok = False
        if ok:
            applied.append(op)
    return re.sub(r"\s+", " ", text).strip(), applied
