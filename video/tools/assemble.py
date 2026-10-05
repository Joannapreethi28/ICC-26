"""Assemble the demo video: cards + screen clips + Bella voice + burned captions -> video/make-ai-know-her-demo.mp4.

Inputs: video/narration.txt (10 blocks), video/voice/NN.mp3, video/cards/scene01|09|10.png,
video/raw/sceneNN.mp4 for scenes 02-08 (recorded by whoever owns the screen). Missing scene04 -> freeze of scene03's last
frame; any other missing clip -> a labelled "recording pending" slate (draft mode). Clips longer than their slot are
sped up (max 2.5x, warned); shorter ones hold their last frame. Real answers are never edited, only timed.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
V = ROOT / "video"
TARGET = {1: 10, 2: 15, 3: 15, 4: 8, 5: 26, 6: 22, 7: 22, 8: 20, 9: 18, 10: 14}  # Codex storyboard, seconds
CARDS = {1, 9, 10}
LEAD = 0.4  # voice starts 0.4 s into each scene


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip())


def run(args):
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-800:])


def blocks():
    t = (V / "narration.txt").read_text(encoding="utf-8")
    return [b.strip() for b in re.split(r"(?m)^\d{2}\s*$", t) if b.strip()]


def chunks(text, n=84):
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return out + ([cur] if cur else [])


def ts(s):
    h, m = int(s // 3600), int(s % 3600 // 60)
    return f"{h:02d}:{m:02d}:{s % 60:06.3f}".replace(".", ",")


def segment(i, slot, out):
    vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white,fps=30,format=yuv420p"
    raw = V / "raw" / f"scene{i:02d}.mp4"
    if i in CARDS:
        run(["-loop", "1", "-t", f"{slot}", "-i", str(V / "cards" / f"scene{i:02d}.png"), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "18", str(out)])
        return "card"
    if i == 4 and not raw.exists() and (V / "raw" / "scene03.mp4").exists():
        src = V / "raw" / "scene03.mp4"
        run(["-sseof", "-0.2", "-i", str(src), "-frames:v", "1", str(V / "build" / "s04.png")])
        run(["-loop", "1", "-t", f"{slot}", "-i", str(V / "build" / "s04.png"), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "18", str(out)])
        return "freeze of scene03"
    if not raw.exists():
        run(["-f", "lavfi", "-t", f"{slot}", "-i", "color=c=#F3F4F6:s=1920x1080:r=30", "-vf",
             f"drawtext=fontfile='C\\:/Windows/Fonts/segoeuib.ttf':text='SCENE {i:02d} - recording pending':fontsize=64:fontcolor=#6B7280:x=(w-tw)/2:y=(h-th)/2,format=yuv420p",
             "-c:v", "libx264", "-crf", "18", str(out)])
        return "PLACEHOLDER"
    d = dur(raw)
    speed = max(1.0, d / slot)
    note = f"clip {d:.1f}s"
    ss = 0.0
    if speed > 2.6:  # too long even at 2.6x: keep the END (the answer), drop early typing/waiting
        ss = d - slot * 2.6
        note += f" trimmed first {ss:.1f}s, 2.6x"
        speed = 2.6
    elif speed > 1.0:
        note += f" sped up {speed:.2f}x"
    run(["-ss", f"{ss}", "-i", str(raw), "-vf", f"setpts=PTS/{speed},{vf},tpad=stop_mode=clone:stop_duration={slot}", "-an",
         "-c:v", "libx264", "-crf", "18", "-t", f"{slot}", str(out)])
    return note


def main():
    (V / "build").mkdir(exist_ok=True)
    texts = blocks()
    t0, srt, segs, auds, n = 0.0, [], [], [], 1
    for i in range(1, 11):
        vo = V / "voice" / f"{i:02d}.mp3"
        vd = dur(vo)
        slot = round(max(4.0, vd + LEAD + 0.5), 2)  # narration-driven: no dead air
        seg = V / "build" / f"seg{i:02d}.mp4"
        info = segment(i, slot, seg)
        segs.append(seg)
        parts = chunks(texts[i - 1])
        total = sum(len(p) for p in parts)
        start = t0 + LEAD
        for p in parts:
            end = start + vd * len(p) / total
            srt.append(f"{n}\n{ts(start)} --> {ts(end)}\n{p}\n")
            n, start = n + 1, end
        auds.append((vo, t0 + LEAD))
        print(f"scene {i:02d}: slot {slot:5.1f}s voice {vd:4.1f}s  {info}")
        t0 += slot
    print(f"TOTAL {t0:.1f}s ({'OK' if t0 <= 180 else 'OVER 3:00'})")
    (V / "captions.srt").write_text("\n".join(srt), encoding="utf-8")
    lst = V / "build" / "list.txt"
    lst.write_text("".join(f"file '{s.name}'\n" for s in segs), encoding="utf-8")  # relative: the repo path has an apostrophe
    run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(V / "build" / "silent.mp4")])
    inputs, filt = [], []
    for k, (a, start) in enumerate(auds):
        inputs += ["-i", str(a)]
        filt.append(f"[{k + 1}:a]adelay={int(start * 1000)}|{int(start * 1000)}[a{k}]")
    filt.append("".join(f"[a{k}]" for k in range(len(auds))) + f"amix=inputs={len(auds)}:normalize=0,loudnorm=I=-16:TP=-1.5[aout]")
    style = "FontName=Segoe UI,FontSize=15,PrimaryColour=&H00FFFFFF,BackColour=&H33000000,BorderStyle=4,Outline=0,Shadow=0,MarginV=12"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "build/silent.mp4", *[x if not x.startswith(str(V)) else x for x in inputs],
                    "-filter_complex", ";".join(filt) + f";[0:v]subtitles=captions.srt:force_style='{style}'[vout]",
                    "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", "make-ai-know-her-demo.mp4"], cwd=V, check=True)
    print("wrote", V / "make-ai-know-her-demo.mp4", f"{dur(V / 'make-ai-know-her-demo.mp4'):.1f}s")


if __name__ == "__main__":
    main()
