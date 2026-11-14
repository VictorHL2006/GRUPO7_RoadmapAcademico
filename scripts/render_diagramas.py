"""Export the project's small, hand-authored SVG diagrams to 1600x900 PNG."""

import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "docs" / "diagramas"
SIZE = (1600, 900)
FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)
BOLD_CANDIDATES = (
    Path("C:/Windows/Fonts/seguisb.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
)


def _font(size: int, bold: bool = False):
    candidates = BOLD_CANDIDATES if bold else FONT_CANDIDATES
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _styles(root):
    styles = {}
    style_node = root.find("{*}defs/{*}style")
    if style_node is None or not style_node.text:
        return styles
    for selector, body in re.findall(r"\.([\w-]+)\s*\{([^}]*)\}", style_node.text):
        styles[selector] = {
            key.strip(): value.strip()
            for declaration in body.split(";")
            if ":" in declaration
            for key, value in [declaration.split(":", 1)]
        }
    return styles


def _attributes(node, styles):
    result = {}
    for class_name in node.attrib.get("class", "").split():
        result.update(styles.get(class_name, {}))
    result.update({key: value for key, value in node.attrib.items() if key != "class"})
    return result


def _rgba(color):
    if not color or color == "none":
        return None
    return color


def _draw_path(draw, node, attrs):
    tokens = re.findall(r"[MCVH]|-?\d+(?:\.\d+)?", attrs.get("d", ""))
    points = []
    i = 0
    current = (0.0, 0.0)
    while i < len(tokens):
        command = tokens[i]
        i += 1
        if command == "M":
            current = (float(tokens[i]), float(tokens[i + 1]))
            i += 2
            points.append(current)
        elif command == "H":
            current = (float(tokens[i]), current[1])
            i += 1
            points.append(current)
        elif command == "V":
            current = (current[0], float(tokens[i]))
            i += 1
            points.append(current)
        elif command == "C":
            p0 = current
            p1 = (float(tokens[i]), float(tokens[i + 1]))
            p2 = (float(tokens[i + 2]), float(tokens[i + 3]))
            p3 = (float(tokens[i + 4]), float(tokens[i + 5]))
            i += 6
            for step in range(1, 25):
                t = step / 24
                u = 1 - t
                points.append((
                    u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
                ))
            current = p3
    if len(points) < 2:
        return
    color = attrs.get("stroke", "#52657a")
    width = int(float(attrs.get("stroke-width", "2")))
    draw.line(points, fill=color, width=width, joint="curve")
    if "marker-end" in attrs:
        end = points[-1]
        before = points[-2]
        angle = math.atan2(end[1] - before[1], end[0] - before[0])
        length, spread = 13, 6
        left = (end[0] - length * math.cos(angle) + spread * math.sin(angle),
                end[1] - length * math.sin(angle) - spread * math.cos(angle))
        right = (end[0] - length * math.cos(angle) - spread * math.sin(angle),
                 end[1] - length * math.sin(angle) + spread * math.cos(angle))
        draw.polygon([end, left, right], fill=color)


def render(svg_path: Path):
    root = ET.parse(svg_path).getroot()
    styles = _styles(root)
    width = int(root.attrib.get("width", SIZE[0]))
    height = int(root.attrib.get("height", SIZE[1]))
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    for node in root:
        kind = node.tag.rsplit("}", 1)[-1]
        attrs = _attributes(node, styles)
        if kind == "rect":
            x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
            x2, y2 = x + float(attrs.get("width", 0)), y + float(attrs.get("height", 0))
            radius = int(float(attrs.get("rx", 0)))
            outline = _rgba(attrs.get("stroke"))
            fill = _rgba(attrs.get("fill"))
            draw.rounded_rectangle((x, y, x2, y2), radius=radius,
                                   fill=fill, outline=outline,
                                   width=max(1, int(float(attrs.get("stroke-width", 1)))))
        elif kind == "text":
            text = "".join(node.itertext())
            size = int(float(re.sub(r"px$", "", attrs.get("font-size", 18))))
            bold = attrs.get("font-weight", "normal") in {"700", "bold"}
            draw.text((float(attrs.get("x", 0)), float(attrs.get("y", 0))), text,
                      fill=attrs.get("fill", "#172b4d"), font=_font(size, bold), anchor="ls")
        elif kind == "path":
            _draw_path(draw, node, attrs)

    output_path = svg_path.with_suffix(".png")
    image.save(output_path, format="PNG", optimize=True)
    print(f"{output_path.relative_to(ROOT)}: {width}x{height}")


def main():
    for name in ("arquitectura", "emision_verificacion", "seguridad_estado"):
        render(DIAGRAMS / f"{name}.svg")


if __name__ == "__main__":
    main()
