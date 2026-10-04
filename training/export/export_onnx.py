"""Export the shipped Laya to ONNX (+ int8 dynamic quantization) and measure size, CPU latency and agreement (buildplan T2.5).
OWNER: Jabin.  python training/export/export_onnx.py [--model models/laya-mak-v3]
Writes models/<name>-onnx/{model.onnx, model.int8.onnx} and results/onnx_check.json. Nothing is published.
"""
import argparse
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "training" / "finetune")]

import numpy as np  # noqa: E402
import torch  # noqa: E402
from safetensors.torch import load_file  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

from laya.common import build_model  # noqa: E402
from train_laya import collate, load_items  # noqa: E402


class Wrap(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, input_ids, attention_mask, marker_pos, marker_mask, qtype):
        logits, _ = self.m(input_ids, attention_mask, marker_pos, marker_mask, qtype)
        return logits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(ROOT / "models" / "laya-mak-v3"))
    a = ap.parse_args()
    src = pathlib.Path(a.model)
    out = src.parent / f"{src.name}-onnx"
    out.mkdir(exist_ok=True)
    cfg = json.loads((src / "rl_agent_config.json").read_text(encoding="utf-8"))
    cfg["gradient_checkpointing"] = False
    tok = AutoTokenizer.from_pretrained(str(src / "tokenizer"))
    model = build_model(cfg, encoder_dir=str(src / "encoder"))
    model.load_state_dict({k: v.float() for k, v in load_file(str(src / "model.safetensors")).items()}, strict=True)
    model.eval()
    items, _ = load_items(ROOT / "training" / "data" / "calib.jsonl", tok, cfg, limit=200)
    b = collate(items[:4], tok.pad_token_id)
    args = (b["input_ids"], b["attention_mask"], b["marker_pos"], b["marker_mask"], b["qtype"])
    names = ["input_ids", "attention_mask", "marker_pos", "marker_mask", "qtype"]
    dyn = {"input_ids": {0: "b", 1: "t"}, "attention_mask": {0: "b", 1: "t"}, "marker_pos": {0: "b", 1: "k"},
           "marker_mask": {0: "b", 1: "k"}, "qtype": {0: "b"}, "logits": {0: "b", 1: "k"}}
    fp32 = out / "model.onnx"
    torch.onnx.export(Wrap(model), args, str(fp32), input_names=names, output_names=["logits"], dynamic_axes=dyn,
                      opset_version=17, dynamo=False)
    from onnxruntime.quantization import QuantType, quantize_dynamic
    int8 = out / "model.int8.onnx"
    quantize_dynamic(str(fp32), str(int8), weight_type=QuantType.QInt8)
    import onnxruntime as ort
    res = {"model": str(src), "fp32_mb": round(fp32.stat().st_size / 2**20, 1), "int8_mb": round(int8.stat().st_size / 2**20, 1)}
    for tag, path in (("int8", int8),):
        sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        agree, lat = 0, []
        for it in items[:200]:
            bb = collate([it], tok.pad_token_id)
            feed = {n: bb[n].numpy() for n in names}
            t0 = time.perf_counter()
            onnx_logits = sess.run(None, feed)[0][0, : len(it["markers"])]
            lat.append((time.perf_counter() - t0) * 1000)
            with torch.no_grad():
                ref = Wrap(model)(*[bb[n] for n in names])[0, : len(it["markers"])].numpy()
            agree += int(np.argmax(onnx_logits) == np.argmax(ref))
        res[f"{tag}_top_label_agreement_vs_torch"] = agree / len(items[:200])
        res[f"{tag}_cpu_ms_per_question_row_p50"] = float(np.percentile(lat, 50))
        res[f"{tag}_cpu_ms_p95"] = float(np.percentile(lat, 95))
    (ROOT / "results" / "onnx_check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
