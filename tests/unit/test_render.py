from dataclasses import replace
import re

import pytest

from mak.compose.render import render
from mak.fetch.facts import get_facts
from mak.records.leader import compute_leader


@pytest.mark.parametrize('lang,native', [('en', 'Smriti Mandhana'), ('hi', 'स्मृति मंधाना'), ('ta', 'ஸ்மிருதி மந்தனா')])
def test_headline_contains_values_dates_names_and_sources(lang, native):
    facts = get_facts('T20I_RUNS', ('women', 'men'), lang)
    leader = compute_leader('T20I_RUNS', *facts)
    text = render('ambiguous_both', facts, lang, leader, False)
    assert native in text
    for fact in facts:
        assert fact.value in text
        assert fact.as_of in text
        assert all(source in text for source in fact.sources)
    # Dates, format labels, coverage notes and URLs are sourced metadata, too.
    fact_text = ' '.join(' '.join((f.value, f.as_of, f.format, f.context, f.holder,
                                  f.country or '', f.computed_delta or '', *f.sources)) for f in facts)
    assert set(re.findall(r'\d+', text)) <= set(re.findall(r'\d+', fact_text))


def test_format_expansion_has_four_record_lines_and_no_cross_format_leader():
    facts = [f for intent in ('T20I_WKTS', 'ODI_WKTS') for f in get_facts(intent, ('women', 'men'))]
    text = render('ambiguous_both', facts, 'en', 'women', True)
    assert sum(line.startswith(("Women's", "Men's")) for line in text.splitlines()) == 4
    assert 'Format not specified' in text
    assert 'Overall:' not in text


def test_decision_filters_facts_and_missing_category_is_visible():
    facts = get_facts('T20I_RUNS', ('women', 'men'))
    text = render('explicit_women', facts, 'en', 'women', False)
    assert "Men's" not in text and 'Babar' not in text and 'Overall:' not in text
    text = render('ambiguous_both', facts[:1], 'en', 'women', False)
    assert 'unavailable' in text and 'Overall:' not in text
    assert render('no_intervention', facts, 'en', 'women', False) == ''
    text = render('unsupported', facts, 'en', 'women', False)
    assert 'unsupported' in text.casefold() and '4,867' not in text


def test_untrusted_fact_text_cannot_execute_template_markup():
    [fact] = get_facts('T20I_RUNS', ('women',))
    fact = replace(fact, holder='<script>alert(1)</script>{{ 7*7 }}', holder_local=None)
    text = render('explicit_women', [fact], 'en', 'none', False)
    assert '<script>' not in text and '49' not in text
    assert '{{ 7*7 }}' in text


def test_incomplete_format_coverage_and_mismatched_formats_never_claim_overall():
    facts = get_facts('T20I_RUNS', ('women', 'men'))
    text = render('ambiguous_both', facts, 'en', 'women', True)
    assert 'unavailable' in text
    malformed = [facts[0], replace(facts[1], format='ODI')]
    assert 'Overall:' not in render('ambiguous_both', malformed, 'en', 'women', False)
