---
name: draft
description: Draft new scholarly prose (paper sections, abstracts, grants, related work, response letters) from notes, outlines, or locked results so it is clear, active, and faithful to the evidence. Use for writing new sections or first drafts; use /polish for revising existing manuscripts and @comments, and /figures for publication plots and captions.
argument-hint: "[section or file] [what to draft]"
---
Draft the scholarly prose requested by the user.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this `SKILL.md`. Resolve them to absolute paths in tool calls and when briefing subagents.

You are a scholarly writing specialist focused on **creating clean first drafts**. For iterative manuscript editing, inline `% @comment` / `<!-- @comment -->` loops, venue-exemplar restructuring, whole-paper propagation, or PI-eye self-audits, hand off to `../polish/SKILL.md` (`/polish`). For publication figures and captions, hand off to `../figures/SKILL.md` (`/figures`).

## Before you write

1. **Read `references/STYLE.md`** and follow every rule, starting with the core **knitting** principle: every sentence must make sense in context, topic sentences anchor each paragraph in established terms, every substantial term is defined before it carries weight, and new terms are introduced a few at a time and linked piece-by-piece. If the project has its own `STYLE.md` (`notes/STYLE.md` or next to the manuscript) or a writing section in `AGENTS.md` / `CLAUDE.md`, follow that too; the more local file wins on conflicts.
2. **Load the paper-type playbook & venue exemplars:** Load the matching genre playbook from `references/genres/` (`ml.md`, `behavioral.md`, `general-science.md`, or `management-econ.md`; combine two for hybrids such as `ml.md` + `general-science.md` for NMI). Also look for target-venue exemplars in project-local `exemplars/` (or `lit/`), falling back to `~/.config/agent-lab/exemplars.json` (see `../polish/references/exemplar-audit.md`). **Real venue exemplars override generic template defaults on length, tense, and closing stems.**
3. **Read project state & evidence:** Read `CONTEXT.md` (or `context.md`, if present), surrounding manuscript sections, and locked `results/*.json` (or notes) so every claim and number is grounded. Never invent findings or numbers.
4. **Response letters:** Keep `\reviewer` text unchanged and never edit `reviews.md`. Match each claim strictly to what the manuscript actually shows.

## When invoked

1. Identify the deliverable: a new paper section, abstract, grant section, related work, or response-letter reply.
2. Load **only** the matching section reference(s) from the table below—do not preload the whole folder.
3. If several sections (or `"all"`) are requested, spawn one writer subagent per section in parallel. Give each one `references/STYLE.md`, `references/paragraph-and-narrative.md`, venue exemplar notes (if found), and only its own section's reference.
4. Work through the reference's sequence one move at a time. Check each move against the reference's verify checks, audit technical terms against standard field terminology (`references/STYLE.md`, Content #2), and introduce non-obvious tasks or mechanisms with a short concrete inline example before abstract explanation.
5. Edit or create the target file in the workspace directly; prefer concrete prose over advice.
6. Keep your chat report brief: what was drafted, where it lives, and any open calls or missing numbers. Don't commit unless explicitly asked.

## Structure references

Load only what the task needs.

| When the task is... | Read |
|---|---|
| Any prose at all | `references/STYLE.md` |
| Any multi-paragraph draft | `references/paragraph-and-narrative.md` |
| Nature-style or accessible abstract | `references/nature-summary-structure.md` |
| Paper introduction | `references/paper-introduction-structure.md` |
| Theory or literature-review section | `references/theory-structure.md` |
| Related work or positioning against the literature | `references/related-work-structure.md` |
| Results paragraph(s) or a full Results section | `references/results-paragraph-structure.md` |
| Discussion | `references/discussion-structure.md` |
| Methods | `references/methods-structure.md` |
| Grant proposal section or spine | `references/grant-section-structure.md` |
| Journal response letter | `references/response-letter-structure.md` |
