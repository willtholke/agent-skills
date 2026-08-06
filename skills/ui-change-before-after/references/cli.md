# CLI examples

`SKILL` = directory containing this skill's `SKILL.md` (skill root). Scripts are
under `scripts/` relative to that root.

```bash
SKILL="<path-to-ui-change-before-after>"   # dir containing SKILL.md

# list windows
python3 "$SKILL/scripts/capture_window.py" --list

# capture one window (title substring)
python3 "$SKILL/scripts/capture_window.py" --title "Harness Bay" --out /tmp/ui-before.png

# pair compose (default): hug each shot – equal tight margin, soft shadow
python3 "$SKILL/scripts/compose.py" \
  --shots /tmp/ui-before.png /tmp/ui-after.png \
  --outdir /tmp/ui-change-before-after/slug \
  --gradient aurora-rose

# single shot
python3 "$SKILL/scripts/compose.py" \
  --shot /tmp/ui-before.png \
  --out /tmp/ui-before-framed.png \
  --gradient aurora-rose \
  --highlight 120,80,480,220

# optional crop when raws differ (e.g. wide desktop vs inbox column)
python3 "$SKILL/scripts/compose.py" \
  --shots raw-before.png raw-after.png \
  --outdir /tmp/ui-change-before-after/slug \
  --crops '' '0,0,648,1080'

# optional: one wide chat composite (labels off by default for PR parity)
python3 "$SKILL/scripts/side_by_side.py" \
  --before /tmp/ui-before-framed.png \
  --after /tmp/ui-after-framed.png \
  --out /tmp/ui-before-after.png \
  --no-labels
```

Deps: see `requirements.txt` at skill root (`pip install -r requirements.txt`).
macOS only for capture (`screencapture` / `osascript`).

## Output layout

Keep working files under `/tmp/ui-change-before-after/<slug>/` or a path the
user names:

```text
raw-before.png
raw-after.png
before-framed.png
after-framed.png
before-after.png   # optional side_by_side.py output
```
