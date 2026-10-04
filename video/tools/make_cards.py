"""Render 1920x1080 cards for scenes 01 (title), 09 (E1 chart) and 10 (end card) into video/cards/.
Numbers are read from results/e1/tables.md (never typed by hand)."""
import pathlib
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "video" / "cards"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080
BG, INK, MUTED, ACCENT, MEN, WOMEN = "#FFFFFF", "#111827", "#6B7280", "#7C3AED", "#9CA3AF", "#7C3AED"
F = "C:/Windows/Fonts/segoeui.ttf"
FB = "C:/Windows/Fonts/segoeuib.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FB if bold else F, size)


def centered(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def title():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    centered(d, 380, "Make AI Know Her", font(120, True), INK)
    centered(d, 540, "Women's cricket should not need an extra keyword.", font(48), MUTED)
    d.rectangle([(W / 2 - 80, 640), (W / 2 + 80, 648)], fill=ACCENT)
    im.save(OUT / "scene01.png")


def e1_numbers():
    t = (ROOT / "results" / "e1" / "tables.md").read_text(encoding="utf-8")
    en = t.split("## en")[1].split("## hi")[0]
    vals = {}
    for arm in ("plain", "prompt_only", "layer"):
        m = re.search(rf"^\| {arm} \| (\d+) \| (\d+) \| ([0-9.]+) \|", en, re.M)
        vals[arm] = (float(m.group(3)), int(m.group(1)), int(m.group(2)))
    return vals


def chart():
    v = e1_numbers()
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((140, 90), "Women's records shown on neutral English questions", font=font(56, True), fill=INK)
    d.text((140, 170), "Same free local model (Llama 3.1 8B), three conditions", font=font(36), fill=MUTED)
    bars = [("Plain AI", v["plain"][0], MEN), ("Just prompt it", v["prompt_only"][0], MEN), ("With our layer", v["layer"][0], WOMEN)]
    x0, base, maxh, bw, gap = 360, 860, 520, 300, 170
    for i, (lab, val, col) in enumerate(bars):
        x = x0 + i * (bw + gap)
        h = maxh * val
        d.rectangle([(x, base - h), (x + bw, base)], fill=col)
        pct = f"{val * 100:.1f}%"
        d.text((x + (bw - d.textlength(pct, font=font(64, True))) / 2, base - h - 90), pct, font=font(64, True), fill=INK)
        d.text((x + (bw - d.textlength(lab, font=font(38))) / 2, base + 24), lab, font=font(38), fill=INK)
    d.line([(300, base), (W - 300, base)], fill="#D1D5DB", width=3)
    n_q = v["layer"][1]
    d.text((140, 960), f"Preliminary automatic labels; human review pending. {n_q} eligible English questions x 3 samples.",
           font=font(28), fill=MUTED)
    d.text((140, 1002), "Measures women's-record visibility, not factual accuracy. Source: results/e1/tables.md",
           font=font(28), fill=MUTED)
    im.save(OUT / "scene09.png")


def end_card():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    centered(d, 200, "Make AI Know Her", font(96, True), INK)
    centered(d, 330, "Free  ·  Open  ·  MCP + API  ·  English, Hindi, Tamil", font(44), ACCENT)
    centered(d, 430, "github.com/Joannapreethi28/ICC-26", font(40), INK)
    centered(d, 560, "Joanna Preethi (Team Lead)   ·   Jabin Joseph   ·   Efanio Jens", font(40), INK)
    centered(d, 660, "Limits: bounded cricket coverage; Hindi/Tamil native-speaker review pending;", font(30), MUTED)
    centered(d, 702, "temporary laptop-hosted demo; E1 labels preliminary.", font(30), MUTED)
    centered(d, 790, "Voice: ElevenLabs", font(28), MUTED)
    im.save(OUT / "scene10.png")


if __name__ == "__main__":
    title(); chart(); end_card()
    print("cards:", sorted(p.name for p in OUT.glob("*.png")), e1_numbers())
