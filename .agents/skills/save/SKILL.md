---
name: save
description: Checkpoint the session — write a log entry and update context.md
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

## 2. Rewrite `context.md`

Compact `context.md` so a fresh agent can pick up where we left off. Include:
- Current research question and framing
- Open questions and unresolved tensions
- Decided directions (and why)
- Key findings and their status (confirmed, tentative, rejected)
- What was tried and didn't work (so we don't repeat it)

Drop: resolved debates, superseded framings, dead-end details (those live in `log/`).

Add the new log file to a "Session logs" list at the bottom (create the list if it isn't there).

## 3. Propose norms (don't write them)

Skim earlier files in `log/`. If this session's PI feedback repeats a pattern that already appears in earlier logs (roughly 3 or more times in total), propose it to the PI in your reply:
- as a candidate lab norm for `../lab/references/norms.md`, or
- as a persona tweak for `../lab/references/personas.md`

Edit those files only after the PI approves. They apply across all projects, so a project-specific lesson belongs in `context.md` instead. If nothing recurs, skip this step.
