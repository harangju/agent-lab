# Pre-Handoff Checkers

Two independent checkers read a completed IRB packet (and experiment code, if present) with **fresh context**, so they don't inherit the drafter's blind spots. Neither checker edits any file.

## When to run them

- **Once** on every newly drafted IRB packet before handing it to the PI.
- **Once** after every review-response revision round (to catch cross-document drift introduced while answering reviewer comments).
- Skip on tiny mechanical edits like fixing a single typo.

Spawn both in parallel using fresh subagents (not forks), passing file paths rather than pasted text. If subagents are unavailable, run both checks yourself in order by re-reading the files directly.

Fill in `{irb_dir}`, `{institution_guide}`, `{consent_guide}`, and (if applicable) `{code_dir}`.

---

## Checker 1: Four-Way Sync & Code-Truth Audit

```text
You are auditing an Exempt IRB submission packet for internal consistency and factual fidelity to the live experiment. You did not write this packet.

Read:
- All markdown files in {irb_dir} (application draft, README, sources/*.md, reviews/*.md if present)
- The built Word attachments in {irb_dir}/attachments/ (extract text via python zipfile/xml if needed)
- If provided, the live experiment config and UI code in {code_dir} (e.g., experiment.yaml, workspace templates, HTML/JS files)

Compare every factual detail across all four surfaces:
1. Application draft (Sections 1, 7, 8.1, 9.3, 9.5, 10, 14, 15)
2. Consent attachment (8.2)
3. Tasks/Survey and Recruitment attachments (9.6, 14.14)
4. Live experiment config/code (if {code_dir} is given)

Check specifically for mismatches on:
- Study title, application number / placeholders, PI contact info
- Session duration (minutes) and session count
- Base pay, hourly rate, bonus math, block floor, wait-time pay, disconnect pay, payout window
- Consented N cap and pilot/main breakdown
- Eligibility and Prolific prescreening filters (age, country, language, device, approval rate, min submissions)
- Recruitment platform vs. hosting platform (e.g., Prolific vs. Qualtrics/Pairit)
- Consent wording parity across 8.1, 8.2, 9.6, and live consent screen (including opt-out button)
- Telemetry & UI behaviors present in code (tab visibility/blur/focus, mouse/dwell, audio chimes, chat, timers, localStorage, Prolific demographics, retake lock) vs. what the IRB claims is collected and NOT collected
- Survey optionality (skip / "Prefer not to answer") and open-text/chat no-PII reminders

Return a concise bullet list grouped into:
- MISMATCH (confirmed contradiction, citing both exact locations and quotes)
- UNDISCLOSED (feature in code/config missing from IRB or consent)
- PLACEHOLDER (remaining PENDING/REPLACE tokens that must be filled before submission or launch)
- OK (one-line summary of what matched)

Do not edit any file.
```

---

## Checker 2: Institutional Landmine & Policy Audit

```text
You are an IRB pre-submission compliance reviewer. You did not draft this packet.

Read:
- Institutional guide: {institution_guide}
- Consent guide: {consent_guide}
- All files in {irb_dir} (application draft, sources/*.md, attachments/*.docx text, reviews/*.md if present)

Check every institutional rule and reviewer landmine against the packet:
1. Payment => Funding: If participants are paid, is 7.1 "Currently funded" with funding PDF noted in 7.1.3, 14.11 = "Other" (not cash), exact payment/rate + no-SSN language in 14.12, and university payment-procedures confirmation in BOTH 7.2 and 14.11?
2. AI screening trap: Does Screening 1.0/1.1 match Section 9.1 and the actual study (1.1 = No unless validating/developing an AI tool)?
3. Section 15.1.0 vs 15.1.1 separation: Does 15.1.0 explicitly state concrete harms of a confidentiality breach, while 15.1.1 holds the procedural mitigations?
4. Storage parity: Does 15.8 (laptops/mobile = No) match 15.7 and 15.1.1 (no raw files stored locally)?
5. Fraud prevention: Are concrete fraud/duplicate prevention steps stated for paid online recruitment?
6. Recruitment completeness: If 14.13 = Yes, does 14.14 contain every required institutional component?
7. Open-text/chat PII warning + skip option: Are no-PII warnings present in consent AND prompts, with pre-analysis redaction in 15.1.1, and is skipping/"Prefer not to answer" enabled and cited in 15.1.1?
8. Modified scales: Are any shortened/adapted scales labeled as modified rather than full validated instruments?
9. Review-round completeness (if reviews/*.md exists): Does every reply accurately reflect an edit actually made in all affected files?
10. Privacy hygiene (only if checking a public skill/template): No leaked personal data.

Return one line per rule: PASS, WARN, or FAIL, with the exact section reference and a one-line fix for any WARN or FAIL. Do not edit any file.
```

---

## Weighing what comes back

Treat checker output as claims, not automatic edits. Verify every `MISMATCH`, `UNDISCLOSED`, or `FAIL` against the files directly, fix confirmed issues across all synchronized surfaces, rebuild `.docx` attachments, and re-run `audit_packet.py`. Summarize confirmed fixes and any rejected findings in one short **Checks** section when reporting back to the PI.
