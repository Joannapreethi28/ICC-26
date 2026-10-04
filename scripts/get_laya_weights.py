"""Download the shipped Laya v3 weights from the GitHub Release, verify SHA-256, unzip to models/laya-mak-v3/.
Free, no account needed.  python scripts/get_laya_weights.py
"""
import hashlib
import pathlib
import sys
import urllib.request
import zipfile

URL = "https://github.com/Joannapreethi28/ICC-26/releases/download/laya-mak-v3/laya-mak-v3-105403.zip"
ZIP_SHA256 = "ef6101e63819013d508f5c9cabd9533ad7cbe89f3a79c0c2556b8a3069fddbe5"
MODEL_SHA256 = "b8c4cbf2f4677fd9ffee177a460d80c340edc61ebb026f08ab3971c65dd36a26"
ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / "models" / "laya-mak-v3"


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if (DEST / "model.safetensors").exists() and sha(DEST / "model.safetensors") == MODEL_SHA256:
        print("already present and verified:", DEST)
        return
    tmp = ROOT / "models" / "laya-mak-v3.zip"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    print("downloading", URL)
    urllib.request.urlretrieve(URL, tmp)
    if sha(tmp) != ZIP_SHA256:
        sys.exit("zip SHA-256 mismatch: download corrupted or tampered; not unzipping")
    with zipfile.ZipFile(tmp) as z:
        z.extractall(DEST)
    tmp.unlink()
    if sha(DEST / "model.safetensors") != MODEL_SHA256:
        sys.exit("model.safetensors SHA-256 mismatch after unzip")
    print("ok:", DEST)


if __name__ == "__main__":
    main()
