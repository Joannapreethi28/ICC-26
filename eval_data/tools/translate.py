"""Offline, resumable IndicTrans2 generation; outputs remain unreviewed candidates.

Input JSONL: id, text, target_lang (hi/ta), evaluation_set (nlu/benchmark).
No labels are inferred or copied by this script. Raw output is always retained.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
MODEL = ROOT / "models/indictrans2-en-indic-dist-200M"
RUNTIME = WORKSPACE / ".icc-tools/indictrans-runtime"
VENDOR = WORKSPACE / ".icc-tools/indictrans-vendor"
LANGUAGES = {"hi": "hin_Deva", "ta": "tam_Taml"}
PARAMETERS = {"num_beams": 5, "num_return_sequences": 1, "do_sample": False,
              "min_length": 0, "max_length": 256, "use_cache": True}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_install():
    report_path = ROOT / "eval_data/preparation/indictrans2_install.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report["revision"] != "173b94239f7c38886b2747b8d4a5db771a7e1232":
        raise ValueError("Unreviewed model revision")
    files = [(MODEL, row) for row in report["small_files"]]
    files += [(VENDOR, row) for row in report["processor_sources"]]
    files.append((MODEL, {"filename": "model.safetensors", "bytes": report["weight_bytes"],
                          "sha256": report["weight_sha256"]}))
    for base, row in files:
        path = (base / row["filename"]).resolve()
        if not path.is_relative_to(base.resolve()):
            raise ValueError("File outside verified installation")
        if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            raise ValueError(f"Installation checksum mismatch: {row['filename']}")
    return report, digest(report_path)


def load_requests(path):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Translation requests must have unique IDs and cannot be empty")
    for row in rows:
        if row["target_lang"] not in LANGUAGES or not isinstance(row["text"], str) or not row["text"].strip():
            raise ValueError("Invalid translation language/text")
        if row["evaluation_set"] not in {"nlu", "benchmark", "pilot"}:
            raise ValueError("Invalid translation purpose")
    return rows


def signature(row, install_hash, threads):
    payload = {"request": row, "install_sha256": install_hash, "parameters": PARAMETERS,
               "threads": threads, "device": "cpu", "dtype": "float32"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--limit", type=int, help="Small compatibility/speed pilot only")
    args = parser.parse_args(argv)
    if args.threads < 1 or args.batch_size < 1 or (args.limit is not None and args.limit < 1):
        raise ValueError("Thread, batch and pilot limits must be positive")
    sys.stdout.reconfigure(encoding="utf-8")
    requests = load_requests(args.input)
    if args.limit:
        requests = requests[:args.limit]
    report, install_hash = verify_install()
    expected = {row["id"]: signature(row, install_hash, args.threads) for row in requests}
    existing = []
    if args.output.exists():
        existing = [json.loads(line) for line in args.output.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len({row["id"] for row in existing}) != len(existing):
        raise ValueError("Duplicate cached translation ID")
    for row in existing:
        if expected.get(row["id"]) != row.get("request_sha256"):
            raise ValueError("Cached output belongs to different inputs, model or settings")
    completed = {row["id"] for row in existing}
    pending = [row for row in requests if row["id"] not in completed]
    if not pending:
        print(f"All {len(existing)} translations already cached; semantic review still required.")
        return
    # Embedded Windows Python ignores PYTHONPATH; put the isolated runtime first.
    sys.path.insert(0, str(RUNTIME))
    for key, value in {"HF_HOME": str(WORKSPACE / ".icc-tools/hf-home"),
                       "HF_MODULES_CACHE": str(WORKSPACE / ".icc-tools/hf-modules"),
                       "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
                       "HF_HUB_DISABLE_TELEMETRY": "1", "TOKENIZERS_PARALLELISM": "false"}.items():
        os.environ[key] = value
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    torch.manual_seed(20261003)
    processor_spec = importlib.util.spec_from_file_location("icc_indic_processor", VENDOR / "processor.py")
    processor_module = importlib.util.module_from_spec(processor_spec)
    processor_spec.loader.exec_module(processor_module)
    processor = processor_module.IndicProcessor(inference=True)
    started = time.perf_counter()
    print("Loading verified local model on CPU...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL), trust_remote_code=True, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        str(MODEL), trust_remote_code=True, local_files_only=True,
        torch_dtype=torch.float32, attn_implementation="eager").eval()
    load_seconds = time.perf_counter() - started
    print(f"Model ready in {load_seconds:.1f}s; {len(pending)} translations pending.", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generation_seconds = 0.0
    with args.output.open("a", encoding="utf-8", newline="\n") as output:
        for lang, tag in LANGUAGES.items():
            selected = [row for row in pending if row["target_lang"] == lang]
            for offset in range(0, len(selected), args.batch_size):
                batch = selected[offset:offset + args.batch_size]
                batch_started = time.perf_counter()
                prepared = processor.preprocess_batch([row["text"] for row in batch],
                    src_lang="eng_Latn", tgt_lang=tag, show_progress_bar=False)
                encoded = tokenizer(prepared, truncation=False, padding="longest", return_tensors="pt")
                if encoded["input_ids"].shape[1] > 256:
                    raise ValueError("Input exceeds model context; refusing silent truncation")
                with torch.inference_mode():
                    generated = model.generate(**encoded, **PARAMETERS)
                raw = tokenizer.batch_decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                translated = processor.postprocess_batch(raw, lang=tag)
                seconds = time.perf_counter() - batch_started
                generation_seconds += seconds
                for row, before, raw_text, text, tokens in zip(batch, prepared, raw, translated, generated):
                    result = {**row, "source_text": row["text"], "text": text,
                              "lang": lang, "source": "indictrans2", "raw_decoded": raw_text,
                              "preprocessed": before, "request_sha256": expected[row["id"]],
                              "model_id": report["repo_id"], "model_revision": report["revision"],
                              "processor_revision": report["processor_revision"],
                              "install_sha256": install_hash, "parameters": PARAMETERS,
                              "cpu_threads": args.threads, "batch_size": len(batch),
                              "batch_seconds": seconds, "generated_tokens": tokens.tolist(),
                              "generation_limit_reached": len(tokens) >= PARAMETERS["max_length"],
                              "created_at": datetime.now(timezone.utc).isoformat(),
                              "status": "UNREVIEWED ACTUAL MODEL OUTPUT"}
                    output.write(json.dumps(result, ensure_ascii=False) + "\n")
                    completed.add(row["id"])
                output.flush()
                print(f"Translated {len(completed)}/{len(requests)}; last {len(batch)} {lang} queries: {seconds:.1f}s", flush=True)
    print(json.dumps({"translations": len(completed), "new_translations": len(pending),
                      "load_seconds": load_seconds, "generation_seconds": generation_seconds,
                      "seconds_per_translation": generation_seconds / len(pending),
                      "status": "Actual translations saved; semantic review pending"}), flush=True)


if __name__ == "__main__":
    main()
