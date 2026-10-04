"""Calibration check + GENDER_THRESHOLD fit on calib.jsonl ONLY (buildplan T2.3 Step 2; never on test sets). OWNER: Jabin.

Temperatures per option-count bucket are fitted inside training/train_laya.py and stored in the model's
rl_agent_config.json. This script (1) reports gender ECE with those temperatures and (2) fits GENDER_THRESHOLD:
the lowest threshold t such that, on calibration rows where the RULES found no explicit cue (the only rows where the
threshold is used), Laya's accepted gender decisions (women/men/both_named with p >= t) are >= 98% correct, in EVERY
language. Below t the pipeline treats the question as neutral (show both). Writes results/calibration/gender_threshold.json.
config.py is changed by hand afterwards with a CONTRACT CHANGE message (shared file).

  python training/calibrate/fit_temperature.py [--model models/laya-mak-v2]
"""
import argparse
import json
import os
import pathlib
import sys

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src")]

from mak.eval.classifier_eval import ece  # noqa: E402
from mak.nlu.laya_head import LayaHead  # noqa: E402
from mak.nlu.rules import rules_parse  # noqa: E402

TARGET = 0.98
GRID = [round(0.50 + 0.01 * i, 2) for i in range(45)] + [round(0.950 + 0.001 * i, 3) for i in range(50)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(ROOT / "models" / "laya-mak-v3"))
    a = ap.parse_args()
    head = LayaHead.load(a.model)
    rows = [json.loads(x) for x in open(ROOT / "training" / "data" / "calib.jsonl", encoding="utf-8")]
    recs = []
    for r in rows:
        lang, gold = r["meta"]["lang"], r["meta"]["gender_signal"]
        g, p = head.predict(r["state"])["gender_signal"]
        rule = rules_parse(r["state"], lang)
        recs.append({"lang": lang, "gold": gold, "pred": g, "p": p, "rule_cue": rule.gender_conf >= 1.0 or rule.injection_suspected})
    out = {"model": a.model, "target": TARGET, "n_calib": len(recs), "per_lang": {}}
    for lang in ("en", "hi", "ta"):
        xs = [x for x in recs if x["lang"] == lang]
        out["per_lang"][lang] = {"gender_acc_all": sum(x["pred"] == x["gold"] for x in xs) / len(xs),
                                 "gender_ece_all": ece([x["p"] for x in xs], [int(x["pred"] == x["gold"]) for x in xs])}
    pool = [x for x in recs if not x["rule_cue"]]
    table = []
    for t in GRID:
        row = {"t": t}
        ok_all = True
        for lang in ("en", "hi", "ta"):
            acc = [x for x in pool if x["lang"] == lang and x["pred"] != "none" and x["p"] >= t]
            n_lang = sum(1 for x in pool if x["lang"] == lang)
            a_ = sum(x["pred"] == x["gold"] for x in acc) / len(acc) if acc else 1.0
            row[lang] = {"accepted": len(acc), "accuracy": round(a_, 4), "accept_rate": round(len(acc) / max(1, n_lang), 4)}
            ok_all &= a_ >= TARGET
        row["meets"] = ok_all
        table.append(row)
    chosen = next((r["t"] for r in table if r["meets"]), None)
    out.update(no_rule_cue_rows=len(pool), chosen_threshold=chosen, grid=table,
               note="fit on calibration data only; if None, no threshold reaches the target -> keep the safe default and report")
    dst = ROOT / "results" / "calibration"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "gender_threshold.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "grid"}, indent=1))
    for r in table[::5]:
        print(r)


if __name__ == "__main__":
    main()
