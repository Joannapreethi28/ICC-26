"""Render the MCP flow diagram for the deck: submission/screenshots/mcp_flow.png (1920x1080, white)."""
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "submission" / "screenshots" / "mcp_flow.png"
W, H = 1920, 1080
INK, MUTED, ACCENT, SOFT, LINE = "#111827", "#6B7280", "#7C3AED", "#F3E8FF", "#D1D5DB"


def font(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf", size)


def box(d, x, y, w, h, title, lines, fill="#FFFFFF", edge=LINE, tcol=INK):
    d.rounded_rectangle([(x, y), (x + w, y + h)], radius=24, fill=fill, outline=edge, width=4)
    d.text((x + 32, y + 26), title, font=font(38, True), fill=tcol)
    for i, ln in enumerate(lines):
        d.text((x + 32, y + 88 + i * 46), ln, font=font(30), fill=MUTED)


def arrow(d, x1, y1, x2, y2, label=""):
    d.line([(x1, y1), (x2, y2)], fill=ACCENT, width=6)
    d.polygon([(x2, y2), (x2 - 22, y2 - 14), (x2 - 22, y2 + 14)], fill=ACCENT)
    if label:
        tw = d.textlength(label, font=font(26))
        d.text(((x1 + x2 - tw) / 2, y1 - 44), label, font=font(26), fill=ACCENT)


def main():
    im = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    d.text((100, 70), "How any AI assistant uses Make AI Know Her (MCP)", font=font(56, True), fill=INK)
    d.text((100, 150), "MCP = a standard plug that lets ChatGPT, Claude or any MCP client call our tool for the facts.",
           font=font(32), fill=MUTED)

    box(d, 100, 300, 440, 330, "AI assistant", ['"Who has taken the most', 'wickets?"', "", "ChatGPT / Claude / any", "MCP client"])
    arrow(d, 540, 465, 680, 465, "MCP call")

    d.rounded_rectangle([(680, 250), (1300, 830)], radius=28, fill=SOFT, outline=ACCENT, width=4)
    d.text((712, 268), "Our MCP tool: resolve_sports_query", font=font(34, True), fill=ACCENT)
    steps = [("1  Understand", "Laya v3 (our fine-tuned model) + rules"),
             ("2  Decide", "Policy in plain code: neutral -> BOTH"),
             ("3  Fetch facts", "Verified database, source + as-of date"),
             ("4  Answer", "Template in English, Hindi or Tamil")]
    for i, (t, s) in enumerate(steps):
        y = 340 + i * 118
        d.rounded_rectangle([(712, y), (1268, y + 100)], radius=18, fill="#FFFFFF", outline=LINE, width=3)
        d.text((736, y + 10), t, font=font(32, True), fill=INK)
        d.text((736, y + 54), s, font=font(26), fill=MUTED)

    arrow(d, 1300, 465, 1440, 465, "facts")
    box(d, 1440, 260, 400, 520, "Answer the fan sees", ["Women's record", "Men's record", "", "Each with a source", "and an as-of date", "", "No model writes", "a number."],
        edge=ACCENT)

    d.text((100, 900), "Free and open: local model, open data, no paid API. A model only picks categories; every number comes from the database.",
           font=font(28), fill=MUTED)
    d.text((100, 944), "Demo hosting: temporary Gradio share link from a team laptop (not permanent hosting).", font=font(28), fill=MUTED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
