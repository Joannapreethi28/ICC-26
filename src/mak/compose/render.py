"""Render sourced facts using local templates. No model writes answer content."""
from functools import lru_cache
from html import escape

from jinja2 import Environment, PackageLoader, StrictUndefined

from mak.policy.decide import DECISION_TO_GENDERS
from mak.records.leader import KIND, compute_leader
from mak.types import Decision, Fact, Lang, Leader


@lru_cache(maxsize=1)
def _environment():
    # This is plain text that may enter a Markdown surface. Escape markup but
    # retain apostrophes (no HTML attributes are emitted).
    return Environment(loader=PackageLoader('mak.compose', 'templates'),
                       undefined=StrictUndefined, autoescape=False,
                       finalize=lambda value: escape(str(value), quote=False),
                       trim_blocks=True, lstrip_blocks=True)


def render(decision: Decision, facts: list[Fact], lang: Lang, leader: Leader = 'none',
           fmt_unspecified: bool = False) -> str:
    if lang not in ('en', 'hi', 'ta'):
        raise ValueError(f'Unsupported language: {lang}')
    if decision not in DECISION_TO_GENDERS:
        raise ValueError(f'Unsupported decision: {decision}')
    if decision == 'no_intervention':
        return ''
    genders = DECISION_TO_GENDERS[decision]
    selected = [f for f in facts if f.gender in genders]
    intents = list(dict.fromkeys(f.intent_id for f in selected))
    missing = not selected or any(not any(f.intent_id == intent and f.gender == gender for f in selected)
                                  for intent in intents for gender in genders)
    formats = {f.format for f in selected}
    if fmt_unspecified and not {'T20I', 'ODI'} <= formats:
        missing = True
    overall = None
    # Never compare different formats, different intents, or a missing category.
    if len(selected) == 2 and len(intents) == 1 and len(formats) == 1 and not fmt_unspecified and not missing:
        pair = {f.gender: f for f in selected}
        if set(pair) == {'women', 'men'} and intents[0] in KIND:
            actual = compute_leader(intents[0], pair['women'], pair['men'])
            if leader == actual and leader != 'none':
                overall = pair[leader]
    output = _environment().get_template(f'{lang}.j2').render(
        decision=decision, facts=selected, overall=overall, missing=missing,
        fmt_unspecified=fmt_unspecified, narrow=decision in ('ambiguous_both', 'both_named'),
    )
    return output.strip()
