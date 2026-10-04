"""Fine-tune laya-multilingual on our frozen data, single GPU, offline. OWNER: Jabin.

Adapted from Laya's official Kaggle notebook recipe (policy-gradient reward + soft cross-entropy), with these changes:
  * one GPU (no DDP/nccl), bf16 autocast (no GradScaler), gradient checkpointing for 8 GB VRAM
  * calibration set = training/data/calib.jsonl (template families disjoint from training), not a random slice
  * temperatures fitted per (question type, option-count bucket), clamped to [TEMP_MIN, TEMP_MAX]
  * per-language, per-question accuracy and ECE (before/after calibration) written to results/training_log.md
Never reads testsets/ or eval_data/.

Run from repo root:
  python training/finetune/train_laya.py --smoke          # 15 optimiser steps, prints speed + memory, saves nothing
  python training/finetune/train_laya.py                  # full run -> models/laya-mak-v1/
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import random
import sys
import time

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import numpy as np
import torch
from safetensors.torch import load_file, save_file
from transformers import AutoTokenizer

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src")]

from laya.agent import _fix_tokenizer_config  # noqa: E402
from mak.nlu.laya_head import normalise_for_model  # noqa: E402
from laya.common import (QTYPES, TEMP_MAX, TEMP_MIN, build_model, build_sequence, ece_score,  # noqa: E402
                         proper_reward, render_options, temp_bucket)

MODEL_ID = "convaiinnovations/laya-multilingual"
DATA = ROOT / "training" / "data"
SEED = 20261003
EPOCHS = 2  # v2: 3 epochs saturated the logits (G-026)
LABEL_SMOOTHING = 0.05  # v2: on the cross-entropy target only; the reward keeps the hard target
MICRO_BATCH = 8
GRAD_ACCUM = 4
GROUP_SIZE = 4
LR_ENCODER = 2.5e-5
LR_HEAD = 1.0e-4
SIGMA_START, SIGMA_END = 0.4, 0.1
MAX_LEN, HEAD_MAX_LEN = 512, 256


def log(msg: str = "") -> None:
    print(msg, flush=True)


def build_item(tok, cfg, state, q, gold_q, qid, lang):
    t, crit = q["type"], q.get("criteria", {})
    assert t == "choice", t
    keys = list(crit.keys())
    target = [gold_q["probabilities"].get(k, 0.0) for k in keys]
    s = sum(target)
    target = [v / s for v in target]
    seq, markers = build_sequence(tok, state, {"t": t, "ins": q["instructions"], "crit": crit}, cfg["max_len"], cfg["head_max_len"])
    if len(markers) != len(render_options({"t": t, "crit": crit})):
        return None
    return {"ids": seq, "markers": markers, "qtype": QTYPES[t], "target": target, "label": target.index(max(target)),
            "qid": qid, "lang": lang}


def load_items(path, tok, cfg, limit=None):
    items, dropped = [], 0
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f):
            if limit and n >= limit:
                break
            row = json.loads(line)
            lang = row["meta"]["lang"]
            for qid, q in row["questions"].items():
                it = build_item(tok, cfg, normalise_for_model(row["state"]), q, row["gold"][qid], qid, lang)
                if it is None:
                    dropped += 1
                else:
                    items.append(it)
    return items, dropped


def collate(items, pad_id):
    n, L = len(items), max(len(it["ids"]) for it in items)
    kmax = max(len(it["markers"]) for it in items)
    ids = torch.full((n, L), pad_id, dtype=torch.long)
    att = torch.zeros((n, L), dtype=torch.long)
    mpos = torch.zeros((n, kmax), dtype=torch.long)
    mmask = torch.zeros((n, kmax), dtype=torch.bool)
    target = torch.zeros((n, kmax), dtype=torch.float32)
    for i, it in enumerate(items):
        ids[i, : len(it["ids"])] = torch.tensor(it["ids"])
        att[i, : len(it["ids"])] = 1
        k = len(it["markers"])
        mpos[i, :k] = torch.tensor(it["markers"])
        mmask[i, :k] = True
        target[i, : len(it["target"])] = torch.tensor(it["target"], dtype=torch.float32)
    return {"input_ids": ids, "attention_mask": att, "marker_pos": mpos, "marker_mask": mmask, "target": target,
            "qtype": torch.tensor([it["qtype"] for it in items])}


def fit_one_temp(sel):
    if len(sel) < 10:
        return 1.0
    kmax = max(len(z) for z, _ in sel)
    Z = torch.full((len(sel), kmax), -1e4)
    T = torch.zeros((len(sel), kmax))
    for i, (z, t) in enumerate(sel):
        Z[i, : len(z)] = torch.tensor(z)
        T[i, : len(t)] = torch.tensor(t, dtype=torch.float32)
    log_t = torch.zeros(1, requires_grad=True)
    opt = torch.optim.LBFGS([log_t], lr=0.1, max_iter=100)

    def closure():
        opt.zero_grad()
        loss = -(T * torch.log_softmax(Z / log_t.exp(), -1)).sum(-1).mean()
        loss.backward()
        return loss

    opt.step(closure)
    return float(torch.clamp(log_t.exp(), TEMP_MIN, TEMP_MAX).item())


@torch.no_grad()
def collect_logits(model, items, pad_id, device):
    model.eval()
    out = []
    for i in range(0, len(items), 16):
        chunk = items[i:i + 16]
        b = collate(chunk, pad_id)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits, _ = model(b["input_ids"].to(device), b["attention_mask"].to(device), b["marker_pos"].to(device),
                              b["marker_mask"].to(device), b["qtype"].to(device))
        arr = logits.float().cpu().numpy()
        for r, it in enumerate(chunk):
            out.append(arr[r, : len(it["markers"])])
    return out


def softmax_t(z, t):
    z = np.asarray(z, dtype=np.float64) / t
    z -= z.max()
    p = np.exp(z)
    return p / p.sum()


def report(items, logits, temps_by_bucket, base_t):
    """Accuracy and ECE per (lang, qid), before and after calibration. Returns markdown lines."""
    groups = collections.defaultdict(list)
    for it, z in zip(items, logits):
        groups[(it["lang"], it["qid"])].append((it, z))
    lines = ["| lang | question | n | accuracy | ECE before | ECE after |", "|---|---|---|---|---|---|"]
    tot = collections.defaultdict(lambda: [0, 0])
    for (lang, qid), rows in sorted(groups.items()):
        c0, c1, ok = [], [], []
        for it, z in rows:
            k = len(it["markers"])
            t = temps_by_bucket.get(temp_bucket(it["qtype"], k), base_t)
            p0, p1 = softmax_t(z, 1.0), softmax_t(z, t)
            c0.append(p0.max())
            c1.append(p1.max())
            ok.append(int(p1.argmax() == it["label"]))
        lines.append(f"| {lang} | {qid} | {len(rows)} | {np.mean(ok):.3f} | {ece_score(np.array(c0), np.array(ok)):.3f} | "
                     f"{ece_score(np.array(c1), np.array(ok)):.3f} |")
        tot[lang][0] += sum(ok)
        tot[lang][1] += len(ok)
    lines.append("")
    lines.append("Overall accuracy per language (all questions, calibration set): " +
                 ", ".join(f"{l}={a / n:.3f}" for l, (a, n) in sorted(tot.items())))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--out", default=str(ROOT / "models" / "laya-mak-v3"))
    args = ap.parse_args()
    assert torch.cuda.is_available(), "CUDA not available"
    device = torch.device("cuda")
    random.seed(SEED)
    torch.manual_seed(SEED)

    snaps = pathlib.Path.home() / ".cache" / "huggingface" / "hub" / "models--convaiinnovations--laya-multilingual" / "snapshots"
    model_dir = str(sorted(snaps.iterdir())[-1])
    _fix_tokenizer_config(model_dir)
    with open(os.path.join(model_dir, "rl_agent_config.json")) as f:
        cfg = json.load(f)
    cfg.update(gradient_checkpointing=True, max_len=MAX_LEN, head_max_len=HEAD_MAX_LEN)
    tok = AutoTokenizer.from_pretrained(os.path.join(model_dir, "tokenizer"))

    limit = 400 if args.smoke else None
    train_items, d1 = load_items(DATA / "train.jsonl", tok, cfg, limit)
    calib_items, d2 = load_items(DATA / "calib.jsonl", tok, cfg, 200 if args.smoke else None)
    log(f"train sequences {len(train_items)} (dropped {d1}) | calib sequences {len(calib_items)} (dropped {d2})")
    lens = [len(it["ids"]) for it in train_items]
    log(f"sequence length tokens: mean {np.mean(lens):.0f}, p95 {np.percentile(lens, 95):.0f}, max {max(lens)}")

    model = build_model(cfg, encoder_dir=os.path.join(model_dir, "encoder"))
    model.load_state_dict(load_file(os.path.join(model_dir, "model.safetensors")), strict=True)
    model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.head_checkpointing = True
    model.to(device)

    log("zero-shot (before training) calibration-set accuracy:")
    zs = collect_logits(model, calib_items[:600], tok.pad_token_id, device)
    zs_acc = collections.defaultdict(list)
    for it, z in zip(calib_items[:600], zs):
        zs_acc[it["qid"]].append(int(np.argmax(z) == it["label"]))
    log("  " + ", ".join(f"{q}={np.mean(v):.2f}" for q, v in sorted(zs_acc.items())))
    zs_lines = [f"{q}={np.mean(v):.2f}" for q, v in sorted(zs_acc.items())]

    enc_params = [p for n, p in model.named_parameters() if n.startswith("encoder.")]
    head_params = [p for n, p in model.named_parameters() if not n.startswith("encoder.")]
    optimizer = torch.optim.AdamW([{"params": enc_params, "lr": LR_ENCODER}, {"params": head_params, "lr": LR_HEAD}], weight_decay=0.01)
    epochs = 1 if args.smoke else args.epochs
    updates_per_epoch = len(train_items) // (MICRO_BATCH * GRAD_ACCUM)
    total_updates = max(1, updates_per_epoch * epochs)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_updates, eta_min=1e-6)
    log(f"epochs {epochs} | micro-batch {MICRO_BATCH} x accum {GRAD_ACCUM} = effective {MICRO_BATCH * GRAD_ACCUM} | "
        f"updates/epoch {updates_per_epoch} | LR enc {LR_ENCODER} head {LR_HEAD}")

    t0 = time.time()
    done_updates = 0
    for epoch in range(epochs):
        model.train()
        random.Random(SEED + epoch).shuffle(train_items)
        sigma = SIGMA_START + (SIGMA_END - SIGMA_START) * (epoch / max(1, epochs - 1))
        epoch_loss, nb = 0.0, 0
        optimizer.zero_grad(set_to_none=True)
        for b in range(0, len(train_items) - MICRO_BATCH + 1, MICRO_BATCH):
            batch = collate(train_items[b:b + MICRO_BATCH], tok.pad_token_id)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits, act = model(batch["input_ids"].to(device), batch["attention_mask"].to(device), batch["marker_pos"].to(device),
                                    batch["marker_mask"].to(device), batch["qtype"].to(device))
            logits = logits.float()
            mask = batch["marker_mask"].to(device)
            k = mask.sum(-1, keepdim=True).float()
            target = batch["target"].to(device)
            eps = torch.randn((GROUP_SIZE,) + logits.shape, device=device) * sigma * mask
            eps = (eps - eps.sum(-1, keepdim=True) / k) * mask
            z = logits.detach().unsqueeze(0) + eps
            q = torch.softmax(z.masked_fill(~mask, -1e4), -1)
            with torch.no_grad():
                r = proper_reward(q, target.unsqueeze(0), batch["qtype"].to(device), mask, w_sph=0.75, w_rps=1.0)
                adv = r - r.mean(0, keepdim=True)
                adv = adv / (adv.std() + 1e-6)
            logp = -(((z - logits.unsqueeze(0)) ** 2) * mask).sum(-1) / (2 * sigma ** 2)
            loss_rl = -(adv * logp).mean()
            smooth = (target * (1 - LABEL_SMOOTHING) + LABEL_SMOOTHING / k) * mask
            loss_ce = -(smooth * torch.log_softmax(logits.masked_fill(~mask, -1e4), -1)).sum(-1).mean()
            loss = (loss_rl + loss_ce) / GRAD_ACCUM + 0.0 * act.sum()
            loss.backward()
            nb += 1
            epoch_loss += loss.item() * GRAD_ACCUM
            if nb % GRAD_ACCUM == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                done_updates += 1
                if done_updates % 20 == 0 or args.smoke:
                    el = time.time() - t0
                    log(f"  epoch {epoch + 1}/{epochs} update {done_updates}/{total_updates} loss {loss.item() * GRAD_ACCUM:.4f} "
                        f"ce {loss_ce.item():.4f} | {el:.0f}s elapsed | peak GPU {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
                if args.smoke and done_updates >= 15:
                    break
        log(f"=== epoch {epoch + 1} done in {time.time() - t0:.0f}s, avg loss {epoch_loss / max(1, nb):.4f}")
        if args.smoke:
            sec = time.time() - t0
            per_update = sec / max(1, done_updates)
            est = per_update * updates_per_epoch * EPOCHS if limit is None else per_update * (len(train_items) / 400 and 1)
            log(f"SMOKE: {per_update:.2f}s per update ({MICRO_BATCH * GRAD_ACCUM} sequences); peak {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
            full_updates = (46000 // (MICRO_BATCH * GRAD_ACCUM)) * EPOCHS
            log(f"SMOKE: rough full-run estimate ~{per_update * full_updates / 60:.0f} min for ~46k sequences x {EPOCHS} epochs")
            return

    log("fitting calibration temperatures on calib.jsonl")
    logits = collect_logits(model, calib_items, tok.pad_token_id, device)
    by_bucket = collections.defaultdict(list)
    for it, z in zip(calib_items, logits):
        by_bucket[temp_bucket(it["qtype"], len(it["markers"]))].append((z, it["target"]))
    temps = {b: fit_one_temp(sel) for b, sel in by_bucket.items()}
    base_t = fit_one_temp([s for sel in by_bucket.values() for s in sel])
    log(f"temperatures by bucket: { {b: round(t, 3) for b, t in temps.items()} } | overall {base_t:.3f}")
    lines = report(calib_items, logits, temps, base_t)

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    save_file({k: v.half().contiguous().cpu() for k, v in model.state_dict().items()}, str(out / "model.safetensors"))
    model.encoder.config.save_pretrained(str(out / "encoder"))
    tok.save_pretrained(str(out / "tokenizer"))
    cfg.update(fine_tuned=True, model_name=pathlib.Path(args.out).name, temperature=[base_t, 1.0, 1.0], temperature_by_options=temps)
    (out / "rl_agent_config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    res = ROOT / "results"
    res.mkdir(exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M")
    with (res / "training_log.md").open("a", encoding="utf-8") as f:
        f.write(f"\n## Laya fine-tune run, {stamp}\n\n")
        f.write(f"- base: {MODEL_ID} (local cache, offline); data: training/data/train.jsonl ({len(train_items)} sequences), "
                f"calibration: calib.jsonl ({len(calib_items)} sequences); see training/DATA_FROZEN.md for hashes\n")
        f.write(f"- epochs {epochs}, micro-batch {MICRO_BATCH} x accum {GRAD_ACCUM} (effective {MICRO_BATCH * GRAD_ACCUM}), "
                f"LR encoder {LR_ENCODER} / head {LR_HEAD}, AdamW wd 0.01, cosine to 1e-6, grad clip 1.0, bf16, "
                f"max_len {MAX_LEN}, head_max_len {HEAD_MAX_LEN}, reward group {GROUP_SIZE}, sigma {SIGMA_START}->{SIGMA_END}, seed {SEED}, "
                f"label smoothing {LABEL_SMOOTHING} (CE only), text lowercased (normalise_for_model), out {out.name}\n")
        f.write(f"- wall time {time.time() - t0:.0f}s on {torch.cuda.get_device_name(0)}, peak GPU {torch.cuda.max_memory_allocated() / 1e9:.2f} GB\n")
        f.write(f"- zero-shot accuracy per question on first 600 calib sequences (MEASURED): {', '.join(zs_lines)}\n")
        f.write(f"- fitted temperatures (clamped {TEMP_MIN}-{TEMP_MAX}): {json.dumps({b: round(t, 3) for b, t in temps.items()})}\n\n")
        f.write("Calibration-set results (MEASURED on template-disjoint calibration data, NOT the frozen test sets; "
                "this is not the headline accuracy):\n\n")
        f.write("\n".join(lines) + "\n")
    log("\n".join(lines))
    log(f"saved to {out}")


if __name__ == "__main__":
    main()
