"""Qwen LoRA parser inference (buildplan T2.4). OWNER: Jabin. Comparison arm only.

predict(text, lang) -> {question: (label, confidence)} in the classifier_eval format.
Invalid JSON or an out-of-set label RAISES, so evaluate() counts it as an error (reported, never hidden).
Confidence = product of the generated label tokens' probabilities (greedy decoding); it is NOT temperature-calibrated.
"""
import json
import os
import pathlib
import sys

os.environ.setdefault("HF_HUB_OFFLINE", "1")
sys.path.insert(0, str(pathlib.Path(__file__).parent))

import torch  # noqa: E402
from common import BASE_MODEL, BASE_REVISION, KEYS, ROOT, prompt_messages  # noqa: E402
from mak import labels  # noqa: E402

_state = {}


def load(adapter: str | None = None):
    if "model" not in _state:
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
        adapter = adapter or str(ROOT / "models" / "qwen-mak-lora-v1")
        tok = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_REVISION)
        base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, revision=BASE_REVISION, dtype=torch.bfloat16,
                                                    use_safetensors=True).to("cuda" if torch.cuda.is_available() else "cpu")
        _state.update(tok=tok, model=PeftModel.from_pretrained(base, adapter).eval())
    return _state["tok"], _state["model"]


def _valid(d: dict) -> None:
    allowed = {"gender_signal": labels.GENDER_SIGNAL, "topic": labels.TOPIC, "family": labels.FAMILY, "format": labels.FORMAT}
    for k, v in allowed.items():
        if d.get(k) is not None and d[k] not in v:
            raise ValueError(f"label out of set: {k}={d[k]!r}")
    if d.get("stat") is not None and d["stat"] not in labels.STATS.get(d.get("family"), ()):
        raise ValueError(f"stat {d['stat']!r} not valid for family {d.get('family')!r}")


@torch.no_grad()
def predict(text: str, lang: str = "en") -> dict[str, tuple[str, float]]:
    tok, model = load()
    ids = tok.apply_chat_template(prompt_messages(text), add_generation_prompt=True, return_tensors="pt", return_dict=True).to(model.device)
    out = model.generate(**ids, max_new_tokens=80, do_sample=False, output_scores=True, return_dict_in_generate=True)
    gen = out.sequences[0, ids["input_ids"].shape[1]:]
    raw = tok.decode(gen, skip_special_tokens=True).strip()
    d = json.loads(raw)
    if not isinstance(d, dict) or set(KEYS) - set(d):
        raise ValueError(f"missing keys in {raw!r}")
    _valid(d)
    probs = [torch.softmax(s[0].float(), -1)[t].item() for s, t in zip(out.scores, gen)]
    conf = float(torch.tensor(probs).prod()) if probs else 0.0
    return {k: (d[k], conf) for k in KEYS}
