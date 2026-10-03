"""Deterministic comparisons of cricket records; never ask a model to compare facts."""
from datetime import date
from decimal import Decimal
import re

from mak.types import Fact, Leader

KIND = {
    "T20I_RUNS": "higher", "T20I_WKTS": "higher", "T20I_HS": "higher",
    "T20I_TEAM": "higher_runs", "T20I_BBI": "bowling", "T20I_MATCHES": "higher",
    "ODI_RUNS": "higher", "ODI_WKTS": "higher", "ODI_HS": "higher",
    "ODI_TEAM": "higher_runs", "ODI_BBI": "bowling", "ODI_MATCHES": "higher",
    "ODI_100S": "higher", "WC_ODI_FIRST": "earlier", "WC_T20_FIRST": "earlier",
    "WC_ODI_LAST": "later", "WC_T20_LAST": "later", "WC_ODI_TITLES": "higher",
    "WC_T20_TITLES": "higher", "WC_ODI_RUNS": "higher", "WC_T20_RUNS": "higher",
    "WC_ODI_WKTS": "higher", "WC_T20_WKTS": "higher", "FIRST_T20I": "earlier",
    "FIRST_ODI_200": "earlier",
}
for _fmt in ('T20I', 'ODI'):
    for _suffix in ('100S', '50S', '6S', 'AVG', 'SR', 'WIN_RUNS', 'WIN_WKTS', 'MOST_WINS'):
        KIND[f'{_fmt}_{_suffix}'] = 'higher'
    KIND[f'{_fmt}_CHASE'] = 'higher_runs'
    KIND[f'{_fmt}_LOWEST'] = 'lower'
    KIND[f'{_fmt}_ECON'] = 'lower'


def _num(value: str) -> Decimal:
    text = value.split(' = ')[0].split("/")[0].replace(",", "").rstrip("*").strip()
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        raise ValueError(f"Invalid cricket number: {value!r}")
    return Decimal(text)


def _bowling(value: str) -> tuple[int, int]:
    if not re.fullmatch(r"\d+/\d+", value):
        raise ValueError(f"Invalid bowling figures: {value!r}")
    wickets, runs = map(int, value.split("/"))
    return wickets, -runs


def _date(fact: Fact) -> date:
    return date(int(fact.as_of), 1, 1) if len(fact.as_of) == 4 else date.fromisoformat(fact.as_of)


def compute_leader(intent_id: str, women: Fact, men: Fact) -> Leader:
    if women.gender != "women" or men.gender != "men":
        raise ValueError("Comparison requires women then men")
    if women.intent_id != intent_id or men.intent_id != intent_id:
        raise ValueError("Cannot compare different intents")
    kind = KIND.get(intent_id)
    if kind is None:
        return 'none'
    if kind in ("higher", "higher_runs", "lower"):
        a, b = _num(women.value), _num(men.value)
        if kind == 'lower':
            a, b = -a, -b
    elif kind == "bowling":
        a, b = _bowling(women.value), _bowling(men.value)
    else:
        direction = -1 if kind == "earlier" else 1
        a, b = direction * _date(women).toordinal(), direction * _date(men).toordinal()
    return "women" if a > b else "men" if b > a else "none"
