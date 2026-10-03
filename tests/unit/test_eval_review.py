import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "eval_review", Path(__file__).parents[2] / "eval_data/tools/review.py")
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


def item():
    return {"id": "fixture-1", "lang": "en", "text": "Fixture query",
            "source": "heldout_gen", "evaluation_set": "nlu",
            "private_annotation": "must never reach the blind packet"}


def label(gender="none"):
    return {"id": "fixture-1", "gender_signal": gender, "topic": "cricket_stat",
            "family": "career_record", "stat": "runs", "format": "T20I",
            "expected_decision": "ambiguous_both" if gender == "none" else "explicit_women",
            "slice": "plain", "reason": "Fixture semantic rationale"}


def metadata(family):
    return {"model": "fixture-model", "model_family": family,
            "run_date": "2026-10-03", "seen_training_data": False,
            "seen_other_annotator_labels": False}


def test_blind_packet_contains_only_query_identity_and_task():
    assert review.blind_rows([item()]) == [{"id": "fixture-1", "lang": "en",
                                          "text": "Fixture query", "evaluation_set": "nlu"}]


def test_missing_or_same_family_second_pass_cannot_be_accepted():
    with pytest.raises(ValueError, match="missing"):
        review.reconcile([item()], [label()], [], metadata("gpt"), metadata("claude"), [])
    with pytest.raises(ValueError, match="different model families"):
        review.reconcile([item()], [label()], [label()], metadata("GPT"), metadata("gpt"), [])


def test_unresolved_disagreement_blocks_and_actual_reason_is_preserved():
    args = ([item()], [label()], [label("women")], metadata("gpt"), metadata("claude"))
    with pytest.raises(ValueError, match="Unresolved disagreement"):
        review.reconcile(*args, [])
    decision = {"id": "fixture-1", "chosen": label(), "reason": "Reviewed the subject: no feminine cue."}
    rows, report = review.reconcile(*args, [decision])
    assert rows[0]["adjudicated"] == 1
    assert decision["reason"] in rows[0]["notes"]
    assert report["disagreements"] == 1
    assert report["status"] == "RECONCILED DRAFT — NOT FROZEN"


def test_agreement_is_not_falsely_marked_as_adjudication():
    rows, report = review.reconcile([item()], [label()], [label()], metadata("gpt"), metadata("claude"), [])
    assert rows[0]["adjudicated"] == 0
    assert report["agreements"] == 1


def test_contaminated_review_is_rejected():
    second = metadata("claude")
    second["seen_other_annotator_labels"] = True
    with pytest.raises(ValueError, match="independent"):
        review.reconcile([item()], [label()], [label()], metadata("gpt"), second, [])


def test_cross_sport_packet_accepts_only_the_two_scored_labels():
    row = item() | {"evaluation_set": "xsport", "source": "nq_open"}
    annotation = {"id": row["id"], "gender_signal": "none", "topic": "other_sport_stat",
                  "family": "", "stat": "", "format": "", "expected_decision": "",
                  "slice": "plain", "reason": "Fixture tennis question"}
    rows, _ = review.reconcile([row], [annotation], [annotation], metadata("gpt"), metadata("claude"), [])
    assert rows[0]["expected_decision"] == ""
    with pytest.raises(ValueError, match="cross-sport"):
        review.reconcile([row], [label()], [label()], metadata("gpt"), metadata("claude"), [])


def test_label_contract_rejects_nonexistent_stat_and_injection_override():
    invalid = label() | {"stat": "invented_stat"}
    with pytest.raises(ValueError, match="stat"):
        review.reconcile([item()], [invalid], [invalid], metadata("gpt"), metadata("claude"), [])
    invalid = label("women") | {"slice": "injection"}
    with pytest.raises(ValueError, match="injection"):
        review.reconcile([item()], [invalid], [invalid], metadata("gpt"), metadata("claude"), [])


def test_duplicate_ids_and_extra_adjudication_cannot_silently_overwrite():
    with pytest.raises(ValueError, match="Duplicate"):
        review.reconcile([item(), item()], [label()], [label()], metadata("gpt"), metadata("claude"), [])
    with pytest.raises(ValueError, match="Unexpected adjudication"):
        review.reconcile([item()], [label()], [label()], metadata("gpt"), metadata("claude"),
                         [{"id": "fixture-1", "chosen": label(), "reason": "No disagreement existed"}])
