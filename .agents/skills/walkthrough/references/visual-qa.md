# Walkthrough Visual QA Checklist

Inspect **every captured PNG** with `read_file` before reporting back. Never rely on code inspection alone—compact modes, curve labels, and nav bars routinely hide collisions that only show up at rendered pixel scale.

## Required Captures

Capture at `1440×860` desktop viewport via `scripts/capture_walkthrough.sh`:
1. Every scene in its default state (`scene=0` through `scene=N-1`).
2. Every layout/failure toggle that rearranges tokens—especially **compact/inline modes**, **reset/failure modes**, and **patching/scrubbed states**.

## Audit Checklist

- [ ] **Top navigation bar:** All scene tabs fit in one crisp row with zero horizontal scrollbar or clipped tab labels.
- [ ] **Reading order:** Each scene reads naturally **top-down, left-to-right** (Question/Input at top, stages/passes progressing downward, Output at bottom-right). No inverted list-vs-pass ordering that forces crossing X wires.
- [ ] **Arrow clarity:** Arrowheads are crisp and legible (`8×8`), connectors have generous length (`>= 32px` where possible), and no pulse circle covers an arrowhead or start dot.
- [ ] **Zero overlaps:**
  - No token pill collides with an adjacent connector chip (especially in compact inline modes).
  - No wire passes through text inside a token, card header, or caption line.
  - No row label (`List 1`, `PASS 1`) touches a vertical margin guide line or arrow tip.
  - No floating arc label touches a neighboring node or callout card.
- [ ] **Minimal text & style compliance:** No bulky prose sidebar; concise 1-line captions; no em dashes (`—`), no raw internal script keys; all displayed numbers match locked paper values.
- [ ] **Zero-lag performance hygiene:**
  - `grep -c 'filter="url(#' notes/walkthrough.html` returns `0`.
  - `requestAnimationFrame` loop only calls `animateFrame()` (direct `transform` / attribute updates) during steady playback, never `innerHTML`.
