# Stage 6 — Revise & Resubmit (R&R) Playbook

Operating rules when a manuscript returns with peer-review reports (`/research r&r` or `/research revise`). The goal is **acceptance on this round**, not an abstractly bigger paper.

## Core Principles

1. **Optimize for acceptance, not sparring.** Judge every new analysis, edit, and paragraph by whether it raises the probability of acceptance on this round.
2. **Do not open new attack surfaces.** Fix what reviewers asked; do not volunteer new claims, datasets, or unasked mechanisms that invite fresh objections.
3. **Concede and redirect ("judo").** When a reviewer hits a point the evidence cannot fully defend (such as a pure identification claim), concede that narrow point plainly, preserve the empirical finding, and redirect to what the evidence actually establishes. Make their critique look like it sharpened the paper.
4. **Engineer the score floor, not the mean.** Acceptance requires no reviewer remaining below threshold. Prioritize movable objections from borderline/pivot reviewers over debating immovable critics.

## R&R Execution Sequence

### 1. Day-One Triage Table
Tag every major reviewer objection before writing code or prose:
- **Movable ask:** concrete analysis, robustness check, or clarification that can flip a score. Put effort here.
- **Concede & redirect:** framing or identification overreach that cannot be won by arguing. Shrink the claim cleanly and keep the finding.
- **Closed front:** areas reviewers did not challenge. Leave untouched.

Present the triage and concession-redirect table to the PI for quick approval before launching new analyses.

### 2. Minimum Decisive Analysis
- Prefer one clean robustness check that closes an objection over a sprawling battery that raises new questions.
- Lock all new outputs in `results/*.json`, regenerate figures/tables from scripts, and verify with `pytest`.

### 3. Scope-Lock & Propagation
- Write an explicit "what we claim / what we do not claim" scope lock directly into the manuscript (not only in the response letter).
- **Propagate every scope shrink everywhere:** Abstract, Introduction punchline, Results headlines, Discussion, and figure captions must match the revised claim. A leftover overclaim in the Abstract is a free reject point.

### 4. Response Letter Craft
Follow `../../draft/references/response-letter-structure.md`:
- Map every reply to a concrete manuscript delta: *Reviewer asked X → we did Y → see §Z / Fig. N*.
- Credit the reviewer as co-author of the improvement (*"Following Reviewer 2, we now distinguish..."*).
- Keep tone grateful, precise, and short—no sarcasm, no "the reviewer misunderstood," no multi-page philosophy.

### 5. Hostile Self-Read & Gate 6 (Resubmit)
Before waking the PI for Gate 6:
- Run `lint_manuscript.py --strict --forbid-comments` on the revised manuscript.
- Run a fresh **Hostile Referee** agent reading the revised manuscript as someone trying to reject it—hunting leftover overclaims, unpropagated scope shrinks, or new unverified numbers.
- Verify the Gate 6 checklist:
  - [ ] Conceded points are explicit in both the response letter and manuscript.
  - [ ] The kept finding is sharper, not watered down.
  - [ ] No new claim appears without dedicated evidence.
  - [ ] Abstract, Introduction, Results, and Discussion state the exact same scoped claim.
  - [ ] Every major reviewer comment maps to a visible change with a section/figure pointer.
  - [ ] Zero unresolved inline `@comments` and all figures/numbers pass provenance checks.
