"""Validate reviewed evidence and assemble K-P2 files; --freeze publishes locally.

This tool never derives labels from query text or runs a project classifier.
Rebuilding or freezing after evaluation results requires a versioned amendment.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys
import unicodedata

from mak import labels
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_benchmark
import review

ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "eval_data/preparation"
ANN = ROOT / "eval_data/annotations"
GROUPS = (("heldout", "heldout_candidates"), ("nq_stats", "nq_stats_items"),
          ("nq_controls", "nq_control_items"), ("native", "native_items"),
          ("xsport", "xsport_items"), ("translated", "translated_items"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def csv_write(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def check_unique(rows, id_key, text_key, lang_key):
    review.indexed([{"id": row[id_key]} for row in rows], "release")
    seen = {}
    for row in rows:
        key = row[lang_key], unicodedata.normalize("NFC", row[text_key]).casefold().strip()
        if key in seen:
            raise ValueError(f"Duplicate text: {seen[key]}, {row[id_key]}")
        seen[key] = row[id_key]


def validate_provenance(items, raw_translations, originals):
    for row in items:
        if row["source"] in {"nq_open", "aya"}:
            source = originals.get(row["id"])
            if source is None or any(row.get(k) != source.get(k) for k in
                ("text", "lang", "source", "source_file", "source_row", "source_sha256", "licence")):
                raise ValueError(f"Source text or provenance changed: {row['id']}")
        if row["source"] == "indictrans2":
            raw = raw_translations.get(row["id"])
            if raw is None or any(row.get(k) != raw.get(k) for k in
                ("text", "source_text", "origin_id", "model_revision", "request_sha256", "lang")):
                raise ValueError(f"Translation differs from actual raw model output: {row['id']}")
            if row.get("generation_limit_reached") or not row["text"].strip():
                raise ValueError("Empty or truncated translation")
            if row.get("origin_source") == "nq_open":
                origin = originals.get(row["origin_id"])
                if origin is None or row["source_text"] != origin["text"]:
                    raise ValueError("Translation source does not match original NQ row")


def assemble(destination):
    evidence = set()
    def load(path):
        evidence.add(path)
        return review.load_jsonl(path)
    raw = review.indexed(load(PREP / "translation_output.jsonl") +
                         load(PREP / "translation_reserve_output.jsonl"), "raw translations")
    originals = review.indexed(load(PREP / "source_candidates.jsonl") +
                               load(PREP / "control_candidates.jsonl"), "original sources")
    items, rows, reports = [], [], {}
    for prefix, item_name in GROUPS:
        item_path = PREP / f"{item_name}.jsonl"
        a_path = ANN / f"{prefix}_a.jsonl"
        final_path = ANN / f"{prefix}_self_review.jsonl"
        meta_path = ANN / f"{prefix}_self_review.meta.json"
        evidence.add(meta_path)
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        for key, path in (("items_sha256", item_path), ("first_pass_sha256", a_path)):
            if key in metadata and metadata[key] != sha(path):
                raise ValueError(f"Stale semantic review: {prefix}/{key}")
        group_items = load(item_path)
        group_rows, report = review.self_review(group_items, load(a_path), load(final_path), metadata)
        validate_provenance(group_items, raw, originals)
        items += group_items
        rows += group_rows
        reports[prefix] = report
    exclusions = load(PREP / "release_exclusions.jsonl")
    excluded_ids = set(review.indexed(exclusions, "pre-freeze overlap exclusions"))
    if not excluded_ids <= {row["id"] for row in rows}:
        raise ValueError("Overlap exclusion does not belong to reviewed inputs")
    rows = [row for row in rows if row["id"] not in excluded_ids]
    items = [row for row in items if row["id"] not in excluded_ids]
    check_unique(rows, "id", "text", "lang")
    # Every reviewed English benchmark remains bound to its golden snapshot.
    english_review = ANN / "benchmark_self_review.jsonl"
    evidence.update((build_benchmark.SEEDS, build_benchmark.GOLDEN, english_review,
                     english_review.with_suffix(".meta.json")))
    english, english_report = build_benchmark.build(
        output=destination / "benchmark_english_check.csv", review_path=english_review)
    english_by_id = {r["query_id"]: r for r in english}
    benchmark = [{**r, "notes": r["notes"].removeprefix("DRAFT: ")} for r in english]
    translated_path = PREP / "benchmark_translation_items.jsonl"
    first_path = ANN / "benchmark_translations_a.jsonl"
    final_path = ANN / "benchmark_translations_self_review.jsonl"
    meta_path = final_path.with_suffix(".meta.json")
    evidence.add(meta_path)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    for key, path in (("items_sha256", translated_path), ("first_pass_sha256", first_path),
                      ("english_review_sha256", english_review)):
        if meta.get(key) != sha(path):
            raise ValueError(f"Stale benchmark translation review: {key}")
    if (meta.get("review_method") != "same_agent_self_review" or meta.get("independent") is not False
            or meta.get("prior_labels_visible") is not True or meta.get("seen_training_data") is not False):
        raise ValueError("Incorrect benchmark review declaration")
    translated = load(translated_path)
    first = {r["query_id"]: r for r in load(first_path)}
    final = {r["query_id"]: r for r in load(final_path)}
    if set(first) != set(final) or set(final) != {r["id"] for r in translated}:
        raise ValueError("Missing benchmark translation review")
    validate_provenance(translated, raw, originals)
    provenance = []
    for item in items:
        provenance.append({**item, "release_review_status": "self_reviewed"})
    for seed in load(build_benchmark.SEEDS):
        provenance.append({**seed, "id": seed["query_id"], "lang": seed["language"],
                           "text": seed["prompt"], "evaluation_set": "benchmark",
                           "generator": "GPT-6 (Codex development agent)",
                           "review_method": "same_agent_self_review"})
    for item in translated:
        checked = final[item["id"]]
        if checked.get("outcome") != "confirmed" or not checked.get("review_note"):
            raise ValueError("Unconfirmed benchmark translation")
        origin = english_by_id[item["origin_id"]]
        if item["source_text"] != origin["prompt"] or checked["origin_id"] != item["origin_id"]:
            raise ValueError("Benchmark translation origin mismatch")
        benchmark.append({**origin, "query_id": item["id"], "prompt": item["text"],
                          "language": item["lang"], "source": "indictrans2",
                          "notes": f"review_method=same_agent_self_review; origin_id={item['origin_id']}; "
                                   + checked["review_note"] + " " + origin["notes"].removeprefix("DRAFT: ")})
        provenance.append({**item, "release_review_status": "self_reviewed"})
    check_unique(benchmark, "query_id", "prompt", "language")
    nlu = [r for r in rows if r["evaluation_set"] == "nlu"]
    counts = Counter((r["lang"], r["source"]) for r in nlu)
    if not 250 <= counts["en", "nq_open"] <= 400:
        raise ValueError("REAL-EN target not met")
    for lang in ("en", "hi", "ta"):
        if not 45 <= counts[lang, "heldout_gen"] <= 50:
            raise ValueError("Approximate generated hard-slice target not met")
    if any(not 140 <= counts[lang, "indictrans2"] <= 150 for lang in ("hi", "ta")):
        raise ValueError("Approximate reviewed translation target not met")
    if sum(r["evaluation_set"] == "xsport" for r in rows) < 60:
        raise ValueError("Cross-sport target not met")
    bc = Counter(r["language"] for r in benchmark)
    if bc["en"] < 100 or min(bc["hi"], bc["ta"]) < 25:
        raise ValueError("Benchmark target not met")
    outputs = {}
    for lang in ("en", "hi", "ta", "xsport"):
        selected = [r for r in rows if r["evaluation_set"] == "xsport"] if lang == "xsport" else [r for r in nlu if r["lang"] == lang]
        filename = "xsport.csv" if lang == "xsport" else f"nlu_{lang}.csv"
        path = destination / "testsets" / filename
        csv_write(path, selected, labels.TESTSET_COLUMNS)
        outputs[f"testsets/{filename}"] = {"sha256": sha(path), "rows": len(selected),
            "counts": {k: dict(Counter(r[k] for r in selected)) for k in
                       ("lang", "source", "slice", "gender_signal", "topic", "expected_decision")}}
    path = destination / "eval_data/benchmark_v1.csv"
    csv_write(path, benchmark, build_benchmark.COLUMNS)
    outputs["eval_data/benchmark_v1.csv"] = {"sha256": sha(path), "rows": len(benchmark),
        "counts": {k: dict(Counter(r[k] for r in benchmark)) for k in
                   ("language", "source", "category", "scoring_set", "support")}}
    provenance_path = destination / "eval_data/provenance_v1.jsonl"
    provenance_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in provenance), encoding="utf-8", newline="\n")
    outputs["eval_data/provenance_v1.jsonl"] = {"sha256": sha(provenance_path), "rows": len(provenance)}
    overlap_path = PREP / "final_overlap_audit.json"
    evidence.add(overlap_path)
    overlap = json.loads(overlap_path.read_text(encoding="utf-8"))
    if overlap.get("status") != "CLEAN" or overlap.get("flagged") != 0:
        raise ValueError("Final training-overlap audit is not clean")
    for relative, digest in overlap["training_sha256"].items():
        path = ROOT / relative
        if path.exists() and sha(path) != digest:
            raise ValueError("Training snapshot changed since the overlap audit")
    for relative, info in outputs.items():
        if relative.startswith("testsets/") and overlap["testset_sha256"].get(Path(relative).name) != info["sha256"]:
            raise ValueError("Overlap audit belongs to different test-set bytes")
    for relative in ("eval_data/PREREGISTRATION.md", "eval_data/ANNOTATION_RUBRIC.md",
                     "eval_data/preparation/source_manifest.json", "eval_data/preparation/indictrans2_install.json",
                     "eval_data/preparation/native_exclusions.jsonl", "eval_data/preparation/translation_exclusions.jsonl",
                     "eval_data/preparation/benchmark_translation_exclusions.jsonl",
                     "eval_data/preparation/raw_source_verification.json", "eval_data/DATA_CARD.md",
                     "eval_data/TRANSLATION_SETUP.md", "eval_data/preparation/nq_selected_indices.json",
                     "eval_data/preparation/translation_requests.jsonl",
                     "eval_data/preparation/translation_reserve_requests.jsonl",
                     "eval_data/tools/build_release.py", "eval_data/tools/review.py",
                     "eval_data/tools/translate.py", "eval_data/tools/build_benchmark.py",
                     "eval_data/tools/fetch_sources.py", "eval_data/tools/check_overlap.py",
                     "eval_data/preparation/pre_freeze_overlap_screen.json", "src/mak/labels.py"):
        evidence.add(ROOT / relative)
    result = {"version": "1", "date": "2026-10-03", "status": "VALIDATED DRAFT — NOT FROZEN",
              "files": outputs, "evidence_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(evidence)},
              "review_method": "same_agent_self_review", "reviewer_count": 1,
              "independent_review": False, "human_review": False,
              "review_reports": reports, "benchmark_review": english_report,
              "pre_freeze_overlap_exclusions": exclusions,
              "overlap_audit": overlap,
              "benchmark_translation_review": meta,
              "native_shortfall": "8 Hindi and 21 Tamil NLU prompts retained after semantic eligibility and duplicate review; approximate source targets are not padded.",
              "measurement_status": "No held-out classifier evaluation or answer-benchmark outputs inspected or claimed. Dev-only handoff observations were read after semantic labels were fixed. Training strings were compared opaquely for overlap after annotation; no corpus or prediction-file contents entered the reviewer context."}
    json_write(destination / "eval_data/release_manifest.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--check", action="store_true", help="Verify an existing freeze without rewriting it")
    args = parser.parse_args(argv)
    if args.freeze and args.check:
        raise ValueError("Choose build/freeze or check")
    if args.check:
        manifest = json.loads((ROOT / "eval_data/release_manifest.json").read_text(encoding="utf-8"))
        if manifest["status"] != "FROZEN":
            raise ValueError("Release is not frozen")
        expected = {name: info["sha256"] for name, info in manifest["files"].items()}
        expected.update(manifest["evidence_sha256"])
        for relative, digest in expected.items():
            if sha(ROOT / relative) != digest:
                raise ValueError(f"Frozen file changed: {relative}")
        print(f"Verified {len(expected)} frozen file/evidence hashes.")
        return
    destination = PREP / "release"
    result = assemble(destination)
    if args.freeze:
        existing = ROOT / "eval_data/release_manifest.json"
        if existing.exists():
            raise ValueError("Freeze already exists; do not silently replace a published version")
        for relative in result["files"]:
            target = ROOT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((destination / relative).read_bytes())
        result["status"] = "FROZEN"
        json_write(existing, result)
        lines = ["# K-P2 test sets FROZEN — v1, 3 October 2026", "",
                 "Joanna/Astra: one reviewer, same-agent semantic self-review. No independent agreement",
                 "or human/native-speaker validation is claimed. No project evaluation outputs inspected.", "",
                 "Training firewall: Jabin may read these inputs only after publishing `training/DATA_FROZEN.md`.", "",
                 "| File | Rows | SHA-256 (UTF-8, LF) |", "|---|---:|---|"]
        for relative, info in result["files"].items():
            lines.append(f"| `{relative}` | {info['rows']} | `{info['sha256']}` |")
        lines += ["", "## Measured counts", ""]
        for relative, info in result["files"].items():
            if "counts" not in info:
                continue
            lines += [f"### {relative}", ""]
            for field in ("lang", "language", "source", "slice"):
                if field in info["counts"]:
                    lines.append(f"- {field}: " + ", ".join(f"{k}={v}" for k, v in sorted(info["counts"][field].items())))
            lines.append("")
        lines += ["", "Counts by language/source/slice and every evidence hash are in",
                  "`eval_data/release_manifest.json`. Read `eval_data/DATA_CARD.md` for exclusions,",
                  "licences, source biases and the small native-language subsets.", "",
                  "Verify with `python eval_data/tools/build_release.py --check`.",
                  "The preregistration hash is in the manifest; no results or accuracy are claimed.", ""]
        (ROOT / "testsets/FROZEN.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "files": {k: v["rows"] for k, v in result["files"].items()}}, indent=2))


if __name__ == "__main__":
    main()
