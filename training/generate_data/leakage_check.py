"""Leakage check: no test-set question may appear (exactly or near-exactly) in train/calib/messy data. OWNER: Jabin.

Reads testsets/*.csv READ-ONLY, only to compare strings; nothing from them is ever used for training (G-011).
Prints counts only, never the matching texts (seeing them would be seeing test items).
Exit code 1 if anything leaks. Skips cleanly if no test CSVs exist yet.

  python training/generate_data/leakage_check.py            # check
  python training/generate_data/leakage_check.py --drop     # rewrite data files without the flagged rows
"""
import argparse
import csv
import difflib
import json
import pathlib
import re
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[2]
COLS = ("text", "query", "question")
NEAR = 0.92
NAMES = ("train", "calib", "messy_calib", "voice_calib")
_BY_LEN: dict = {}
_TEST: set = set()


def norm(t):
    return re.sub(r"[\W_]+", " ", t.lower()).strip()


def load_test():
    test = set()
    for f in sorted((ROOT / "testsets").glob("*.csv")):
        with f.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                for c in COLS:
                    if row.get(c):
                        test.add(norm(row[c]))
    return test


def _init(test):
    global _TEST, _BY_LEN
    _TEST = test
    _BY_LEN = {}
    for t in test:
        _BY_LEN.setdefault(len(t) // 8, []).append(t)


def flag(s: str) -> int:
    """0 clean, 1 exact, 2 near."""
    if s in _TEST:
        return 1
    k = len(s) // 8
    for kk in (k - 1, k, k + 1):
        for t in _BY_LEN.get(kk, []):
            if difflib.SequenceMatcher(None, s, t).ratio() >= NEAR:
                return 2
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop", action="store_true")
    a = ap.parse_args()
    test = load_test()
    if not test:
        print("no testsets/*.csv yet; nothing to check (re-run when Joanna's sets land)")
        return 0
    print(f"{len(test)} unique test queries")
    bad = 0
    with Pool(initializer=_init, initargs=(test,)) as pool:
        for name in NAMES:
            p = ROOT / "training" / "data" / f"{name}.jsonl"
            if not p.exists():
                continue
            lines = p.read_text(encoding="utf-8").splitlines()
            flags = pool.map(flag, [norm(json.loads(x)["state"]) for x in lines], chunksize=64)
            exact, near = flags.count(1), flags.count(2)
            print(f"{name}: exact overlaps {exact}, near-duplicates (>= {NEAR}) {near}")
            if a.drop and (exact or near):
                kept = [x for x, f in zip(lines, flags) if f == 0]
                p.write_bytes(("\n".join(kept) + "\n").encode("utf-8"))
                print(f"  dropped {len(lines) - len(kept)} rows from {name} (texts not shown)")
            else:
                bad += exact + near
    print("LEAK FOUND" if bad else "clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
