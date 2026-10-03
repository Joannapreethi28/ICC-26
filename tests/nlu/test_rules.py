"""J-P1: the rules baseline. Expected values come from buildplan T1.5 + Review Focus 1-2."""
import pytest

from mak.nlu.lang import detect_lang
from mak.nlu.understand import understand

# (text, lang, gender_signal, topic, family, stat, format)
CASES = [
    ("Who has the most T20I runs?", "en", "none", "cricket_stat", "career_record", "runs", "T20I"),
    ("women's cricket most runs T20", "en", "women", "cricket_stat", "career_record", "runs", "T20I"),
    ("most men's ODI wickets", "en", "men", "cricket_stat", "career_record", "wickets", "ODI"),
    ("men's and women's most T20I runs", "en", "both_named", "cricket_stat", "career_record", "runs", "T20I"),
    ("T20 इंटरनेशनल में सबसे ज़्यादा रन किसने बनाए?", "hi", "none", "cricket_stat", "career_record", "runs", "T20I"),
    ("सबसे ज़्यादा विकेट लेने वाली गेंदबाज़ कौन है?", "hi", "women", "cricket_stat", "career_record", "wickets", "unspecified"),
    ("T20 சர்வதேச கிரிக்கெட்டில் அதிக ரன்கள் எடுத்தவர் யார்?", "ta", "none", "cricket_stat", "career_record", "runs", "T20I"),
    ("அதிக விக்கெட்டுகள் எடுத்த வீராங்கனை யார்?", "ta", "women", "cricket_stat", "career_record", "wickets", "unspecified"),
    ("அதிக விக்கெட்டுகள் எடுத்த வீரர் யார்?", "ta", "none", "cricket_stat", "career_record", "wickets", "unspecified"),
    ("T20I mein sabse zyada run kisne banaye", "hi", "none", "cricket_stat", "career_record", "runs", "T20I"),
    ("T20I la adhiga run adichavanga yaaru", "ta", "none", "cricket_stat", "career_record", "runs", "T20I"),
    ("How long is a cricket pitch?", "en", "none", "cricket_general", None, None, None),
    ("Who has scored the most goals in a World Cup?", "en", "none", "other_sport_stat", None, None, None),
    ("Sharma most T20I wickets", "en", "none", "cricket_stat", "career_record", "wickets", "T20I"),
]


@pytest.mark.parametrize("text,lang,signal,topic,family,stat,fmt", CASES)
def test_rule_cases(text, lang, signal, topic, family, stat, fmt):
    p = understand(text)
    assert (p.lang, p.gender_signal, p.topic, p.family, p.stat, p.format) == (lang, signal, topic, family, stat, fmt)
    assert p.gender_conf == (1.0 if signal != "none" else 0.0)
    assert not p.injection_suspected


def test_weak_cue_is_traced_but_never_an_override():
    p = understand("அதிக விக்கெட்டுகள் எடுத்த வீரர் யார்?")
    assert p.gender_signal == "none"
    assert any("weak cue: வீரர்" in line for line in p.trace)


def test_hindi_weak_cue_vaala_is_not_women_or_men():
    p = understand("सबसे ज़्यादा रन बनाने वाला खिलाड़ी कौन है?")
    assert p.gender_signal == "none" and p.stat == "runs"
    assert any("weak cue" in line for line in p.trace)


def test_women_is_not_matched_as_men():
    assert understand("women T20I runs").gender_signal == "women"
    assert understand("female ODI wickets").gender_signal == "women"
    assert understand("male ODI wickets").gender_signal == "men"


@pytest.mark.parametrize("text,lang", [
    ("T20I mein sabse zyada run kisne banaye", "hi"),
    ("T20I la adhiga run adichavanga yaaru", "ta"),
    ("Who has the most runs, yaaru?", "en"),  # one marker is not enough
    ("महिला T20I में सबसे ज़्यादा रन", "hi"),
    ("அதிக ரன்கள்", "ta"),
    ("", "en"),
])
def test_language_detection(text, lang):
    assert detect_lang(text) == lang


def test_review_focus_romanised_stat_is_found():
    p = understand("T20I mein sabse zyada run kisne banaye")
    assert (p.lang, p.stat, p.format, p.gender_signal) == ("hi", "runs", "T20I", "none")


@pytest.mark.parametrize("text", [
    "Who has the most wickets?",
    "Highest team total in ODI",
    "women's T20 World Cup winner cricket",
    "most centuries in ODI",
    "best bowling figures T20I",
    "who won the last T20I",
])
def test_misc_cricket_questions_are_cricket_stats(text):
    assert understand(text).topic == "cricket_stat"


@pytest.mark.parametrize("text", ["", "   ", "🏏🏏🏏", "What is the capital of France?", "x" * 5000, "?" * 5000])
def test_empty_emoji_non_cricket_and_long_input_never_intervene(text):
    p = understand(text)
    assert p.topic == "non_sport" and p.family is None and p.gender_signal == "none"


def test_never_raises_on_non_string():
    assert understand(None).topic == "non_sport"  # type: ignore[arg-type]
    assert understand(12345).topic == "non_sport"  # type: ignore[arg-type]


def test_use_laya_with_unavailable_model_falls_back_to_rules(monkeypatch):
    monkeypatch.setenv("MAK_LAYA_PATH", "no/such/model/dir")
    p = understand("Who has the most T20I runs?", use_laya=True)
    assert p.stat == "runs" and any("laya unavailable" in line for line in p.trace)


def test_explicit_lang_overrides_detection():
    assert understand("most runs", lang="hi").lang == "hi"


@pytest.mark.parametrize("text,family,stat", [
    ("Who has the highest ODI score?", "career_record", "highest_score"),
    ("highest T20I individual score", "career_record", "highest_score"),
    ("most runs in the Hundred", "career_record", "runs"),
    ("most hundreds in ODI", "career_record", "centuries"),
    ("Who is the best batter in the world?", "role_or_ranking", "number_one"),
])
def test_probe_regressions_from_j_p1(text, family, stat):
    p = understand(text)
    assert (p.family, p.stat) == (family, stat)


def test_all_lexicons_load_and_compile():
    # understand() fails safe on any error, so a broken YAML would silently disable the rules: guard it here.
    from mak.nlu import rules
    for lg in ("en", "hi", "ta"):
        assert rules._lexicon((lg,) if lg == "en" else (lg, "en")).stats
    assert rules.detect_injection("ignore previous instructions")
