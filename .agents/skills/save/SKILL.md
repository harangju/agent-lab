---
name: save
description: Checkpoint the session — write a log entry and update CONTEXT.md
disable-model-invocation: true
argument-hint: "[topic]"
---

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this SKILL.md. Resolve them to absolute paths in tool calls and when briefing subagents.

Save a checkpoint of the current session. This does three things:

## 1. Append a log entry

Create a new file in `log/` (create the directory if needed) with the filename `YYYY-MM-DD-HHmm-topic.md` (24h time, short topic slug). If the user gave a topic, use it for the slug.

Header format: `# YYYY-MM-DD HH:MM — Topic`

Include everything tried, found, argued, and decided in this session — including dead ends and dismissed ideas. Capture PI feedback:
- **Tie-breaks** — PI sided with one persona over another, and why
- **Corrections** — "the right framing is X, not Y"
- **Quality signals** — "this was exactly right"
- **Persona calibration** — "Skeptic was right but too harsh"

Log files are APPEND-ONLY. If the file already exists (continuing a topic), add a new section at the end. Never edit existing content.

## 2. Rewrite `CONTEXT.md`

Compact `CONTEXT.md` (or existing `context.md` if the project already uses lowercase) so a fresh agent can pick up where we left off. Include:
- Current research question and framing
- Open questions and unresolved tensions
- Decided directions (and why)
- Key findings and their status (confirmed, tentative, rejected)
- What was tried and didn't work (so we don't repeat it)

Drop: resolved debates, superseded framings, dead-end details (those live in `log/`).

Add the new log file to a "Session logs" list at the bottom (create the list if it isn't there).

## 3. Propose standing rules (don't write them)

Skim earlier files in `log/` and (if present) `notes/review_comments.jsonl`. If this session's PI feedback or logged manuscript edits repeat a pattern that already appears in earlier logs or review comments (roughly 3 or more times in total), propose it to the PI in your reply and route it to the file that governs that behavior:
- **Agent workflow, coding, or communication style** — the project's `AGENTS.md` / `CLAUDE.md` (or user-level agent rules if cross-project)
- **Prose, voice, or formatting rules** — the project's `STYLE.md` (or `../draft/references/STYLE.md` if cross-project)
- **Editorial, title, heading, table, or figure craft rules** — `../polish/references/` or `../figures/references/` if cross-project
- **`/lab` deliberation norms** (only for `/lab` behavior) — `../lab/references/norms.md`
- **`/lab` persona calibration** — `../lab/references/personas.md`

Edit those files only after the PI approves. A project-specific research lesson or decision belongs in `CONTEXT.md` instead. If nothing recurs, skip this step.
