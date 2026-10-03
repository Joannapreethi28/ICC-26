"""Fetch official NQ-open/Aya parquet sources, then extract unlabelled candidates.

Usage: python eval_data/tools/fetch_sources.py
This does not call the project's classifier or assign any evaluation labels.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import duckdb
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/evaluation"
OUT = ROOT / "eval_data/preparation"
DATASETS = {"nq_open": "google-research-datasets/nq_open", "aya": "CohereLabs/aya_dataset"}
LICENCES = {"nq_open": "CC-BY-SA-3.0", "aya": "Apache-2.0"}
LIMIT = 900 * 1024 * 1024
HEADERS = {"User-Agent": "MakeAIKnowHer-evaluation/0.1 (https://github.com/Joannapreethi28/ICC-26)"}
CRICKET_EN = re.compile(r"\b(cricket\w*|odi\w*|t20\w*|test match\w*|ipl|wicket\w*|centur\w*|runs?|batsm\w*|batter\w*|bowler\w*|world cup)\b", re.I)
XSPORT_EN = re.compile(r"\b(football|soccer|tennis|basketball|fifa|nba|wnba|wimbledon|ballon d.or|grand slam|olympic\w*|world cup)\b", re.I)
CRICKET_NATIVE = re.compile(r"क्रिकेट|विकेट|शतक|बल्लेबाज|गेंदबाज|கிரிக்கெட்|கிரிக்கெட்ட|விக்கெட்|சதம்|மட்டைப்பந்து", re.I)
XSPORT_NATIVE = re.compile(r"फुटबॉल|टेनिस|बास्केटबॉल|फीफा|கால்பந்து|டென்னிஸ்|கூடைப்பந்து|பீபா|ஃபிஃபா|FIFA", re.I)


def normalised(text: str) -> str:
    # Used only for deduplication; retain original spelling and punctuation in rows.
    import unicodedata
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _get_json(url: str, session, **kwargs) -> dict:
    response = session.get(url, headers=HEADERS, timeout=60, **kwargs)
    response.raise_for_status()
    return response.json()


def file_list(dataset: str, session) -> list[dict]:
    listing = _get_json("https://datasets-server.huggingface.co/parquet", session, params={"dataset": dataset})
    files = [r for r in listing.get("parquet_files", []) if r["config"] == "default"]
    if not files:
        configs = {r["config"] for r in listing.get("parquet_files", [])}
        if len(configs) == 1:
            files = listing["parquet_files"]
        else:
            raise ValueError(f"No unambiguous default config for {dataset}: {sorted(configs)}")
    if any(row["split"] not in {"train", "validation", "test"} for row in files):
        raise ValueError(f"Unexpected source splits for {dataset}")
    return sorted(files, key=lambda row: (row["split"], row["filename"]))


def download_sources(raw_dir: Path = RAW, *, session=None) -> dict:
    session = session or requests.Session()
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = raw_dir / "manifest.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    listings = {key: file_list(dataset, session) for key, dataset in DATASETS.items()}
    planned = sum(row["size"] for key, rows in listings.items() for row in rows
                  if not (raw_dir / key / row["split"] / Path(row["filename"]).name).exists())
    print(f"Official source parquet download: {planned / 1048576:.2f} MiB", flush=True)
    if planned > LIMIT:
        raise RuntimeError("Sources exceed 900 MiB; ask Joanna before a >1 GB download")
    manifest = {"created_at": datetime.now(timezone.utc).isoformat(), "files": [], "complete": False}
    old_files = {row["path"]: row for row in old.get("files", [])}
    # Retain all existing provenance if a resumed run fails part-way through.
    recorded = dict(old_files)
    received = 0
    for key, files in listings.items():
        for row in files:
            relative = f"{key}/{row['split']}/{Path(row['filename']).name}"
            target = raw_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            fetched_at = old_files.get(relative, {}).get("fetched_at")
            if target.exists() and relative not in old_files:
                raise ValueError(f"Cached file lacks download provenance: {relative}; inspect before using")
            if target.exists() and old_files[relative]["url"] != row["url"]:
                raise ValueError(f"Source URL changed: {relative}; inspect before refreshing")
            if not target.exists():
                print(f"Downloading {relative}: {row['size'] / 1048576:.2f} MiB", flush=True)
                partial = target.with_suffix(".parquet.part")
                try:
                    with session.get(row["url"], headers=HEADERS, timeout=90, stream=True) as response:
                        response.raise_for_status()
                        with partial.open("wb") as fh:
                            for block in response.iter_content(1024 * 1024):
                                received += len(block)
                                if received > LIMIT:
                                    raise RuntimeError("Source download exceeded 900 MiB")
                                fh.write(block)
                    if partial.stat().st_size != row["size"]:
                        raise ValueError(f"Wrong download size: {relative}")
                    partial.replace(target)
                    fetched_at = datetime.now(timezone.utc).isoformat()
                finally:
                    partial.unlink(missing_ok=True)
            if target.stat().st_size != row["size"]:
                raise ValueError(f"Cached source size changed: {relative}; inspect before refreshing")
            digest = file_sha256(target)
            if relative in old_files and old_files[relative]["sha256"] != digest:
                raise ValueError(f"Cached source changed: {relative}; inspect before refreshing")
            with duckdb.connect() as conn:
                count = conn.execute("SELECT count(*) FROM read_parquet(?)", [str(target)]).fetchone()[0]
            recorded[relative] = {"dataset": DATASETS[key], "source": key, "split": row["split"],
                "path": relative, "url": row["url"], "bytes": target.stat().st_size, "sha256": digest,
                "rows": count, "fetched_at": fetched_at, "licence": LICENCES[key]}
            manifest["files"] = list(recorded.values())
            _write_manifest(manifest_path, manifest)
            print(f"Validated {relative}: {count:,} rows", flush=True)
    current = {f"{key}/{row['split']}/{Path(row['filename']).name}" for key, rows in listings.items() for row in rows}
    manifest["files"] = [recorded[path] for path in sorted(current)]
    manifest["complete"] = True
    _write_manifest(manifest_path, manifest)
    return manifest


def _write_manifest(path: Path, manifest: dict):
    temporary = path.with_suffix(".json.part")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def extract_candidates(raw_dir: Path = RAW, output_dir: Path = OUT) -> dict:
    manifest = json.loads((raw_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("complete") is not True:
        raise ValueError("Source download manifest is incomplete; finish the download before extraction")
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates, controls, seen = [], [], {}
    counts = Counter()
    for source in manifest["files"]:
        path = raw_dir / source["path"]
        if file_sha256(path) != source["sha256"]:
            raise ValueError(f"Source checksum changed before extraction: {source['path']}")
        with duckdb.connect() as conn:
            if source["source"] == "nq_open":
                rows = conn.execute("SELECT row_number() OVER () - 1, question FROM read_parquet(?)", [str(path)]).fetchall()
            else:
                rows = conn.execute("""SELECT original_row, inputs, language FROM
                    (SELECT row_number() OVER () - 1 AS original_row, * FROM read_parquet(?))
                    WHERE language IN ('Hindi', 'Tamil')""", [str(path)]).fetchall()
        for record in rows:
            index, text = record[:2]
            lang = "en" if source["source"] == "nq_open" else {"Hindi": "hi", "Tamil": "ta"}[record[2]]
            counts[f"scanned_{lang}"] += 1
            key = lang, normalised(text)
            reference = {"file": source["path"], "row": index}
            if key in seen:
                seen[key]["duplicates"].append(reference)
                continue
            cricket = bool((CRICKET_EN if lang == "en" else CRICKET_NATIVE).search(text))
            xsport = bool((XSPORT_EN if lang == "en" else XSPORT_NATIVE).search(text))
            shard = hashlib.sha256(source["path"].encode()).hexdigest()[:8]
            row = {"id": f"{lang}-{'nq' if lang == 'en' else 'aya'}-{source['split']}-{shard}-{index:06d}",
                "lang": lang, "text": text, "source": source["source"], "source_dataset": source["dataset"],
                "source_split": source["split"], "source_file": source["path"], "source_row": index,
                "source_sha256": source["sha256"], "licence": source["licence"], "duplicates": [],
                "candidate_routes": [name for name, hit in (("cricket", cricket), ("xsport", xsport)) if hit]}
            seen[key] = row
            if cricket or xsport:
                candidates.append(row)
            elif lang == "en":
                controls.append(row)
    # Deterministic broad non-sport controls; these still require semantic review.
    controls.sort(key=lambda row: hashlib.sha256(row["text"].encode()).hexdigest())
    selected_controls = controls[:100]
    for row in selected_controls:
        row["candidate_routes"] = ["control_review"]
    for name, rows in (("source_candidates.jsonl", candidates), ("control_candidates.jsonl", selected_controls)):
        with (output_dir / name).open("w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    counts.update({"candidates": len(candidates), "control_candidates": len(selected_controls)})
    report = {"status": "UNLABELLED CANDIDATES — NOT FROZEN", "counts": dict(counts),
              "candidate_counts": dict(Counter(f"{r['lang']}:{route}" for r in candidates for route in r["candidate_routes"])),
              "note": "Keyword matches are a retrieval step, not labels. False matches and oversized multi-task prompts require review.",
              "inputs": manifest}
    (output_dir / "source_manifest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "inputs"}, indent=2, ensure_ascii=True), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract-only", action="store_true")
    args = parser.parse_args()
    if not args.extract_only:
        download_sources()
    extract_candidates()
