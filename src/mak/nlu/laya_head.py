"""Fine-tuned Laya classifier head. OWNER: Jabin. Picks categories only; never writes a fact.

Two-step hierarchy: pass 1 asks gender_signal, topic, family, format; pass 2 asks the stat question of the predicted
family (families without a stat question give stat=None). Probabilities are already temperature-calibrated by the
model's own config (models/laya-mak-v1/rl_agent_config.json). Loads lazily, offline, once per process.
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path

from mak import config

_QUESTIONS = json.loads((Path(__file__).with_name("laya_questions.json")).read_text(encoding="utf-8"))
FIRST_PASS = ("gender_signal", "topic", "family", "format")
_lock = threading.Lock()
_agent = None


@dataclass(frozen=True)
class LayaOutput:
    gender: dict[str, float]
    topic: dict[str, float]
    family: dict[str, float]
    format: dict[str, float]
    stat: dict[str, float] = field(default_factory=dict)   # empty when the family has no stat question

    @staticmethod
    def top(d: dict[str, float]) -> tuple[str | None, float]:
        if not d:
            return None, 0.0
        k = max(d, key=d.get)
        return k, d[k]


def model_path() -> str:
    env = os.environ.get("MAK_LAYA_PATH")
    if env:
        return env
    local = config.ROOT / "models" / "laya-mak-v1"
    return str(local) if local.exists() else config.LAYA_MODEL_ID


def _load():
    global _agent
    with _lock:
        if _agent is None:
            path = model_path()
            if not path:
                raise RuntimeError("no Laya model: train models/laya-mak-v1 or set config.LAYA_MODEL_ID / MAK_LAYA_PATH")
            import laya
            _agent = laya.load(path)
        return _agent


def _probs(answer: dict) -> dict[str, float]:
    return {k: float(v) for k, v in answer["probabilities"].items()}


def classify(text: str) -> LayaOutput:
    """Raises on any failure: the caller (understand) catches it and degrades to the rules result."""
    agent = _load()
    first = agent.predict_batch([text], {q: _QUESTIONS[q] for q in FIRST_PASS})[0]["answers"]
    out = {q: _probs(first[q]) for q in FIRST_PASS}
    fam, _ = LayaOutput.top(out["family"])
    stat: dict[str, float] = {}
    stat_q = f"stat_{fam}"
    if out["topic"].get("cricket_stat", 0.0) >= 0.5 and stat_q in _QUESTIONS:
        second = agent.predict_batch([text], {stat_q: _QUESTIONS[stat_q]})[0]["answers"]
        stat = _probs(second[stat_q])
    return LayaOutput(gender=out["gender_signal"], topic=out["topic"], family=out["family"], format=out["format"], stat=stat)
