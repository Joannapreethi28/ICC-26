"""Comparison arm: fine-tune a plain multilingual encoder (default xlm-roberta-base) on the SAME frozen data. OWNER: Jabin.

One shared encoder + one linear head per question (gender_signal, topic, family, format, stat_<family>).
Same train.jsonl / calib.jsonl, same per-question temperature scaling, same report format as train_laya.py,
so the winner can be chosen on held-out per-language results only.
Never reads testsets/ or eval_data/.

  python training/train_encoder_baseline.py --smoke
  python training/train_encoder_baseline.py --model FacebookAI/xlm-roberta-base --name xlmr-mak-v1
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import random
import time

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "training" / "data"
SEED = 20261003
EPOCHS = 3
MICRO_BATCH = 16
GRAD_ACCUM = 2
LR_ENCODER = 3e-5
LR_HEAD = 1e-3
MAX_LEN = 128
TEMP_MIN, TEMP_MAX = 0.5, 5.0


def log(m=""):
    print(m, flush=True)


def load_rows(path, limit=None):
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f):
            if limit and n >= limit:
                break
            rows.append(json.loads(line))
    return rows


def option_sets(rows):
    """qid -> ordered option list (union over rows; stat_<family> options are per family)."""
    opts = collections.OrderedDict()
    for r in rows:
        for qid, q in r["questions"].items():
            cur = opts.setdefault(qid, [])
            for k in q["criteria"]:
                if k not in cur:
                    cur.append(k)
    return opts


def encode_rows(rows, opts, tok):
    enc = tok([r["state"] for r in rows], truncation=True, max_length=MAX_LEN)
    out = []
    for i, r in enumerate(rows):
        labels = {}
        for qid, g in r["gold"].items():
            p = g["probabilities"]
            best = max(p, key=p.get)
            labels[qid] = opts[qid].index(best)
        out.append({"ids": enc["input_ids"][i], "labels": labels, "lang": r["meta"]["lang"]})
    return out


def collate(items, qids, pad_id):
    L = max(len(it["ids"]) for it in items)
    ids = torch.full((len(items), L), pad_id, dtype=torch.long)
    att = torch.zeros((len(items), L), dtype=torch.long)
    y = torch.full((len(items), len(qids)), -100, dtype=torch.long)
    for i, it in enumerate(items):
        ids[i, : len(it["ids"])] = torch.tensor(it["ids"])
        att[i, : len(it["ids"])] = 1
        for j, q in enumerate(qids):
            if q in it["labels"]:
                y[i, j] = it["labels"][q]
    return ids, att, y


class MultiHead(nn.Module):
    def __init__(self, enc, qids, opts):
        super().__init__()
        self.enc, self.qids = enc, qids
        h = enc.config.hidden_size
        self.drop = nn.Dropout(0.1)
        self.heads = nn.ModuleDict({q: nn.Linear(h, len(opts[q])) for q in qids})

    def forward(self, ids, att):
        x = self.enc(input_ids=ids, attention_mask=att).last_hidden_state[:, 0]
        x = self.drop(x)
        return {q: self.heads[q](x) for q in self.qids}


def fit_temp(Z, y):
    if len(y) < 10:
        return 1.0
    Z, y = torch.tensor(np.array(Z)), torch.tensor(y)
    lt = torch.zeros(1, requires_grad=True)
    opt = torch.optim.LBFGS([lt], lr=0.1, max_iter=100)

    def closure():
        opt.zero_grad()
        loss = nn.functional.cross_entropy(Z / lt.exp(), y)
        loss.backward()
        return loss

    opt.step(closure)
    return float(torch.clamp(lt.exp(), TEMP_MIN, TEMP_MAX))


def ece(conf, ok, bins=10):
    conf, ok = np.array(conf), np.array(ok, dtype=float)
    e = 0.0
    for b in range(bins):
        m = (conf > b / bins) & (conf <= (b + 1) / bins)
        if m.any():
            e += m.mean() * abs(ok[m].mean() - conf[m].mean())
    return e


@torch.no_grad()
def predict(model, items, qids, pad_id, dev):
    model.eval()
    out = {q: [] for q in qids}
    for i in range(0, len(items), 64):
        ids, att, y = collate(items[i:i + 64], qids, pad_id)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = model(ids.to(dev), att.to(dev))
        for j, q in enumerate(qids):
            for r in range(len(y)):
                out[q].append((lg[q][r].float().cpu().numpy(), int(y[r, j])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="FacebookAI/xlm-roberta-base")
    ap.add_argument("--name", default="xlmr-mak-v1")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    a = ap.parse_args()
    dev = torch.device("cuda")
    random.seed(SEED)
    torch.manual_seed(SEED)

    tok = AutoTokenizer.from_pretrained(a.model)
    tr_rows = load_rows(DATA / "train.jsonl", 600 if a.smoke else None)
    ca_rows = load_rows(DATA / "calib.jsonl", 300 if a.smoke else None)
    opts = option_sets(tr_rows + ca_rows)
    qids = list(opts)
    train = encode_rows(tr_rows, opts, tok)
    calib = encode_rows(ca_rows, opts, tok)
    log(f"train rows {len(train)} calib rows {len(calib)} questions {len(qids)}")

    model = MultiHead(AutoModel.from_pretrained(a.model, use_safetensors=True), qids, opts).to(dev)
    model.enc.gradient_checkpointing_enable()
    groups = [{"params": model.enc.parameters(), "lr": LR_ENCODER}, {"params": model.heads.parameters(), "lr": LR_HEAD}]
    optim = torch.optim.AdamW(groups, weight_decay=0.01)
    epochs = 1 if a.smoke else a.epochs
    total = max(1, (len(train) // (MICRO_BATCH * GRAD_ACCUM)) * epochs)
    sched = torch.optim.lr_scheduler.OneCycleLR(optim, max_lr=[LR_ENCODER, LR_HEAD], total_steps=total + 1, pct_start=0.06)
    t0, upd = time.time(), 0
    for ep in range(epochs):
        model.train()
        random.Random(SEED + ep).shuffle(train)
        nb = 0
        for b in range(0, len(train) - MICRO_BATCH + 1, MICRO_BATCH):
            ids, att, y = collate(train[b:b + MICRO_BATCH], qids, tok.pad_token_id)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                lg = model(ids.to(dev), att.to(dev))
            y = y.to(dev)
            losses = [nn.functional.cross_entropy(lg[q].float(), y[:, j], ignore_index=-100) for j, q in enumerate(qids) if (y[:, j] >= 0).any()]
            loss = sum(losses) / len(losses)
            (loss / GRAD_ACCUM).backward()
            nb += 1
            if nb % GRAD_ACCUM == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optim.step()
                sched.step()
                optim.zero_grad(set_to_none=True)
                upd += 1
                if upd % 20 == 0 or a.smoke:
                    log(f"  ep {ep + 1}/{epochs} upd {upd}/{total} loss {loss.item():.4f} | {time.time() - t0:.0f}s | peak {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
                if a.smoke and upd >= 10:
                    log(f"SMOKE ok: {(time.time() - t0) / upd:.2f}s/update; est full {(time.time() - t0) / upd * (11000 // (MICRO_BATCH * GRAD_ACCUM)) * EPOCHS / 60:.0f} min")
                    return

    pred = predict(model, calib, qids, tok.pad_token_id, dev)
    temps = {}
    for q in qids:
        pq = [(z, y) for z, y in pred[q] if y >= 0]
        temps[q] = fit_temp([z for z, _ in pq], [y for _, y in pq])
    lines = ["| lang | question | n | accuracy | ECE before | ECE after |", "|---|---|---|---|---|---|"]
    tot = collections.defaultdict(lambda: [0, 0])
    for lang in ("en", "hi", "ta"):
        for q in qids:
            idx = [i for i, it in enumerate(calib) if it["lang"] == lang and q in it["labels"]]
            if not idx:
                continue
            c0, c1, ok = [], [], []
            for i in idx:
                z, y = pred[q][i]
                p0, p1 = torch.softmax(torch.tensor(z), -1).numpy(), torch.softmax(torch.tensor(z) / temps[q], -1).numpy()
                c0.append(p0.max()); c1.append(p1.max()); ok.append(int(p1.argmax() == y))
            lines.append(f"| {lang} | {q} | {len(idx)} | {np.mean(ok):.3f} | {ece(c0, ok):.3f} | {ece(c1, ok):.3f} |")
            tot[lang][0] += sum(ok); tot[lang][1] += len(ok)
    lines += ["", "Overall accuracy per language (calibration set): " + ", ".join(f"{l}={s / n:.3f}" for l, (s, n) in sorted(tot.items()))]

    out = ROOT / "models" / a.name
    out.mkdir(parents=True, exist_ok=True)
    torch.save({"state": model.state_dict(), "qids": qids, "opts": dict(opts), "temps": temps, "base": a.model}, out / "model.pt")
    tok.save_pretrained(out / "tokenizer")
    res = ROOT / "results"
    res.mkdir(exist_ok=True)
    with (res / "training_log.md").open("a", encoding="utf-8") as f:
        f.write(f"\n## {a.name} ({a.model}) run, {time.strftime('%Y-%m-%d %H:%M')}\n\n- epochs {epochs}, batch {MICRO_BATCH}x{GRAD_ACCUM}, LR enc {LR_ENCODER} head {LR_HEAD}, max_len {MAX_LEN}, seed {SEED}, wall {time.time() - t0:.0f}s\n")
        f.write(f"- temperatures per question: {json.dumps({q: round(t, 3) for q, t in temps.items()})}\n\nCalibration-set results (MEASURED, template-disjoint calib data; NOT headline test accuracy):\n\n" + "\n".join(lines) + "\n")
    log("\n".join(lines))


if __name__ == "__main__":
    main()
