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
- Never draw "Before" / "After" text on the gradient – table headers are enough
- Never ship before/after framed PNGs at different pixel sizes
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

# pair compose (preferred): same canvas + shared letterboxed window slot
python3 "$SKILL/scripts/compose.py" \
  --shots /tmp/ui-before.png /tmp/ui-after.png \
  --outdir /tmp/ui-change-before-after/slug \
  --gradient aurora-rose \
  --width 1920 --height 1200 \
  --margin 0.035

# single shot (same defaults: no in-image label, tight margin, soft shadow)
python3 "$SKILL/scripts/compose.py" \
  --shot /tmp/ui-before.png \
  --out /tmp/ui-before-framed.png \
  --gradient aurora-rose \
  --width 1920 --height 1200 \
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

Requires macOS (`screencapture`) and Pillow (`pip install pillow` if missing).

### Compose defaults (do not re-break)

| Knob | Default | Intent |
| --- | --- | --- |
| In-image label | off | Markdown `Before` / `After` table headers only |
| `--margin` | `0.035` (~3.5%) | UI window dominates; not 8%+ with label space |
| Shadow | large blur, low opacity, small offset | Soft lift, not a hard dark edge |
| Canvas | gradient native, or `--width`/`--height` | Both framed outputs identical W×H |
| Pair `--shots` | shared slot + letterbox | Same window chrome even if raw aspects differ |

When raws are landscape vs portrait of the same UI, crop to a comparable region
(inbox column, etc.) with `--crop` / `--crops`, or rely on pair letterboxing
inside the shared slot. Verify with Pillow/`identify` that both framed PNGs
have the same pixel size before upload.

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
4. **Compose** — run `compose.py --shots … --outdir …` with the same
   `--gradient`, `--width`/`--height`, and `--margin`. Add `--highlight` /
   `--highlights` around the changed region when useful. **Do not** pass
   `--label` / `--labels` for PR frames. Crop raws toward the same UI chrome
   when aspects diverge. Both outputs must be gradient-framed at the **same
   pixel dimensions**.
5. **Show** — `Read` both framed PNGs so they appear in the agent chat. The user
   must see them. Optionally also show `side_by_side.py --no-labels` output.
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
   table (renders on GitHub) — labels live in the headers, not on the PNGs:

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
