"""Connect the project to Hugging Face and inspect IndicTrans2 before downloading weights.

Run in normal PowerShell with the project's Python. Credentials stay in the
workspace's .icc-tools/hf-home directory, outside the project repository.
No model code is executed, and no large model weights are downloaded here.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
REPO_ID = "ai4bharat/indictrans2-en-indic-dist-200M"
CLI_VERSION = "2.1.1"
MODEL_DIR = ROOT / "models/indictrans2-en-indic-dist-200M"
PLAN_PATH = ROOT / "eval_data/preparation/indictrans2_download_plan.json"
METADATA_LIMIT = 50 * 1024 * 1024
WEIGHT_SUFFIXES = {".safetensors", ".bin", ".pt", ".pth", ".h5", ".msgpack", ".onnx", ".gguf"}


def plan_files(siblings):
    metadata, weights = [], []
    for item in siblings:
        filename, size = item.rfilename, item.size
        path = PurePosixPath(filename)
        if path.is_absolute() or ".." in path.parts or "\\" in filename or ":" in filename:
            raise ValueError("Unsafe repository filename")
        if not isinstance(size, int) or size < 0:
            raise ValueError(f"Missing file size: {filename}")
        record = {"filename": filename, "bytes": size}
        if path.suffix in WEIGHT_SUFFIXES:
            if filename == "model.safetensors":
                weights.append(record)
        else:
            metadata.append(record)
    if len(weights) != 1:
        raise ValueError("Expected exactly model.safetensors; inspect repository layout")
    if sum(row["bytes"] for row in metadata) > METADATA_LIMIT:
        raise ValueError("Small-file inspection exceeds 50 MiB; stopped before downloading")
    return metadata, weights


def inspect_model(api, downloader):
    info = api.model_info(REPO_ID, files_metadata=True, token=True)
    revision = info.sha
    if not isinstance(revision, str) or len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise ValueError("The Hub did not return a pinned Git revision")
    metadata, weights = plan_files(info.siblings)
    print(f"Model access confirmed. Revision: {revision}", flush=True)
    print(f"Small configuration/source files: {sum(r['bytes'] for r in metadata) / 1048576:.2f} MiB", flush=True)
    print(f"Model weights, NOT downloaded: {sum(r['bytes'] for r in weights) / 1048576:.2f} MiB", flush=True)
    records = []
    for row in metadata:
        path = Path(downloader(repo_id=REPO_ID, filename=row["filename"], revision=revision,
                               local_dir=MODEL_DIR, token=True))
        if path.stat().st_size != row["bytes"]:
            raise ValueError(f"Wrong downloaded size: {row['filename']}")
        records.append(row | {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    plan = {"status": "ACCESS CHECKED; SMALL FILES DOWNLOADED; WEIGHTS NOT DOWNLOADED",
            "checked_at": datetime.now(timezone.utc).isoformat(), "repo_id": REPO_ID,
            "revision": revision, "hub_version": CLI_VERSION, "small_files": records,
            "planned_weight_files": weights, "planned_weight_bytes": sum(r["bytes"] for r in weights),
            "custom_code_review": "pending; no downloaded model code executed",
            "runtime_packages": "not yet installed; separate runtime plan required",
            "large_download_approval": "pending"}
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("HF access ready. Large model download has NOT started.", flush=True)
    print(f"Plan saved: {PLAN_PATH}", flush=True)


def main():
    # Pin the official CLI. No remote shell installer, global PATH change or Git credential change.
    os.environ["HF_HOME"] = str(WORKSPACE / ".icc-tools/hf-home")
    os.environ["HF_HUB_DISABLE_UPDATE_CHECK"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    from importlib.metadata import PackageNotFoundError, version
    try:
        installed = version("huggingface_hub")
    except PackageNotFoundError:
        installed = None
    if installed != CLI_VERSION:
        print("Installing the official Hugging Face CLI into the project Python environment...", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                        f"huggingface_hub=={CLI_VERSION}"], check=True)
    print("Choose 'Log in with your browser' if asked. Follow the URL/code in this terminal.", flush=True)
    print("Keep login codes and tokens in your browser/terminal; do not paste them into chat.", flush=True)
    subprocess.run([sys.executable, "-m", "huggingface_hub.cli.hf", "auth", "login", "--format", "human"], check=True)
    from huggingface_hub import HfApi, hf_hub_download
    inspect_model(HfApi(), hf_hub_download)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError:
        print("CLI setup/login did not finish. Share the error text, not tokens or login codes.", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        # Do not dump HTTP headers, token-bearing request objects or raw auth exceptions.
        print(f"Access check did not finish ({type(exc).__name__}). No model weights were downloaded.", file=sys.stderr)
        if isinstance(exc, (ValueError, OSError)):
            print(str(exc), file=sys.stderr)
        print("Check that the browser account accepted the model's access conditions, then retry.", file=sys.stderr)
        raise SystemExit(1)
