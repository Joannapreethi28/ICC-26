"""Typed-question definitions for Laya. OWNER: Jabin.

The ONE place where question wording and option descriptions live. Training data, calibration, evaluation and the
serving code (laya_head.py) must all import from here: if the wording differs between training and serving, the
model sees a question it was never trained on (gotcha G-003).

Each question is {"type": "choice", "instructions": str, "criteria": {label: description}}, the shape the Laya
fine-tuning notebook uses. Every choice keeps well under 20 options.
"""
from __future__ import annotations

from mak import labels

MODEL_ID = "convaiinnovations/laya-multilingual"

GENDER_CRITERIA = {
    "women": "the question explicitly asks about women's cricket (women, female, WPL, WT20I, feminine wording)",
    "men": "the question explicitly asks about men's cricket (men, male, IPL, masculine wording)",
    "both_named": "the question names both women's and men's cricket",
    "none": "no explicit gender is stated; the question does not say women's or men's",
}
TOPIC_CRITERIA = {
    "cricket_stat": "asks for a cricket record, statistic, result, winner or ranking",
    "cricket_general": "a cricket question that is not a record (rules, pitch length, how the game works)",
    "other_sport_stat": "asks for a record or statistic in a sport other than cricket",
    "non_sport": "not about sport",
}
FAMILY_CRITERIA = {
    "career_record": "a player's career total or best, such as most runs, wickets or centuries",
    "world_cup_record": "about the World Cup: winners, titles, top scorers, first edition",
    "firsts_history": "a first in cricket history, such as the first match or first double century",
    "team_record": "a team record: lowest total, biggest win, highest chase, most wins",
    "player_stat": "stats or a career summary for one named player",
    "recent_result": "the latest or most recent match result",
    "role_or_ranking": "a captain or a number-one ranking",
    "other_stat": "a cricket statistic that fits none of the other families",
}
FORMAT_CRITERIA = {
    "T20I": "T20 international matches",
    "ODI": "one-day international matches",
    "Test": "Test matches",
    "T20_WC": "the T20 World Cup",
    "ODI_WC": "the ODI (50-over) World Cup",
    "league": "a franchise league such as IPL, WPL, BBL or WBBL",
    "unspecified": "no format is stated",
}
STAT_CRITERIA: dict[str, dict[str, str]] = {
    "career_record": {
        "runs": "most career runs", "wickets": "most career wickets", "highest_score": "highest individual score",
        "team_total": "highest team total", "best_bowling": "best bowling figures", "matches": "most matches played",
        "centuries": "most centuries", "fifties": "most fifties", "sixes": "most sixes",
        "average": "best batting or bowling average", "strike_rate": "best strike rate", "economy": "best economy rate",
    },
    "world_cup_record": {
        "first_edition": "when or where the first World Cup was played", "latest_winner": "who won the most recent World Cup",
        "most_titles": "which team has won the most World Cups", "most_runs": "most runs in World Cups",
        "most_wickets": "most wickets in World Cups", "edition_winner": "who won a World Cup in a named year",
        "edition_top_scorer": "top run scorer of a World Cup in a named year",
    },
    "firsts_history": {
        "first_match": "the first match played", "first_double_century": "the first double century",
        "other_first": "any other first in cricket history",
    },
    "team_record": {
        "lowest_total": "lowest team total", "biggest_win_runs": "biggest win by runs",
        "biggest_win_wickets": "biggest win by wickets", "highest_chase": "highest successful run chase",
        "most_wins": "most match wins",
    },
    "player_stat": {"career_line": "a player's career stats summary", "vs_team": "a player's record against one team"},
    "recent_result": {"last_result": "result of the latest match"},
    "role_or_ranking": {"captain": "who is or was captain", "number_one": "who is ranked number one or the best"},
    "other_stat": {"other": "a statistic not listed above"},
}


def _q(instructions: str, criteria: dict[str, str]) -> dict:
    return {"type": "choice", "instructions": instructions, "criteria": dict(criteria)}


def build_questions() -> dict[str, dict]:
    qs = {
        "gender_signal": _q("Does the cricket question explicitly say women's or men's?", GENDER_CRITERIA),
        "topic": _q("What is this question about?", TOPIC_CRITERIA),
        "family": _q("Which kind of cricket record does the question ask for?", FAMILY_CRITERIA),
        "format": _q("Which cricket format does the question mean?", FORMAT_CRITERIA),
    }
    for fam, crit in STAT_CRITERIA.items():
        if len(crit) > 1:
            qs[f"stat_{fam}"] = _q(f"Which exact {fam.replace('_', ' ')} statistic is asked?", crit)
    return qs


QUESTIONS = build_questions()


def _check() -> None:
    assert tuple(GENDER_CRITERIA) == labels.GENDER_SIGNAL
    assert tuple(TOPIC_CRITERIA) == labels.TOPIC
    assert tuple(FAMILY_CRITERIA) == labels.FAMILY
    assert tuple(FORMAT_CRITERIA) == labels.FORMAT
    assert set(STAT_CRITERIA) == set(labels.STATS)
    for fam, crit in STAT_CRITERIA.items():
        assert tuple(crit) == labels.STATS[fam], fam
    assert all(len(q["criteria"]) < 20 for q in QUESTIONS.values())


_check()
