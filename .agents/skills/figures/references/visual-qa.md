# Publication Figure Visual-QA Checklist (Universal Core)

Inspect every figure at its **actual compiled manuscript PDF scale** (rendered at 200–300 DPI via `scripts/render_pdf_pages.py` and opened with `read_file`). Load the matching paper-type playbook in `../../draft/references/genres/` (`ml.md`, `behavioral.md`, `general-science.md`, `management-econ.md`) for venue- and genre-specific figure micro-rules.

## 1. Typography & Legibility
- **Readable at print scale:** Every axis label, tick label, legend item, panel title, and embedded example must be comfortably legible on the rendered PDF page without extreme zooming.
- **Consistent typography:** Match the target venue's font family and weight hierarchy across all figures in the manuscript.
- **Plain, full labels:** Prefer spelled-out plain-English labels over cramped abbreviations or raw variable names.

## 2. Layout, Spacing & Overlap
- **Zero collisions:** Check for title-to-ylabel overlap, legends covering data, colliding tick labels, overlapping value annotations, and clipped margins or stimulus edges.
- **Consistent panel hierarchy:** Align panel identifiers (`A.`, `B.`, `C.`) cleanly in the same relative position across all figures, and keep legends frameless and well-organized.
- **Intentional aspect ratio & whitespace:** Use available column/page space cleanly—avoid tiny cramped plots surrounded by wasted horizontal or vertical gutters.

## 3. Visual & Cross-Figure Coherence
- **Consistent visual encoding:** Hold colors, line styles, and baseline ordering constant across figures—especially across paired figures meant to be compared side-by-side.
- **Clear uncertainty & axes:** Show appropriate uncertainty bands/bars (95% CIs or SEM), avoid meaningless negative axis ticks on bounded metrics, and keep scales comparable across sibling panels.
- **Vetted concrete examples:** Inspect any embedded visual stimuli, screenshots, or data plates for clipping, readability, and appropriateness.
