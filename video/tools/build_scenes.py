"""Cut the raw screen takes into scene clips (only the meaningful moments), zoomed into the content area.
Writes video/raw/scene02..08.mp4 for assemble.py. Real answers are never edited, only trimmed/cropped."""
import pathlib
import subprocess

V = pathlib.Path(__file__).resolve().parents[1]
R = V / "raw"
CHAT = "crop=1280:720:320:70"      # ChatGPT / Gemini answers (1.5x zoom)
DEMO = "crop=1600:900:160:150"     # product page: records + sources table (1.2x zoom)
SCENES = {
    2: ("scene02_full.mp4", "crop=1280:720:320:190", [(2, 14)]),
    3: ("scene03_full.mp4", CHAT, [(0, 3), (13, 27)]),
    5: ("scene05_full.mp4", CHAT, [(8, 17), (25, 37), (46, 54)]),
    6: ("demo_take.mp4", DEMO, [(2, 24)]),
    7: ("demo_take.mp4", DEMO, [(40, 52), (62, 74)]),
    8: ("demo_take.mp4", DEMO, [(88, 96), (112, 120), (132, 145)]),
}


def main():
    for n, (src, crop, parts) in SCENES.items():
        filt, labels = [], []
        for k, (a, b) in enumerate(parts):
            filt.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,{crop},scale=1920:1080,fps=30[v{k}]")
            labels.append(f"[v{k}]")
        filt.append("".join(labels) + f"concat=n={len(parts)}:v=1:a=0,format=yuv420p[out]")
        out = R / f"scene{n:02d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(R / src), "-filter_complex", ";".join(filt),
                        "-map", "[out]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)], check=True)
        print("wrote", out.name, sum(b - a for a, b in parts), "s")


if __name__ == "__main__":
    main()
