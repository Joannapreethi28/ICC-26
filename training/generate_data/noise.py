"""Noise for training queries: typos, casing, dropped question marks, SMS spelling, filler words, cricket abbreviations
(data v2). OWNER: Jabin.

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


_ABBREV = [(r"\bwickets\b", ("wkts", "wkt")), (r"\bcenturies\b", ("100s", "tons")), (r"\bhundreds\b", ("100s",)),
           (r"\bhalf centuries\b", ("50s",)), (r"\bfifties\b", ("50s",)), (r"\baverage\b", ("avg",)),
           (r"\bstrike rate\b", ("SR", "s/r")), (r"\beconomy rate\b", ("econ", "eco")), (r"\beconomy\b", ("econ",)),
           (r"\binternationals?\b", ("intl",)), (r"\bmatches\b", ("games",)), (r"\bhighest\b", ("top",))]


def abbreviate(text: str, rng: random.Random) -> tuple[str, bool]:
    """Cricket abbreviations fans type (wkts, 100s, avg, SR, econ). Same meaning, so labels are unchanged."""
    changed = False
    for pat, alts in _ABBREV:
        if re.search(pat, text, flags=re.I) and rng.random() < 0.7:
            text = re.sub(pat, rng.choice(alts), text, count=1, flags=re.I)
            changed = True
    return text, changed


def add_filler(text: str, bank: dict, rng: random.Random) -> tuple[str, bool]:
    if rng.random() < 0.6:
        pre = rng.choice(bank["fillers_prefix"])
        return pre + text[0].lower() + text[1:] if text[:1].isascii() else pre + text, True
    return text.rstrip("?।. ") + rng.choice(bank["fillers_suffix"]), True


def apply_noise(text: str, bank: dict, rng: random.Random) -> tuple[str, list[str]]:
    """Apply 1-3 random noise operations; returns (noisy text, names of operations applied)."""
    variant, applied = bank["variant"], []
    ops = ["typo", "case", "qmark", "sms", "filler", "abbrev"]
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
        elif op == "abbrev" and bank["script"] == "latin":
            text, ok = abbreviate(text, rng)
        elif op == "filler":
            text, ok = add_filler(text, bank, rng)
        else:
            ok = False
        if ok:
            applied.append(op)
    return re.sub(r"\s+", " ", text).strip(), applied


# ---- v3: speech-to-text style (voice assistants, esp. Hindi/Tamil). Labels unchanged; gender cue words untouched. ----
_VOICE_TERMS = {
    "latin": [(r"\bT20Is?\b", ("t twenty", "t twenty international", "tee twenty")), (r"\bT20\b", ("t twenty", "twenty twenty")),
              (r"\bODIs?\b", ("one day", "o d i", "one dayer")), (r"\bWPL\b", ("w p l",)), (r"\bIPL\b", ("i p l",)),
              (r"\bWC\b", ("world cup",)), (r"\b2024\b", ("twenty twenty four",)), (r"\b2023\b", ("twenty twenty three",)),
              (r"\b2022\b", ("twenty twenty two",))],
    "deva": [(r"T20I?s?|टी20", ("टी ट्वेंटी", "टी-ट्वेंटी")), (r"ODIs?|वनडे", ("वनडे", "वन डे", "ओडीआई")), (r"IPL", ("आईपीएल",)),
             (r"WPL", ("डब्ल्यूपीएल",))],
    "taml": [(r"T20I?s?|டி20", ("டி ட்வென்டி", "டி-20")), (r"ODIs?", ("ஒன் டே", "ஒருநாள்")), (r"IPL", ("ஐபிஎல்",))],
}
_VOICE_FILLERS = {"en": ("umm ", "uh ", "so ", "hey "), "hi": ("अच्छा ", "मतलब ", "यार "), "hi_rom": ("accha ", "matlab ", "yaar "),
                  "ta": ("சொல்லுங்க ", "அப்புறம் "), "ta_rom": ("sollunga ", "appuram ", "enna ")}
_MISHEAR = {"Mandhana": "Mandana", "Babar": "Babur", "Kohli": "Koli", "Harmanpreet": "Harmanprit", "Perry": "Peri",
            "Tendulkar": "Tendulkur", "Mithali": "Mitali", "Rashid": "Rashed"}


def voice(text: str, bank: dict, rng: random.Random) -> str:
    script = {"latin": "latin"}.get(bank["script"], "deva" if bank["lang"] == "hi" else "taml")
    for pat, alts in _VOICE_TERMS[script] + (_VOICE_TERMS["latin"] if script != "latin" else []):
        if re.search(pat, text) and rng.random() < 0.8:
            text = re.sub(pat, rng.choice(alts), text, count=1)
    for a, b in _MISHEAR.items():
        if a in text and rng.random() < 0.4:
            text = text.replace(a, b)
    text = re.sub(r"[?!.,;:()\"'।]", " ", text).lower()
    if rng.random() < 0.5:
        text = rng.choice(_VOICE_FILLERS.get(bank["variant"], ("",))) + text
    return re.sub(r"\s+", " ", text).strip()
