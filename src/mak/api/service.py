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
    """Answer a cricket question with labelled records, sources and snapshot dates.

    Args:
        query: A cricket question, between 1 and 2000 characters.
        lang: Answer language: en, hi, ta, or auto.

    Returns:
        Facts, answer text, policy decision and trace. Empty facts mean no verified answer.
    """
    request = ResolveRequest(query=query, lang=lang)
    with _inference_lock:
        result = asdict(resolve(request.query, request.lang))
    for fact in result['results']:
        fact['sources'] = list(fact['sources'])
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
