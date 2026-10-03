import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("eval_release", ROOT / "eval_data/tools/build_release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


def test_release_preserves_reviewed_rows_and_exact_golden_answers(tmp_path):
    report = release.assemble(tmp_path)
    expected = {"nlu_en.csv": 350, "nlu_hi.csv": 208, "nlu_ta.csv": 221, "xsport.csv": 61}
    for name, count in expected.items():
        with (tmp_path / "testsets" / name).open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == count
        assert all(row["adjudicated"] == "" for row in rows)
        assert all("same_agent_self_review" in row["notes"] for row in rows)
        if name == "xsport.csv":
            assert all(not row[k] for row in rows for k in ("family", "stat", "format", "expected_decision"))
    with release.build_benchmark.GOLDEN.open(encoding="utf-8-sig", newline="") as stream:
        truth = {(r["intent_id"], r["gender"]): r for r in csv.DictReader(stream)}
    with (tmp_path / "eval_data/benchmark_v1.csv").open(encoding="utf-8", newline="") as stream:
        benchmark = list(csv.DictReader(stream))
    assert len(benchmark) == 188
    for row in benchmark:
        if row["intent_id"]:
            for gender in ("women", "men"):
                assert json.loads(row[f"{gender}_answer"]) == truth[row["intent_id"], gender]
        else:
            assert row["women_answer"] == row["men_answer"] == ""
    assert report["files"]["eval_data/provenance_v1.jsonl"]["rows"] == 1028


def test_release_rejects_rewritten_source_or_fake_translation():
    item = {"id": "original", "source": "nq_open", "text": "exact original"}
    with pytest.raises(ValueError, match="Source text or provenance changed"):
        release.validate_provenance([{**item, "text": "silently fixed"}], {}, {"original": item})
    translated = {"id": "translated", "source": "indictrans2", "text": "raw output"}
    with pytest.raises(ValueError, match="actual raw model output"):
        release.validate_provenance([{**translated, "text": "agent rewrite"}], {"translated": translated}, {})


def test_duplicate_normalized_queries_cannot_inflate_release():
    rows = [{"id": "a", "lang": "en", "text": "Same query"},
            {"id": "b", "lang": "en", "text": "same query "}]
    with pytest.raises(ValueError, match="Duplicate text"):
        release.check_unique(rows, "id", "text", "lang")
