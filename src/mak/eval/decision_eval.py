"""E4 end-to-end decision accuracy (docs/11 E4, buildplan T2.5 Step 3). OWNER: Jabin.

raw query -> understand(use_laya=...) -> catalogue lookup -> policy decide() -> decision, compared with the frozen
expected_decision column. Per language, slice and source, Wilson 95% CI, plus a confusion table.

  python -m mak.eval.decision_eval --arm rules|shipped [--laya models/laya-mak-v3] [--tag v3]
Writes results/e4/<arm>_<tag>.json and .md. Labelled post-hoc when the model was changed after the official test run.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import Counter, defaultdict

from mak import config
from mak.eval.classifier_eval import wilson
from mak.fetch.catalogue import lookup
from mak.nlu.understand import understand
from mak.policy.decide import decide

SETS = [config.TESTSET_DIR / f"nlu_{lang}.csv" for lang in ("en", "hi", "ta")]


def run(use_laya: bool) -> list[dict]:
    out = []
    for path in SETS:
        for r in csv.DictReader(path.open(encoding="utf-8", newline="")):
            p = understand(r["text"], r["lang"], use_laya=use_laya)
            supported = bool(lookup(p.family, p.stat, p.format)) if p.topic == "cricket_stat" else False
            dec, _ = decide(p, supported)
            out.append({"id": r["id"], "lang": r["lang"], "slice": r.get("slice", ""), "source": r.get("source", ""),
                        "gold": r["expected_decision"], "pred": dec, "ok": int(dec == r["expected_decision"])})
    return out


def table(recs, key):
    g = defaultdict(list)
    for x in recs:
        g[x[key]].append(x["ok"])
    return {k: {"n": len(v), "acc": sum(v) / len(v), "ci": wilson(sum(v), len(v))} for k, v in sorted(g.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("rules", "shipped"), required=True)
    ap.add_argument("--laya", default=None)
    ap.add_argument("--tag", default="official")
    a = ap.parse_args()
    if a.laya:
        os.environ["MAK_LAYA_PATH"] = a.laya
    recs = run(a.arm == "shipped")
    res = {"arm": a.arm, "tag": a.tag, "laya": a.laya, "gender_threshold": config.GENDER_THRESHOLD, "when": time.strftime("%Y-%m-%d %H:%M"),
           "overall": table(recs, "lang"), "by_slice": table([dict(x, k=f"{x['lang']}/{x['slice']}") for x in recs], "k"),
           "by_source": table([dict(x, k=f"{x['lang']}/{x['source']}") for x in recs], "k"),
           "confusion": dict(Counter(f"{x['gold']} -> {x['pred']}" for x in recs).most_common())}
    out = config.RESULTS_DIR / "e4"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.arm}_{a.tag}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    for lang, v in res["overall"].items():
        print(f"{a.arm} {a.tag} {lang}: decision accuracy {v['acc']:.3f} (95% CI {v['ci'][0]:.3f}-{v['ci'][1]:.3f}, n={v['n']})")


if __name__ == "__main__":
    main()
