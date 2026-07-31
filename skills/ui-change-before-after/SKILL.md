---
name: ui-change-before-after
description: >-
  Capture before/after UI screenshots, frame them on mesh gradients with a
  highlight, show both in chat for approval, then (only after yes) upload
  gradient-framed images and put a side-by-side Before|After table on the PR.
  Use when the user invokes /ui-change-before-after or asks for visual
  before/after approval of a UI change.
disable-model-invocation: true
---

# UI change before / after

Two phases. **Phase A is mandatory.** Do not edit any GitHub PR until the user
approves in chat.

## Never

- Never touch a PR body (or upload for a PR) before Phase A approval
- Never skip showing both framed images in chat via the Read tool
- Never skip the approval question after showing both images
- Never put a lone Before image on the PR – always side-by-side Before | After
- Never embed raw (unframed) window shots on the PR – use gradient-framed PNGs
- Never screenshot the whole desktop when a window capture will do
- Never commit framed PNGs into a product repo unless the user asks
- Never destroy or reimplement `github-pr-images` – read and follow that skill
- Never use private `raw.githubusercontent.com` URLs for embeds
- Never add Cursor co-author trailers to commits

## Assets

Mesh gradients live in `assets/gradients/` (see `manifest.json`):

`aurora-rose`, `sunset-flare`, `midnight-orchid`, `arctic-mint`, `citrus-sky`,
`peach-bloom`, `ember-violet`, `lagoon`, `dusk-haze`, `neon-prism`

Default: `aurora-rose`. Pick another if the UI is light (try `arctic-mint` /
`peach-bloom` / `dusk-haze`) or the user names one. Framed outputs must clearly
sit on the chosen mesh (compose.py centers the window on the full gradient).

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

# optional: one wide chat/PR composite
python3 "$SKILL/scripts/side_by_side.py" \
  --before /tmp/ui-before-framed.png \
  --after /tmp/ui-after-framed.png \
  --out /tmp/ui-before-after.png
```

Requires macOS (`screencapture`) and Pillow (`pip install pillow` if missing).

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

---

## Phase A — Propose in chat (required)

Do this before any PR edit.

1. **Before** — capture the target window (`capture_window.py`). Same title later.
2. **Change** — make the UI edit (or confirm it is already made).
3. **After** — capture again with the same `--title`.
4. **Compose** — run `compose.py` on both shots. Same `--gradient`. Add
   `--highlight x,y,w,h` around the changed region when useful. Labels:
   `Before` / `After`. Both outputs must be gradient-framed.
5. **Show** — `Read` both framed PNGs so they appear in the agent chat. The user
   must see them. Optionally also show `side_by_side.py` output.
6. **Hard stop** — ask:

   > Approve this UI change? (`yes` / describe a tweak / `no`)

7. **Do not** upload images, run `gh pr edit`, or otherwise touch GitHub until
   the user answers `yes` (or an equivalent clear approval). On tweak: redo
   capture/compose/show and ask again. On `no`: stop.

A PR that currently has only a lone Before image (e.g. harnessbay #6 style) is
exactly what Phase B fixes – but only after approval.

---

## Phase B — After approval, update the PR (side-by-side)

Only when the user said **yes** (or clear equivalent) and wants these on a PR:

1. **Upload** both **framed** images using the **github-pr-images** skill.
   Read `~/.cursor/skills/github-pr-images/SKILL.md` (or the clone under
   `skills/github-pr-images/`) and follow its preference order (`gh image` if
   available, else Litterbox / similar public hosts that work on private repos).
   Never private `raw.githubusercontent.com` embeds.
2. **Edit the PR body** to include a side-by-side section. Prefer a markdown
   table (renders on GitHub):

   ```markdown
   ## Before / After

   | Before | After |
   | --- | --- |
   | ![Before](URL_BEFORE) | ![After](URL_AFTER) |
   ```

   Both URLs must point at the **gradient-framed** versions, not raw window
   shots. A single wide `side_by_side.py` image is optional; the table is enough
   when both URLs work.
3. **Replace** any old single-before-only section (`## Before` with one image,
   no After). Do not leave a lone Before as the visual summary.
4. Use `gh pr edit <n> --body "$(cat <<'EOF' … EOF)"` (or equivalent) with the
   full intended body so you do not accidentally drop Summary / Test plan.

---

## Highlight tips

- Box the **changed control or copy**, not the whole window
- Slightly pad the region; `compose.py` adds ring padding
- If unsure of pixels, capture once, open the raw shot, estimate, iterate

## Related skill

Upload URL acquisition stays in **github-pr-images**. This skill owns capture,
compose, chat approval, and the PR body shape (side-by-side table).
