import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("benchmark_draft", ROOT / "eval_data/tools/build_benchmark.py")
benchmark = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(benchmark)


def test_answer_key_copies_exact_source_rows_and_keeps_missing_truth_empty(tmp_path):
    rows, report = benchmark.build(output=tmp_path / "benchmark.csv")
    with benchmark.GOLDEN.open(encoding="utf-8-sig", newline="") as fh:
        golden = {(row["intent_id"], row["gender"]): row for row in csv.DictReader(fh)}
    assert len(rows) >= 100
    assert set(report["category_counts"]) >= {"A", "B", "C", "D", "F", "G"}
    for row in rows:
        assert row["annotation_status"] == "unreviewed"
        if row["intent_id"]:
            for gender in ("women", "men"):
                assert json.loads(row[f"{gender}_answer"]) == golden[(row["intent_id"], gender)]
        else:
            assert row["women_answer"] == row["men_answer"] == ""
    assert report["translation_status"] == "not run"
    assert report["source_caveats"]


def test_reviewed_draft_keeps_exact_truth_and_records_single_reviewer(tmp_path):
    review = ROOT / "eval_data/annotations/benchmark_self_review.jsonl"
    rows, report = benchmark.build(output=tmp_path / "reviewed.csv", review_path=review)
    with benchmark.GOLDEN.open(encoding="utf-8-sig", newline="") as fh:
        golden = {(row["intent_id"], row["gender"]): row for row in csv.DictReader(fh)}
    assert len(rows) == 120
    assert report["review"]["reviewer_count"] == 1
    assert report["review"]["independent"] is False
    for row in rows:
        assert row["annotation_status"] == "self_reviewed"
        assert "review_method=same_agent_self_review" in row["notes"]
        if row["intent_id"]:
            for gender in ("women", "men"):
                assert json.loads(row[f"{gender}_answer"]) == golden[row["intent_id"], gender]
        else:
            assert row["women_answer"] == row["men_answer"] == ""


def test_review_cannot_survive_changed_inputs_or_missing_rows(tmp_path):
    original = ROOT / "eval_data/annotations/benchmark_self_review.jsonl"
    review = tmp_path / "review.jsonl"
    review.write_bytes(original.read_bytes())
    review.with_suffix(".meta.json").write_bytes(original.with_suffix(".meta.json").read_bytes())
    seeds = tmp_path / "seeds.jsonl"
    seeds.write_text(benchmark.SEEDS.read_text(encoding="utf-8").replace(
        "Who has scored the most career runs in T20 internationals?", "Who has scored the most runs in Test cricket?"
    ), encoding="utf-8")
    with pytest.raises(ValueError, match="Stale benchmark review: seeds_sha256"):
        benchmark.build(seeds=seeds, output=tmp_path / "stale.csv", review_path=review)
    assert not (tmp_path / "stale.csv").exists()

    review.write_text("\n".join(review.read_text(encoding="utf-8").splitlines()[1:]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="every item exactly once"):
        benchmark.build(output=tmp_path / "incomplete.csv", review_path=review)
    assert not (tmp_path / "incomplete.csv").exists()
