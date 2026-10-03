import importlib.util
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location("eval_sources", ROOT / "eval_data/tools/fetch_sources.py")
sources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sources)


def test_candidate_extraction_preserves_text_and_does_not_create_labels(tmp_path):
    raw, output = tmp_path / "raw", tmp_path / "output"
    raw.mkdir()
    with duckdb.connect() as conn:
        conn.execute("CREATE TABLE nq(question VARCHAR)")
        conn.executemany("INSERT INTO nq VALUES (?)", [
            ["who hit most runs in cricket ?"], ["  Who hit most RUNS in cricket ?  "],
            ["what happened in the 19th century"], ["who won wimbledon"], ["capital of france"]])
        conn.execute("COPY nq TO ? (FORMAT PARQUET)", [str(raw / "nq.parquet")])
        conn.execute("CREATE TABLE aya(inputs VARCHAR, language VARCHAR)")
        conn.executemany("INSERT INTO aya VALUES (?, ?)", [
            ["क्रिकेट में सबसे अधिक रन किसके हैं?", "Hindi"],
            ["கிரிக்கெட்டில் அதிக ரன்கள் எடுத்தவர் யார்?", "Tamil"],
            ["Who won the cricket match?", "English"]])
        conn.execute("COPY aya TO ? (FORMAT PARQUET)", [str(raw / "aya.parquet")])
    manifest = {"complete": True, "files": [{"source": key, "dataset": key, "path": filename, "split": "train",
                            "sha256": sources.file_sha256(raw / filename), "licence": "fixture"}
                          for key, filename in (("nq_open", "nq.parquet"), ("aya", "aya.parquet"))]}
    (raw / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = sources.extract_candidates(raw, output)
    rows = [json.loads(line) for line in (output / "source_candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    first = next(row for row in rows if row["source_row"] == 0 and row["lang"] == "en")
    assert first["text"] == "who hit most runs in cricket ?"
    assert first["duplicates"] == [{"file": "nq.parquet", "row": 1}]
    assert all("gender_signal" not in row and "expected_decision" not in row for row in rows)
    assert {row["lang"] for row in rows} == {"en", "hi", "ta"}
    # Retrieval deliberately keeps false positives for semantic review, rather than labelling them.
    assert any("19th century" in row["text"] for row in rows)
    assert report["counts"]["control_candidates"] == 1


def test_incomplete_source_download_cannot_be_used(tmp_path):
    import pytest
    (tmp_path / "manifest.json").write_text('{"complete": false, "files": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="incomplete"):
        sources.extract_candidates(tmp_path, tmp_path / "out")


def test_changed_source_bytes_cannot_keep_old_provenance(tmp_path):
    import pytest
    (tmp_path / "input.parquet").write_bytes(b"changed")
    (tmp_path / "manifest.json").write_text(json.dumps({"complete": True, "files": [
        {"path": "input.parquet", "sha256": "old-hash"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="checksum changed"):
        sources.extract_candidates(tmp_path, tmp_path / "out")
