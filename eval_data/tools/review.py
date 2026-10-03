"""Export blind review packets and reconcile real annotation passes, without labelling.

These tools produce drafts only. They do not certify reviewer independence or
freeze a benchmark. Metadata is an attestation; retain the original review output.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

from mak import labels

ROOT = Path(__file__).resolve().parents[2]
FIELDS = ("gender_signal", "topic", "family", "stat", "format", "expected_decision", "slice")
BLIND_FIELDS = ("id", "lang", "text", "evaluation_set")


def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def indexed(rows, name):
    result = {}
    for row in rows:
        identity = row.get("id")
        if not isinstance(identity, str) or not identity.strip():
            raise ValueError(f"Missing ID in {name}")
        if identity in result:
            raise ValueError(f"Duplicate ID {identity} in {name}")
        result[identity] = row
    return result


def blind_rows(items):
    indexed(items, "items")
    return [{field: row[field] for field in BLIND_FIELDS} for row in items]


def validate_metadata(a, b):
    for metadata in (a, b):
        for key in ("model", "model_family", "run_date"):
            if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                raise ValueError(f"Missing actual review metadata: {key}")
        date.fromisoformat(metadata["run_date"])
        if any(metadata.get(key) is not False for key in
               ("seen_training_data", "seen_other_annotator_labels")):
            raise ValueError("Review must be independent of training and the other annotator's labels")
    if a["model_family"].strip().casefold() == b["model_family"].strip().casefold():
        raise ValueError("Annotators must be from different model families")


def validate_label(annotation, item):
    identity = item["id"]
    if annotation.get("id") != identity:
        raise ValueError(f"Annotation ID mismatch: {identity}")
    if not isinstance(annotation.get("reason"), str) or not annotation["reason"].strip():
        raise ValueError(f"Missing annotation reason: {identity}")
    vocabularies = {"gender_signal": labels.GENDER_SIGNAL, "topic": labels.TOPIC,
                    "slice": labels.SLICES}
    for field, vocabulary in vocabularies.items():
        if annotation.get(field) not in vocabulary:
            raise ValueError(f"Invalid {field}: {identity}")
    if any(field not in annotation or not isinstance(annotation[field], str) for field in FIELDS):
        raise ValueError(f"Missing or non-string annotation field: {identity}")
    if item["evaluation_set"] == "xsport":
        if annotation["topic"] != "other_sport_stat" or any(
            annotation[field] for field in ("family", "stat", "format", "expected_decision")
        ):
            raise ValueError(f"Invalid cross-sport labels: {identity}")
        return
    if annotation["topic"] == "cricket_stat":
        if annotation["family"] not in labels.FAMILY:
            raise ValueError(f"Invalid family: {identity}")
        if annotation["stat"] not in labels.STATS[annotation["family"]]:
            raise ValueError(f"Invalid stat for family: {identity}")
        if annotation["format"] not in labels.FORMAT:
            raise ValueError(f"Invalid format: {identity}")
        expected = {"none": "ambiguous_both", "women": "explicit_women",
                    "men": "explicit_men", "both_named": "both_named"}[annotation["gender_signal"]]
        if annotation["expected_decision"] not in {expected, "unsupported"}:
            raise ValueError(f"Inconsistent gender and decision: {identity}")
    else:
        expected = "unsupported" if annotation["topic"] == "other_sport_stat" else "no_intervention"
        if any(annotation[field] for field in ("family", "stat", "format")) or annotation["expected_decision"] != expected:
            raise ValueError(f"Inapplicable fields must be empty with {expected}: {identity}")
    if annotation["slice"] == "injection" and annotation["gender_signal"] != "none":
        raise ValueError(f"An injection cannot override gender policy: {identity}")


def reconcile(items, pass_a, pass_b, metadata_a, metadata_b, adjudications):
    """Validate labels humans/models supplied; never derive a label from query text."""
    inputs = indexed(items, "items")
    if not inputs:
        raise ValueError("No items to reconcile")
    a, b = indexed(pass_a, "annotator A"), indexed(pass_b, "annotator B")
    decisions = indexed(adjudications, "adjudications")
    validate_metadata(metadata_a, metadata_b)
    for name, annotations in (("A", a), ("B", b)):
        missing, extra = inputs.keys() - annotations.keys(), annotations.keys() - inputs.keys()
        if missing or extra:
            raise ValueError(f"Annotator {name}: missing={sorted(missing)}, extra={sorted(extra)}")
    if decisions.keys() - inputs.keys():
        raise ValueError("Unexpected adjudication ID")
    rows, disagreements = [], 0
    for identity, item in inputs.items():
        if item.get("lang") not in {"en", "hi", "ta"} or item.get("source") not in labels.SOURCES:
            raise ValueError(f"Invalid item language/source: {identity}")
        if item.get("evaluation_set") not in {"nlu", "xsport"} or not isinstance(item.get("text"), str) or not item["text"].strip():
            raise ValueError(f"Invalid item set/text: {identity}")
        validate_label(a[identity], item)
        validate_label(b[identity], item)
        differences = [field for field in FIELDS if a[identity][field] != b[identity][field]]
        if differences:
            if identity not in decisions:
                raise ValueError(f"Unresolved disagreement: {identity}, {differences}")
            resolution = decisions[identity]
            reason = resolution.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(f"Missing adjudication reason: {identity}")
            chosen = resolution.get("chosen", {})
            validate_label(chosen, item)
            disagreements += 1
            note = f"Adjudicated ({', '.join(differences)}): {reason}"
        else:
            if identity in decisions:
                raise ValueError(f"Unexpected adjudication for agreement: {identity}")
            chosen = a[identity]
            note = "Independent A/B agreement. " + chosen["reason"]
        rows.append({**{field: item[field] for field in ("id", "lang", "text", "source")},
                     **{field: chosen[field] for field in FIELDS},
                     "adjudicated": int(bool(differences)), "notes": note,
                     "evaluation_set": item["evaluation_set"]})
    report = {"status": "RECONCILED DRAFT — NOT FROZEN", "items": len(rows),
              "agreements": len(rows) - disagreements, "disagreements": disagreements,
              "annotator_a": metadata_a, "annotator_b": metadata_b,
              "independence_note": "Model family and isolation are declared metadata, not automatically verified.",
              "counts": {field: dict(Counter(row[field] for row in rows))
                         for field in ("lang", "source", "slice", "evaluation_set")}}
    return rows, report


def write_packet(items, destination):
    destination.mkdir(parents=True, exist_ok=True)
    queries = blind_rows(items)
    vocabulary = {key: getattr(labels, key) for key in
                  ("GENDER_SIGNAL", "TOPIC", "FAMILY", "STATS", "FORMAT", "DECISIONS", "SLICES")}
    # An allowlist prevents hidden A-labels/provenance notes leaking to B.
    (destination / "queries.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in queries), encoding="utf-8")
    (destination / "rubric.md").write_text(
        (ROOT / "eval_data/ANNOTATION_RUBRIC.md").read_text(encoding="utf-8"), encoding="utf-8")
    (destination / "vocabulary.json").write_text(json.dumps(vocabulary, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    packet = sub.add_parser("packet")
    packet.add_argument("--items", type=Path, required=True)
    packet.add_argument("--out", type=Path, required=True)
    merge = sub.add_parser("reconcile")
    for name in ("items", "a", "b", "meta-a", "meta-b", "adjudications", "out"):
        merge.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "packet":
        write_packet(load_jsonl(args.items), args.out)
        print(f"Blind query packet written to {args.out}; no annotation pass has been completed.")
        return
    rows, report = reconcile(load_jsonl(args.items), load_jsonl(args.a), load_jsonl(args.b),
        json.loads(args.meta_a.read_text(encoding="utf-8-sig")),
        json.loads(args.meta_b.read_text(encoding="utf-8-sig")), load_jsonl(args.adjudications))
    report["input_sha256"] = {name: hashlib.sha256(getattr(args, name).read_bytes()).hexdigest()
                              for name in ("items", "a", "b", "meta_a", "meta_b", "adjudications")}
    args.out.mkdir(parents=True, exist_ok=True)
    for group in ("en", "hi", "ta", "xsport"):
        selected = [row for row in rows if (row["evaluation_set"] == "xsport" if group == "xsport"
                    else row["evaluation_set"] == "nlu" and row["lang"] == group)]
        filename = "xsport.csv" if group == "xsport" else f"nlu_{group}.csv"
        with (args.out / filename).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=labels.TESTSET_COLUMNS, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            writer.writerows(selected)
    (args.out / "review_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
