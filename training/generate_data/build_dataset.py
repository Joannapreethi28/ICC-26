"""Build Laya training + calibration files. OWNER: Jabin.

Run from the repo root:   python training/generate_data/build_dataset.py [--audit]
Writes training/data/train.jsonl and training/data/calib.jsonl (Laya item format + a `meta` block).
Never reads testsets/ or eval_data/ (firewall). Leakage against the frozen test sets is checked separately
(training/generate_data/leakage_check.py) only after training/DATA_FROZEN.md exists.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "training" / "generate_data")]

import grammar  # noqa: E402
import schema  # noqa: E402
from mak import labels  # noqa: E402

OUT = ROOT / "training" / "data"
PARA_DIR = ROOT / "training" / "generate_data" / "paraphrases"
SIZES = {"train": {"en": 3600, "hi": 3600, "ta": 3600}, "calib": {"en": 1000, "hi": 1000, "ta": 1000}}
SEED = 20261003


def load_paraphrases(lang: str, split: str) -> list[dict]:
    """Dev-time LLM paraphrases (see PROMPTS.md). Last ~15% of each file (by line) feeds calibration."""
    path = PARA_DIR / f"{lang}.jsonl"
    if not path.exists():
        return []
    lines = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    cut = int(len(lines) * 0.85)
    chosen = lines[cut:] if split == "calib" else lines[:cut]
    rows = []
    for i, r in enumerate(chosen):
        rows.append({"text": r["text"].strip(), "lang": lang, "variant": r.get("variant", lang), "gender_signal": r["gender_signal"],
                     "topic": r["topic"], "family": r.get("family", ""), "stat": r.get("stat", ""), "format": r.get("format", ""),
                     "template_family": f"para|{lang}|{split}|{i}", "source": "paraphrase", "slice": r.get("slice", "plain")})
    return rows


def validate_row(r: dict) -> None:
    assert r["lang"] in ("en", "hi", "ta"), r
    assert r["gender_signal"] in labels.GENDER_SIGNAL, r
    assert r["topic"] in labels.TOPIC, r
    if r["topic"] == "cricket_stat":
        assert r["family"] in labels.FAMILY, r
        assert r["stat"] in labels.STATS[r["family"]], r
        assert r["format"] in labels.FORMAT, r
    else:
        assert not r["family"] and not r["stat"] and not r["format"], r
    assert r["source"] in ("grammar", "noise", "paraphrase"), r
    assert r["slice"] in labels.SLICES, r


def to_laya_item(r: dict) -> dict:
    qids = ["gender_signal", "topic"]
    answers = {"gender_signal": r["gender_signal"], "topic": r["topic"]}
    if r["topic"] == "cricket_stat":
        qids += ["family", "format"]
        answers.update(family=r["family"], format=r["format"])
        if len(labels.STATS[r["family"]]) > 1:
            qids.append(f"stat_{r['family']}")
            answers[f"stat_{r['family']}"] = r["stat"]
    gold = {q: {"probabilities": {k: 1.0 if k == answers[q] else 0.0 for k in schema.QUESTIONS[q]["criteria"]}} for q in qids}
    meta = {k: r[k] for k in ("lang", "variant", "slice", "source", "template_family", "gender_signal", "topic", "family", "stat", "format")}
    return {"state": r["text"], "questions": {q: schema.QUESTIONS[q] for q in qids}, "gold": gold, "meta": meta}


def to_laya_jsonl(rows: list[dict], path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(to_laya_item(r), ensure_ascii=False) + "\n")


def build(split: str) -> list[dict]:
    rows = []
    for lang, n in SIZES[split].items():
        para = load_paraphrases(lang, split)
        gen = grammar.generate(lang, n - len(para), SEED, split)
        rows += gen + para
    seen, out = set(), []
    for r in rows:
        k = grammar._norm(r["text"])
        if k and k not in seen:
            seen.add(k)
            out.append(r)
    for r in out:
        validate_row(r)
    return out


def report(name: str, rows: list[dict]) -> None:
    print(f"\n== {name}: {len(rows)} rows")
    for lang in ("en", "hi", "ta"):
        sub = [r for r in rows if r["lang"] == lang]
        print(f"  {lang}: {len(sub)}")
        for key in ("gender_signal", "topic", "source", "slice", "variant"):
            c = collections.Counter(r[key] for r in sub)
            print(f"     {key}: " + ", ".join(f"{k}={v} ({100 * v / len(sub):.0f}%)" for k, v in sorted(c.items())))
        fam = collections.Counter(r["family"] for r in sub if r["topic"] == "cricket_stat")
        print("     family: " + ", ".join(f"{k}={v}" for k, v in sorted(fam.items())))
        fmt = collections.Counter(r["format"] for r in sub if r["topic"] == "cricket_stat")
        print("     format: " + ", ".join(f"{k}={v}" for k, v in sorted(fmt.items())))


def audit_against_rules(rows: list[dict]) -> None:
    """Diagnostic only: how often does the rules labeller disagree with the template labels? Labels are NOT changed."""
    from mak.nlu.rules import rules_parse
    bad = collections.Counter()
    shown = collections.defaultdict(list)
    for r in rows:
        p = rules_parse(r["text"], r["lang"])
        for key, got, want in (("gender", p.gender_signal, r["gender_signal"]), ("topic", p.topic, r["topic"])):
            if got != want:
                bad[(r["lang"], key)] += 1
                if len(shown[(r["lang"], key)]) < 6:
                    shown[(r["lang"], key)].append((want, got, r["text"]))
    print("\n== audit vs rules labeller (disagreements; NOT errors by themselves)")
    for k in sorted(bad):
        print(f"  {k}: {bad[k]}")
        for want, got, text in shown[k]:
            print(f"     template={want} rules={got} | {text}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()
    train, calib = build("train"), build("calib")
    train_keys = {grammar._norm(r["text"]) for r in train}
    calib = [r for r in calib if grammar._norm(r["text"]) not in train_keys]
    families_overlap = {r["template_family"] for r in train} & {r["template_family"] for r in calib}
    assert not families_overlap, f"template_family in both train and calib: {sorted(families_overlap)[:5]}"
    to_laya_jsonl(train, OUT / "train.jsonl")
    to_laya_jsonl(calib, OUT / "calib.jsonl")
    report("train", train)
    report("calib", calib)
    if args.audit:
        audit_against_rules(train)
    print(f"\nwrote {OUT / 'train.jsonl'} and {OUT / 'calib.jsonl'}")


if __name__ == "__main__":
    main()
