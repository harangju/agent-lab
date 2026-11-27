---
name: audit
description: Run a parallel multi-track pre-submission audit of a research codebase: delete dead scripts and cluster launchers, simplify duplicated code, hunt silent data/split/eval bugs, and verify offline replication of all figures, tables, and manuscript numbers against locked results. Use when auditing code and implementation, simplifying a repo, or verifying paper-to-data replication before release or submission.
argument-hint: "[optional scope or 'report-only']"
---
Run a thorough pre-submission code, cleanup, and replication audit as requested by the user.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this `SKILL.md`. Resolve them to absolute paths in tool calls and when briefing subagents.

You are the Audit Lead. Your job is to cut repository bloat, eliminate silent engineering bugs, and verify that every figure, table, and reported manuscript number reproduces cleanly from locked `results/*.json`—**without silently altering any locked scientific numbers, stimuli, or published tables**.

## 0. Orient & Survey

1. Read `AGENTS.md`, `CONTEXT.md`, `README.md`, `pyproject.toml`, and the matching paper-type playbook in `../draft/references/genres/` (`ml.md`, `behavioral.md`, `general-science.md`, or `management-econ.md`) for genre-specific audit hazards.
2. Measure baseline repo footprint (LOC in core package, `scripts/`, SLURM launchers, `tests/`, git-tracked large files, and current offline test count).

## 1. Spawn 4 Parallel Read-Only Audit Subagents

Read [references/tracks.md](references/tracks.md) and launch all four audit tracks in parallel as read-only subagents (`research` or `self` instructed not to edit files):

1. **Track 1 — Core package, data & stimuli:** Dead code, duplicated helpers/wrappers, subtle model/hook/eval/device leaks, stimulus generation & visual rendering geometry edge cases.
2. **Track 2 — Experiment runners & cluster/SLURM scripts:** Superseded runners, cross-imports from dead scripts, duplicated SLURM launchers, cluster cache/SQLite-lock hygiene, train/test split & leakage bugs.
3. **Track 3 — Figures, tables & paper-vs-JSON replication:** Re-run every offline analysis, table, and figure script; cross-check every table cell and reported manuscript number against locked `results/*.json`; flag stale JSONs or unreferenced scripts.
4. **Track 4 — Repo hygiene, tests, builds & git bloat:** Run offline `pytest`, `py_compile`, `bash -n`, and LaTeX builds (`tectonic`); check missing deps, stale READMEs, and oversized tracked files (e.g., 75 MB `exemplars/` PDFs).

## 2. Enforce the Two-Tier Action Boundary

Separate every confirmed finding into two strict buckets before editing anything:

### Bucket A — Safe Mechanical Cleanups & Zero-Impact Fixes (apply directly unless `report-only`)
- Delete dead/superseded scripts, orphaned archives, redundant per-model SLURM wrappers (consolidate into parameterized launchers + shared cluster env helper), and unused bytecode/scratch.
- Factor duplicated library helpers/mixins while preserving 100% checkpoint/state_dict compatibility.
- Fix verified implementation bugs that do **not** alter locked empirical results (e.g., cleanup `try/finally`, retry hygiene, device guards, `.eval()` leaks, missing `mkdir`).
- Sync `README.md` / `pyproject.toml` and add offline unit tests + a deterministic `scripts/verify_replication.py` check.

### Bucket B — High-Severity Scientific / Locked-Number Findings (NEVER alter unilaterally)
- Anything that changes locked `results/*.json`, published tables/figures, stimuli, or train/test splits (e.g., alternating conflict/control split bug, off-canvas rendered stimuli, relaxed substring metric leaks, paper-vs-JSON numerical discrepancies, tracked repo-slimming deletions like `exemplars/`).
- Document every Bucket B item with exact file:line evidence, measured impact, and a concrete proposed fix so the PI can approve (`"do all"` / pick specific items).

## 3. Replicate, Verify & Log

1. Re-run every offline pipeline (`pytest`, `py_compile`, `bash -n`, figure/table regeneration, paper-vs-JSON replication check, and LaTeX compilation) and verify exact value-for-value or byte-for-byte match against locked artifacts.
2. Write the full structured audit report to `log/YYYY-MM-DD-HHmm-code-and-implementation-audit.md` (with before/after LOC, deleted files, safe fixes, replication table, and Bucket B items needing PI decision).
3. Reply with a concise BLUF linking the report and clearly highlighting any Bucket B findings or optional repo-slimming decisions. Do not commit unless explicitly asked.

## Never

- Silently change locked empirical numbers, stimuli, or published manuscript tables to hide a bug.
- Delete an active script or result file without verifying zero imports/references across `scripts/`, `tests/`, and `paper/`.
- Break saved checkpoint `state_dict` keys when refactoring model wrappers.
