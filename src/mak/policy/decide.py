"""Pure, deterministic category policy. Query instructions never override it."""
from mak.config import GENDER_THRESHOLD
from mak.types import Decision, Gender, Parse

SIGNAL_TO_DECISION: dict[str, Decision] = {
    'women': 'explicit_women', 'men': 'explicit_men',
    'both_named': 'both_named', 'none': 'ambiguous_both',
}
DECISION_TO_GENDERS: dict[str, tuple[Gender, ...]] = {
    'explicit_women': ('women',), 'explicit_men': ('men',),
    'both_named': ('women', 'men'), 'ambiguous_both': ('women', 'men'),
    'no_intervention': (), 'unsupported': (),
}


def decide(p: Parse, supported: bool) -> tuple[Decision, list[str]]:
    # Injection check MUST come first - it overrides everything
    if p.injection_suspected:
        return 'ambiguous_both', ['policy: injection suspected -> fail-safe both']
    if p.topic in ('cricket_general', 'non_sport'):
        return 'no_intervention', ['policy: gender-insensitive or non-sport -> stay silent']
    if not supported:
        return 'unsupported', ['policy: stats question outside catalogue -> unsupported (never invent)']
    signal, trace = p.gender_signal, []
    # A NaN or invalid confidence must not bypass the fail-safe.
    if signal in ('women', 'men') and not GENDER_THRESHOLD <= p.gender_conf <= 1:
        trace.append(f'policy: gender confidence outside trusted range ({GENDER_THRESHOLD}..1) -> fail-safe both')
        signal = 'none'
    decision = SIGNAL_TO_DECISION.get(signal, 'ambiguous_both')
    trace.append(f'policy: {signal} -> {decision}')
    return decision, trace
