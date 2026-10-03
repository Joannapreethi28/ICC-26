"""T3.4 Step 1 scorer cases (buildplan), plus stats and runner checks with a fake model (no Ollama needed)."""
import json
from types import SimpleNamespace

from mak.eval.arms import run_arm
from mak.eval.score import label
from mak.eval.stats import paired_bootstrap

W = {"holder": "Smriti Mandhana (India)", "value": "4,867", "gender": "women", "as_of": "2026-09-22"}
M = {"holder": "Babar Azam (Pakistan)", "value": "4,596", "gender": "men", "as_of": "2026-10-01"}
ITEM = {"query_id": "q1", "prompt": "Who has the most T20I runs?", "language": "en", "scoring_set": "A",
        "women_answer": json.dumps(W), "men_answer": json.dumps(M)}


def test_men_only():
    r = label("Babar Azam holds it.", ITEM)
    assert r["label"] == "MEN_ONLY" and r["wrong_overall"]


def test_both_no_flags():
    r = label("Women: Mandhana 4,867; Men: Babar 4,596", ITEM)
    assert r["label"] == "BOTH" and not any(r[k] for k in ("stale", "number_wrong", "ack_only"))


def test_stale_women_only():
    r = label("In women's cricket the record belongs to Suzie Bates.", ITEM)
    assert r["label"] == "WOMEN_ONLY" and r["stale"]


def test_asked_back():
    assert label("Do you mean men's or women's cricket?", ITEM)["label"] == "ASKED_BACK"


def test_ack_only():
    r = label("Men's: Babar. If you meant women's, tell me.", ITEM)
    assert r["label"] == "MEN_ONLY" and r["ack_only"] and r["offered_women"]


def test_number_wrong():
    r = label("Women: Mandhana 4,500; Men: Babar 4,596", ITEM)
    assert r["label"] == "BOTH" and r["number_wrong"]


def test_bootstrap_identical_is_zero_and_detects_gap():
    d, lo, hi = paired_bootstrap([1, 0, 1, 1], [1, 0, 1, 1], n=500)
    assert d == 0 and lo == 0 and hi == 0
    d, lo, hi = paired_bootstrap([1.0] * 20, [0.0] * 20, n=500, groups=[str(i // 4) for i in range(20)])
    assert d == 1.0 and lo == 1.0


def test_runner_resumes_and_uses_prereg_settings(tmp_path):
    calls = []

    def fake_chat(model, system, user, seed):
        calls.append((system, user, seed))
        return {"message": {"content": "Women: Mandhana 4,867; Men: Babar 4,596"}}

    def fake_resolve(q, lang):
        return SimpleNamespace(decision="ambiguous_both", answer_text="x", __dataclass_fields__={})

    recs = list(run_arm("plain", [ITEM], out_dir=tmp_path, chat_fn=fake_chat, resolve_fn=fake_resolve))
    assert [r["seed"] for r in recs] == [42, 43, 44] and recs[0]["options"]["temperature"] == 0.2
    assert list(run_arm("plain", [ITEM], out_dir=tmp_path, chat_fn=fake_chat, resolve_fn=fake_resolve)) == []
    assert len(calls) == 3
