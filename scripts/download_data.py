"""Download bounded, validated Cricsheet inputs; optionally build the K-P1 artefacts.

Run from the repository: python scripts/download_data.py --build --labels
Raw archives and DuckDB stay local; CSV exports and provenance are shareable.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
ARCHIVES = ("t20s_male_json", "t20s_female_json", "odis_male_json", "odis_female_json")
URLS = {f"{name}.zip": f"https://cricsheet.org/downloads/{name}.zip" for name in ARCHIVES}
URLS.update({f"{name}.csv": f"https://cricsheet.org/register/{name}.csv" for name in ("people", "names")})
USER_AGENT = "MakeAIKnowHer/0.1 (https://github.com/Joannapreethi28/ICC-26)"
MAX_BYTES = 900 * 1024 * 1024  # Explicitly stop below the team's 1 GB approval boundary.


def validate(path: Path) -> None:
    if path.name.endswith(".zip") or path.name.endswith(".zip.part"):
        with zipfile.ZipFile(path) as archive:
            if not any(name.endswith(".json") for name in archive.namelist()):
                raise ValueError(f"No match JSON in {path}")
            if archive.testzip() is not None:
                raise ValueError(f"Corrupt ZIP: {path}")
    else:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            fields = csv.DictReader(fh).fieldnames or []
            if not {"identifier", "name"}.issubset(fields):
                raise ValueError(f"Unexpected register CSV header: {path}")


def download(raw_dir: Path) -> dict:
    raw_dir.mkdir(parents=True, exist_ok=True)
    previous_path = raw_dir / "manifest.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else {}
    manifest, downloaded = {}, 0
    planned = 0
    for name, url in URLS.items():
        path = raw_dir / name
        if path.exists():
            print(f"Cached {name}: {path.stat().st_size / 1048576:.2f} MiB", flush=True)
            continue
        with urlopen(Request(url, method="HEAD", headers={"User-Agent": USER_AGENT}), timeout=60) as response:
            size = response.headers.get("Content-Length")
        if size is None:
            raise RuntimeError(f"Server did not report size for {url}; inspect it before downloading")
        planned += int(size)
        print(f"Will download {name}: {int(size) / 1048576:.2f} MiB", flush=True)
    if planned > MAX_BYTES:
        raise RuntimeError("Download exceeds 900 MiB: ask Joanna before a >1 GB job; no files downloaded")
    print(f"Total new download: {planned / 1048576:.2f} MiB", flush=True)
    for name, url in URLS.items():
        path, partial = raw_dir / name, raw_dir / (name + ".part")
        fetched_at = previous.get(name, {}).get("fetched_at")
        if not path.exists():
            try:
                with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=90) as response, partial.open("wb") as fh:
                    while block := response.read(1024 * 1024):
                        downloaded += len(block)
                        if downloaded > MAX_BYTES:
                            raise RuntimeError("Download grew beyond the 900 MiB limit")
                        fh.write(block)
                validate(partial)
                partial.replace(path)
                fetched_at = datetime.now(timezone.utc).isoformat()
            finally:
                partial.unlink(missing_ok=True)
        validate(path)
        with path.open("rb") as fh:
            digest = hashlib.file_digest(fh, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else _digest(fh)
        manifest[name] = {"url": url, "bytes": path.stat().st_size, "sha256": digest,
                          "fetched_at": fetched_at, "validated_at": datetime.now(timezone.utc).isoformat()}
        previous_path.write_text(json.dumps({**previous, **manifest}, indent=2) + "\n", encoding="utf-8")
        print(f"Validated {name}", flush=True)
    return manifest


def _digest(fh) -> str:
    digest = hashlib.sha256()
    while block := fh.read(1024 * 1024):
        digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--db-path", type=Path, default=ROOT / "data/processed/mak.duckdb")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--labels", action="store_true", help="Fetch Wikidata names after building the registry")
    args = parser.parse_args()
    manifest = download(args.raw_dir)
    if args.build:
        from mak.ingest.cricsheet import build_db, coverage
        from mak.registry.people import build_registry, export_registry
        counts = build_db(args.raw_dir, args.db_path)
        build_registry(args.raw_dir, args.db_path)
        if args.labels:
            from mak.registry.wikidata import populate_labels
            populate_labels(args.db_path)
        export_registry(args.db_path)
        report = {"generated_at": datetime.now(timezone.utc).isoformat(), "inputs": manifest,
                  "tables": counts, "coverage": coverage(args.db_path)}
        report_dir = ROOT / "data/registry"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "build_manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report["coverage"], indent=2), flush=True)
        print("K-P1 data build complete. Run the test suite next.", flush=True)
    elif args.labels:
        parser.error("--labels requires --build")


if __name__ == "__main__":
    main()
