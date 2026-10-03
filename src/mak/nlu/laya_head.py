"""Laya backend for the category classifier (buildplan T2.5). OWNER: Jabin. Picks categories only; never writes a fact.

CANDIDATE, not a decision: Laya vs xlm-roberta-base (and others) is decided by held-out per-language results in J-P4.
If another model wins, add a sibling backend with the same predict(text) -> {question: (label, probability)};
understand.merge() and its tests are model-neutral (they only read those pairs).

Two-step hierarchy (docs/09): pass 1 asks gender_signal, topic, family, format; pass 2 asks the stat question of the
predicted family (no stat question for recent_result/other_stat, so no "stat" key). Probabilities are temperature-
calibrated by the model's own config (models/laya-mak-v1/rl_agent_config.json). Offline, loaded once per process.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from mak import config

_QUESTIONS = json.loads(Path(__file__).with_name("laya_questions.json").read_text(encoding="utf-8"))
FIRST_PASS = ("gender_signal", "topic", "family", "format")
_lock = threading.Lock()
_cache: dict[str, "LayaHead"] = {}


def default_path() -> str:
    env = os.environ.get("MAK_LAYA_PATH")
    if env:
        return env
    for name in ("laya-mak-v2", "laya-mak-v1"):
        local = config.ROOT / "models" / name
        if local.exists():
            return str(local)
    return config.LAYA_MODEL_ID


class LayaHead:
    def __init__(self, agent):
        self._agent = agent

    @classmethod
    def load(cls, path: str | None = None) -> "LayaHead":
        path = path or default_path()
        if not path:
            raise RuntimeError("no Laya model: train models/laya-mak-v1, set config.LAYA_MODEL_ID or MAK_LAYA_PATH")
        with _lock:
            if path not in _cache:
                import laya
                _cache[path] = cls(laya.load(path))
            return _cache[path]

    def predict(self, text: str) -> dict[str, tuple[str, float]]:
        """{question: (top label, calibrated probability)}. Raises on failure; understand() degrades to rules."""
        text = normalise_for_model(text)
        first = self._agent.predict_batch([text], {q: _QUESTIONS[q] for q in FIRST_PASS})[0]["answers"]
        out = {q: _top(first[q]) for q in FIRST_PASS}
        stat_q = f"stat_{out['family'][0]}"
        if out["topic"][0] == "cricket_stat" and stat_q in _QUESTIONS:
            out["stat"] = _top(self._agent.predict_batch([text], {stat_q: _QUESTIONS[stat_q]})[0]["answers"][stat_q])
        return out


def normalise_for_model(text: str) -> str:
    """Casing carries no label information; ALL-CAPS text made the cased tokenizer miss WOMENS/MENS (G-026)."""
    return " ".join(text.lower().split())


def _top(answer: dict) -> tuple[str, float]:
    probs = answer["probabilities"]
    label = max(probs, key=probs.get)
    return label, float(probs[label])
