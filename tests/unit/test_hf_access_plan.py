import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location("hf_access", Path(__file__).parents[2] / "eval_data/tools/setup_hf_access.py")
access = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(access)


def file(name, size):
    return SimpleNamespace(rfilename=name, size=size)


def test_access_check_only_downloads_small_files_and_pins_revision(tmp_path, monkeypatch):
    monkeypatch.setattr(access, "MODEL_DIR", tmp_path / "model")
    monkeypatch.setattr(access, "PLAN_PATH", tmp_path / "plan.json")
    info = SimpleNamespace(sha="a" * 40, siblings=[file("config.json", 2),
        file("model.safetensors", 1_100_000_000), file("pytorch_model.bin", 1_100_000_000)])
    calls = []

    def download(**kwargs):
        calls.append(kwargs)
        path = tmp_path / kwargs["filename"]
        path.write_bytes(b"{}")
        return path

    access.inspect_model(SimpleNamespace(model_info=lambda *a, **kw: info), download)
    assert [call["filename"] for call in calls] == ["config.json"]
    assert calls[0]["revision"] == "a" * 40
    assert '"large_download_approval": "pending"' in access.PLAN_PATH.read_text()


def test_oversized_metadata_and_unsafe_paths_stop_before_download():
    with pytest.raises(ValueError, match="50 MiB"):
        access.plan_files([file("model.safetensors", 1_100_000_000), file("large.txt", 60 * 1024 * 1024)])
    with pytest.raises(ValueError, match="Unsafe"):
        access.plan_files([file("../outside.py", 20)])


def test_setup_reaches_browser_login_without_venv_or_cli(tmp_path, monkeypatch):
    pytest.importorskip("huggingface_hub")
    import huggingface_hub._login as hub_login
    import importlib.metadata

    calls = []
    monkeypatch.setattr(access, "WORKSPACE", tmp_path)
    monkeypatch.setattr(importlib.metadata, "version", lambda name: access.CLI_VERSION)
    monkeypatch.setitem(sys.modules, "venv", None)  # Windows embedded Python omits it.
    # Run the real SDK terminal-login entry point, stopping at the browser/network boundary.
    monkeypatch.setattr(hub_login, "get_token", lambda: None)
    monkeypatch.setattr(hub_login, "_prompt_login_method", lambda: "browser")
    monkeypatch.setattr(hub_login, "_device_code_login", lambda: calls.append("browser"))
    monkeypatch.setattr(access, "inspect_model", lambda api, downloader: calls.append("inspect"))

    def no_cli(*args, **kwargs):
        raise AssertionError("Login must not launch the CLI extension loader")

    monkeypatch.setattr(access, "subprocess", SimpleNamespace(run=no_cli))
    access.main()
    assert calls == ["browser", "inspect"]
