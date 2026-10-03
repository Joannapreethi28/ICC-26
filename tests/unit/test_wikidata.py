import pytest
import requests

from mak.registry.wikidata import fetch_golden_ids, fetch_labels


class Reply:
    def raise_for_status(self):
        pass

    def json(self):
        return {"results": {"bindings": [{
            "id": {"value": "597806"}, "item": {"value": "http://www.wikidata.org/entity/Q16224802"},
            "en": {"value": "Smriti Mandhana"}, "hi": {"value": "स्मृति मंधाना"},
            "ta": {"value": "ஸ்மிருதி மந்தனா"}, "sex": {"value": "http://www.wikidata.org/entity/Q6581072"},
        }]}}


class Source:
    def get(self, url, **kwargs):
        assert "wdt:P2697" in kwargs["params"]["query"]
        assert kwargs["headers"]["User-Agent"]
        return Reply()


class Offline:
    def get(self, *args, **kwargs):
        raise requests.ConnectionError("offline")


def test_labels_are_cached_and_missing_ids_stay_missing(tmp_path):
    cache = tmp_path / "cache.csv"
    result = fetch_labels(["597806", "999"], cache_path=cache, session=Source())
    assert result["597806"]["qid"] == "Q16224802"
    assert result["597806"]["hi"] == "स्मृति मंधाना"
    assert result["597806"]["ta"] == "ஸ்மிருதி மந்தனா"
    assert result["999"]["status"] == "missing"
    assert fetch_labels(["597806", "999"], cache_path=cache, session=Offline()) == result


def test_network_failure_is_not_cached_as_missing(tmp_path):
    cache = tmp_path / "cache.csv"
    with pytest.raises(requests.ConnectionError):
        fetch_labels(["597806"], cache_path=cache, session=Offline(), attempts=1)
    assert not cache.exists()


def test_non_numeric_ids_are_rejected_before_network(tmp_path):
    with pytest.raises(ValueError, match="numeric"):
        fetch_labels(['123" } UNION {'], cache_path=tmp_path / "cache.csv", session=Offline())


def test_golden_lookup_rejects_ambiguous_identity_and_caches_missing(tmp_path):
    class GoldenReply(Reply):
        def json(self):
            return {"results": {"bindings": [
                {"requested": {"value": "Same Name"}, "item": {"value": "http://www.wikidata.org/entity/Q1"}, "id": {"value": "1"}},
                {"requested": {"value": "Same Name"}, "item": {"value": "http://www.wikidata.org/entity/Q2"}, "id": {"value": "2"}},
                {"requested": {"value": "Old Player"}, "item": {"value": "http://www.wikidata.org/entity/Q3"}, "id": {"value": "3"}},
            ]}}

    class GoldenSource:
        def get(self, *args, **kwargs):
            return GoldenReply()

    cache = tmp_path / "golden.csv"
    result = fetch_golden_ids(["Same Name", "Old Player", "Missing"], cache, session=GoldenSource())
    assert result["Same Name"]["status"] == "ambiguous"
    assert result["Same Name"]["cricinfo_id"] == ""
    assert result["Old Player"]["cricinfo_id"] == "3"
    assert result["Missing"]["status"] == "missing"
    assert fetch_golden_ids(list(result), cache, session=Offline()) == result
