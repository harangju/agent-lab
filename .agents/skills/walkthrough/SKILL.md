---
name: walkthrough
description: Build a self-contained, interactive 2D animated visuospatial walkthrough of a paper's concepts, mechanisms, and real examples (e.g., notes/walkthrough.html) with port-to-port SVG animations, top-down left-to-right reading flow, zero-rebuild 60-120fps motion, and headless-Chrome visual QA. Use when asked for an animated walkthrough, visual explainer, interactive concept demo, or talk-ready companion page for a paper.
argument-hint: "[paper path or topic] [output html path]"
---
Build a self-contained, interactive 2D animated visuospatial walkthrough of a paper's core concepts and real examples, saved by default to `notes/walkthrough.html`.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this `SKILL.md`. Resolve them to absolute paths in tool calls.

Every walkthrough must open directly offline in any browser (zero external build steps or CDN dependencies), teach through **concrete verbatim examples** and **locked paper numbers**, run smoothly at 60–120fps without per-frame DOM rebuilds, and pass **headless-Chrome visual QA across every scene and toggle state** before you report back.

## 0. Orient First

1. Read the manuscript (`paper/main.tex`, `main.md`, or `CONTEXT.md`) and `notes/STYLE.md` (plus `../draft/references/STYLE.md` if present) so every label, condition name, and number matches the paper verbatim.
2. Identify **4–5 core conceptual beats** that form a complete narrative arc:
   - **Scene 1 — Core Thesis / Overview:** Contrast the key failure vs. mechanism on the paper's flagship Figure 1 example.
   - **Scenes 2–4 — Causal Mechanisms & Controls:** Interactive probes, ablations, patching demos, depth/time scrubbers, or attention pathways using real examples from the paper.
   - **Final Scene — Practical Rule & Boundary Conditions:** Side-by-side before/after on real downstream benchmarks plus explicit failure modes where the effect fades or reverses.
3. Lock every displayed metric (accuracy, margins, pass counts, token counts, sample sizes) directly to verified manuscript values before writing HTML.

## 1. Visual & Spatial Rules (Non-Negotiable)

- **Crisp 2D vector animation, not 3D:** Default to a flat 2D vector stage. Avoid 3D camera orbit unless the user explicitly demands 3D—3D forces manual rotation, foreshortens text, and hides labels behind oblique planes.
- **Canvas-first, minimal text:** Do not build a 400px prose essay sidebar. Use a slim top scene-stepper bar, one short heading + one-line caption with inline toggle pills, a full-width 2D SVG stage (`viewBox="0 0 1160 560"`), and a compact bottom playback/scrubber dock.
- **Top-down, left-to-right reading flow:**
  - Place the **Question, Prompt, or Input Sentence at the top** so the reader sees the task first.
  - Align **Lists / Inputs (top → bottom)** directly across from **Passes / Stages (top → bottom)** so connecting wires run straight across with zero crossing X tangles.
  - Land the **Output / Prediction** at the bottom-right where the eye naturally finishes.
- **100% port-to-port connected geometry:** Read [references/engine-patterns.md](references/engine-patterns.md). Every node helper returns exact edge ports (`top`, `bottom`, `left`, `right`, `cx`, `cy`). Every arrow starts on a solid port dot and terminates cleanly on its target port—never floating in space and never cutting across intermediate text.
- **Generous arrow spans & unobstructed arrowheads:** Use crisp arrowheads (`8×8`), leave at least `32–40px` between connected nodes wherever space allows, skip animated pulse circles on short connectors (`< 28px`), and verify exact pixel budgets for dense inline/compact modes so pills never collide.
- **Semantic color discipline:** Reuse the paper's exact color palette (e.g., blue for structural anchors, amber for keys/intermediates, green for success/recovery, red for resets/failures/distractors) on a clean light drafting canvas. Follow `STYLE.md` (no em dashes, no raw script identifiers).

## 2. Silky 60–120fps Performance Architecture

Read [references/engine-patterns.md](references/engine-patterns.md) before writing `<script>`:

- **Zero per-frame DOM rebuilds:** Split `buildScene()` (writes SVG once on scene switch, toggle click, or scrubber drag) from `animateFrame()` (updates only `transform="translate(x,y) scale(s)"`, `stroke-dashoffset`, and highlight attributes on cached element refs during `requestAnimationFrame`).
- **Zero SVG blur/shadow filters:** Never use `<feGaussianBlur>` or `<feDropShadow>` inside an animated SVG—they force full-canvas rasterization on Retina displays and cause stutter. Use lightweight translucent vector halo rects instead (`grep -c 'filter="url(#'` must be `0`).
- **Presentation & deep-link polish:** Support `←` / `→` keyboard scene navigation, `Space` play/pause, `prefers-reduced-motion`, clickable in-diagram elements (e.g., patching or toggling individual items), and URL query parameters (`?scene=0&key=val`) so any state can be linked directly or captured deterministically.

## 3. Mandatory Headless-Chrome Visual QA

Read [references/visual-qa.md](references/visual-qa.md). Never deliver a walkthrough without inspecting screenshots of **every scene and every critical toggle state** (especially dense/inline layouts and reset/failure modes):

1. Capture all scenes and key modes to PNG with the bundled helper:
   ```bash
   bash <skill-dir>/scripts/capture_walkthrough.sh notes/walkthrough.html /tmp/wt_qa \
     "s1:scene=0" "s1_inline:scene=0&..." "s2:scene=1" ...
   ```
2. Open **every PNG** with `read_file` and audit against [references/visual-qa.md](references/visual-qa.md):
   - Zero overlapping tokens, pills, dashed guides, or caption lines (check compact/inline states explicitly).
   - Every wire cleanly connected port-to-port with visible arrowheads and no wire crossing through text.
   - Consistent top-down, left-to-right flow and zero horizontal scrollbar in the top navigation bar at `1440×860`.
   - Zero SVG filter references (`grep -c 'filter="url(#' notes/walkthrough.html` returns `0`).
3. Fix every defect, re-capture affected views, and re-inspect until clean.

## Never

- Rebuild the full SVG via `innerHTML` inside `requestAnimationFrame`.
- Ship `<feGaussianBlur>` or `<feDropShadow>` filters in an animated SVG.
- Flip vertical ordering between input lists (top-down) and model passes (bottom-up) so connecting wires cross in an X.
- Put a dense prose essay sidebar beside the diagram or use abstract `Box A → Box B` placeholders instead of real examples from the paper.
- Ship without visually inspecting headless-Chrome screenshots of every scene and compact/failure toggle state.
