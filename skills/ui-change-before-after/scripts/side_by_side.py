#!/usr/bin/env python3
"""Composite two framed Before/After images into one wide PNG.

Usage:
  python3 side_by_side.py \\
    --before before-framed.png \\
    --after after-framed.png \\
    --out before-after.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_fit(path: Path, target_h: int) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    if im.size[1] != target_h:
        scale = target_h / im.size[1]
        im = im.resize(
            (max(1, int(im.size[0] * scale)), target_h),
            Image.Resampling.LANCZOS,
        )
    return im


def side_by_side(
    before_path: Path,
    after_path: Path,
    out_path: Path,
    gap: int,
    pad: int,
    bg: tuple[int, int, int],
    labels: bool,
) -> Path:
    before = Image.open(before_path).convert("RGBA")
    after = Image.open(after_path).convert("RGBA")
    target_h = min(before.size[1], after.size[1])
    before = load_fit(before_path, target_h)
    after = load_fit(after_path, target_h)

    label_h = 44 if labels else 0
    width = pad * 2 + before.size[0] + gap + after.size[0]
    height = pad * 2 + label_h + target_h
    canvas = Image.new("RGB", (width, height), bg)
    rgba = canvas.convert("RGBA")

    y = pad + label_h
    rgba.alpha_composite(before, (pad, y))
    rgba.alpha_composite(after, (pad + before.size[0] + gap, y))

    if labels:
        d = ImageDraw.Draw(rgba)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 28)
        except OSError:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            except OSError:
                font = ImageFont.load_default()
        d.text((pad, max(8, pad // 2)), "Before", fill=(255, 255, 255, 230), font=font)
        d.text(
            (pad + before.size[0] + gap, max(8, pad // 2)),
            "After",
            fill=(255, 255, 255, 230),
            font=font,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


def parse_bg(raw: str) -> tuple[int, int, int]:
    parts = [int(p.strip()) for p in raw.split(",")]
    if len(parts) != 3:
        raise SystemExit("--bg must be R,G,B")
    return parts[0], parts[1], parts[2]


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--before", required=True, type=Path)
    p.add_argument("--after", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--gap", type=int, default=32)
    p.add_argument("--pad", type=int, default=24)
    p.add_argument("--bg", default="18,18,22", help="R,G,B canvas behind the pair")
    p.add_argument("--no-labels", action="store_true", help="skip Before/After captions")
    args = p.parse_args(argv)

    out = side_by_side(
        before_path=args.before,
        after_path=args.after,
        out_path=args.out,
        gap=args.gap,
        pad=args.pad,
        bg=parse_bg(args.bg),
        labels=not args.no_labels,
    )
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
