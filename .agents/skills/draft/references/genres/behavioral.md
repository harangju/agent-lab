# Paper-Type Playbook: Behavioral & Human-Subjects Experiments

Load alongside `../STYLE.md` for online or lab behavioral studies (*Nature Human Behaviour*, *PNAS*, *Science*, *Psychological Science*, *Management Science* behavioral track, *JMR*). Combine with `general-science.md` for general-interest science journals.

## Structure & Headings
- **Escalating study arc:** Organize multi-study papers so each study answers one clean question left open by the last (e.g., *Study 1: Main Behavioral Effect* → *Study 2: Mechanism / Process* → *Study 3: Robustness or Incentive-Compatible Field/Extension*).
- **Preregistration & ethics clarity:** State preregistration status, IRB exemption/approval, recruitment platform, sample size determination (power analysis), and exclusion criteria transparently in Methods (and summarize sample size briefly in Results).
- **Confirmatory vs. exploratory boundary:** Clearly separate preregistered primary tests from post-hoc exploratory analyses without sounding defensive.

## Prose & Terminology Micro-Rules
- **Plain-English condition names:** Refer to experimental arms by intuitive descriptive labels (*advice-first*, *independent-then-revise*, *transparent AI*) rather than internal survey/config codes (`arm_b_delay`, `cond_2`).
- **Concrete actors:** Write `participants chose`, `raters judged`, `teams allocated` rather than passive `subjects were exposed to` or `responses were elicited`.
- **Honest scale labeling:** Never label a questionnaire as a full validated scale (e.g., `"NASA-TLX"`) if items, wording, or response anchors were modified; call it a modified or adapted measure.
- **Readable statistics in prose:** Anchor prose claims with plain-language effect sizes, baseline means, and exact contrasts (e.g., *"increased accuracy by 11.4 percentage points, from 61.2% to 72.6%, 95% CI [7.1, 15.7], p < 0.001"*); delegate full regression/ANOVA models and secondary covariates to tables or SI.

## Tables & Figures Micro-Rules
- **Show what participants actually saw:** Include a clean Figure 1 task/stimulus schematic or verbatim trial screenshot so any reader immediately understands the interface, decision, and incentive structure.
- **Transparent uncertainty & distributions:** Show condition means with 95% CIs (and underlying distributions, jittered points, or rainclouds where clean) plus exact cell sample sizes (`n` per arm) in the caption or axis label.
- **Sample & balance reporting:** Provide a concise sample-characteristics and randomization-balance table (main text or SI) documenting recruitment, exclusions, and attrition across arms.

## Code, Data & IRB Audit Hazards
- **Randomization & attrition checks:** Verify random assignment actually balanced across arms, check for differential dropout/attrition by treatment, and verify exclusion counts match preregistered comprehension/attention rules exactly.
- **Repeated-measures inference:** Confirm standard errors are clustered at the participant (or group/session) level whenever participants complete multiple trials or interact in groups—never treat within-person trials as independent observations.
- **Code ↔ IRB ↔ Manuscript parity:** Verify pay rates, bonus formulas, task timing, telemetry/logging, opt-out controls, and debrief wording match across the live experiment config (`experiment.yaml` / Qualtrics / HTML), the approved IRB packet, and the Methods section verbatim.
- **Data hygiene:** Confirm retake/duplicate-worker locks, timezone/timestamp handling, and zero PII leakage in committed analysis datasets.
