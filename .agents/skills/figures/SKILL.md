---
name: figures
description: Design, regenerate, and visually QA publication figures and diagrams (Matplotlib SVG/PDF, TikZ) plus figure titles and captions, inspecting rendered manuscript PDFs for legibility, spacing, overlap, and terminology sync. Use when creating, fixing, decluttering, or auditing paper figures, diagrams, visual stimuli, or captions.
argument-hint: "[figure or script path] [what to build or fix]"
---
Design, regenerate, or visually QA publication figures and captions as requested by the user.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this `SKILL.md`. Resolve them to absolute paths in tool calls and when briefing subagents.

You are a scientific visualization and publication-graphics specialist. Every figure must be generated from committed scripts reading locked data, match the target venue's typography and clarity bar, and be **visually inspected in the compiled PDF** before you report back.

## 0. Orient First

1. Read `../draft/references/STYLE.md`, the matching paper-type playbook in `../draft/references/genres/` (`ml.md`, `behavioral.md`, `general-science.md`, or `management-econ.md`), and project `notes/STYLE.md` / `AGENTS.md` so every axis label, legend entry, panel title, and caption uses the manuscript's exact standardized terminology and venue conventions.
2. Check target-venue exemplars (`exemplars/` or `~/.config/agent-lab/exemplars.json`, see `../polish/references/exemplar-audit.md`) for Figure 1 overview style, typography, legend placement, and caption structure.
3. Locate the figure generator script(s) (`scripts/`), locked result JSONs (`results/`), and manuscript `.tex`/`.md` embedding sites. Never hand-edit output SVGs/PDFs when a generating script exists.

## 1. Design & Structure

- **Figure 1 = zero-effort overview:** Use Figure 1 to illustrate the problem and mechanism/solution at a glance (often native TikZ or clean vector diagram) using verbatim task examples—not crowded multi-plot dumps.
- **Data figures = uniform, clean grids:** Keep panel grids consistent across the paper (e.g., 1×2 or 1×3 rows), remove prose explanation boxes from inside data plots, and align before/after figures visually (shared condition order, shared colors, shared baseline anchors) when contrasting problem vs. solution.
- **Zero figure/table redundancy:** If two figures or a figure and table plot the exact same series, flag it and recommend merging or moving one to the Appendix/SI.
- **Uniform controls & models:** Hold condition sets and evaluation depth uniform across panels rather than swapping models or controls arbitrarily without explicit explanation.

## 2. Generate & Recompile

1. Edit the figure generator script (or TikZ source) so all data come directly from locked `results/*.json` (never hardcoded synthetic curves).
2. Regenerate vector outputs (SVG/PDF) and recompile the full manuscript PDF (`tectonic` or `pdflatex`/`latexmk`) so figures are inspected at their **actual printed column/page scale**, not standalone browser preview scale.

## 3. Mandatory Rendered-PDF Visual QA

Read [references/visual-qa.md](references/visual-qa.md). Never ship a figure edit without looking at the compiled PDF page:

1. Render the relevant PDF page(s) to PNG using the helper script:
   ```bash
   python3 <skill-dir>/scripts/render_pdf_pages.py <paper.pdf> --out /tmp/fig_qa [--pages 1,4-6 | --figures] --dpi 200
   ```
2. Open **every rendered PNG** with `read_file` and audit against [references/visual-qa.md](references/visual-qa.md):
   - Print-scale font legibility (especially embedded examples, tick labels, and dual-column figures).
   - Zero overlapping titles, y-labels, tick labels, legends, bar annotations (`+`), or clipped borders.
   - Clean vertical/line spacing in TikZ cards and balanced horizontal/vertical aspect ratio (no squished tall plots or wasted margins).
   - Frameless, hierarchically grouped legends (`frameon=False`) and aligned panel headers (`A.`, `B.`, `C.`).
   - Appropriate, non-clipped real visual examples (if showing dataset/stimulus plates).
3. Fix every visual defect, re-render, and re-inspect until clean.

## 4. Titles, Captions & Terminology Sync

Read [references/captions.md](references/captions.md).
- Update figure captions in the manuscript to match every panel title, legend label, literal syntax cue (e.g., `\n -> "while"`), and standardized term used in the prose.
- If a terminology rename occurred in a figure, propagate it across prose, tables, and appendix (or run `/polish propagate`), and log substantive caption/figure edits to `notes/review_comments.jsonl`.

## Never

- Ship a figure change without inspecting the rendered manuscript PDF page image directly.
- Leave tiny illegible text in PDF print view just because a standalone HTML/SVG preview looked readable.
- Use raw script keys, undefined mathematical shorthand, or retired labels on axes, legends, or captions.
- Draw stylized or idealized curves instead of plotting locked `results/*.json` outputs.
