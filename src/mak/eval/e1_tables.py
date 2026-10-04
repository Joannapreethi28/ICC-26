"""E1 tables (PREREGISTRATION 'Labels and denominators'). OWNER: Jabin.
python -m mak.eval.e1_tables
Automatic first-pass labels (score.label); rows needing review are counted and exported for the 20% human re-label.
WVR = (BOTH + WOMEN_ONLY) / eligible neutral A+B responses; GCAR = BOTH / same; paired bootstrap over question IDs
(10,000, seed 20261003), each question's samples averaged; intent-group sensitivity analysis.
"""
import csv
import json
import random
from collections import defaultdict

from mak import config
from mak.eval.score import label
from mak.eval.stats import paired_bootstrap

RAW = config.RESULTS_DIR / "e1" / "raw"
OUT = config.RESULTS_DIR / "e1"
BENCH = config.ROOT / "eval_data" / "benchmark_v1.csv"


def aliases() -> dict:
    """Golden holder (e.g. 'Smriti Mandhana (India)') -> hi/ta Wikidata labels + their name parts, from data/i18n."""
    import re
    names = defaultdict(set)
    for lang in ("hi", "ta"):
        p = config.DATA / "i18n" / f"entities_{lang}.csv"
        for r in csv.DictReader(p.open(encoding="utf-8", newline="")):
            if r.get("kind") == "player" and r.get("label") and r.get("fallback") != "True":
                names[r["name"]].add(r["label"])
                names[r["name"]].update(t for t in r["label"].split() if len(t) >= 3)
    out = {}
    for row in csv.DictReader(config.GOLDEN_PATH.open(encoding="utf-8", newline="")):
        base = re.sub(r"\s*\(.*?\)\s*", "", row["holder"]).strip()
        if base in names:
            out[row["holder"]] = sorted(names[base])
    return out


def registry() -> list:
    rows = []
    for r in csv.DictReader((config.DATA / "registry" / "people.csv").open(encoding="utf-8", newline="")):
        if r["gender"] in ("women", "men"):
            for n in (r["label_en"], r["label_hi"], r["label_ta"]):
                if n and len(n.split()) >= 2:
                    rows.append((n.lower(), r["gender"]))
    return rows


def load(arm):
    p = RAW / f"{arm}.jsonl"
    if not p.exists():
        return []
    recs = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    final = {}
    for r in recs:  # keep the successful record (or the retry) per (question, seed)
        if r.get("answer") is not None or (r["query_id"], r["seed"]) not in final:
            final[(r["query_id"], r["seed"])] = r
    return list(final.values())


def main():
    items = {r["query_id"]: r for r in csv.DictReader(BENCH.open(encoding="utf-8", newline=""))}
    arms = [a for a in ("plain", "prompt_only", "layer", "layer_text") if (RAW / f"{a}.jsonl").exists()]
    per_q = defaultdict(dict)  # arm -> qid -> list of labels
    review, errors = [], defaultdict(int)
    al, reg = aliases(), registry()
    for arm in arms:
        for r in load(arm):
            it = items[r["query_id"]]
            if r.get("answer") is None:
                errors[arm] += 1
                continue
            lab = label(r["answer"], it, aliases=al, registry=reg)
            per_q[arm].setdefault(r["query_id"], []).append(lab)
            if lab["needs_review"]:
                review.append({"arm": arm, "query_id": r["query_id"], "seed": r["seed"], "auto_label": lab["label"]})
    md = ["# E1 three-arm results (automatic first-pass labels; human re-label pending)", "",
          "Model llama3.1:8b-instruct-q4_K_M via Ollama, settings and prompts per eval_data/PREREGISTRATION.md "
          "(manifest in results/e1/raw/). Labels are AUTOMATIC (src/mak/eval/score.py); every needs_review row plus a "
          "random 20% must be human re-labelled before these become final.", ""]
    for lang in ("en", "hi", "ta"):
        md += [f"## {lang}", "", "| arm | n questions | n responses | WVR | GCAR | MEN_ONLY | ASKED_BACK | NEITHER | wrong-overall (A) | number_wrong | errors |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm in arms:
            qs = [q for q, labs in per_q[arm].items() if items[q]["language"] == lang and items[q]["scoring_set"] in ("A", "B")]
            labs = [l for q in qs for l in per_q[arm][q]]
            if not labs:
                continue
            n = len(labs)
            c = lambda k: sum(l["label"] == k for l in labs) / n
            a_labs = [l for q in qs if items[q]["scoring_set"] == "A" for l in per_q[arm][q]]
            wo = sum(l["wrong_overall"] for l in a_labs) / len(a_labs) if a_labs else 0
            nw = sum(l["number_wrong"] for l in labs) / n
            md.append(f"| {arm} | {len(qs)} | {n} | {c('BOTH') + c('WOMEN_ONLY'):.3f} | {c('BOTH'):.3f} | {c('MEN_ONLY'):.3f} | "
                      f"{c('ASKED_BACK'):.3f} | {c('NEITHER'):.3f} | {wo:.3f} | {nw:.3f} | {errors[arm]} |")
        md.append("")
        if "plain" in arms and "prompt_only" in arms:
            common = sorted(q for q in per_q["plain"] if q in per_q["prompt_only"] and items[q]["language"] == lang
                            and items[q]["scoring_set"] in ("A", "B"))
            if common:
                score = lambda arm, q: sum(l["label"] in ("BOTH", "WOMEN_ONLY") for l in per_q[arm][q]) / len(per_q[arm][q])
                a = [score("prompt_only", q) for q in common]
                b = [score("plain", q) for q in common]
                d, lo, hi = paired_bootstrap(a, b)
                dg, log, hig = paired_bootstrap(a, b, groups=[items[q]["intent_id"] for q in common])
                md.append(f"WVR prompt_only - plain: {d:+.3f} (95% CI {lo:+.3f} to {hi:+.3f}; intent-group CI {log:+.3f} to {hig:+.3f}; n={len(common)} questions)")
                md.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    rng = random.Random(20261003)
    allrows = [{"arm": arm, "query_id": q, "auto_label": l["label"]} for arm in arms for q, labs in per_q[arm].items() for l in labs[:1]]
    sample = rng.sample(allrows, max(1, len(allrows) // 5)) if allrows else []
    with (OUT / "human_review_queue.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["arm", "query_id", "seed", "auto_label", "reason"])
        w.writeheader()
        for r in review:
            w.writerow({**r, "reason": "needs_review"})
        for r in sample:
            w.writerow({**r, "seed": "", "reason": "random_20pct"})
    print("wrote", OUT / "tables.md", "| review queue:", len(review), "+", len(sample))


if __name__ == "__main__":
    main()
