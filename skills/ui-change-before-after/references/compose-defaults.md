# Compose defaults (do not re-break)

| Knob | Default | Intent |
| --- | --- | --- |
| In-image label | off | Markdown `Before` / `After` table headers only |
| Framing | **hug content** | `canvas = shot + 2×margin` – no giant empty gradient |
| `--margin` | `0.03` (~3% of min side, ≥36px) | Equal tight pad on all four sides of the shot |
| Shadow | large blur, low opacity, small offset | Soft lift, not a hard dark edge |
| Corner radius | ~2% of min(shot side) | Same treatment on before and after |
| Output size | **may differ** before vs after | Same border treatment matters, not matching W×H |
| `--width` / `--height` / `--slot` | omit | Opt-in legacy fixed canvas / letterbox only |

**Optimize for:** identical border treatment (equal margin, shadow, radius), not
identical canvas dimensions. Crop raws toward comparable UI chrome when aspects
diverge (`--crop` / `--crops`). Do **not** pass `--width 1920 --height 1200`
unless the user explicitly wants a fixed poster canvas.

## Highlight tips

- Box the **changed control or copy**, not the whole window
- Slightly pad the region; `compose.py` adds ring padding
- If unsure of pixels, capture once, open the raw shot, estimate, iterate
