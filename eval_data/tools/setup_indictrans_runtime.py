"""Install the isolated CPU runtime and fetch the approved, pinned translation model.

Default is a local plan only. --approved-download is used only after Joanna approves
the >1 GB download. No translation or downloaded model code is run by this helper.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
RUNTIME = WORKSPACE / ".icc-tools/indictrans-runtime"
VENDOR = WORKSPACE / ".icc-tools/indictrans-vendor"
MODEL = ROOT / "models/indictrans2-en-indic-dist-200M"
ACCESS_PLAN = ROOT / "eval_data/preparation/indictrans2_download_plan.json"
INSTALL_REPORT = ROOT / "eval_data/preparation/indictrans2_install.json"
REPO_ID = "ai4bharat/indictrans2-en-indic-dist-200M"
REVISION = "173b94239f7c38886b2747b8d4a5db771a7e1232"
WEIGHT_BYTES = 1_098_427_592
PROCESSOR_REVISION = "0e68fb5872f4d821578a5252f90ad43c9649370f"
PROCESSOR_BASE = f"https://raw.githubusercontent.com/VarunGumma/IndicTransToolkit/{PROCESSOR_REVISION}"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_plan():
    plan = json.loads(ACCESS_PLAN.read_text(encoding="utf-8"))
    if (plan["repo_id"] != REPO_ID or plan["revision"] != REVISION
            or plan["planned_weight_files"] != [{"filename": "model.safetensors", "bytes": WEIGHT_BYTES}]):
        raise ValueError("Model download no longer matches the reviewed plan")
    for row in plan["small_files"]:
        path = (MODEL / row["filename"]).resolve()
        if not path.is_relative_to(MODEL.resolve()):
            raise ValueError("Model file is outside the planned directory")
        if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
            raise ValueError(f"Model file changed: {row['filename']}")
    return plan


def small_source(url, destination):
    import requests
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    if len(response.content) > 100_000:
        raise ValueError("Unexpectedly large processor source")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)
    return {"url": url, "filename": destination.name,
            "bytes": destination.stat().st_size, "sha256": sha256(destination)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-download", action="store_true")
    args = parser.parse_args(argv)
    plan = validate_plan()
    print(f"Model: {REPO_ID} at {REVISION}", flush=True)
    print(f"Weights: {WEIGHT_BYTES / 1e9:.3f} GB; CPU packages add an estimated 0.3-0.6 GB.", flush=True)
    print("CPU runtime: torch 2.6.0+cpu / transformers 4.51.3 in .icc-tools/indictrans-runtime.", flush=True)
    print("English-to-Hindi/Tamil processor: pinned official pure-Python source; no compiler needed.", flush=True)
    if not args.approved_download:
        print("Plan only. Joanna's approval is required before the large download.", flush=True)
        return
    if sys.platform != "win32" or sys.version_info[:2] != (3, 11):
        raise ValueError("This prepared runtime targets Windows x64 / Python 3.11")
    os.environ["HF_HOME"] = str(WORKSPACE / ".icc-tools/hf-home")
    os.environ["PIP_CACHE_DIR"] = str(WORKSPACE / ".icc-tools/pip-cache")
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    # Download source for inspection. Importing this processor happens only in the later local pilot.
    sources = [small_source(PROCESSOR_BASE + "/IndicTransTokenizer/processor.py", VENDOR / "processor.py"),
               small_source(PROCESSOR_BASE + "/LICENSE", VENDOR / "LICENSE")]
    pip_report = WORKSPACE / ".icc-tools/indictrans-pip-report.json"
    print("Installing pinned CPU packages into their separate project-local directory...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                    "--only-binary=:all:", "--upgrade", "--target", str(RUNTIME),
                    "--index-url", "https://pypi.org/simple", "--report", str(pip_report),
                    "-r", str(ROOT / "eval_data/indictrans-runtime-requirements.txt")], check=True)
    # Keep the login SDK and its device credentials separate from the older inference SDK.
    from huggingface_hub import HfApi, hf_hub_download
    info = HfApi().model_info(REPO_ID, revision=REVISION, files_metadata=True, token=True)
    weight = next(row for row in info.siblings if row.rfilename == "model.safetensors")
    expected_hash = weight.lfs.sha256 if weight.lfs is not None else None
    if weight.size != WEIGHT_BYTES or not expected_hash or len(expected_hash) != 64:
        raise ValueError("Pinned weight metadata changed or has no SHA-256")
    print("Downloading the single safetensors weight file (existing partial downloads are reused)...", flush=True)
    path = Path(hf_hub_download(REPO_ID, "model.safetensors", revision=REVISION, local_dir=MODEL, token=True))
    if path.stat().st_size != WEIGHT_BYTES or sha256(path) != expected_hash:
        raise ValueError("Downloaded model failed size/checksum verification")
    installs = json.loads(pip_report.read_text(encoding="utf-8"))["install"]
    packages = [{"name": row["metadata"]["name"], "version": row["metadata"]["version"],
                 "url": row["download_info"]["url"],
                 "hashes": row["download_info"].get("archive_info", {}).get("hashes", {})} for row in installs]
    report = {"status": "DOWNLOADED AND INSTALLED; INFERENCE PILOT PENDING",
              "installed_at": datetime.now(timezone.utc).isoformat(),
              "repo_id": REPO_ID, "revision": REVISION,
              "weight_bytes": WEIGHT_BYTES, "weight_sha256": expected_hash,
              "small_files": plan["small_files"], "processor_sources": sources,
              "processor_revision": PROCESSOR_REVISION, "packages": packages,
              "runtime": "Windows x64 / Python 3.11 / CPU float32",
              "download_approval": "Joanna; helper run explicitly with --approved-download",
              "translation_status": "not run"}
    INSTALL_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Translation files ready. Astra can now run the local compatibility/speed pilot.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError:
        print("Package installation did not finish. Share the pip error above.", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        print(f"Translation setup stopped ({type(exc).__name__}). No translation was run.", file=sys.stderr)
        if isinstance(exc, (ValueError, OSError)):
            print(str(exc), file=sys.stderr)
        raise SystemExit(1)
