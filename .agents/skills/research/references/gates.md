# Gate Schemas and Decision Memos

Every PI wake-up uses a compact, scannable format: **BLUF (1–3 sentences)**, **one visual** (diagram, chart, or rendered `template.html` card), **explicit crux options**, **anomalies**, and **verification status**.

When running inside `run_workflow`, require every gate-producing agent to return JSON matching the schema below so verbose prose never leaks into the PI brief.

---

## Shared Gate JSON Schema

```json
{
  "type": "object",
  "required": ["gate", "bluf", "checks", "crux_options", "anomalies", "recommendation"],
  "properties": {
    "gate": { "type": "string" },
    "bluf": { "type": "string", "description": "At most 3 plain sentences." },
    "visual_path": { "type": ["string", "null"] },
    "cost_usd_est": { "type": ["number", "null"] },
    "runtime_min_est": { "type": ["number", "null"] },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "status", "detail"],
        "properties": {
          "name": { "type": "string" },
          "status": { "type": "string", "enum": ["pass", "warn", "fail", "not_run"] },
          "detail": { "type": "string" }
        }
      }
    },
    "anomalies": { "type": "array", "items": { "type": "string" } },
    "crux_options": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "tradeoff"],
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "tradeoff": { "type": "string" }
        }
      }
    },
    "recommendation": { "type": "string" }
  }
}
```

---

## Gate 1 — RQ + Venue Charter (End of Stage 0)

**Purpose:** Lock the question, nearest-neighbor differentiation, target venue, and falsifiable claim before writing code or running sweeps.

**Deliverables:**
- **3 competing sharp RQs** (one recommended, with why it beats the other two).
- **Nearest-neighbor check:** 1–3 closest papers, what they already show, and the exact gap this project owns.
- **Target venue & constraints:** journal/conference, word limit, figure cap, expected evidence bar.
- **Falsifiable cargo (anti-hook-only test):** an intuitive hook is not enough—state the non-obvious, quantified, falsifiable cargo (law, crossover, mechanism separation, or benchmark win) that cannot be guessed from the hook alone, plus what outcome would *disprove* it.
- **Minimal PoC & release plan:** Stage 1 toy model, Stage 2 1-seed pilot design, and what reusable artifact (code, dataset, benchmark, protocol) others can build on.

**PI decision:** Approve charter (locks Stage 0 → scaffolds repo), redirect framing, or kill early.

---

## Gate 2 — Mechanism & Non-Triviality (End of Stage 1)

**Purpose:** Confirm the mechanism is coherent, non-circular, and worth spending compute/data effort on.

**Deliverables:**
- **Mechanism visual:** one clean diagram or toy simulation curve from actual code output.
- **Non-triviality check:** direct answer to *"is this mechanical/tautological, or does it produce a genuine surprise?"*
- **Assumptions & generalization ledger:** load-bearing assumptions and which ones Stage 2/3 will relax or test. For scaling or universality claims, verify the Stage 3 plan spans >= 3 distinct model families/settings and avoids self-generated benchmarks judged solely by same-family models.
- **Exemplar benchmark:** target lengths, section shares, and figure density from `lit/`.
- **Tests:** deterministic `pytest` suite passing.

**PI decision:** Proceed to Stage 2 pilot, tighten assumptions/model, or reframe.

---

## Gate 3 — Pilot → Sweep Sign-Off (End of Stage 2)

**Purpose:** Prevent wasted sweeps and catch instrumentation bugs on 1 seed before scaling.

**Deliverables (render with `template.html`):**
- **BLUF:** did the 1-seed pilot work cleanly, and what did the signal look like?
- **Leak audit (`pilot_scan.py` + Trajectory Inspector):** truncation count, JSON/schema parse errors, empty outputs, prompt leaks, tool failures (must be `0` engineering leaks).
- **Raw trajectory sample:** 1–2 verbatim excerpts from actual `.jsonl` logs showing the behavior in the wild.
- **Prompt/config pins:** SHA-256 hashes verified by tests.
- **Budget & runtime projection:** exact pilot cost/time scaled by `sweep_multiplier` (`N` seeds × `K` arms).
- **Ceiling / floor / anomaly flags:** explicit check on whether the task is too easy, too hard, or contradicting the hypothesis.

**PI decision:** Approve full sweep, adjust testbed difficulty/design, or halt.

---

## Gate 4 — PI Craft Pass (End of Stage 4)

**Purpose:** Hand the PI a clean, linted, provenance-verified, `/lab`-audited draft so PI attention goes strictly to scientific craft and narrative.

**Deliverables (render with `template.html` or `/fan-out` review page):**
- **Manuscript link** (ready for direct editing / inline `@comments`).
- **Verification ledger:**
  - `lint_manuscript.py`: 0 errors (style, citations, word count vs. venue cap, unverified numbers).
  - `pytest` + provenance regeneration: passing.
  - Code-verified `/lab review`: list of confirmed bugs already fixed vs. unresolved cruxes.
- **Key visuals:** current publication figures next to headline claims.
- **Needs PI call:** only unresolved framing, scope, or persona contradictions.

**PI decision:** Leave inline comments / tie-break cruxes → Stage 5 polish.

---

## Gate 5 — Submit (End of Stage 5)

**Purpose:** Final verification before submission or release.

**Deliverables:**
- Submission packet manifest (main text PDF/TeX, SI, vector figures, verified `.bib`, provenance manifest).
- `/figures` visual QA pass on the compiled PDF (legible print-scale fonts, zero overlaps, synced labels).
- `/refs` primary-source bibliography & in-text citation audit (0 factual/author/venue errors, 0 mis-citations).
- `/audit` pre-submission code cleanup & paper-vs-JSON replication audit (all offline tests & tables exact, Bucket B items resolved).
- Final `pytest` + `lint_manuscript.py --strict --forbid-comments` pass (0 unresolved `% @comment` / `<!-- @comment -->`, 0 missing figures).
- Clean git diff / release tag confirmation.

---

## Gate 6 — Resubmit (End of Stage 6 / R&R)

**Purpose:** Final verification before sending a revised manuscript and response letter back to referees.

**Deliverables:**
- Concession-and-redirect summary: every conceded point is explicit in both the response letter and manuscript.
- Scope-propagation check: Abstract, Introduction, Results, Discussion, and figure captions state the exact same scoped claim.
- Reviewer-delta map: every major objection maps to a visible change (`§Z` / `Fig. N`) without opening new attack surfaces.
- Hostile self-read verdict + `pytest` + `lint_manuscript.py --strict --forbid-comments` pass.

---

## Anomaly Circuit-Breaker Memo (Any Stage)

Fire immediately whenever a pilot or sweep:
- contradicts the working hypothesis on a core prediction,
- hits a ceiling or floor (>95% or <5% on a key metric), or
- shows unexplained variance or instrumentation drift across arms/models.

**Required sections:**
1. **What happened** (exact numbers + locked file path).
2. **Raw trajectory evidence** (verbatim excerpt from logs—never a paraphrase alone).
3. **Competing explanations** (always include at least: (a) engineering/measurement artifact, (b) testbed difficulty/regime mismatch, (c) the hypothesis is wrong or scoped differently).
4. **Proposed diagnostic** (a cheap 1-seed test to separate the explanations).

Do **not** proceed to the next stage or modify prompts/filters until the PI chooses a branch.
