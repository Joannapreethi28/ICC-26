import csv
import importlib.util
import json
from pathlib import Path

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
