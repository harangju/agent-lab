---
name: save
description: Checkpoint the session — write a log entry and update context.md
---

Save a checkpoint of the current session. This does two things:

## 1. Append a log entry

Create a new file in `log/` with the filename `YYYY-MM-DD-HHmm-topic.md` (24h time, short topic slug). If $ARGUMENTS includes a topic, use it for the slug.

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

Add the new log file to the session logs list at the bottom.
