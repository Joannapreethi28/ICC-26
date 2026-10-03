from mak.eval.classifier_eval import ece, evaluate, rules_predict, wilson


def test_wilson_known_value():
    lo, hi = wilson(90, 100)
    assert abs(lo - 0.826) < 0.002 and abs(hi - 0.945) < 0.002


def test_ece_perfect_and_overconfident():
    assert ece([1.0, 1.0], [1, 1]) == 0.0
    assert abs(ece([0.9] * 10, [0] * 10) - 0.9) < 1e-9


def test_evaluate_on_tiny_csv(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text("id,lang,text,gender_signal,topic,family,stat,format,expected_decision,slice,source,adjudicated,notes\n"
                 "a,en,Who has the most T20I runs?,none,cricket_stat,career_record,runs,T20I,ambiguous_both,plain,nq_open,0,\n"
                 "b,en,How long is a cricket pitch?,none,cricket_general,,,,no_intervention,control_insensitive,nq_open,0,\n",
                 encoding="utf-8")
    res = evaluate(rules_predict, p)
    acc = {(r["q"], r["lang"]): r["acc"] for r in res["by_q_lang"]}
    assert acc[("gender_signal", "en")] == 1.0 and acc[("stat", "en")] == 1.0
    assert res["n_queries"] == 2 and res["errors"] == 0
