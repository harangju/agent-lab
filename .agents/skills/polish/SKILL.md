---
name: polish
description: Revise, tighten, and align an existing scholarly manuscript (LaTeX or Markdown): resolve inline % @comment or HTML @comment notes into notes/review_comments.jsonl, benchmark structure/titles/headings/tables against venue exemplars, audit standard field terminology, propagate renames across prose/figures/tables, and run a fresh PI-eye self-audit. Use when editing an existing draft, addressing review comments, tightening prose, or syncing terminology across a paper.
argument-hint: "[comments | exemplars | terminology | propagate | self-audit | file] [instructions]"
---
Revise and polish the target manuscript as requested by the user.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this `SKILL.md`. Resolve them to absolute paths in tool calls and when briefing subagents.

You are a senior scholarly editor. Unlike `/draft` (which writes first drafts from scratch), `/polish` operates on **existing manuscripts**—preserving the PI's voice and edits verbatim, benchmarking every structural choice against real venue exemplars, keeping terminology synchronized across prose/figures/tables/scripts, and recording every substantive edit in `notes/review_comments.jsonl`.

## 0. Orient First

1. **Read style rules & paper-type playbook:** Read `../draft/references/STYLE.md`, the matching genre playbook in `../draft/references/genres/` (`ml.md`, `behavioral.md`, `general-science.md`, or `management-econ.md`; combine two for hybrid venues), and the project's `notes/STYLE.md` and `AGENTS.md` (local rules win on conflicts). Apply the two highest-priority craft rules on every pass:
   - **Knit terms piece-by-piece in context:** Introduce every substantial term before it carries weight, link each new concept onto already-established terms stitch by stitch, and anchor every paragraph with a topic sentence framed in established terms (never drop cold examples or unexplained jargon).
   - **Use standard field terminology only:** Replace every ad-hoc paraphrase, colloquial substitute, or invented label with the canonical term used in the target field's cited literature—and verify that the term accurately covers every paper cited beside it.
2. **Re-read target files before every edit:** The PI frequently edits `.tex`/`.md` files directly between turns. Always preserve PI wording verbatim unless asked to revise it, and treat a PI question as a question rather than an instruction to rewrite.
3. **Resolve venue exemplars:** Check project-local `exemplars/` (or `lit/`) first, then `~/.config/agent-lab/exemplars.json` (see [references/exemplar-audit.md](references/exemplar-audit.md)).
4. **Read `CONTEXT.md`** so claims stay anchored to locked results and agreed framing.

## Modes (run one or chain as requested)

### 1. Inline `@comment` & Review-Log Loop (`comments`)
Read [references/review-loop.md](references/review-loop.md).
- Locate every `% @comment (...)` (LaTeX) or `<!-- @comment -->` (Markdown) in the target files, plus any substantive chat review feedback.
- Address each comment cleanly while keeping surrounding text intact.
- **Log before stripping:** Append one JSON line per comment/edit to `notes/review_comments.jsonl` before removing `% @comment` / `<!-- @comment -->` tags.
- **Cross-paper taste replay:** If the PI points to another project's `notes/review_comments.jsonl`, extract its recurring editorial patterns (not project-specific facts) and apply those same standards to the current manuscript.

### 2. Venue-Exemplar Alignment (`exemplars`)
Read [references/exemplar-audit.md](references/exemplar-audit.md).
- Compare the manuscript against 3–6 published papers from the target venue (abstract word cap & tense, intro opening/closing, section/subsection granularity, experimental setup layout, venue LaTeX template compliance).
- Flag concrete mismatches against the exemplars before restructuring large sections.

### 3. Knitting, Standard Terminology & Structural Craft (`terminology`, `titles`, `headings`, `tables`)
Read [references/titles-headings-tables.md](references/titles-headings-tables.md), `../draft/references/STYLE.md`, and the matching `../draft/references/genres/` playbook.
- **Knitting & clarity pass:** Verify every substantial term is defined before use, sentences build piece-by-piece in context, topic sentences skim cleanly without backward demonstratives, and non-obvious setups open with a short concrete example.
- **Standard field terminology pass:** Audit section-by-section for any non-standard, colloquial, or ad-hoc phrasing, undefined bare symbols, stacked parentheticals, or dense inline number dumps, replacing them with canonical field terms and anchored headline contrasts.
- **Titles, headings & tables pass:** Tighten paper titles, positive standard section headings, and clean non-redundant tables using the matching genre playbook and venue exemplars.

### 4. Whole-Manuscript Propagation (`propagate`)
Whenever a concept, condition, model group, or claim is renamed or reframed:
- Grep across **every surface**: all `paper/**/*.tex` (or `notes/*.md`), figure & table generator scripts (`scripts/`), captions, appendix/SI, `CONTEXT.md`, and `README.md`.
- Update retired terms everywhere in one pass; if figure/table scripts changed, regenerate outputs and hand off visual verification to `../figures/SKILL.md` (`/figures`).

### 5. Fresh PI-Eye Self-Audit (`self-audit`)
Before declaring a section or manuscript done (or when the PI asks *"review your work"* / *"read as I would read"*):
- Spawn a **fresh-context subagent** (passing only file paths: the edited sections, `../draft/references/STYLE.md`, project `notes/STYLE.md`, locked `results/*.json`, and relevant exemplar notes) tasked with hunting:
  1. Unintroduced terms, broken knitting, or cold examples;
  2. Non-sequiturs, reversed comparisons, or dropped setups;
  3. Overclaims, missing citations, or mismatches against locked JSON numbers;
  4. Leftover retired labels, bare symbols, em dashes, or gerund subjects.
- Verify every subagent finding against the actual files and locked JSONs before editing; apply confirmed fixes and log them to `notes/review_comments.jsonl`.

## 6. Post-Edit Verification

1. Run the manuscript linter:
   ```bash
   python3 <skill-dir>/../research/scripts/lint_manuscript.py <manuscript> [--bib <refs.bib>] [--results results/*.json]
   ```
2. If editing LaTeX, recompile (`tectonic` or `pdflatex`/`latexmk`) and verify zero undefined citations, broken cross-references, or overfull boxes introduced by the edit.
3. Report briefly: what changed, how many entries were logged to `notes/review_comments.jsonl`, linter/build status, and any framing calls left to the PI. Do not commit unless explicitly asked.

## Never

- Strip `% @comment` or `<!-- @comment -->` annotations before appending them to `notes/review_comments.jsonl`.
- Silently overwrite PI edits or reword untouched passages when asked to fix one span.
- Rename a key term in prose without propagating it to figures, captions, tables, and appendix.
- Hand-edit reported empirical numbers without checking locked `results/*.json`.
