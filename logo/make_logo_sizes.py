"""Make transparent-corner sizes of logo_for_mcp.png: logo_mcp_512.png, logo_mcp_128.png (ChatGPT connector icon), favicon.png."""
import pathlib

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
src = Image.open(HERE / "logo_for_mcp.png").convert("RGBA")
side = min(src.size)
src = src.crop(((src.width - side) // 2, (src.height - side) // 2, (src.width + side) // 2, (src.height + side) // 2))
big = side * 4  # supersampled mask for a smooth edge
mask = Image.new("L", (big, big), 0)
ImageDraw.Draw(mask).ellipse((10, 10, big - 10, big - 10), fill=255)
src.putalpha(mask.resize((side, side), Image.LANCZOS))
for name, px in (("logo_mcp_512.png", 512), ("logo_mcp_128.png", 128), ("favicon.png", 32)):
    src.resize((px, px), Image.LANCZOS).save(HERE / name, optimize=True)
    print("wrote", name)
