#!/usr/bin/env python3
"""Compose a window screenshot onto a mesh gradient.

Usage:
  python3 compose.py \\
    --shot before.png \\
    --out before-framed.png \\
    --gradient aurora-rose \\
    --width 1920 --height 1200

  # Pair: identical canvas + shared window slot (letterboxed)
  python3 compose.py \\
    --shots before.png after.png \\
    --outdir /tmp/ui-change-before-after/slug \\
    --gradient aurora-rose

Highlight is x,y,w,h in screenshot pixel space (optional).
Labels are off by default — use markdown table headers on the PR.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKILL_ROOT = Path(__file__).resolve().parents[1]
GRADIENTS = SKILL_ROOT / "assets" / "gradients"
MANIFEST = GRADIENTS / "manifest.json"

# Tight frame: UI dominates. Soft shadow (large blur, low alpha, small offset).
DEFAULT_MARGIN = 0.035
SHADOW_PAD = 56
SHADOW_OFFSET = (3, 5)
SHADOW_ALPHA = 56
SHADOW_BLUR = 42


def load_gradient(gradient_id: str | None) -> Image.Image:
    data = json.loads(MANIFEST.read_text())
    gid = gradient_id or data.get("default") or data["gradients"][0]["id"]
    entry = next((g for g in data["gradients"] if g["id"] == gid), None)
    if entry is None:
        known = ", ".join(g["id"] for g in data["gradients"])
        raise SystemExit(f"Unknown gradient {gid!r}. Known: {known}")
    return Image.open(GRADIENTS / entry["file"]).convert("RGB")


def canvas_from_gradient(
    gradient_id: str | None, width: int | None, height: int | None
) -> Image.Image:
    bg = load_gradient(gradient_id).convert("RGBA")
    if width is None and height is None:
        return bg
    tw = width or bg.size[0]
    th = height or bg.size[1]
    if (tw, th) == bg.size:
        return bg
    # Cover-scale then center-crop so the mesh still fills the canvas.
    sw, sh = bg.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    scaled = bg.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return scaled.crop((left, top, left + tw, top + th))


def parse_wh(raw: str | None, flag: str) -> tuple[int, int] | None:
    if not raw:
        return None
    parts = [int(p.strip()) for p in raw.lower().replace("x", ",").split(",")]
    if len(parts) != 2 or parts[0] < 1 or parts[1] < 1:
        raise SystemExit(f"{flag} must be W,H or WxH")
    return parts[0], parts[1]


def parse_crop(raw: str | None) -> tuple[int, int, int, int] | None:
    if not raw:
        return None
    parts = [int(p.strip()) for p in raw.replace("x", ",").split(",")]
    if len(parts) != 4:
        raise SystemExit("--crop must be x,y,w,h")
    return parts[0], parts[1], parts[2], parts[3]


def parse_highlight(raw: str | None) -> tuple[int, int, int, int] | None:
    if not raw:
        return None
    parts = [int(p.strip()) for p in raw.replace("x", ",").split(",")]
    if len(parts) != 4:
        raise SystemExit("--highlight must be x,y,w,h")
    return parts[0], parts[1], parts[2], parts[3]


def parse_rgb(raw: str | None) -> tuple[int, int, int] | None:
    if not raw:
        return None
    parts = [int(p.strip()) for p in raw.split(",")]
    if len(parts) != 3:
        raise SystemExit("--fill must be R,G,B")
    return parts[0], parts[1], parts[2]


def sample_fill(shot: Image.Image) -> tuple[int, int, int]:
    """Pick a dark UI chrome color from shot corners (fallback charcoal)."""
    rgba = shot.convert("RGBA")
    w, h = rgba.size
    pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (0, h // 2)]
    colors = [rgba.getpixel(p)[:3] for p in pts]
    # median-ish via sort of luminance
    colors.sort(key=lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])
    mid = colors[len(colors) // 2]
    if 0.2126 * mid[0] + 0.7152 * mid[1] + 0.0722 * mid[2] > 80:
        return (28, 26, 24)
    return mid


def apply_crop(shot: Image.Image, crop: tuple[int, int, int, int] | None) -> Image.Image:
    if not crop:
        return shot
    x, y, w, h = crop
    return shot.crop((x, y, x + w, y + h))


def content_box(cw: int, ch: int, margin: float) -> tuple[int, int]:
    max_w = max(1, int(cw * (1 - 2 * margin)))
    max_h = max(1, int(ch * (1 - 2 * margin)))
    # Keep soft-shadow falloff on-canvas (blur clips if the slot fills the margin).
    shadow_room = SHADOW_OFFSET[1] + SHADOW_BLUR // 2
    max_w = max(1, max_w - 2 * shadow_room)
    max_h = max(1, max_h - 2 * shadow_room)
    return max_w, max_h


def fit_to_box(
    shot: Image.Image, max_w: int, max_h: int, *, allow_upscale: bool = True
) -> Image.Image:
    sw, sh = shot.size
    scale = min(max_w / sw, max_h / sh)
    if not allow_upscale:
        scale = min(scale, 1.0)
    if abs(scale - 1.0) < 1e-6:
        return shot
    return shot.resize(
        (max(1, int(sw * scale)), max(1, int(sh * scale))),
        Image.Resampling.LANCZOS,
    )


def scale_highlight(
    highlight: tuple[int, int, int, int] | None,
    src_size: tuple[int, int],
    dst_size: tuple[int, int],
) -> tuple[int, int, int, int] | None:
    if not highlight:
        return None
    sx = dst_size[0] / max(1, src_size[0])
    sy = dst_size[1] / max(1, src_size[1])
    hx, hy, hw, hh = highlight
    return (
        int(hx * sx),
        int(hy * sy),
        max(1, int(hw * sx)),
        max(1, int(hh * sy)),
    )


def letterbox(
    shot: Image.Image,
    slot: tuple[int, int],
    fill: tuple[int, int, int],
) -> tuple[Image.Image, tuple[int, int]]:
    """Fit shot into slot; return (slot image, offset of shot inside slot)."""
    fitted = fit_to_box(shot, slot[0], slot[1], allow_upscale=True)
    canvas = Image.new("RGBA", slot, (*fill, 255))
    ox = (slot[0] - fitted.size[0]) // 2
    oy = (slot[1] - fitted.size[1]) // 2
    canvas.paste(fitted.convert("RGBA"), (ox, oy), fitted.convert("RGBA"))
    return canvas, (ox, oy)


def rounded_shadow(size: tuple[int, int], radius: int, pad: int) -> Image.Image:
    w, h = size
    ox, oy = SHADOW_OFFSET
    shadow = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    d.rounded_rectangle(
        [pad + ox, pad + oy, pad + w + ox, pad + h + oy],
        radius=radius,
        fill=(0, 0, 0, SHADOW_ALPHA),
    )
    return shadow.filter(ImageFilter.GaussianBlur(radius=SHADOW_BLUR))


def round_window(shot: Image.Image, radius: int) -> Image.Image:
    shot = shot.convert("RGBA")
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, shot.size[0] - 1, shot.size[1] - 1], radius=radius, fill=255
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
    pad = max(18, int(min(w, h) * 0.12))
    rw, rh = w / 2 + pad, h / 2 + pad
    if abs(w - h) / max(w, h, 1) < 0.25:
        r = max(rw, rh)
        rw = rh = r
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    thickness = max(4, int(min(canvas.size) * 0.004))
    bbox = [cx - rw, cy - rh, cx + rw, cy + rh]
    d.ellipse(bbox, outline=(*color, 230), width=thickness)
    glow = overlay.filter(ImageFilter.GaussianBlur(radius=thickness))
    canvas.alpha_composite(glow)
    canvas.alpha_composite(overlay)


def shared_slot_for_shots(
    shots: list[Image.Image], max_w: int, max_h: int
) -> tuple[int, int]:
    """Same window slot for every shot: max fitted size, clamped to content box."""
    fitted = [fit_to_box(s, max_w, max_h, allow_upscale=True) for s in shots]
    slot_w = max(im.size[0] for im in fitted)
    slot_h = max(im.size[1] for im in fitted)
    # Prefer filling the content box when aspects differ a lot, so both frames
    # share identical chrome rather than a skinny union box.
    # Use content box as the slot when either shot is >15% smaller on an axis
    # after independent fit — letterboxing equalizes the frame.
    aspect_spread = max(im.size[0] / im.size[1] for im in fitted) / min(
        im.size[0] / im.size[1] for im in fitted
    )
    if aspect_spread > 1.15:
        return max_w, max_h
    return min(slot_w, max_w), min(slot_h, max_h)


def compose_one(
    shot: Image.Image,
    bg: Image.Image,
    *,
    slot: tuple[int, int],
    fill: tuple[int, int, int],
    label: str | None,
    highlight: tuple[int, int, int, int] | None,
    highlight_src_size: tuple[int, int] | None,
) -> Image.Image:
    cw, ch = bg.size
    window_src, (inner_ox, inner_oy) = letterbox(shot, slot, fill)
    # Scale highlight from original (post-crop) shot space → fitted shot → slot
    hl = None
    if highlight and highlight_src_size:
        fitted = fit_to_box(shot, slot[0], slot[1], allow_upscale=True)
        hl = scale_highlight(highlight, highlight_src_size, fitted.size)
        if hl:
            hx, hy, hw, hh = hl
            hl = (hx + inner_ox, hy + inner_oy, hw, hh)

    radius = max(12, int(min(window_src.size) * 0.02))
    window = round_window(window_src, radius=radius)
    shadow = rounded_shadow(window.size, radius=radius, pad=SHADOW_PAD)

    ox = (cw - window.size[0]) // 2
    oy = (ch - window.size[1]) // 2
    # Optional label reserves a little top bias; PR frames leave labels off.
    if label:
        oy = max(int(ch * 0.06), oy - 8)

    canvas = bg.copy()
    canvas.alpha_composite(shadow, (ox - SHADOW_PAD, oy - SHADOW_PAD))
    canvas.alpha_composite(window, (ox, oy))

    if hl:
        hx, hy, hw, hh = hl
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

    return canvas


def compose(
    shot_path: Path,
    out_path: Path,
    gradient_id: str | None,
    label: str | None,
    highlight: tuple[int, int, int, int] | None,
    margin: float,
    width: int | None,
    height: int | None,
    slot: tuple[int, int] | None,
    crop: tuple[int, int, int, int] | None,
    fill: tuple[int, int, int] | None,
) -> Path:
    bg = canvas_from_gradient(gradient_id, width, height)
    shot = apply_crop(Image.open(shot_path).convert("RGBA"), crop)
    max_w, max_h = content_box(bg.size[0], bg.size[1], margin)
    use_slot = slot or (max_w, max_h)
    use_fill = fill or sample_fill(shot)
    src_size = shot.size
    canvas = compose_one(
        shot,
        bg,
        slot=use_slot,
        fill=use_fill,
        label=label,
        highlight=highlight,
        highlight_src_size=src_size,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


def compose_pair(
    shot_paths: list[Path],
    out_paths: list[Path],
    gradient_id: str | None,
    labels: list[str | None],
    highlights: list[tuple[int, int, int, int] | None],
    margin: float,
    width: int | None,
    height: int | None,
    slot: tuple[int, int] | None,
    crops: list[tuple[int, int, int, int] | None],
    fill: tuple[int, int, int] | None,
) -> list[Path]:
    bg = canvas_from_gradient(gradient_id, width, height)
    max_w, max_h = content_box(bg.size[0], bg.size[1], margin)
    shots: list[Image.Image] = []
    for path, crop in zip(shot_paths, crops):
        shots.append(apply_crop(Image.open(path).convert("RGBA"), crop))
    use_slot = slot or shared_slot_for_shots(shots, max_w, max_h)
    # One fill for the pair so letterbox chrome matches.
    use_fill = fill or sample_fill(shots[0])
    written: list[Path] = []
    for shot, out_path, label, highlight in zip(shots, out_paths, labels, highlights):
        canvas = compose_one(
            shot,
            bg,
            slot=use_slot,
            fill=use_fill,
            label=label,
            highlight=highlight,
            highlight_src_size=shot.size,
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out_path, "PNG", optimize=True)
        written.append(out_path)
        print(f"{out_path}  slot={use_slot[0]}x{use_slot[1]}  canvas={bg.size[0]}x{bg.size[1]}")
    return written


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shot", type=Path, help="single screenshot")
    p.add_argument("--out", type=Path, help="output for --shot")
    p.add_argument(
        "--shots",
        nargs=2,
        type=Path,
        metavar=("BEFORE", "AFTER"),
        help="pair mode: shared canvas + shared window slot",
    )
    p.add_argument(
        "--outdir",
        type=Path,
        help="with --shots, writes before-framed.png and after-framed.png",
    )
    p.add_argument("--gradient", default=None, help="id from assets/gradients/manifest.json")
    p.add_argument(
        "--label",
        default=None,
        help="optional in-image caption (off by default; prefer PR table headers)",
    )
    p.add_argument(
        "--labels",
        nargs=2,
        metavar=("BEFORE", "AFTER"),
        help="optional pair labels (usually omit)",
    )
    p.add_argument("--highlight", default=None, help="x,y,w,h in screenshot pixels")
    p.add_argument(
        "--highlights",
        nargs=2,
        metavar=("BEFORE", "AFTER"),
        help="pair highlights as x,y,w,h or '' to skip",
    )
    p.add_argument("--margin", type=float, default=DEFAULT_MARGIN)
    p.add_argument("--width", type=int, default=None, help="output canvas width")
    p.add_argument("--height", type=int, default=None, help="output canvas height")
    p.add_argument(
        "--slot",
        default=None,
        help="fixed window slot WxH (letterbox inside). Pair mode defaults to a shared slot",
    )
    p.add_argument("--crop", default=None, help="crop shot first: x,y,w,h")
    p.add_argument(
        "--crops",
        nargs=2,
        metavar=("BEFORE", "AFTER"),
        help="pair crops as x,y,w,h or '' to skip",
    )
    p.add_argument("--fill", default=None, help="letterbox fill R,G,B (default: sample shot)")
    args = p.parse_args(argv)

    slot = parse_wh(args.slot, "--slot")
    fill = parse_rgb(args.fill)

    if args.shots:
        if not args.outdir:
            raise SystemExit("--shots requires --outdir")
        crops_raw = args.crops or ["", ""]
        crops = [parse_crop(c if c else None) for c in crops_raw]
        if args.highlights:
            highlights = [
                parse_highlight(h if h else None) for h in args.highlights
            ]
        else:
            highlights = [None, None]
        labels: list[str | None]
        if args.labels:
            labels = [args.labels[0] or None, args.labels[1] or None]
        else:
            labels = [None, None]
        outdir: Path = args.outdir
        outs = [outdir / "before-framed.png", outdir / "after-framed.png"]
        compose_pair(
            shot_paths=list(args.shots),
            out_paths=outs,
            gradient_id=args.gradient,
            labels=labels,
            highlights=highlights,
            margin=args.margin,
            width=args.width,
            height=args.height,
            slot=slot,
            crops=crops,
            fill=fill,
        )
        return 0

    if not args.shot or not args.out:
        raise SystemExit("Provide --shot/--out or --shots/--outdir")

    out = compose(
        shot_path=args.shot,
        out_path=args.out,
        gradient_id=args.gradient,
        label=args.label,
        highlight=parse_highlight(args.highlight),
        margin=args.margin,
        width=args.width,
        height=args.height,
        slot=slot,
        crop=parse_crop(args.crop),
        fill=fill,
    )
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
