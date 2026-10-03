"""Checks on the generated Laya training/calibration data. Run: python -m pytest tests/nlu/test_dataset.py"""
import csv
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "training" / "generate_data")]

from mak import labels  # noqa: E402

DATA = ROOT / "training" / "data"
FROZEN = ROOT / "training" / "DATA_FROZEN.md"


def _load(name):
    path = DATA / f"{name}.jsonl"
    if not path.exists():
        pytest.skip(f"{path} not built; run training/generate_data/build_dataset.py")
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _norm(t):
    return re.sub(r"[\W_]+", " ", t.lower()).strip()


@pytest.fixture(scope="module")
def train():
    return _load("train")


@pytest.fixture(scope="module")
def calib():
    return _load("calib")


def test_labels_valid(train, calib):
    for it in train + calib:
        m = it["meta"]
        assert m["lang"] in ("en", "hi", "ta")
        assert m["gender_signal"] in labels.GENDER_SIGNAL
        assert m["topic"] in labels.TOPIC
        assert m["slice"] in labels.SLICES
        if m["topic"] == "cricket_stat":
            assert m["family"] in labels.FAMILY
            assert m["stat"] in labels.STATS[m["family"]]
            assert m["format"] in labels.FORMAT
        gold = it["gold"]["gender_signal"]["probabilities"]
        assert gold[m["gender_signal"]] == 1.0 and sum(gold.values()) == 1.0


@pytest.mark.parametrize("lang", ["en", "hi", "ta"])
def test_each_gender_label_at_least_15_percent(train, lang):
    rows = [it["meta"]["gender_signal"] for it in train if it["meta"]["lang"] == lang]
    for g in labels.GENDER_SIGNAL:
        assert rows.count(g) / len(rows) >= 0.15, (lang, g)


def test_train_calib_disjoint(train, calib):
    assert {it["meta"]["template_family"] for it in train}.isdisjoint({it["meta"]["template_family"] for it in calib})
    assert {_norm(it["state"]) for it in train}.isdisjoint({_norm(it["state"]) for it in calib})


def test_injection_rows_keep_underlying_gender(train):
    inj = [it for it in train if it["meta"]["slice"] == "injection"]
    assert inj
    assert any(it["meta"]["gender_signal"] == "none" for it in inj)
    assert all(it["meta"]["topic"] == "cricket_stat" for it in inj)


def test_no_overlap_with_testsets():
    if not FROZEN.exists():
        pytest.skip("training/DATA_FROZEN.md not written yet; test sets stay closed (G-011)")
    files = list((ROOT / "testsets").glob("*.csv"))
    if not files:
        pytest.skip("no testsets/*.csv present")
    seen = set()
    for f in files:
        with f.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                for col in ("text", "query", "question"):
                    if row.get(col):
                        seen.add(_norm(row[col]))
    leaked = {_norm(it["state"]) for it in _load("train") + _load("calib")} & seen
    assert not leaked, sorted(leaked)[:5]
