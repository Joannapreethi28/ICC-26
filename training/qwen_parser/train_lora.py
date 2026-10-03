"""SFT Qwen2.5-1.5B-Instruct + LoRA r=16 on the SAME frozen train.jsonl (buildplan T2.4). OWNER: Jabin.
Loss only on the assistant JSON (prompt-completion format). Offline, bf16, gradient checkpointing, 8 GB GPU.
Never reads testsets/ or eval_data/.

  python training/qwen_parser/train_lora.py --smoke     # 10 steps: speed + memory, saves nothing
  python training/qwen_parser/train_lora.py             # -> models/qwen-mak-lora-v1/
"""
import argparse
import json
import os
import time

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from datasets import Dataset  # noqa: E402
from peft import LoraConfig  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
from trl import SFTConfig, SFTTrainer  # noqa: E402

from common import BASE_MODEL, BASE_REVISION, ROOT, to_example  # noqa: E402

SEED = 20261003


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--epochs", type=float, default=1.0)
    a = ap.parse_args()
    rows = [json.loads(x) for x in open(ROOT / "training" / "data" / "train.jsonl", encoding="utf-8")]
    ds = Dataset.from_list([to_example(r) for r in rows]).shuffle(seed=SEED)
    if a.smoke:
        ds = ds.select(range(200))
    tok = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_REVISION)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, revision=BASE_REVISION, dtype=torch.bfloat16, use_safetensors=True)
    out = ROOT / "models" / "qwen-mak-lora-v1"
    cfg = SFTConfig(
        output_dir=str(out), num_train_epochs=a.epochs, max_steps=10 if a.smoke else -1,
        per_device_train_batch_size=8, gradient_accumulation_steps=4, learning_rate=2e-4, lr_scheduler_type="cosine",
        bf16=True, gradient_checkpointing=True, max_length=512, completion_only_loss=True, packing=False,
        logging_steps=1 if a.smoke else 20, save_strategy="no", report_to="none", seed=SEED,
    )
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds, processing_class=tok, peft_config=lora)
    t0 = time.time()
    trainer.train()
    sec = time.time() - t0
    peak = torch.cuda.max_memory_allocated() / 1e9
    steps = trainer.state.global_step
    if a.smoke:
        full = len(rows) / 32 * a.epochs
        print(f"SMOKE: {sec / steps:.2f}s/step, peak {peak:.2f} GB, est full run {sec / steps * full / 60:.0f} min ({full:.0f} steps)")
        return
    trainer.save_model(str(out))
    tok.save_pretrained(str(out))
    (ROOT / "results").mkdir(exist_ok=True)
    with open(ROOT / "results" / "training_log.md", "a", encoding="utf-8") as f:
        f.write(f"\n## Qwen LoRA parser run, {time.strftime('%Y-%m-%d %H:%M')}\n\n- base {BASE_MODEL}@{BASE_REVISION[:12]}, "
                f"LoRA r=16 alpha=32 dropout 0.05 on all attention+MLP projections, epochs {a.epochs}, batch 8x4, LR 2e-4 cosine, "
                f"bf16, completion-only loss, seed {SEED}; {len(rows)} train rows; wall {sec:.0f}s, peak GPU {peak:.2f} GB, "
                f"final train loss {trainer.state.log_history[-1].get('train_loss', 'n/a')}\n")
    print(f"saved {out}")


if __name__ == "__main__":
    main()
