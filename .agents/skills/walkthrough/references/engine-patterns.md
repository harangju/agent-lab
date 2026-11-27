# 2D Animated Walkthrough Engine Patterns

Reference architecture for self-contained, zero-dependency, 60–120fps 2D SVG walkthroughs (`notes/walkthrough.html`).

## 1. Port-Returning Node Helper (`makeToken`)

Always compute exact edge port coordinates from the same `(x, y, w, h)` box that renders the tile so wires never drift or float:

```js
const GLOW_COLORS = {
  glowBlue: '#0284C7',
  glowGreen: '#16A34A',
  glowRed: '#DC2626',
};

function makeToken(x, y, w, h, label, toneKey = 'slate', opts = {}) {
  const t = TONES[toneKey] || TONES.slate;
  const r = opts.rx ?? 8;
  const cls = opts.action ? ` class="clickable" data-action="${esc(opts.action)}"` : '';
  const rectId = opts.rectId ? ` id="${opts.rectId}"` : '';

  let svg = `<g${cls}>`;
  // Zero-cost vector halo (replaces expensive SVG <feGaussianBlur>)
  if (opts.glow && GLOW_COLORS[opts.glow]) {
    svg += `<rect x="${(x - 4).toFixed(1)}" y="${(y - 4).toFixed(1)}" width="${(w + 8).toFixed(1)}" height="${(h + 8).toFixed(1)}" rx="${r + 3.5}" fill="${GLOW_COLORS[opts.glow]}" fill-opacity="0.18"/>`;
  }
  svg += `<rect${rectId} x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" rx="${r}" fill="${t.fill}" stroke="${t.stroke}" stroke-width="${opts.strokeWidth ?? 1.5}"/>`;
  // ... centered label & optional sub-label ...
  svg += `</g>`;

  return {
    svg, x, y, w, h,
    cx: x + w / 2, cy: y + h / 2,
    top: [x + w / 2, y], bottom: [x + w / 2, y + h],
    left: [x, y + h / 2], right: [x + w, y + h / 2],
  };
}
```

## 2. Port-to-Port Cubic Bézier Wires & Cached Pulse Refs

Populate `livePackets` and `liveDashes` once inside `buildScene()`, then mutate ONLY `transform` and `stroke-dashoffset` inside `animateFrame()`:

```js
let livePackets = [];
let liveDashes = [];

function bezierWire(p0, p1, c1, c2, opts = {}) {
  const color = opts.color ?? '#0284C7';
  const w = opts.width ?? 2.6;
  const d = `M ${p0[0].toFixed(1)} ${p0[1].toFixed(1)} C ${c1[0].toFixed(1)} ${c1[1].toFixed(1)}, ${c2[0].toFixed(1)} ${c2[1].toFixed(1)}, ${p1[0].toFixed(1)} ${p1[1].toFixed(1)}`;
  // 1. Soft translucent under-stroke (only for solid lines)
  // 2. Crisp main stroke with 8x8 marker-end arrowhead
  // 3. Solid port anchor dot at p0 (and p1 if arrow === false)
  // 4. Persistent <g id="pkt-N"> pulse elements ONLY when approxLen >= 28px
  const approxLen = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
  if ((opts.packets ?? 2) > 0 && approxLen >= 28) {
    // push { id, p0, c1, c2, p1, speed, offset, el: null } to livePackets
  }
}
```

### Convenience Routing Helpers
- `hWire(p0, p1, opts)`: horizontal S-curve (`dx = (p1[0] - p0[0]) * 0.45`).
- `vWire(p0, p1, opts)`: vertical S-curve (`dy = (p1[1] - p0[1]) * 0.45`).
- `archWire(p0, p1, archY, opts)`: clean arch above (`archY > 0`) or below (`archY < 0`) a token row.

## 3. Zero-Rebuild Animation Loop

```js
function buildScene() {
  livePackets = [];
  liveDashes = [];
  svgScene.innerHTML = renderCurrentScene();
  for (const pk of livePackets) pk.el = document.getElementById(pk.id);
  for (const ld of liveDashes) ld.el = document.getElementById(ld.id);
  animateFrame();
}

function animateFrame() {
  const t = state.time;
  for (let i = 0; i < livePackets.length; i++) {
    const pk = livePackets[i];
    if (!pk.el) continue;
    const u = ((t * pk.speed + pk.offset) % 1 + 1) % 1;
    const mt = 1 - u, mt2 = mt * mt, u2 = u * u;
    const x = mt2*mt*pk.p0[0] + 3*mt2*u*pk.c1[0] + 3*mt*u2*pk.c2[0] + u2*u*pk.p1[0];
    const y = mt2*mt*pk.p0[1] + 3*mt2*u*pk.c1[1] + 3*mt*u2*pk.c2[1] + u2*u*pk.p1[1];
    const s = 0.74 + 0.36 * Math.sin(u * Math.PI);
    pk.el.setAttribute('transform', `translate(${x.toFixed(1)},${y.toFixed(1)}) scale(${s.toFixed(2)})`);
  }
  for (let i = 0; i < liveDashes.length; i++) {
    if (liveDashes[i].el) liveDashes[i].el.setAttribute('stroke-dashoffset', (t * liveDashes[i].speed).toFixed(1));
  }
}
```

- Only call `buildScene()` on user interactions (scene switch, toggle button, diagram click, scrubber `input`) or during a short (<300ms) layout-morph transition—snap cleanly to the target once `Math.abs(target - current) <= 0.004`.
- Parse `window.location.search` at startup so any state (`?scene=2&mode=buried&pass=3`) loads deterministically for direct links and headless-Chrome QA.

## 4. Pixel-Budget Layout Discipline

- Standard stage `viewBox="0 0 1160 560"`.
- Keep `>= 32–40px` horizontal/vertical clearance for connected arrows so arrowheads (`markerWidth="8" markerHeight="8"`) and gliding pulses never collide.
- For dense inline modes (e.g., collapsing multiple rows onto one horizontal strip), calculate exact cumulative widths (`sum(tokenW + gap)`) so every inline connector pill sits with `>= 4–6px` clean gutter on both sides and fits well inside its container.
- Route wires *around* intermediate chips (`A → rel → B` as two short edge-to-edge segments) rather than drawing one wire straight through `rel`'s text.
