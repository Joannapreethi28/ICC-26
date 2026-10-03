import csv
import json

import pytest

from mak.nlu.entities import resolve_entities


@pytest.fixture
def registry(tmp_path):
    people = [
        ("v", "V Kohli", "men", "253802", ["Virat Kohli", "V Kohli"]),
        ("s", "SM Mandhana", "women", "597806", ["Smriti Mandhana", "SM Mandhana", "स्मृति मंधाना", "ஸ்மிருதி மந்தனா"]),
        ("r", "RG Sharma", "men", "34102", ["Rohit Sharma", "RG Sharma"]),
        ("d", "DB Sharma", "women", "597811", ["Deepti Sharma", "DB Sharma"]),
        ("h", "H Kaur", "women", "1", ["Harmanpreet Kaur"]),
    ]
    with (tmp_path / "people.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["person_id", "name", "gender", "cricinfo_id", "aliases", "match_count"])
        writer.writeheader()
        for pid, name, gender, cricinfo, aliases in people:
            writer.writerow(dict(person_id=pid, name=name, gender=gender, cricinfo_id=cricinfo,
                                 aliases=json.dumps(aliases, ensure_ascii=False), match_count=1))
    (tmp_path / "teams_i18n.csv").write_text("team,gender,label_hi,label_ta\nIndia,women,भारत,இந்தியா\nIndia,men,भारत,இந்தியா\n", encoding="utf-8")
    return tmp_path


def test_named_comparison_resolves_both_categories(registry):
    entities = resolve_entities("Kohli vs Mandhana T20I runs", registry_dir=registry)
    assert {e.gender for e in entities} == {"men", "women"}
    assert {e.entity_id for e in entities} == {"v", "s"}


@pytest.mark.parametrize("text", ["Sharma most T20I wickets", "Kaur matches", "India last result"])
def test_surname_or_shared_team_never_guesses_gender(registry, text):
    entities = resolve_entities(text, registry_dir=registry)
    assert entities
    assert all(e.gender is None for e in entities)


@pytest.mark.parametrize("name", ["Smriti Mandhana", "Smrti Mandhana", "स्मृति मंधाना", "ஸ்மிருதி மந்தனா"])
def test_full_names_native_names_and_minor_typo(registry, name):
    entities = resolve_entities(f"{name} T20I runs", registry_dir=registry)
    assert len(entities) == 1
    assert (entities[0].entity_id, entities[0].gender) == ("s", "women")


@pytest.mark.parametrize("text", ["most runs", "", "🔥", "a" * 5000, "Kohliwood Mandhanaville", "unknown Sharma player"])
def test_no_spurious_gender_from_substrings_or_unknown_names(registry, text):
    assert all(e.gender is None for e in resolve_entities(text, registry_dir=registry))


def test_missing_registry_fails_safe(tmp_path):
    assert resolve_entities("Virat Kohli", registry_dir=tmp_path) == ()
