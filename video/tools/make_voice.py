"""Generate one Bella clip per narration block from video/narration.txt and report durations (key from env; never printed)."""
import pathlib
import re
import subprocess

from tts import tts

BELLA = "hpp4J3VqNfWAUOO0d1Us"
ROOT = pathlib.Path(__file__).resolve().parents[2]
SAY = {"MCP": "M C P", "API": "A P I", "Laya": "Laaya"}  # spoken forms only; captions keep the written text

text = (ROOT / "video" / "narration.txt").read_text(encoding="utf-8")
blocks = [b.strip() for b in re.split(r"(?m)^\d{2}\s*$", text) if b.strip()]
out = ROOT / "video" / "voice"
out.mkdir(parents=True, exist_ok=True)
total = 0.0
for i, b in enumerate(blocks, 1):
    spoken = b
    for k, v in SAY.items():
        spoken = re.sub(rf"\b{k}\b", v, spoken)
    f = out / f"{i:02d}.mp3"
    if not f.exists():
        tts(BELLA, spoken, str(f))
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                             capture_output=True, text=True).stdout.strip())
    total += d
    print(f"{i:02d}  {d:5.1f}s  {b[:70]}")
print(f"TOTAL {total:.1f}s")
