---
name: ui-change-before-after
description: >-
  Capture before/after UI screenshots, frame them on mesh gradients with a
  highlight, show both in chat for approval, then (only after yes) upload
  gradient-framed images and put a side-by-side Before/After table on the PR.
  Use when the user invokes /ui-change-before-after or asks for visual
  before/after approval of a UI change.
disable-model-invocation: true
compatibility: Requires macOS (screencapture/osascript) and Python 3 + Pillow
---

# UI change before / after

Two phases. **Phase A is mandatory.** Do not edit any GitHub PR until the user
approves in chat.

Deps: `requirements.txt` at skill root (`pip install -r requirements.txt`).

## Never

- Never touch a PR body (or upload for a PR) before Phase A approval
- Never skip showing both framed images in chat via the Read tool
- Never skip the succinct change bullet(s) under the images in chat or the PR
- Never skip the approval question after showing both images
- Never put a lone Before image on the PR – always side-by-side Before / After
- Never embed raw (unframed) window shots on the PR – use gradient-framed PNGs
- Never draw "Before" / "After" text on the gradient – table headers are enough
- Never force before/after framed PNGs to the same pixel dimensions (hug each shot)
- Never letterbox into a giant fixed canvas (e.g. 1920×1200) by default
- Never use one gradient for every Before/After pair on a multi-change PR –
  each change gets its own id; Before and After in a pair must match
- Never screenshot the whole desktop when a window capture will do
- Never commit framed PNGs into a product repo unless the user asks
- Never destroy or reimplement `github-pr-images` – follow that skill for upload
  URL rules (no private `raw.githubusercontent.com`, no Cursor co-author trailers)

## References (load on demand)

- Read [references/cli.md](references/cli.md) for capture / compose / side_by_side
  examples and output layout
- Read [references/gradients.md](references/gradients.md) for multi-change
  rotation and light/dark picks
- Read [references/compose-defaults.md](references/compose-defaults.md) for
  hug-content defaults, margins, legacy flags, and highlight tips

`SKILL` = directory containing this `SKILL.md`. Run scripts as
`python3 "$SKILL/scripts/<name>.py …"`.

Default single-change gradient: `aurora-rose` (see gradients reference).

---

## Phase A — Propose in chat (required)

Do this before any PR edit.

1. **Before** — capture the target window (`scripts/capture_window.py`). Same title later.
2. **Change** — make the UI edit (or confirm it is already made).
3. **After** — capture again with the same `--title`.
4. **Compose** — run `scripts/compose.py --shots … --outdir …` with the same
   `--gradient` and `--margin` for that change's Before and After. When the PR
   has multiple visual sections, choose a **different** `--gradient` id per
   section (see gradients reference). **Omit** `--width` / `--height` /
   `--slot` so each frame hugs its shot. Add `--highlight` / `--highlights`
   around the changed region when useful. **Do not** pass `--label` /
   `--labels` for PR frames. Crop raws toward the same UI chrome when aspects
   diverge. Framed outputs may differ in pixel size; both must use the same
   tight equal margin and soft shadow.
5. **Show** — `Read` both framed PNGs so they appear in the agent chat. The user
   must see them. Optionally also show `scripts/side_by_side.py --no-labels` output.
6. **Describe** — under the images, add a succinct change description: **one
   bullet, maybe two max**. Not an essay. Example:

   ```markdown
   ## Before / After

   | Before | After |
   | --- | --- |
   | ![Before](…) | ![After](…) |

   - Center empty-state subtitle and vertically center the empty block in the inbox list
   ```

7. **Hard stop** — ask:

   > Approve this UI change? (`yes` / describe a tweak / `no`)

8. **Do not** upload images, run `gh pr edit`, or otherwise touch GitHub until
   the user answers `yes` (or an equivalent clear approval). On tweak: redo
   capture/compose/show and ask again. On `no`: stop.

A PR that currently has only a lone Before image (e.g. harnessbay #6 style) is
exactly what Phase B fixes – but only after approval.

---

## Phase B — After approval, update the PR (side-by-side)

Only when the user said **yes** (or clear equivalent) and wants these on a PR:

1. **Upload** both **framed** images using the **github-pr-images** skill.
   Follow its preference order. Never private `raw.githubusercontent.com` embeds.
2. **Edit the PR body** to include a side-by-side section. Prefer a markdown
   table (renders on GitHub) — labels live in the headers, not on the PNGs.
   Under the table, include the same succinct change description as Phase A
   (**one bullet, maybe two max**):

   ```markdown
   ## Before / After

   | Before | After |
   | --- | --- |
   | ![Before](URL_BEFORE) | ![After](URL_AFTER) |

   - Center empty-state subtitle and vertically center the empty block in the inbox list
   ```

   Both URLs must point at the **gradient-framed** versions, not raw window
   shots. A single wide `side_by_side.py` image is optional; the table is enough
   when both URLs work. For multiple visual changes on one PR, use one section
   per change (heading + table + bullets each).
3. **Replace** any old single-before-only section (`## Before` with one image,
   no After). Do not leave a lone Before as the visual summary.
4. Use `gh pr edit <n> --body "$(cat <<'EOF' … EOF)"` (or equivalent) with the
   full intended body so you do not accidentally drop Summary / Test plan.

## Related skill

Upload URL acquisition stays in **github-pr-images**. This skill owns capture,
compose, chat approval, and the PR body shape (side-by-side table).
