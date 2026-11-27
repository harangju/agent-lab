# Project Scaffold Templates (Gate 1)

When Gate 1 is approved on a new research question, create the minimal directory structure and starter files below (skipping any file that already exists).

## Directory Layout

```
<project>/
├── AGENTS.md                   # Project operational invariants
├── CONTEXT.md                  # Living state (stage, charter, locked outputs, dead ends)
├── log/                        # Append-only checkpoint logs (YYYY-MM-DD-HHmm-topic.md)
├── lit/                        # Nearest-neighbor notes (keep large exemplar PDFs outside git via ~/.config/agent-lab/exemplars.json)
├── notes/
│   ├── STYLE.md                # Project-specific terminology & voice overrides
│   └── review_comments.jsonl   # Append-only log of resolved % @comment / chat editorial edits
├── paper/                      # Modular LaTeX manuscript (main.tex, sections/*.tex, ref.bib, tables/, figures/)
│                               # (or notes/paper.md for Markdown-first drafts)
├── scripts/                    # Analysis, simulation, table & figure generators + verify_replication.py
├── results/                    # Locked JSON / parquet / CSV outputs + provenance manifests
└── tests/                      # Deterministic model invariants, prompt pins, provenance tests
```

---

## Starter `CONTEXT.md`

```markdown
# Project Context

**Stage:** Stage 1 (Theory & Toy Proof)
**Target venue:** <venue> (cap: <N> words, <M> figures)
**Last updated:** YYYY-MM-DD

## Research Question & Framing
- **Core RQ:** <1-sentence sharp question>
- **Falsifiable prediction:** <what confirms vs. disproves it>
- **Nearest neighbor:** <Author (Year)> — how we differ in one line.

## Decided Directions
- <Gate 1 charter decisions and rationale>

## Locked Artifacts
- None yet.

## Open Questions
- <Key unknowns for the current stage>

## Confirmed Dead Ends
*(Never retry these without stating what materially changed.)*
- None yet.

## Session Logs
- `log/YYYY-MM-DD-HHmm-gate1-charter.md`
```

---

## Starter `AGENTS.md`

```markdown
# AGENTS.md

Project-level operational rules for all agents working in this repository.

## Communication
- Lead every update and gate memo with a 1–3 sentence BLUF.
- Show visuals, tables, or raw excerpts before long prose explanations.
- Never dump walls of text; surface only decisions, anomalies, and verified facts.

## Experimental Discipline
- **1-seed pilot before scaling:** Never launch a multi-seed or paid sweep before validating 1 seed per arm, inspecting raw logs directly, and receiving PI Gate 3 sign-off.
- **Diagnose raw logs first:** Inspect raw `.jsonl` / trajectory outputs before proposing fixes or interpretations.
- **Pin prompts and configs:** Lock prompt templates and run configs with SHA-256 hashes tested in `tests/`.
- **Anomaly circuit-breaker:** If results contradict the hypothesis or hit a ceiling/floor, stop and escalate with raw evidence. Never silently tweak prompts or filters to rescue an effect.

## Manuscript & Provenance
- **No hand-edited numbers:** Every reported statistic, table, and figure must be generated from scripts reading locked `results/` outputs.
- **Follow `notes/STYLE.md`:** Project style rules override global defaults on conflicts.
- **Review comments log:** Whenever addressing inline `% @comment (...)` / `<!-- @comment -->` annotations or substantive chat review feedback, append each edit to `notes/review_comments.jsonl` before stripping comment tags.
- **Git hygiene:** Auto-commit on green at stage boundaries: `false` (flip to `true` only if the PI opts in). Keep heavy reference PDFs out of git (use `~/.config/agent-lab/exemplars.json` instead).
```

---

## Starter `notes/STYLE.md`

```markdown
# Project Style Guide (`notes/STYLE.md`)

Project-specific terminology and prose rules. Extends global `draft/references/STYLE.md` and wins on conflicts.

## Terminology
- Preferred terms: <add canonical project terms here>
- Avoid: <add jargon, internal variable names, or CLI flags banned from main text>

## Venue Budget
- Main text cap: <N> words (excluding references and figure captions)
- Figures: <= <M>
- References: <= <R>

## Linter Config (`lint_manuscript.py`)
Create `notes/lint.json` if you want project-specific banned regexes or word caps enforced automatically:
```json
{
  "max_words": 4500,
  "banned_terms": [],
  "ambiguous_verbs": ["splits", "breaks", "cuts", "spreads", "partitions"]
}
```
```
