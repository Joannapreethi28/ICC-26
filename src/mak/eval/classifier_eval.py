"""Classifier evaluation (buildplan T2.3, docs/11 E2, gates in docs/09 §6). OWNER: Jabin.

evaluate(predict_fn, testset_path) -> dict
  predict_fn(text, lang) -> {question: (label, confidence)} for gender_signal, topic, family, stat, format.
  testset_path: a frozen test CSV (labels.TESTSET_COLUMNS) or, for development only, a training-format JSONL
  (calib.jsonl / messy_calib.jsonl). Development numbers are NOT test results and must be labelled as such.
Reports accuracy per question x language / slice / source with Wilson 95% intervals, ECE (15 bins), confusion matrices,
confident errors (wrong with confidence >= 0.9), optional option-order sensitivity, latency p50/p95.
"""
from __future__ import annotations

import csv
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

QUESTIONS = ("gender_signal", "topic", "family", "stat", "format")
Pred = dict[str, tuple[str, float]]
PredictFn = Callable[[str, str], Pred]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def ece(conf: list[float], ok: list[int], bins: int = 15) -> float:
    n = len(conf)
    if n == 0:
        return 0.0
    tot = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, c in enumerate(conf) if (lo < c <= hi) or (b == 0 and c == 0.0)]
        if idx:
            tot += len(idx) / n * abs(sum(ok[i] for i in idx) / len(idx) - sum(conf[i] for i in idx) / len(idx))
    return tot


def load_rows(path: str | Path) -> list[dict]:
    path = Path(path)
    rows = []
    if path.suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                rows.append({"id": r["id"], "lang": r["lang"], "text": r["text"], "slice": r.get("slice", ""),
                             "source": r.get("source", ""), **{q: (r.get(q) or None) for q in QUESTIONS}})
    else:
        for i, line in enumerate(path.open(encoding="utf-8")):
            r = json.loads(line)
            m = r["meta"]
            rows.append({"id": f"{path.stem}-{i}", "lang": m["lang"], "text": r["state"], "slice": m.get("slice", ""),
                         "source": m.get("source", ""), **{q: m.get(q) for q in QUESTIONS}})
    for r in rows:  # stat/family/format only scored for cricket_stat rows
        if r["topic"] != "cricket_stat":
            r["family"] = r["stat"] = r["format"] = None
    return rows


def _pct(xs: list[float], q: float) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    return s[min(len(s) - 1, int(round(q * (len(s) - 1))))]


def evaluate(predict_fn: PredictFn, testset_path: str | Path, shuffled_fn: PredictFn | None = None,
             limit: int | None = None) -> dict:
    rows = load_rows(testset_path)[:limit] if limit else load_rows(testset_path)
    lat, recs, changed, n_shuf = [], [], 0, 0
    for r in rows:
        t0 = time.perf_counter()
        try:
            pred, err = predict_fn(r["text"], r["lang"]), None
        except Exception as exc:  # noqa: BLE001 - an error is a scored miss, never a crash
            pred, err = {}, f"{type(exc).__name__}: {exc}"
        lat.append((time.perf_counter() - t0) * 1000)
        if shuffled_fn is not None:
            try:
                sp = shuffled_fn(r["text"], r["lang"])
                n_shuf += 1
                changed += any(sp.get(q, (None,))[0] != pred.get(q, (None,))[0] for q in ("gender_signal", "topic", "family"))
            except Exception:  # noqa: BLE001
                pass
        for q in QUESTIONS:
            gold = r[q]
            if gold is None:
                continue
            label, conf = pred.get(q, (None, 0.0))
            recs.append({"id": r["id"], "lang": r["lang"], "slice": r["slice"], "source": r["source"], "q": q,
                         "gold": gold, "pred": label, "conf": float(conf), "ok": int(label == gold), "text": r["text"],
                         "error": err})

    def table(keys: tuple[str, ...]) -> list[dict]:
        groups = defaultdict(list)
        for x in recs:
            groups[tuple(x[k] for k in keys)].append(x)
        out = []
        for key, xs in sorted(groups.items()):
            k, n = sum(x["ok"] for x in xs), len(xs)
            lo, hi = wilson(k, n)
            out.append({**dict(zip(keys, key)), "n": n, "acc": k / n, "lo": lo, "hi": hi,
                        "ece": ece([x["conf"] for x in xs], [x["ok"] for x in xs])})
        return out

    confusion = {q: Counter((x["gold"], x["pred"]) for x in recs if x["q"] == q) for q in QUESTIONS}
    return {
        "testset": str(testset_path), "n_queries": len(rows),
        "by_q_lang": table(("q", "lang")), "by_q_slice": table(("q", "slice")), "by_q_source": table(("q", "source")),
        "confusion": {q: {f"{g} -> {p}": c for (g, p), c in sorted(cm.items(), key=lambda kv: -kv[1])} for q, cm in confusion.items()},
        "confident_errors": [x for x in recs if not x["ok"] and x["conf"] >= 0.9],
        "errors": sum(1 for r in recs if r["error"]),
        "option_order_changed": (changed / n_shuf) if n_shuf else None,
        "latency_ms": {"p50": _pct(lat, 0.5), "p95": _pct(lat, 0.95)},
        "records": recs,
    }


def gates(res: dict) -> list[str]:
    """docs/09 §6 targets, checked per language (proposed targets, not results)."""
    tgt = {"gender_signal": {"en": .98, "hi": .98, "ta": .98},
           "stat": {"en": .90, "hi": .85, "ta": .80}, "format": {"en": .90, "hi": .85, "ta": .80}}
    out = []
    for row in res["by_q_lang"]:
        t = tgt.get(row["q"], {}).get(row["lang"])
        if t is not None:
            out.append(f"{row['q']} {row['lang']}: {row['acc']:.3f} (95% CI {row['lo']:.3f}-{row['hi']:.3f}, n={row['n']}) "
                       f"target {t:.2f} -> {'MET' if row['acc'] >= t else 'MISSED'}")
    return out


def to_markdown(name: str, res: dict, note: str) -> str:
    L = [f"### {name}", "", f"- set: `{res['testset']}` ({res['n_queries']} queries). {note}",
         f"- latency per query p50 {res['latency_ms']['p50']:.1f} ms, p95 {res['latency_ms']['p95']:.1f} ms; "
         f"prediction errors {res['errors']}; confident errors (conf >= 0.9) {len(res['confident_errors'])}"]
    if res["option_order_changed"] is not None:
        L.append(f"- option-order sensitivity: {res['option_order_changed']:.1%} of queries changed a top label")
    L += ["", "| question | lang | n | accuracy | 95% CI | ECE |", "|---|---|---|---|---|---|"]
    L += [f"| {r['q']} | {r['lang']} | {r['n']} | {r['acc']:.3f} | {r['lo']:.3f}-{r['hi']:.3f} | {r['ece']:.3f} |" for r in res["by_q_lang"]]
    L += ["", "Gates (docs/09 §6):", ""] + [f"- {g}" for g in gates(res)] + [""]
    return "\n".join(L)


def save(name: str, res: dict, out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with (out / f"{name}_records.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res["records"][0].keys()) if res["records"] else ["id"])
        w.writeheader()
        w.writerows(res["records"])
    slim = {k: v for k, v in res.items() if k != "records"}
    (out / f"{name}_summary.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")


def rules_predict(text: str, lang: str) -> Pred:
    """Baseline (a). Rules are deterministic: confidence 1.0 for a fired rule, 0.0 when gender has no cue."""
    from mak.nlu.rules import rules_parse
    p = rules_parse(text, lang)
    return {"gender_signal": (p.gender_signal, p.gender_conf if p.gender_signal != "none" else 1.0),
            "topic": (p.topic, 1.0), "family": (p.family, 1.0), "stat": (p.stat, 1.0), "format": (p.format, 1.0)}


def shipped_predict(text: str, lang: str, policy: str | None = None) -> Pred:
    """Baseline (d): understand(use_laya=True), i.e. fine-tuned model + rules override (merge policy v1/v2)."""
    from mak.nlu import understand as u
    if policy:
        old, u.MERGE_POLICY = u.MERGE_POLICY, policy
        try:
            p = u.understand(text, lang, use_laya=True)
        finally:
            u.MERGE_POLICY = old
    else:
        p = u.understand(text, lang, use_laya=True)
    return {"gender_signal": (p.gender_signal, p.gender_conf), "topic": (p.topic, 1.0), "family": (p.family, 1.0),
            "stat": (p.stat, 1.0), "format": (p.format, 1.0)}
