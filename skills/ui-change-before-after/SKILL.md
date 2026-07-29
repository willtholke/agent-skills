---
name: ui-change-before-after
description: >-
  Capture before/after UI screenshots of an app window, frame them on mesh
  gradients with a highlight, show both in chat, and ask for approval. Use when
  the user invokes /ui-change-before-after or asks for visual before/after
  approval of a UI change.
disable-model-invocation: true
---

# UI change before / after

Produce polished **Before** and **After** frames of a real app window, show them
in chat, and **stop for approval** before continuing (merge, more UI work, or
PR upload).

## Never

- Never skip the approval question after showing both images
- Never screenshot the whole desktop when a window capture will do
- Never commit framed PNGs into a product repo unless the user asks
- Never destroy or reimplement `github-pr-images` — call it when uploading
- Never add Cursor co-author trailers to commits

## Assets

Mesh gradients live in `assets/gradients/` (see `manifest.json`):

`aurora-rose`, `sunset-flare`, `midnight-orchid`, `arctic-mint`, `citrus-sky`,
`peach-bloom`, `ember-violet`, `lagoon`, `dusk-haze`, `neon-prism`

Default: `aurora-rose`. Pick another if the UI is light (try `arctic-mint` /
`peach-bloom` / `dusk-haze`) or the user names one.

## Scripts (this skill folder)

```bash
SKILL=~/.cursor/skills/ui-change-before-after   # or the cloned path

# list windows
python3 "$SKILL/scripts/capture_window.py" --list

# capture one window (title substring)
python3 "$SKILL/scripts/capture_window.py" --title "Harness Bay" --out /tmp/ui-before.png

# frame + optional highlight (x,y,w,h in screenshot pixels)
python3 "$SKILL/scripts/compose.py" \
  --shot /tmp/ui-before.png \
  --out /tmp/ui-before-framed.png \
  --gradient aurora-rose \
  --label Before \
  --highlight 120,80,480,220
```

Requires macOS (`screencapture`) and Pillow (`pip install pillow` if missing).

## Workflow

1. **Before** — capture the target window (`capture_window.py`). Same title later.
2. **Change** — make the UI edit (or confirm it is already made).
3. **After** — capture again with the same `--title`.
4. **Compose** — run `compose.py` on both shots. Same `--gradient`. Add
   `--highlight x,y,w,h` around the changed region (estimate from the edit;
   prefer a circle-friendly box). Labels: `Before` / `After`.
5. **Show** — `Read` both framed PNGs so they appear in chat.
6. **Ask** — hard stop:

   > Approve this UI change? (`yes` / describe a tweak / `no`)

   Do not merge, ship, or attach to a PR until the user answers.

7. **Optional PR** — if they want these on a GitHub PR/issue, follow the
   `github-pr-images` skill for upload URLs, then put both in the body under
   `## Before` / `## After`.

## Highlight tips

- Box the **changed control or copy**, not the whole window
- Slightly pad the region; `compose.py` adds ring padding
- If unsure of pixels, capture once, open the raw shot, estimate, iterate

## Output layout

Keep working files under `/tmp/ui-change-before-after/<slug>/` or a path the
user names. Suggested names:

```text
raw-before.png
raw-after.png
before-framed.png
after-framed.png
```
