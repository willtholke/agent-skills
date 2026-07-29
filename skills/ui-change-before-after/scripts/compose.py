#!/usr/bin/env python3
"""Compose a window screenshot onto a mesh gradient with an optional highlight.

Usage:
  python3 compose.py \\
    --shot before.png \\
    --out before-framed.png \\
    --gradient aurora-rose \\
    --label Before \\
    --highlight 120,80,480,220

Highlight is x,y,w,h in screenshot pixel space (optional).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKILL_ROOT = Path(__file__).resolve().parents[1]
GRADIENTS = SKILL_ROOT / "assets" / "gradients"
MANIFEST = GRADIENTS / "manifest.json"


def load_gradient(gradient_id: str | None) -> Image.Image:
    data = json.loads(MANIFEST.read_text())
    gid = gradient_id or data.get("default") or data["gradients"][0]["id"]
    entry = next((g for g in data["gradients"] if g["id"] == gid), None)
    if entry is None:
        known = ", ".join(g["id"] for g in data["gradients"])
        raise SystemExit(f"Unknown gradient {gid!r}. Known: {known}")
    return Image.open(GRADIENTS / entry["file"]).convert("RGB")


def rounded_shadow(size: tuple[int, int], radius: int, pad: int) -> Image.Image:
    w, h = size
    shadow = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    d.rounded_rectangle(
        [pad + 6, pad + 10, pad + w + 6, pad + h + 10],
        radius=radius,
        fill=(0, 0, 0, 90),
    )
    return shadow.filter(ImageFilter.GaussianBlur(radius=18))


def round_window(shot: Image.Image, radius: int) -> Image.Image:
    shot = shot.convert("RGBA")
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, shot.size[0], shot.size[1]], radius=radius, fill=255
    )
    out = Image.new("RGBA", shot.size, (0, 0, 0, 0))
    out.paste(shot, (0, 0), mask)
    return out


def draw_highlight(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int] = (255, 59, 48),
) -> None:
    """Draw a CleanShot-style circle/ellipse around a region (x,y,w,h on canvas)."""
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    # pad so the ring sits outside the target
    pad = max(18, int(min(w, h) * 0.12))
    rw, rh = w / 2 + pad, h / 2 + pad
    # prefer a circle when nearly square
    if abs(w - h) / max(w, h, 1) < 0.25:
        r = max(rw, rh)
        rw = rh = r
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # thick ring via outer/inner ellipses
    thickness = max(4, int(min(canvas.size) * 0.004))
    bbox = [cx - rw, cy - rh, cx + rw, cy + rh]
    d.ellipse(bbox, outline=(*color, 230), width=thickness)
    # soft glow
    glow = overlay.filter(ImageFilter.GaussianBlur(radius=thickness))
    canvas.alpha_composite(glow)
    canvas.alpha_composite(overlay)


def fit_shot(shot: Image.Image, max_w: int, max_h: int) -> Image.Image:
    sw, sh = shot.size
    scale = min(max_w / sw, max_h / sh, 1.0)
    if scale < 1.0:
        shot = shot.resize(
            (max(1, int(sw * scale)), max(1, int(sh * scale))),
            Image.Resampling.LANCZOS,
        )
    return shot


def compose(
    shot_path: Path,
    out_path: Path,
    gradient_id: str | None,
    label: str | None,
    highlight: tuple[int, int, int, int] | None,
    margin: float,
) -> Path:
    bg = load_gradient(gradient_id).convert("RGBA")
    cw, ch = bg.size
    shot = Image.open(shot_path).convert("RGBA")

    max_w = int(cw * (1 - 2 * margin))
    max_h = int(ch * (1 - 2 * margin))
    # leave a little room for label
    if label:
        max_h = int(max_h * 0.92)
    scale = min(max_w / shot.size[0], max_h / shot.size[1], 1.0)
    if scale < 1.0:
        shot = shot.resize(
            (max(1, int(shot.size[0] * scale)), max(1, int(shot.size[1] * scale))),
            Image.Resampling.LANCZOS,
        )
        if highlight:
            hx, hy, hw, hh = highlight
            highlight = (
                int(hx * scale),
                int(hy * scale),
                max(1, int(hw * scale)),
                max(1, int(hh * scale)),
            )

    radius = max(12, int(min(shot.size) * 0.02))
    window = round_window(shot, radius=radius)
    shadow = rounded_shadow(window.size, radius=radius, pad=28)

    ox = (cw - window.size[0]) // 2
    oy = (ch - window.size[1]) // 2
    if label:
        oy = max(int(ch * 0.08), oy - 12)

    canvas = bg.copy()
    canvas.alpha_composite(shadow, (ox - 28, oy - 28))
    canvas.alpha_composite(window, (ox, oy))

    if highlight:
        hx, hy, hw, hh = highlight
        draw_highlight(canvas, (ox + hx, oy + hy, hw, hh))

    if label:
        d = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 36)
        except OSError:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except OSError:
                font = ImageFont.load_default()
        d.text((ox, max(24, oy - 52)), label, fill=(255, 255, 255, 235), font=font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


def parse_highlight(raw: str | None) -> tuple[int, int, int, int] | None:
    if not raw:
        return None
    parts = [int(p.strip()) for p in raw.replace("x", ",").split(",")]
    if len(parts) != 4:
        raise SystemExit("--highlight must be x,y,w,h")
    return parts[0], parts[1], parts[2], parts[3]


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shot", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--gradient", default=None, help="id from assets/gradients/manifest.json")
    p.add_argument("--label", default=None)
    p.add_argument("--highlight", default=None, help="x,y,w,h in screenshot pixels")
    p.add_argument("--margin", type=float, default=0.08)
    args = p.parse_args(argv)

    out = compose(
        shot_path=args.shot,
        out_path=args.out,
        gradient_id=args.gradient,
        label=args.label,
        highlight=parse_highlight(args.highlight),
        margin=args.margin,
    )
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
