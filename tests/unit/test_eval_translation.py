import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("eval_translate", ROOT / "eval_data/tools/translate.py")
translate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(translate)


def test_resume_signature_binds_text_language_model_and_settings(monkeypatch):
    row = {"id": "x", "text": "A question", "target_lang": "hi", "evaluation_set": "nlu"}
    original = translate.signature(row, "model-install-a", 4)
    assert translate.signature({**row, "text": "Changed question"}, "model-install-a", 4) != original
    assert translate.signature({**row, "target_lang": "ta"}, "model-install-a", 4) != original
    assert translate.signature(row, "model-install-b", 4) != original
    monkeypatch.setitem(translate.PARAMETERS, "num_beams", 1)
    assert translate.signature(row, "model-install-a", 4) != original


def test_requests_reject_duplicate_ids_before_loading_model(tmp_path):
    path = tmp_path / "requests.jsonl"
    row = {"id": "x", "text": "A question", "target_lang": "hi", "evaluation_set": "nlu"}
    path.write_text((json.dumps(row) + "\n") * 2, encoding="utf-8")
    with pytest.raises(ValueError, match="unique IDs"):
        translate.load_requests(path)
