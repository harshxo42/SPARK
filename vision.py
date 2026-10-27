"""
vision.py — SPARK Image Comparison Module
==========================================
Provides pixel-level difference highlighting between a reference gearbox image
and a current inspection image.

IMPORTANT DISCLAIMER:
This module performs basic pixel comparison for visual inspection assistance
only. It does NOT perform AI-based fault detection, damage classification,
or any validated diagnostic analysis. The change_percent value is a visual
comparison metric showing what fraction of pixels differ noticeably between
two images — it is NOT a probability of gearbox fault or damage.

Public interface:
    compare_images(reference_path, current_path)
        -> dict with keys: highlighted_image, summary, change_percent
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageChops, ImageDraw, ImageFilter

if TYPE_CHECKING:
    pass

# ──────────────────────────────────────────────
# Configuration constants
# ──────────────────────────────────────────────
# Pixels whose per-channel absolute difference exceeds this threshold on ANY
# channel are counted as "changed". Value range 0-255. Higher values ignore
# minor color noise; lower values are more sensitive.
DIFF_THRESHOLD: int = 30

# Colour used to mark changed regions in the highlighted output image.
HIGHLIGHT_COLOUR: tuple[int, int, int] = (220, 30, 30)  # red


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def compare_images(
    reference_path: str | os.PathLike,
    current_path: str | os.PathLike,
) -> dict:
    """
    Compare two gearbox images and return a highlighted difference image.

    Parameters
    ----------
    reference_path : str | PathLike
        File-system path to the reference (baseline) gearbox image.
    current_path : str | PathLike
        File-system path to the current inspection image.

    Returns
    -------
    dict with keys
        highlighted_image : PIL.Image.Image
            RGB image with changed pixels painted in red (HIGHLIGHT_COLOUR).
        summary : str
            Plain-language description of the comparison result.
        change_percent : float
            Percentage of pixels exceeding DIFF_THRESHOLD.
            This is a VISUAL COMPARISON METRIC, not a fault probability.

    Raises
    ------
    FileNotFoundError
        If either image file does not exist.
    ValueError
        If a file exists but cannot be read as an image.
    """
    ref_path = Path(reference_path)
    cur_path = Path(current_path)

    # ── Validate file existence ──────────────────────────────────────────
    if not ref_path.exists():
        raise FileNotFoundError(
            f"Reference image not found: {ref_path}"
        )
    if not cur_path.exists():
        raise FileNotFoundError(
            f"Current image not found: {cur_path}"
        )

    # ── Load images ──────────────────────────────────────────────────────
    try:
        ref_img = Image.open(ref_path).convert("RGB")
    except Exception as exc:
        raise ValueError(
            f"Cannot read reference image '{ref_path}': {exc}"
        ) from exc

    try:
        cur_img = Image.open(cur_path).convert("RGB")
    except Exception as exc:
        raise ValueError(
            f"Cannot read current image '{cur_path}': {exc}"
        ) from exc

    # ── Resize current image to reference dimensions if needed ───────────
    ref_w, ref_h = ref_img.size
    if cur_img.size != (ref_w, ref_h):
        cur_img = cur_img.resize((ref_w, ref_h), Image.LANCZOS)

    # ── Pixel-level difference using ImageChops ──────────────────────────
    diff = ImageChops.difference(ref_img, cur_img)

    # Split into per-channel arrays
    r_ch, g_ch, b_ch = diff.split()

    # Build boolean mask: True where ANY channel exceeds the threshold
    r_data = list(r_ch.getdata())
    g_data = list(g_ch.getdata())
    b_data = list(b_ch.getdata())

    total_pixels = ref_w * ref_h
    changed_pixels = 0
    mask_data = []

    for r, g, b in zip(r_data, g_data, b_data):
        if r > DIFF_THRESHOLD or g > DIFF_THRESHOLD or b > DIFF_THRESHOLD:
            changed_pixels += 1
            mask_data.append(255)
        else:
            mask_data.append(0)

    change_percent = round((changed_pixels / total_pixels) * 100, 2)

    # ── Build highlighted output image ───────────────────────────────────
    # Start with the reference image so the user can see the baseline context
    highlighted = ref_img.copy()
    draw = ImageDraw.Draw(highlighted)

    # Paint each changed pixel in the highlight colour
    pixels = highlighted.load()
    idx = 0
    for y in range(ref_h):
        for x in range(ref_w):
            if mask_data[idx] == 255:
                pixels[x, y] = HIGHLIGHT_COLOUR
            idx += 1

    # ── Build human-readable summary ─────────────────────────────────────
    summary = _build_summary(change_percent)

    return {
        "highlighted_image": highlighted,
        "summary": summary,
        "change_percent": change_percent,
    }


def _build_summary(change_percent: float) -> str:
    """
    Return a plain-language summary based on the visual change percentage.

    This summary describes visual differences only.  It does NOT diagnose
    gearbox faults or recommend specific repair actions.
    """
    if change_percent < 1.0:
        level = "minimal"
        detail = (
            "The two images are nearly identical. "
            "No significant visual differences were detected at the configured sensitivity level."
        )
    elif change_percent < 5.0:
        level = "minor"
        detail = (
            "Small visual differences were detected between the reference and current images. "
            "These may reflect lighting variation, minor surface marks, or positioning differences."
        )
    elif change_percent < 15.0:
        level = "moderate"
        detail = (
            "Moderate visual differences are present. "
            "Red-highlighted regions show areas where the pixel values differ notably from the reference image. "
            "A qualified technician should review these areas."
        )
    elif change_percent < 35.0:
        level = "significant"
        detail = (
            "Significant visual differences were detected. "
            "Multiple regions are highlighted in red. "
            "A qualified maintenance engineer should assess these areas before any action is taken."
        )
    else:
        level = "extensive"
        detail = (
            "Extensive visual differences were detected across a large portion of the image. "
            "This may indicate major differences in component positioning, image quality, "
            "or viewpoint. Review is strongly recommended by a qualified maintenance engineer."
        )

    return (
        f"Visual comparison result: {level} differences detected "
        f"({change_percent:.2f}% of pixels exceeded the threshold). "
        f"{detail}"
    )
