"""
sample_generator.py — SPARK Illustrative Schematic Generator
=============================================================
Creates two clearly labeled illustrative 2D gearbox schematics:
    assets/reference.png  — baseline schematic
    assets/current.png    — schematic with a visually obvious marked area

These are ILLUSTRATIVE SCHEMATICS, not photographs of real industrial gearboxes.
They are provided solely to demonstrate the image-comparison feature of SPARK.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

IMG_W, IMG_H = 640, 480

# Colour palette — dark industrial look
BG_COLOUR = (18, 28, 45)          # dark navy
HOUSING_FILL = (35, 50, 70)       # charcoal blue
HOUSING_OUTLINE = (80, 140, 200)  # steel blue
GEAR_FILL = (45, 65, 90)
GEAR_OUTLINE = (100, 180, 220)    # cyan-ish
SHAFT_COLOUR = (140, 160, 180)
TEXT_COLOUR = (200, 220, 240)
LABEL_ACCENT = (0, 200, 200)      # electric cyan
WARN_COLOUR = (220, 60, 30)       # red-orange for current image marking


def _draw_gear(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    tooth_count: int = 12,
    fill=GEAR_FILL,
    outline=GEAR_OUTLINE,
    line_width: int = 2,
) -> None:
    """Draw a simple gear shape (circle with rectangular teeth)."""
    # Tooth polygon points
    points = []
    for i in range(tooth_count * 2):
        angle_deg = (360 / (tooth_count * 2)) * i - 90
        angle_rad = math.radians(angle_deg)
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle_rad)
        y = cy + r * math.sin(angle_rad)
        points.append((x, y))
    draw.polygon(points, fill=fill, outline=outline)
    # Hub circle
    hub_r = inner_r * 0.3
    draw.ellipse(
        [cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r],
        fill=SHAFT_COLOUR,
        outline=GEAR_OUTLINE,
        width=line_width,
    )


def _draw_housing(draw: ImageDraw.ImageDraw) -> None:
    """Draw the main gearbox housing rectangle with rounded feel."""
    margin = 40
    x0, y0 = margin, margin + 30
    x1, y1 = IMG_W - margin, IMG_H - margin - 10
    # Outer shadow
    draw.rounded_rectangle(
        [x0 + 4, y0 + 4, x1 + 4, y1 + 4],
        radius=12,
        fill=(10, 16, 26),
    )
    # Main housing
    draw.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=12,
        fill=HOUSING_FILL,
        outline=HOUSING_OUTLINE,
        width=3,
    )
    # Inner panel
    draw.rounded_rectangle(
        [x0 + 14, y0 + 14, x1 - 14, y1 - 14],
        radius=8,
        fill=(25, 38, 58),
        outline=(60, 100, 140),
        width=1,
    )


def _draw_shafts(draw: ImageDraw.ImageDraw, cx1: int, cy1: int, cx2: int, cy2: int) -> None:
    """Draw horizontal shafts through both gears."""
    shaft_w = 7
    for cx, cy in [(cx1, cy1), (cx2, cy2)]:
        draw.rectangle(
            [55, cy - shaft_w // 2, IMG_W - 55, cy + shaft_w // 2],
            fill=SHAFT_COLOUR,
            outline=(180, 200, 220),
        )
        # Shaft collars
        for x_off in [-80, 80]:
            xc = cx + x_off
            draw.ellipse(
                [xc - 8, cy - 12, xc + 8, cy + 12],
                fill=(80, 110, 140),
                outline=SHAFT_COLOUR,
                width=1,
            )


def _draw_labels(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    """Draw title, subtitle, and component labels using default font."""
    # Title bar
    draw.rectangle([0, 0, IMG_W, 30], fill=(10, 16, 28))
    draw.text((10, 6), title, fill=LABEL_ACCENT)
    draw.text((IMG_W - 260, 6), subtitle, fill=(140, 160, 180))

    # Component labels with leader lines
    labels = [
        (120, 90, "Housing"),
        (200, 230, "Drive Gear"),
        (430, 310, "Driven Gear"),
        (60, 250, "Input Shaft"),
        (490, 180, "Output Shaft"),
    ]
    for lx, ly, text in labels:
        draw.text((lx, ly), f"▸ {text}", fill=TEXT_COLOUR)

    # Footer disclaimer
    draw.rectangle([0, IMG_H - 22, IMG_W, IMG_H], fill=(8, 14, 24))
    draw.text(
        (8, IMG_H - 18),
        "ILLUSTRATIVE SCHEMATIC ONLY — Not a photograph of a real gearbox",
        fill=(100, 120, 150),
    )


def create_reference_image(path: Path) -> None:
    """Create the reference (baseline) gearbox schematic."""
    img = Image.new("RGB", (IMG_W, IMG_H), BG_COLOUR)
    draw = ImageDraw.Draw(img)

    _draw_housing(draw)

    cx1, cy1 = 210, 230   # large drive gear centre
    cx2, cy2 = 430, 290   # smaller driven gear centre

    _draw_shafts(draw, cx1, cy1, cx2, cy2)
    _draw_gear(draw, cx1, cy1, outer_r=90, inner_r=72, tooth_count=16)
    _draw_gear(draw, cx2, cy2, outer_r=60, inner_r=48, tooth_count=10)

    # Mesh point indicator
    draw.ellipse([315, 285, 335, 305], fill=(60, 200, 80), outline=(120, 240, 120), width=2)
    draw.text((338, 290), "Mesh", fill=(120, 240, 120))

    _draw_labels(
        draw,
        "SPARK — Gearbox Schematic",
        "GB-DEMO-001 | Reference State",
    )
    img.save(path, "PNG")
    print(f"  [OK] Reference image saved: {path}")


def create_current_image(path: Path) -> None:
    """Create the current inspection schematic with a visually obvious altered area."""
    img = Image.new("RGB", (IMG_W, IMG_H), BG_COLOUR)
    draw = ImageDraw.Draw(img)

    _draw_housing(draw)

    cx1, cy1 = 210, 230
    cx2, cy2 = 430, 290

    _draw_shafts(draw, cx1, cy1, cx2, cy2)

    # Drive gear slightly different fill to create pixel difference
    _draw_gear(
        draw, cx1, cy1, outer_r=90, inner_r=72, tooth_count=16,
        fill=(60, 80, 105),   # intentionally shifted colour
        outline=(120, 200, 240),
    )
    _draw_gear(draw, cx2, cy2, outer_r=60, inner_r=48, tooth_count=10)

    # ── Obvious visual alteration: marked area on upper-left of drive gear ──
    # This is the region that will appear RED in the comparison output.
    alert_x0, alert_y0 = 148, 158
    alert_x1, alert_y1 = 228, 200
    # Bright filled rectangle to guarantee pixel difference
    draw.rectangle(
        [alert_x0, alert_y0, alert_x1, alert_y1],
        fill=(200, 100, 30),
        outline=WARN_COLOUR,
        width=2,
    )
    draw.text((alert_x0 + 4, alert_y0 + 4), "⚠ MARK", fill=(255, 240, 30))

    # Mesh point (same position)
    draw.ellipse([315, 285, 335, 305], fill=(60, 200, 80), outline=(120, 240, 120), width=2)
    draw.text((338, 290), "Mesh", fill=(120, 240, 120))

    _draw_labels(
        draw,
        "SPARK — Gearbox Schematic",
        "GB-DEMO-001 | Current State",
    )
    img.save(path, "PNG")
    print(f"  [OK] Current image saved: {path}")


def generate_sample_images(force: bool = False) -> None:
    """
    Generate reference.png and current.png if they do not exist (or force=True).
    """
    ref_path = ASSETS_DIR / "reference.png"
    cur_path = ASSETS_DIR / "current.png"

    if not ref_path.exists() or force:
        print("Generating reference schematic…")
        create_reference_image(ref_path)
    else:
        print(f"  [skip] Reference image already exists: {ref_path}")

    if not cur_path.exists() or force:
        print("Generating current schematic…")
        create_current_image(cur_path)
    else:
        print(f"  [skip] Current image already exists: {cur_path}")


if __name__ == "__main__":
    print("SPARK Sample Image Generator")
    print("=" * 40)
    generate_sample_images(force=True)
    print("Done.")
