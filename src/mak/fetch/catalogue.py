"""Closed supported intents. No format means the planned T20I + ODI default."""

CATALOGUE: dict[tuple[str, str, str], str] = {}
for _fmt in ('T20I', 'ODI'):
    for _stat, _suffix in {
        'runs': 'RUNS', 'wickets': 'WKTS', 'highest_score': 'HS', 'team_total': 'TEAM',
        'best_bowling': 'BBI', 'matches': 'MATCHES', 'centuries': '100S', 'fifties': '50S',
        'sixes': '6S', 'average': 'AVG', 'strike_rate': 'SR', 'economy': 'ECON',
    }.items():
        CATALOGUE['career_record', _stat, _fmt] = f'{_fmt}_{_suffix}'
    for _stat, _suffix in {
        'lowest_total': 'LOWEST', 'biggest_win_runs': 'WIN_RUNS',
        'biggest_win_wickets': 'WIN_WKTS', 'highest_chase': 'CHASE', 'most_wins': 'MOST_WINS',
    }.items():
        CATALOGUE['team_record', _stat, _fmt] = f'{_fmt}_{_suffix}'
    CATALOGUE['player_stat', 'career_line', _fmt] = f'{_fmt}_PLAYER_LINE'
    CATALOGUE['recent_result', 'last_result', _fmt] = f'{_fmt}_LAST_RESULT'
for _fmt, _prefix in (('ODI_WC', 'WC_ODI'), ('T20_WC', 'WC_T20')):
    for _stat, _suffix in {
        'first_edition': 'FIRST', 'latest_winner': 'LAST', 'most_titles': 'TITLES',
        'most_runs': 'RUNS', 'most_wickets': 'WKTS',
    }.items():
        CATALOGUE['world_cup_record', _stat, _fmt] = f'{_prefix}_{_suffix}'
CATALOGUE['firsts_history', 'first_match', 'T20I'] = 'FIRST_T20I'
CATALOGUE['firsts_history', 'first_double_century', 'ODI'] = 'FIRST_ODI_200'

UNSPECIFIED_EXPANSION = {'unspecified': ('T20I', 'ODI')}


def lookup(family: str | None, stat: str | None, fmt: str | None) -> list[str]:
    if not family or not stat:
        return []
    formats = UNSPECIFIED_EXPANSION.get(fmt or 'unspecified', (fmt,))
    return [CATALOGUE[family, stat, f] for f in formats if (family, stat, f) in CATALOGUE]
