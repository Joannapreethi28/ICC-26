"""Read-only string hygiene after training freeze; never expose corpus text.

Reports evaluation IDs and counts only. This is not classifier evaluation or proof
of semantic/pretraining independence. Never modify training or evaluation files.
"""
import argparse
import bisect
from collections import Counter
import csv
import difflib
import hashlib
import json
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[2]
THRESHOLD = 0.92


def norm(text):
    return re.sub(r"[\W_]+", " ", text.lower()).strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--testsets", type=Path, default=ROOT / "testsets")
    parser.add_argument("--report", type=Path, default=ROOT / "eval_data/overlap_audit.json")
    args = parser.parse_args(argv)
    if not (ROOT / "training/DATA_FROZEN.md").exists():
        raise ValueError("Training freeze marker is required before string comparison")
    training, hashes = [], {}
    for name in ("train", "calib", "messy_calib"):
        path = ROOT / "training/data" / f"{name}.jsonl"
        if not path.exists():
            continue
        hashes[f"training/data/{name}.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text(encoding="utf-8").splitlines():
            text = norm(json.loads(line)["state"])
            training.append((len(text), text, Counter(text), name))
    if not training:
        raise ValueError("No frozen training/calibration strings to compare")
    training.sort(key=lambda row: row[0])
    lengths = [r[0] for r in training]
    items, input_hashes = [], {}
    for path in sorted(args.testsets.glob("*.csv")):
        input_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open(encoding="utf-8", newline="") as stream:
            items += list(csv.DictReader(stream))
    if not items:
        raise ValueError("No evaluation rows to compare")
    results, started = [], time.perf_counter()
    for index, item in enumerate(items):
        target = norm(item["text"])
        size, counter, matches = len(target), Counter(target), []
        # All lengths whose theoretical maximum character ratio can pass.
        low = bisect.bisect_left(lengths, int(size * THRESHOLD / (2 - THRESHOLD)))
        high = bisect.bisect_right(lengths, int(size * (2 - THRESHOLD) / THRESHOLD) + 1)
        matcher = difflib.SequenceMatcher(None, "", target)
        for length, text, counts, split in training[low:high]:
            if text == target:
                matches.append({"split": split, "kind": "exact", "ratio": 1.0})
                continue
            # Character multiset upper bound cannot discard a real passing pair.
            upper = 2 * sum(min(n, counts.get(c, 0)) for c, n in counter.items()) / (size + length)
            if upper < THRESHOLD:
                continue
            matcher.set_seq1(text)
            ratio = matcher.ratio()
            if ratio >= THRESHOLD:
                matches.append({"split": split, "kind": "near", "ratio": round(ratio, 6)})
        if matches:
            results.append({"id": item["id"], "source": item["source"], "lang": item["lang"], "matches": matches})
        if (index + 1) % 100 == 0:
            print(f"Compared {index + 1}/{len(items)} evaluation rows; no corpus text shown.", flush=True)
    result = {"status": "CLEAN" if not results else "OVERLAP FLAGGED", "date": "2026-10-03",
              "rows_checked": len(items), "flagged": len(results), "threshold": THRESHOLD,
              "training_content_exposed_to_reviewer": False,
              "method": "punctuation-normalized lowercase exact/character SequenceMatcher comparison; all eligible lengths",
              "training_sha256": hashes, "testset_sha256": input_hashes,
              "seconds": time.perf_counter() - started, "items": results}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {"items", "training_sha256", "testset_sha256"}}, indent=2))
    return int(bool(results))


if __name__ == "__main__":
    raise SystemExit(main())
