"""Vista PNG de las tres páginas drawio (uv run --with pillow scripts/render_architecture.py)."""

import math
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def render() -> None:
    tree = ET.parse(ROOT / "docs/MVP_OCD_Arquitectura.drawio")
    diagrams = tree.findall("diagram")
    canvas = Image.new("RGB", (1280, 800 * len(diagrams)), "white")
    draw = ImageDraw.Draw(canvas)
    font_path = Path("C:/Windows/Fonts/arial.ttf")

    def font(size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(font_path), size)

    for page, diagram in enumerate(diagrams):
        cells = diagram.findall(".//mxCell")
        boxes = {}
        for cell in cells:
            if cell.get("vertex") != "1":
                continue
            geometry = cell.find("mxGeometry")
            boxes[cell.get("id")] = (
                float(geometry.get("x")),
                float(geometry.get("y")) + 800 * page,
                float(geometry.get("width")),
                float(geometry.get("height")),
            )
        for cell in cells:
            if cell.get("edge") != "1":
                continue
            x, y, w, h = boxes[cell.get("source")]
            tx, ty, tw, th = boxes[cell.get("target")]
            if abs(tx - x) < 30:
                a, b = (x + w / 2, y + h), (tx + tw / 2, ty)
            else:
                a, b = (x + w, y + h / 2), (tx, ty + th / 2)
            draw.line([a, b], fill="#536273", width=2)
            angle = math.atan2(b[1] - a[1], b[0] - a[0])
            draw.polygon(
                [
                    b,
                    *[
                        (b[0] - 10 * math.cos(angle + delta), b[1] - 10 * math.sin(angle + delta))
                        for delta in (-0.4, 0.4)
                    ],
                ],
                fill="#536273",
            )
            cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            label = cell.get("value", "")
            bounds = draw.textbbox((cx, cy - 12), label, font=font(14), anchor="mm")
            draw.rectangle(bounds, fill="white")
            draw.text((cx, cy - 12), label, font=font(14), fill="#283647", anchor="mm")
        for cell in cells:
            if cell.get("vertex") != "1":
                continue
            x, y, w, h = boxes[cell.get("id")]
            style = dict(item.split("=", 1) for item in cell.get("style").split(";") if "=" in item)
            if "fillColor" in style:
                draw.rounded_rectangle(
                    (x, y, x + w, y + h),
                    radius=12,
                    fill=style["fillColor"],
                    outline=style["strokeColor"],
                    width=2,
                )
            size = int(style.get("fontSize", "17"))
            value = cell.get("value", "")
            if style.get("align") == "left":
                draw.multiline_text((x, y + 10), value, font=font(size), fill="#17283b", spacing=7)
            else:
                draw.multiline_text(
                    (x + w / 2, y + h / 2),
                    value,
                    font=font(size),
                    fill="#17283b",
                    anchor="mm",
                    align="center",
                    spacing=7,
                )
        if page:
            draw.line((0, page * 800, 1280, page * 800), fill="#b8c3d1", width=2)
    canvas.save(ROOT / "docs/MVP_OCD_Arquitectura.png")


if __name__ == "__main__":
    render()
