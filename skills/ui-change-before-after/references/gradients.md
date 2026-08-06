# Gradients

Mesh gradients live in `assets/gradients/` (see `manifest.json`):

`aurora-rose`, `sunset-flare`, `midnight-orchid`, `arctic-mint`, `citrus-sky`,
`peach-bloom`, `ember-violet`, `lagoon`, `dusk-haze`, `neon-prism`

Default for a **single** change: `aurora-rose`. Pick another if the UI is light
(try `arctic-mint` / `peach-bloom` / `dusk-haze`) or the user names one.

## Multiple changes on one PR (do not re-break)

When composing **more than one** Before/After section for the same PR:

- Pick a gradient **per change** from `assets/gradients/manifest.json`.
- Before and After for that change **must share the same `--gradient` id**.
- Different changes on the same PR must use **different** gradient ids. Rotate
  through the pack (e.g. `aurora-rose`, `sunset-flare`, `midnight-orchid`,
  `arctic-mint`, `citrus-sky`, `peach-bloom`, `ember-violet`, `lagoon`,
  `dusk-haze`, `neon-prism`). Prefer darker packs (`midnight-orchid`,
  `ember-violet`, `lagoon`) when the UI chrome is dark and light packs
  (`citrus-sky`, `peach-bloom`, `arctic-mint`) when it is light–or follow an
  explicit assignment from the user.
- **Do not** use one gradient for the whole PR.
