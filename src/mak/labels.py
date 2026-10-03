"""Closed label sets used by BOTH the training data (Jabin) and the test sets (Joanna).
SHARED CONTRACT: change only with a CONTRACT CHANGE message in document/handoffs.md.

Test-set CSV format (testsets/*.csv), one row per query, columns = TESTSET_COLUMNS:
  id                 unique id, e.g. "en-nq-0001"
  lang               en | hi | ta
  text               the query exactly as written (keep real spelling)
  gender_signal      one of GENDER_SIGNAL
  topic              one of TOPIC
  family             one of FAMILY, empty if topic is not a stat question
  stat               one of STATS[family], empty if not applicable
  format             one of FORMAT, empty if not applicable
  expected_decision  ambiguous_both | explicit_women | explicit_men | both_named | no_intervention | unsupported
  slice              one of SLICES
  source             nq_open | aya | indictrans2 | heldout_gen
  adjudicated        0 (both annotators agreed) | 1 (decided after disagreement; reason in notes)
  notes              free text
"""

GENDER_SIGNAL = ("women", "men", "both_named", "none")
TOPIC = ("cricket_stat", "cricket_general", "other_sport_stat", "non_sport")
FAMILY = ("career_record", "world_cup_record", "firsts_history", "team_record",
          "player_stat", "recent_result", "role_or_ranking", "other_stat")
STATS = {
    "career_record": ("runs", "wickets", "highest_score", "team_total", "best_bowling", "matches",
                      "centuries", "fifties", "sixes", "average", "strike_rate", "economy"),
    "world_cup_record": ("first_edition", "latest_winner", "most_titles", "most_runs", "most_wickets",
                         "edition_winner", "edition_top_scorer"),
    "firsts_history": ("first_match", "first_double_century", "other_first"),
    "team_record": ("lowest_total", "biggest_win_runs", "biggest_win_wickets", "highest_chase", "most_wins"),
    "player_stat": ("career_line", "vs_team"),
    "recent_result": ("last_result",),
    "role_or_ranking": ("captain", "number_one"),
    "other_stat": ("other",),
}
FORMAT = ("T20I", "ODI", "Test", "T20_WC", "ODI_WC", "league", "unspecified")
DECISIONS = ("ambiguous_both", "explicit_women", "explicit_men", "both_named", "no_intervention", "unsupported")
SLICES = ("plain", "typo", "romanised", "grammatical_gender", "injection", "mixed_gender",
          "surname", "control_insensitive", "unsupported", "explicit")
SOURCES = ("nq_open", "aya", "indictrans2", "heldout_gen")
TESTSET_COLUMNS = ("id", "lang", "text", "gender_signal", "topic", "family", "stat", "format",
                   "expected_decision", "slice", "source", "adjudicated", "notes")
