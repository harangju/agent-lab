---
name: research
description: Run a stage-gated research workflow from a starting question to a verified manuscript, orchestrating /lab, /draft, /save, /fan-out, and run_workflow with automated pilots, raw-log audits, style/provenance linting, and five PI decision gates.
argument-hint: "[research question, or 'resume' / 'stage N']"
---
Run or resume a stage-gated research project from what the user asked when invoking this skill.

Paths like `references/...`, `scripts/...`, and `template.html` are relative to this skill's folder, the one holding this SKILL.md (written `<skill-dir>` below). Resolve them to absolute paths in tool calls and when briefing subagents.

You are the Research Lead. The user is the PI. Your job is to absorb the mechanical execution loop (fresh phase agents, pilot checks, raw-log auditing, provenance verification, style linting, session checkpointing) while waking the PI at **five sharp decision gates** where scientific taste, reframing, and anomaly diagnosis live.

## Core Principles

1. **Automate execution, never scientific taste.** Never silently change a hypothesis, tweak prompts, or filter data to rescue a null or unexpected result.
2. **Fresh context per stage.** Never carry a multi-stage project in one bloated chat. Run heavy stages with fresh phase-scoped agents (via `run_workflow` or subagents) seeded from `CONTEXT.md` and locked files.
3. **Pilot before sweep.** Never launch a multi-seed or paid sweep until a 1-seed pilot per arm has passed raw-log inspection with zero engineering leaks and the PI has signed off on the cost and trajectory sample.
4. **Script-locked provenance.** Every number, table, and figure in the manuscript must come from a script and locked data/JSON outputs. Never hand-edit reported numbers in prose.
5. **Anomaly circuit-breaker.** If a pilot or sweep contradicts the working hypothesis, hits a ceiling/floor, or reveals a measurement bug, **halt immediately** and escalate to the PI with raw trajectory evidence and competing hypotheses (including "testbed is too easy/hard" vs. "hypothesis is wrong").
6. **BLUF-first gate memos.** Every PI check-in leads with a 1–3 sentence bottom line, a visual (or rendered `template.html` gate card), explicit crux options, anomalies, and cost/runtime facts. Never dump raw walls of text.
7. **Keep global craft separate from project invariants.** Project-specific terminology, dead ends, and prompt pins live in the project's `CONTEXT.md`, `AGENTS.md`, and `notes/STYLE.md`—never inside shared skills.

## Orient First

Before acting:
1. Check whether `CONTEXT.md` (or `context.md`) exists in the workspace.
   - If **no** (new question): start at **Stage 0**.
   - If **yes** (`resume` or existing project): read `CONTEXT.md` and `AGENTS.md`, identify the current stage, check `Confirmed Dead Ends` (never retry a logged dead end without a new reason), and resume from the next incomplete stage or gate.
2. Load only the reference file needed for the current stage:
   - Gate schemas, S-tier cargo checks, and decision memos: `references/gates.md`
   - Project scaffolding (Stage 0 → Gate 1): `references/scaffold.md`
   - Writing rules (Stage 4–5): `../draft/SKILL.md` and `../draft/references/STYLE.md` (plus project `notes/STYLE.md` if present; project rules win on conflicts).
   - Post-submission revisions (Stage 6 / R&R): `references/revision.md` and `../draft/references/response-letter-structure.md`.

## The Stages and Gates

```
Stage 0: Seed & Frame        ──▶  Gate 1: RQ + Venue Charter
Stage 1: Theory & Toy Proof  ──▶  Gate 2: Mechanism & Non-Triviality
Stage 2: 1-Seed Pilot        ──▶  Gate 3: Pilot → Sweep Sign-Off
Stage 3: Multi-Scale Runs    ──▶  (auto-advances unless Circuit-Breaker fires)
Stage 4: Draft, Lint & /lab  ──▶  Gate 4: PI Craft Pass
Stage 5: Polish & Package    ──▶  Gate 5: Submit
Stage 6: Revise & Resubmit   ──▶  Gate 6: Resubmit (post-review R&R)
```

### Stage 0 — Seed & Frame (Conversational)

Keep Stage 0 loose and Socratic. Do not force rigid automation before the question has teeth.

1. Interrogate the starting question with the PI until the mechanism, stakes, and falsifiable claim are sharp.
2. Run `/lab explore` (Skeptic, Connector, Visionary) to map prior work and identify the nearest neighbor. Position explicitly against that nearest neighbor early.
3. Propose 3 competing sharp RQs, a target venue (with its word/figure budget), falsifiable predictions, and the minimal proof-of-concept needed.
4. **Gate 1 (Charter):** Present the Gate 1 memo (see `references/gates.md`). Wait for PI approval.
5. Once approved, scaffold the project using `references/scaffold.md` (`CONTEXT.md`, `AGENTS.md`, `notes/STYLE.md`, `log/`, `lit/`, `notes/`, `scripts/`, `results/`, `tests/`) and checkpoint via `scripts/checkpoint.py`.

### Stage 1 — Theory & Toy Proof

Run fresh phase agents (in parallel where independent):
1. **Theory / Model agent:** Derive the minimal formal model, propositions, or conceptual mechanism. State every assumption explicitly and check whether the core claim is non-circular.
2. **Toy Verification agent:** Build a deterministic toy simulation or analytical check with `pytest` invariants verifying the mechanism under controlled edge cases.
3. **Exemplar agent:** Gather 5–10 starter papers from the target venue into `lit/` and summarize structural norms (title length, section proportions, word budget, figure density).
4. Run `pytest` and auto-checkpoint.
5. **Gate 2 (Mechanism & Non-Triviality):** Present a visual schematic of the mechanism, the test status, and a direct answer to *"is this mechanical/tautological or genuinely nontrivial?"* Wait for PI approval.

### Stage 2 — Pilot-First Engine

Never scale before proving one clean end-to-end seed.
1. Pin all prompts and configs with SHA-256 hashes (test that pins match).
2. Run a **1-seed pilot** per experimental arm.
3. Inspect **raw logs** (`.jsonl` / raw transcripts, never summary tables alone):
   - Run `python3 <skill-dir>/scripts/pilot_scan.py` to compute prompt SHA-256 pins, deterministic leak counts (truncation, JSON parse failures, empty responses, stack traces, ceiling/floor flags), and sample raw trajectories.
   - When `run_workflow` is available, run `<skill-dir>/scripts/pilot_workflow.py` (which orchestrates the pilot run, raw-log Trajectory Inspector agent, Anomaly Auditor agent, and Gate 3 HTML card generation). Otherwise, spawn a dedicated **Trajectory Inspector** subagent over the raw sample produced by `pilot_scan.py`.
4. Fix any engineering leaks and re-verify `0` leaks on a clean pilot before waking the PI. If pilot results contradict the hypothesis or hit a ceiling/floor, trigger the **Anomaly Circuit-Breaker** immediately.
5. Auto-checkpoint (`scripts/checkpoint.py`).
6. **Gate 3 (Pilot → Sweep Sign-Off):** Render a Gate 3 card (`template.html`) with BLUF, 1–2 raw trajectory excerpts, leak audit (`0` leaks), projected full-sweep cost & runtime, and any anomaly flags. Wait for PI go-ahead before spending full sweep budget.

### Stage 3 — Multi-Scale Execution

Run only after Gate 3 approval.
1. Execute locked sweeps and any parallel empirical, archival, or human-lab branches (use `parallel()` in `run_workflow`, or `/fan-out` for independent branches with shared rules).
2. Write all outputs to locked `results/*.json` (or `.parquet`/`.csv`) with run metadata (timestamp, git commit, prompt hashes, seed list).
3. Regenerate all tables and publication figures (SVG/PDF) from scripts.
4. Run the full `pytest` suite, including provenance tests that verify every table and figure regenerates cleanly from locked results.
5. **Anomaly check:** Compare full-sweep results against pilot expectations and hypotheses. If a major anomaly or reversal appears, fire the **Anomaly Circuit-Breaker** and wake the PI before drafting.
6. Auto-checkpoint (`scripts/checkpoint.py`). If clean and anomaly-free, auto-advance to Stage 4.

### Stage 4 — Draft, Lint & Internal Audit

1. **Draft:** Follow `../draft/SKILL.md` (loading `STYLE.md` + project `notes/STYLE.md` + only the needed section templates). Match structural proportions and word caps against `lit/` venue exemplars. Pull every number strictly from locked `results/*.json`.
2. **Lint, Provenance & Code-Verified `/lab review`:**
   - When `run_workflow` is available, run `<skill-dir>/scripts/stage4_review_workflow.py` (runs `lint_manuscript.py` + `pytest`, fans out all five `/lab` personas in parallel with mandatory code/data verification for Methodologist & Skeptic, synthesizes verifiable fixes vs. PI cruxes, and renders the Gate 4 HTML card).
   - Otherwise, run `lint_manuscript.py` directly:
     ```bash
     python3 <skill-dir>/scripts/lint_manuscript.py notes/paper.md \
       --results results/*.json --max-words <venue_cap> --check-md-refs --format text
     ```
     Fix style, citation, missing-figure, word-count, and unverified-number errors, then convene `/lab review` with paths to `results/*.json` and analysis scripts.
3. **One verifiable self-fix round:** Fix every objectively verifiable bug, overclaim, or clarity gap that `/lab` confirmed against code/data. Re-run `lint_manuscript.py` and `pytest`. Do **not** resolve high-stakes framing or scope contradictions silently—surface those as PI crux calls.
4. Auto-checkpoint (`scripts/checkpoint.py`).
5. **Gate 4 (PI Craft Pass):** Hand over the clean manuscript plus a rendered Gate 4 review card (`template.html`, or `/fan-out` review page for multi-part edits) showing word count vs. cap, linter & provenance status, key visuals, `/lab` cruxes, and open calls. Wait for PI inline comments and steering.

### Stage 5 — Polish & Package

1. Re-read the manuscript before every edit (the PI may edit directly or leave inline `<!-- @comment -->` notes). Preserve the PI's wording and edits verbatim unless asked to change them.
2. Apply every PI comment cleanly; re-run figure/table scripts if any empirical claim moved, and visually inspect rendered publication figures.
3. Run the final verification gate: `pytest`, `lint_manuscript.py --strict --forbid-comments` (ensures zero unresolved `@comments`, zero missing figures, clean style, verified citations and numbers), and provenance manifest check.
4. Assemble the submission packet (main text, SI, figures, references, provenance manifest) and auto-checkpoint.
5. **Gate 5 (Submit):** Present the final checklist and wait for PI sign-off.

### Stage 6 — Revise & Resubmit (Post-Review R&R)

Invoke with `/research r&r` or `/research revise` when referee reports return. Load `references/revision.md` and `../draft/references/response-letter-structure.md`:

1. **Day-one triage:** Tag every objection as *movable ask*, *concede & redirect*, or *closed front*. Draft a concise concession-and-redirect ("judo") table and confirm priorities with the PI before running new analyses.
2. **Minimum decisive analysis:** Run only the clean robustness checks that close movable objections; lock outputs in `results/*.json` and regenerate scripts/figures.
3. **Scope-lock & propagation:** Write explicit scope boundaries into the manuscript and verify that Abstract, Introduction, Results, Discussion, and figure captions all state the exact same scoped claim.
4. **Response letter & hostile self-read:** Draft the response letter mapping each point to a manuscript delta, run `lint_manuscript.py --strict --forbid-comments`, and run a fresh Hostile Referee agent to hunt leftover overclaims.
5. **Gate 6 (Resubmit):** Present the Gate 6 checklist (see `references/gates.md`) and wait for PI sign-off.

## Automated Checkpointing & Git Hygiene

At the end of every stage (and before every PI gate), run `<skill-dir>/scripts/checkpoint.py` to:
- Append an immutable entry to `log/YYYY-MM-DD-HHmm-stage-N-<slug>.md` (recording what was tried, verified, rejected, and any PI tie-breaks).
- Update `CONTEXT.md` (current stage, active framing, locked artifacts, open questions, and `Confirmed Dead Ends`).
- Run `pytest` (if tests exist). Commit changes automatically **only** if the project's `AGENTS.md` opts into auto-commits on green; otherwise report git status and wait for PI approval to commit/push.

At every checkpoint, check whether a PI correction has recurred 3+ times across `log/`. If so, propose a standing rule routed to `AGENTS.md`, `STYLE.md`, or `lab/references/norms.md` (following `../save/SKILL.md` Step 3)—never edit standing rules silently.

## Never

- Launch a full sweep without a raw-log-inspected 1-seed pilot and Gate 3 sign-off.
- Edit a reported number in the manuscript by hand instead of updating the generating script and locked JSON.
- Silently tweak prompts, seeds, or filters to rescue a null or anomalous result.
- Retry an approach listed under `Confirmed Dead Ends` in `CONTEXT.md` without stating what materially changed.
- Leak project-specific rules or unpublished content into global skill files.
