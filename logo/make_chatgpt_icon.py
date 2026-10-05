"""ChatGPT connector icon: 256x256 PNG under 10 KB (form limit) -> logo/logo_chatgpt_256.png."""
import pathlib

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
img = Image.open(HERE / "logo_mcp_512.png").convert("RGBA").resize((256, 256), Image.LANCZOS)
for colors in (64, 32, 16, 8):
    out = HERE / "logo_chatgpt_256.png"
    img.quantize(colors=colors, method=Image.Quantize.FASTOCTREE).save(out, optimize=True)
    size = out.stat().st_size
    print(colors, "colours ->", size, "bytes")
    if size <= 10 * 1024:
        break
