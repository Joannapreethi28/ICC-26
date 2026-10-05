"""Shared validated entry points for REST, Gradio and MCP."""
from dataclasses import asdict
from threading import Lock
from typing import Literal
from pydantic import BaseModel, Field, field_validator
from mak import config
from mak.pipeline import resolve

_inference_lock = Lock()

class ResolveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    lang: Literal['auto', 'en', 'hi', 'ta'] = 'auto'

    @field_validator('query')
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Enter a question.')
        return value


def resolve_sports_query(query: str, lang: str = 'auto') -> dict:
    """Answer a cricket question with labelled records, sources and as-of dates.

    Pass the user's latest question exactly as they wrote it. Do not add, remove
    or infer a gender word ("men's", "women's") and do not carry gender over from
    earlier messages: the tool itself decides whether the question names a gender.
    When the result contains both a women's and a men's record, present both.
    Present the answer naturally, starting with the answer itself, in the
    descriptive style of a normal assistant reply: a few well-written sentences
    that give context (who holds each record, the numbers, how they compare,
    and which is the overall leader when the tool says so), using only the
    returned facts. No emojis, no country flags or country-code badges, no
    decorative symbols. Give every record its own as-of date.
    Avoid technical introductions such as "according to the plugin" or "as of
    the latest verified snapshots". Preserve the returned gender categories,
    factual values, source links and each record's as-of date. Do not describe
    dated records as live totals. Keep missing-data, uncertainty and computed
    coverage qualifications when present. Do not recite the internal trace or
    implementation details unless the user asks. Native tool-use indicators
    belong to the host assistant and should remain visible.

    Args:
        query: The user's question, verbatim (1 to 2000 characters); no added gender words.
        lang: Answer language: en, hi, ta, or auto.

    Returns:
        Facts, answer text, policy decision and trace. Empty facts mean no verified answer.
    """
    request = ResolveRequest(query=query, lang=lang)
    with _inference_lock:
        result = asdict(resolve(request.query, request.lang))
    for fact in result['results']:
        fact['sources'] = list(fact['sources'])
    print(f"resolve: {result['decision']} lang={request.lang} q={request.query[:200]!r}", flush=True)  # host logs only
    return result


def list_supported_intents() -> list[dict]:
    """List catalogue intents. Catalogue support does not guarantee local data coverage."""
    from mak.fetch.catalogue import CATALOGUE
    return [dict(intent_id=i, family=f, stat=s, format=fmt)
            for (f, s, fmt), i in CATALOGUE.items()]


def coverage() -> dict:
    from mak.records.golden import load_golden
    facts = load_golden()
    return dict(supported_intents=len(list_supported_intents()), golden_records=len(facts),
                golden_intents=len({f.intent_id for f in facts}), languages=['en', 'hi', 'ta'],
                formats=sorted({f.format for f in facts}),
                as_of_dates=sorted({f.as_of for f in facts}),
                computed_database_available=config.DB_PATH.is_file())


def health() -> dict:
    from mak.nlu.laya_head import default_path, _cache
    return dict(status='ok', version='0.1.0', use_laya=config.USE_LAYA,
                gender_threshold=config.GENDER_THRESHOLD,
                model_status=('disabled' if not config.USE_LAYA else
                              'loaded' if _cache else
                              'configured_not_loaded' if default_path() else 'missing_weights'))
