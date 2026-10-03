"""E1 launcher (buildplan T3.4; PREREGISTRATION 'Model and sampling'). OWNER: Jabin.

  python -m mak.eval.run_e1 --arms plain,prompt_only          # overnight-safe, resumable
  python -m mak.eval.run_e1 --arms layer,layer_text           # after Joanna's real resolve() lands

Before any generation it writes results/e1/run_manifest_<arms>.json with: model tag + resolved digest, Ollama version,
model licence line, hardware, runtime options, git commit, hashes of the frozen inputs. Keeps Windows awake only while
running (SetThreadExecutionState, process-scoped; no system setting is changed).
"""
from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import platform
import subprocess
import sys
import time
import urllib.request

from mak import config
from mak.eval import arms as A

BENCH = config.ROOT / "eval_data" / "benchmark_v1.csv"
FROZEN_INPUTS = [BENCH, config.ROOT / "eval_data" / "PREREGISTRATION.md", config.GOLDEN_PATH, config.ROOT / "testsets" / "FROZEN.md"]


def _sha(p) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "missing"


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8").stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"unavailable: {exc}"


def _ollama(path: str, body: dict | None = None) -> dict:
    url = "http://localhost:11434" + path
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}), timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def manifest(arms: list[str]) -> dict:
    tags = _ollama("/api/tags").get("models", [])
    tag = next((m for m in tags if m.get("name") == A.MODEL or m.get("model") == A.MODEL), None)
    if tag is None:
        sys.exit(f"{A.MODEL} is not pulled; run: ollama pull {A.MODEL}")
    show = _ollama("/api/show", {"model": A.MODEL})
    lic = (show.get("license") or "").strip().splitlines()
    return {
        "created": time.strftime("%Y-%m-%d %H:%M:%S %z"), "arms": arms, "model": A.MODEL, "digest": tag.get("digest"),
        "model_details": tag.get("details"), "model_parameters_text": show.get("parameters"),
        "licence_first_line": lic[0] if lic else "", "ollama_version": _ollama("/api/version").get("version"),
        "options": A.OPTIONS, "seeds": A.SEEDS, "prompts": {"plain": A.PLAIN_SYSTEM, "prompt_only": A.PROMPT_ONLY_SYSTEM,
                                                            "layer": A.LAYER_SYSTEM, "layer_user": A.LAYER_USER},
        "hardware": {"platform": platform.platform(), "cpu": platform.processor(),
                     "gpu": _run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])},
        "git_commit": _run(["git", "-C", str(config.ROOT), "rev-parse", "HEAD"]),
        "git_dirty": bool(_run(["git", "-C", str(config.ROOT), "status", "--porcelain", "src"])),
        "frozen_inputs_sha256": {str(p.relative_to(config.ROOT)): _sha(p) for p in FROZEN_INPUTS},
    }


def keep_awake(on: bool) -> None:
    if platform.system() == "Windows":
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", required=True)
    ap.add_argument("--limit", type=int, default=None, help="smoke only: first N questions; never for the real run")
    a = ap.parse_args()
    arms = a.arms.split(",")
    for arm in arms:
        if arm not in ("plain", "prompt_only", "layer", "layer_text"):
            sys.exit(f"unknown arm {arm}")
    items = list(csv.DictReader(BENCH.open(encoding="utf-8", newline="")))
    out = config.RESULTS_DIR / "e1" / ("smoke" if a.limit else "raw")
    if a.limit:
        items = items[: a.limit]
    out.mkdir(parents=True, exist_ok=True)
    (out / f"run_manifest_{'_'.join(arms)}.json").write_text(json.dumps(manifest(arms), indent=1, ensure_ascii=False), encoding="utf-8")
    keep_awake(True)
    try:
        for arm in arms:
            t0, n, errs = time.time(), 0, 0
            for rec in A.run_arm(arm, items, out_dir=out):
                n += 1
                errs += bool(rec.get("transport_error"))
                if n % 25 == 0:
                    print(f"{arm}: {n} records, {errs} transport errors, {time.time() - t0:.0f}s", flush=True)
            print(f"{arm} DONE: {n} new records, {errs} transport errors, {time.time() - t0:.0f}s", flush=True)
    finally:
        keep_awake(False)


if __name__ == "__main__":
    main()
