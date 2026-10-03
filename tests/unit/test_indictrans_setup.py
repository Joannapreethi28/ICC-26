import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location("translation_setup", Path(__file__).parents[2] / "eval_data/tools/setup_indictrans_runtime.py")
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


def test_default_only_prints_plan_without_installing_or_downloading(monkeypatch, capsys):
    monkeypatch.setattr(setup, "validate_plan", lambda: {})

    def forbidden(*args, **kwargs):
        raise AssertionError("Network/install is not allowed without explicit approval flag")

    monkeypatch.setattr(setup, "subprocess", SimpleNamespace(run=forbidden))
    monkeypatch.setattr(setup, "small_source", forbidden)
    setup.main([])
    assert "Plan only" in capsys.readouterr().out


def test_download_rejects_changed_model_source_before_network(tmp_path, monkeypatch):
    model = tmp_path / "model"
    model.mkdir()
    (model / "config.json").write_bytes(b"{}")
    plan = {"repo_id": setup.REPO_ID, "revision": setup.REVISION,
            "planned_weight_files": [{"filename": "model.safetensors", "bytes": setup.WEIGHT_BYTES}],
            "small_files": [{"filename": "config.json", "bytes": 2,
                             "sha256": hashlib.sha256(b"{}").hexdigest()}]}
    access = tmp_path / "access.json"
    access.write_text(json.dumps(plan))
    monkeypatch.setattr(setup, "MODEL", model)
    monkeypatch.setattr(setup, "ACCESS_PLAN", access)
    assert setup.validate_plan() == plan
    (model / "config.json").write_bytes(b"[]")
    with pytest.raises(ValueError, match="Model file changed"):
        setup.validate_plan()
