"""Language detection for en / hi / ta, by script first and then by romanised marker words. OWNER: Jabin."""
from __future__ import annotations

import re

from mak.types import Lang

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_TAMIL = re.compile(r"[஀-௿]")
_TOKEN = re.compile(r"[a-z]+")

HINGLISH_MARKERS = frozenset({
    "sabse", "zyada", "jyada", "kisne", "kaun", "kaunsa", "banaye", "banaya", "mein", "kitne", "kitna",
    "kiska", "hain", "liye", "lene", "wali", "waali", "mahila", "mahilaon", "ladkiyon",
})
TANGLISH_MARKERS = frozenset({
    "yaaru", "yaar", "adhiga", "adhigam", "athiga", "adichavanga", "adichavar", "eduthavanga",
    "eduthavar", "evlo", "evalo", "la", "irukku", "enna", "magalir", "pengal",
})


def detect_lang(text: str) -> Lang:
    """Indic script wins (the script with more letters); otherwise 2+ distinct romanised markers; else English."""
    t = text or ""
    dev, tam = len(_DEVANAGARI.findall(t)), len(_TAMIL.findall(t))
    if dev or tam:
        return "hi" if dev >= tam else "ta"
    tokens = set(_TOKEN.findall(t.lower()))
    hi_hits, ta_hits = len(tokens & HINGLISH_MARKERS), len(tokens & TANGLISH_MARKERS)
    if max(hi_hits, ta_hits) >= 2:
        return "hi" if hi_hits >= ta_hits else "ta"
    return "en"
