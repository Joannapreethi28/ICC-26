"""Interface regressions: public tools, validation and honest evidence."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from mak.api.app import app
from mak.api.service import resolve_sports_query
from mak.ui.demo import PRESETS, baseline_html, build_demo, resolve_fn

@pytest.mark.parametrize('query', ['', '   ', 'x' * 2001])
def test_shared_validation(query):
    assert TestClient(app).post('/resolve', json={'query': query}).status_code == 422
    with pytest.raises(ValidationError):
        resolve_sports_query(query)

@pytest.mark.parametrize('lang', ['en', 'hi', 'ta'])
def test_demo_native_headline(lang):
    answer, trace, sources, baseline = resolve_fn(PRESETS[lang][0], lang)
    assert 'record-row' in answer
    assert f'lang="{lang}"' in answer
    assert 'Source 1' in sources
    assert '2026-' in sources
    assert trace


def test_capture_is_exact_and_dated():
    recorded = baseline_html(PRESETS['en'][0], 'en')
    assert 'Virat Kohli' in recorded
    assert '2026-10-03' in recorded
    assert 'llama3.1' in recorded
    assert 'No saved' in baseline_html('a completely new query', 'en')


def test_only_intended_public_tools():
    demo = build_demo()
    public = {d['api_name'] for d in demo.config['dependencies'] if d['api_visibility'] == 'public'}
    assert public == {'resolve_sports_query', 'list_supported_intents'}


def test_named_player_never_returns_unrelated_global_leader():
    result = resolve_sports_query('Virat Kohli T20I runs')
    assert all(f['holder'] == 'Virat Kohli' for f in result['results'])
    assert result['intent'] == 'T20I_PLAYER_LINE'
