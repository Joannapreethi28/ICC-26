"""Build a draft with exact golden answers and optional recorded semantic review."""
from __future__ import annotations

import csv
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from mak.records.golden import audit_golden, load_golden

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "data/golden/records_v1.csv"
SEEDS = ROOT / "eval_data/preparation/benchmark_seeds.jsonl"
OUT = ROOT / "eval_data/preparation/benchmark_en_draft.csv"
COLUMNS = ("query_id", "prompt", "language", "category", "gender_relevance",
           "expected_interpretation", "women_answer", "men_answer", "data_timestamp",
           "ground_truth_source", "notes", "intent_id", "scoring_set", "support",
           "source", "annotation_status", "golden_sha256")


def load_review(seeds, golden, candidates, review_path):
    """Bind a human-readable review record to the exact inputs it inspected."""
    metadata = json.loads(review_path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    for key, path in (("seeds_sha256", seeds), ("golden_sha256", golden)):
        if metadata.get(key) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"Stale benchmark review: {key}")
    if (metadata.get("review_method") != "same_agent_self_review"
            or metadata.get("independent") is not False
            or metadata.get("prior_labels_visible") is not True
            or metadata.get("seen_training_data") is not False
            or metadata.get("reviewer_count") != 1):
        raise ValueError("Benchmark review must declare the actual single-agent method")
    reviews = [json.loads(line) for line in review_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    indexed = {row["query_id"]: row for row in reviews}
    if (len(indexed) != len(reviews)
            or set(indexed) != {row["query_id"] for row in candidates}
            or metadata.get("items") != len(candidates)):
        raise ValueError("Benchmark review must cover every item exactly once")
    for row in reviews:
        if row.get("outcome") != "confirmed" or not str(row.get("review_note", "")).strip():
            raise ValueError("Every benchmark item requires a confirmed review and reason")
    return indexed, metadata


def build(seeds=SEEDS, golden=GOLDEN, output=OUT, review_path=None):
    # Reuse schema/date/provenance validation, never a classifier or answer generator.
    facts = load_golden(golden)
    with golden.open(encoding="utf-8-sig", newline="") as fh:
        truth = {(row["intent_id"], row["gender"]): row for row in csv.DictReader(fh)}
    digest = hashlib.sha256(golden.read_bytes()).hexdigest()
    candidates = [json.loads(line) for line in seeds.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len({row["query_id"] for row in candidates}) != len(candidates):
        raise ValueError("Duplicate benchmark IDs")
    reviews, review_metadata = load_review(seeds, golden, candidates, review_path) if review_path else ({}, None)
    rows = []
    for seed in candidates:
        intent, interpretation = seed["intent_id"], seed["interpretation"]
        answers = {gender: truth[(intent, gender)] if intent else None for gender in ("women", "men")}
        if (seed["support"] == "golden") != bool(intent):
            raise ValueError("Golden support and intent must match")
        if intent and any((intent, gender) not in {(f.intent_id, f.gender) for f in facts} for gender in answers):
            raise ValueError("Unvalidated fact in answer key")
        scoring_set = seed.get("scoring_set")
        if not scoring_set:
            if interpretation == "insensitive":
                scoring_set = "G"
            elif interpretation == "women":
                scoring_set = "C"
            elif interpretation in {"men", "both_named"}:
                scoring_set = interpretation
            else:
                # A/B is record-specific; unsupported neutral questions stay B.
                scoring_set = "A" if intent and answers["women"]["overall_leader"] == "women" else "B"
        urls = sorted({r[key].split(" ", 1)[0] for r in answers.values() if r
                       for key in ("source_1", "source_2") if r[key]})
        rows.append({"query_id": seed["query_id"], "prompt": seed["prompt"],
                     "language": seed["language"], "category": seed["category"],
                     "gender_relevance": "insensitive" if interpretation == "insensitive" else "relevant",
                     "expected_interpretation": "both" if interpretation == "both_named" else interpretation,
                     "women_answer": json.dumps(answers["women"], ensure_ascii=False, sort_keys=True) if intent else "",
                     "men_answer": json.dumps(answers["men"], ensure_ascii=False, sort_keys=True) if intent else "",
                     "data_timestamp": "2026-10-03", "ground_truth_source": json.dumps(urls),
                     "notes": ("DRAFT: review_method=same_agent_self_review; " + reviews[seed["query_id"]]["review_note"] + " "
                               if reviews else "DRAFT: design labels await semantic self-review. ")
                              + "Snapshot date is not a fresh source verification; per-fact as_of and verification caveats are retained. Both truth rows are stored; score only the requested category.",
                     "intent_id": intent, "scoring_set": scoring_set, "support": seed["support"],
                     "source": seed["source"], "annotation_status": "self_reviewed" if reviews else "unreviewed", "golden_sha256": digest})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report = {"status": "SELF-REVIEWED DRAFT — NOT FROZEN" if reviews else "UNREVIEWED DRAFT — NOT FROZEN", "rows": len(rows),
              "source_snapshot": "2026-10-03", "golden_sha256": digest,
              "seeds_sha256": hashlib.sha256(seeds.read_bytes()).hexdigest(),
              "category_counts": dict(Counter(r["category"] for r in rows)),
              "scoring_set_counts": dict(Counter(r["scoring_set"] for r in rows)),
              "support_counts": dict(Counter(r["support"] for r in rows)),
              "source_caveats": audit_golden(golden),
              "translation_status": "not run", "annotation_status": "same_agent_self_review" if reviews else "not run"}
    if reviews:
        report["review"] = review_metadata | {
            "review_sha256": hashlib.sha256(review_path.read_bytes()).hexdigest(),
            "metadata_sha256": hashlib.sha256(review_path.with_suffix(".meta.json").read_bytes()).hexdigest(),
        }
    output.with_suffix(".manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return rows, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewed", action="store_true", help="Use the recorded input-bound semantic self-review")
    args = parser.parse_args()
    _, result = build(output=OUT.with_name("benchmark_en_self_reviewed.csv") if args.reviewed else OUT,
                      review_path=ROOT / "eval_data/annotations/benchmark_self_review.jsonl" if args.reviewed else None)
    print(json.dumps({key: value for key, value in result.items() if key != "source_caveats"}, indent=2))
