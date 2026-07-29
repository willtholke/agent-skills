#!/usr/bin/env python3
"""Capture a macOS application window by title substring.

Usage:
  python3 capture_window.py --title "Harness Bay" --out before.png
  python3 capture_window.py --list
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


LIST_SCRIPT = """
ObjC.import("CoreGraphics");
const windows = $.CGWindowListCopyWindowInfo(
  $.kCGWindowListOptionOnScreenOnly | $.kCGWindowListExcludeDesktopElements,
  $.kCGNullWindowID
);
const out = [];
for (let i = 0; i < windows.count; i++) {
  const w = windows.objectAtIndex(i);
  const layer = w.objectForKey("kCGWindowLayer");
  if (layer && layer.intValue !== 0) continue;
  const bounds = w.objectForKey("kCGWindowBounds");
  const width = bounds.objectForKey("Width").doubleValue;
  const height = bounds.objectForKey("Height").doubleValue;
  if (width < 80 || height < 80) continue;
  out.push({
    id: w.objectForKey("kCGWindowNumber").intValue,
    app: String(w.objectForKey("kCGWindowOwnerName") || ""),
    title: String(w.objectForKey("kCGWindowName") || ""),
    width: Math.round(width),
    height: Math.round(height),
  });
}
JSON.stringify(out);
"""


def list_windows() -> list[dict]:
    raw = subprocess.check_output(
        ["osascript", "-l", "JavaScript", "-e", LIST_SCRIPT],
        text=True,
    ).strip()
    return json.loads(raw)


def pick_window(title_substr: str) -> dict:
    needle = title_substr.lower()
    windows = list_windows()
    matches = [
        w
        for w in windows
        if needle in w["title"].lower() or needle in w["app"].lower()
    ]
    if not matches:
        names = ", ".join(f'{w["app"]}:{w["title"] or "(no title)"}' for w in windows[:12])
        raise SystemExit(f"No window matching {title_substr!r}. Visible: {names}")
    # prefer largest match (main window)
    matches.sort(key=lambda w: w["width"] * w["height"], reverse=True)
    return matches[0]


def capture(window_id: int, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    # -l window id, -x no shadow (we add our own), -o no window shadow in older macOS
    cmd = ["screencapture", "-l", str(window_id), "-x", str(out)]
    subprocess.check_call(cmd)
    if not out.exists() or out.stat().st_size < 100:
        raise SystemExit(f"screencapture failed for window id {window_id}")
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list", action="store_true", help="list capturable windows")
    p.add_argument("--title", help="substring match on window title or app name")
    p.add_argument("--out", type=Path, help="output PNG path")
    args = p.parse_args(argv)

    if args.list:
        for w in list_windows():
            print(f'{w["id"]:>6}  {w["width"]}x{w["height"]}  {w["app"]} — {w["title"] or "(no title)"}')
        return 0

    if not args.title or not args.out:
        raise SystemExit("--title and --out are required (or use --list)")

    win = pick_window(args.title)
    path = capture(win["id"], args.out)
    print(json.dumps({"path": str(path), **win}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
