"""E3 cross-sport transfer (docs/11 E3): gender/topic on testsets/xsport.csv, never seen in training or model selection.
OWNER: Jabin.  python -m mak.eval.e3_xsport --laya models/laya-mak-v3
"""
import argparse
import os

from mak import config
from mak.eval import classifier_eval as ce


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--laya", required=True)
    a = ap.parse_args()
    from mak.nlu.laya_head import LayaHead
    head = LayaHead.load(a.laya)
    os.environ["MAK_LAYA_PATH"] = a.laya
    arms = {"rules": ce.rules_predict, "laya_ft": lambda t, l: head.predict(t), "shipped": ce.shipped_predict}
    out = config.RESULTS_DIR / "e3"
    md = ["## E3 cross-sport (testsets/xsport.csv), first and only run with the selected model", ""]
    for name, fn in arms.items():
        res = ce.evaluate(fn, config.TESTSET_DIR / "xsport.csv")
        ce.save(f"xsport_{name}", res, out)
        md.append(ce.to_markdown(f"{name} on xsport", res, f"model {a.laya}; only gender_signal/topic are meaningful here"))
        print(name, {f"{r['q']}/{r['lang']}": round(r["acc"], 3) for r in res["by_q_lang"] if r["q"] in ("gender_signal", "topic")})
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
