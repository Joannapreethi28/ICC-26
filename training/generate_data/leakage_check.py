"""Leakage check: no test-set question may appear (exactly or near-exactly) in train/calib/messy data. OWNER: Jabin.

Reads testsets/*.csv READ-ONLY, only to compare strings; nothing from them is ever used for training (G-011).
Exit code 1 if anything leaks. Skips cleanly if no test CSVs exist yet.

  python training/generate_data/leakage_check.py
"""
import csv
import difflib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
COLS = ("text", "query", "question")
NEAR = 0.92


def norm(t):
    return re.sub(r"[\W_]+", " ", t.lower()).strip()


def main():
    files = sorted((ROOT / "testsets").glob("*.csv"))
    if not files:
        print("no testsets/*.csv yet; nothing to check (re-run when Joanna's sets land)")
        return 0
    test = set()
    for f in files:
        with f.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                for c in COLS:
                    if row.get(c):
                        test.add(norm(row[c]))
    print(f"{len(test)} unique test queries from {len(files)} file(s)")
    by_len = {}
    for t in test:
        by_len.setdefault(len(t) // 8, []).append(t)
    bad = 0
    for name in ("train", "calib", "messy_calib"):
        p = ROOT / "training" / "data" / f"{name}.jsonl"
        if not p.exists():
            continue
        exact = near = 0
        for line in p.open(encoding="utf-8"):
            s = norm(json.loads(line)["state"])
            if s in test:
                exact += 1
                continue
            k = len(s) // 8
            if any(difflib.SequenceMatcher(None, s, t).ratio() >= NEAR for kk in (k - 1, k, k + 1) for t in by_len.get(kk, [])):
                near += 1
        print(f"{name}: exact overlaps {exact}, near-duplicates (>= {NEAR}) {near}")
        bad += exact + near
    print("LEAK FOUND" if bad else "clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
