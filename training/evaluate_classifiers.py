"""Run every classifier arm through mak.eval.classifier_eval (buildplan T2.3, docs/09 §5 baselines a-e + xlm-r). OWNER: Jabin.

  python training/evaluate_classifiers.py --mode dev                 # calib + messy_calib (development, repeatable)
  python training/evaluate_classifiers.py --mode test --i-confirm-single-run
        # Joanna's frozen testsets/nlu_{en,hi,ta}.csv, ONCE. Writes results/classifier/TEST_RUN.lock; refuses to run again
        # (SJ decision: v2 first, then test once). The test run is also the model-selection run; the report says so.

Arms: a rules | b laya_zeroshot | c laya_ft | d shipped (laya_ft + rules, understand merge) | e qwen_lora | f xlmr_ft
Every model arm sees the same lowercased, whitespace-normalised text (G-026).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "training" / "qwen_parser")]

from mak.eval import classifier_eval as ce  # noqa: E402

OUT = ROOT / "results" / "classifier"
LOCK = OUT / "TEST_RUN.lock"
LAYA_V2 = ROOT / "models" / "laya-mak-v2"
XLMR_V2 = ROOT / "models" / "xlmr-mak-v2"
QWEN_V2 = ROOT / "models" / "qwen-mak-lora-v2"


def norm(t: str) -> str:
    return " ".join(t.lower().split())


def laya_arm(path: str):
    from mak.nlu.laya_head import LayaHead
    head = LayaHead.load(path)
    return lambda text, lang: head.predict(text)


def laya_base_path() -> str:
    snaps = pathlib.Path.home() / ".cache" / "huggingface" / "hub" / "models--convaiinnovations--laya-multilingual" / "snapshots"
    return str(sorted(snaps.iterdir())[-1])


def shipped_arm(path: str):
    os.environ["MAK_LAYA_PATH"] = path
    return ce.shipped_predict


def xlmr_arm(path: pathlib.Path):
    import torch
    sys.path.insert(0, str(ROOT / "training"))
    from train_encoder_baseline import MultiHead
    from transformers import AutoConfig, AutoModel, AutoTokenizer
    ck = torch.load(path / "model.pt", map_location="cpu", weights_only=False)
    tok = AutoTokenizer.from_pretrained(path / "tokenizer")
    enc = AutoModel.from_config(AutoConfig.from_pretrained(ck["base"]))
    model = MultiHead(enc, ck["qids"], ck["opts"])
    model.load_state_dict(ck["state"])
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev).eval()
    opts, temps = ck["opts"], ck["temps"]

    @torch.no_grad()
    def predict(text, lang):
        b = tok([norm(text)], truncation=True, max_length=128, return_tensors="pt").to(dev)
        lg = model(b["input_ids"], b["attention_mask"])

        def top(q):
            p = torch.softmax(lg[q][0].float() / temps[q], -1)
            i = int(p.argmax())
            return opts[q][i], float(p[i])
        out = {q: top(q) for q in ("gender_signal", "topic", "family", "format")}
        sq = f"stat_{out['family'][0]}"
        if out["topic"][0] == "cricket_stat" and sq in lg:
            out["stat"] = top(sq)
        return out
    return predict


def qwen_arm():
    import predict as qp
    qp.load(str(QWEN_V2))
    return lambda text, lang: qp.predict(text, lang)


ARMS = {
    "a_rules": lambda: ce.rules_predict,
    "b_laya_zeroshot": lambda: laya_arm(laya_base_path()),
    "c_laya_ft": lambda: laya_arm(str(LAYA_V2)),
    "d_shipped": lambda: shipped_arm(str(LAYA_V2)),
    "e_qwen_lora": qwen_arm,
    "f_xlmr_ft": lambda: xlmr_arm(XLMR_V2),
}
NOTES = {
    "a_rules": "Rules are deterministic: confidence 1.0, so ECE is not meaningful for this arm.",
    "b_laya_zeroshot": "Base Laya, no fine-tuning, default temperatures (expected near chance).",
    "c_laya_ft": "Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.",
    "d_shipped": "understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.",
    "e_qwen_lora": "Qwen2.5-1.5B + LoRA v2; confidence = product of generated token probabilities, NOT calibrated; invalid JSON = error.",
    "f_xlmr_ft": "xlm-roberta-base v2, per-question temperature on calib.jsonl.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("dev", "test"), required=True)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--limit", type=int, default=None, help="dev only: first N rows per set")
    ap.add_argument("--i-confirm-single-run", action="store_true")
    a = ap.parse_args()
    if a.mode == "test":
        if not a.i_confirm_single_run:
            sys.exit("test mode needs --i-confirm-single-run (frozen test sets are scored once)")
        if LOCK.exists():
            sys.exit(f"{LOCK} exists: the single test run already happened. Do not rerun and present it as held-out.")
        if a.limit:
            sys.exit("--limit is not allowed in test mode")
        sets = {lang: ROOT / "testsets" / f"nlu_{lang}.csv" for lang in ("en", "hi", "ta")}
        out_dir = OUT / "test"
        OUT.mkdir(parents=True, exist_ok=True)
        LOCK.write_text(json.dumps({"started": time.strftime("%Y-%m-%d %H:%M"), "arms": a.arms}), encoding="utf-8")
    else:
        sets = {"calib": ROOT / "training" / "data" / "calib.jsonl", "messy": ROOT / "training" / "data" / "messy_calib.jsonl"}
        out_dir = OUT / "dev"
    md = [f"## Classifier evaluation, mode={a.mode}, {time.strftime('%Y-%m-%d %H:%M')}", ""]
    if a.mode == "dev":
        md.append("DEVELOPMENT numbers on template-labelled calibration data. NOT test results; do not quote as accuracy.\n")
    else:
        md.append("Frozen test sets (Joanna K-P2, testsets/FROZEN.md). This single run is ALSO the model-selection run "
                  "(disclosed per K-P2 handoff). Labels follow the product policy; training templates differ on weak cues, "
                  "mixed-gender pairs and injection rows (G-022), not relabelled.\n")
    for arm in a.arms.split(","):
        t0 = time.time()
        try:
            fn = ARMS[arm]()
        except Exception as exc:  # noqa: BLE001 - a missing arm is reported, not hidden
            md += [f"### {arm}", "", f"- NOT RUN: {type(exc).__name__}: {exc}", ""]
            print(arm, "NOT RUN", exc, flush=True)
            continue
        for name, path in sets.items():
            res = ce.evaluate(fn, path, limit=a.limit)
            ce.save(f"{arm}_{name}", res, out_dir)
            md.append(ce.to_markdown(f"{arm} on {name}", res, NOTES[arm]))
            print(arm, name, {f"{r['q']}/{r['lang']}": round(r["acc"], 3) for r in res["by_q_lang"]}, flush=True)
        md.append(f"_({arm} wall time {time.time() - t0:.0f}s)_\n")
        import gc
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:  # noqa: BLE001
            pass
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote", out_dir / "report.md")


if __name__ == "__main__":
    main()
