---
name: irb
description: Draft, sync, revise, stamp, or closeout Exempt human-subjects IRB packets for online behavioral and survey studies (e.g., Prolific with Qualtrics or Pairit). Use when creating a new IRB application, generating consent/recruitment/task Word attachments, syncing or auditing an experiment codebase against an IRB packet, answering IRB reviewer feedback, stamping an assigned IRB number, or logging an approval determination.
argument-hint: "[draft | sync | revise | stamp | closeout] [study or irb path]"
---
Draft, sync, revise, stamp, or closeout an Exempt IRB packet, as requested when invoking this skill.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this `SKILL.md` (written `<skill-dir>` below). Resolve them to absolute paths in tool calls and when briefing subagents.

Your job is to produce an Exempt IRB submission that clears review cleanly on the first round, stays truthful to the live experiment code, and leaves room for routine calibration without unnecessary amendments.

## 0. Orient

1. **Read the PI's private profile** (outside any public skill repo):
   - Check `~/.config/agent-lab/irb-profile.md` first, then a gitignored `irb-profile.md` in the project if present.
   - If neither exists, ask the PI for the missing boilerplate once (name, affiliation, email, default funding label/account, CITI training date, institution) and offer to save it to `~/.config/agent-lab/irb-profile.md` using [references/profile.example.md](references/profile.example.md).
2. **Load the institution guide**:
   - Read `references/institutions/<id>.md` matching the profile's institution (default: [references/institutions/jhu-hirb.md](references/institutions/jhu-hirb.md)).
   - If the institution has no file yet, work from the portal fields the user provides and offer to save a new file under `references/institutions/`.
3. **Check existing repo conventions**:
   - Inspect any existing `irb/` (or `notes/human/irb/`) folder, `README.md`, `CONTEXT.md`, study design/preregistration docs, and experiment code/configs (`experiment.yaml`, HTML/JS templates, Qualtrics exports).
   - **Existing project files win on layout.** If a project already has its own `sources/build_attachments.py`, keep using or updating it unless the user asks to migrate to `<skill-dir>/scripts/build_docx.py`.
   - Default folder layout when starting fresh:
     ```text
     irb/
     ├── README.md                    # packet index + submission checklist + status
     ├── eHIRB-Application-Draft.md   # copy-paste portal mirror (renamed to <IRB_ID>.md after submission)
     ├── sources/                     # canonical markdown sources (or generator scripts)
     ├── attachments/                 # compiled .docx / .pdf uploads (Consent, Recruitment, Tasks)
     ├── reviews/                     # YYYY-MM-DD.md reviewer comments + point-by-point replies
     └── archive/                     # dated snapshots saved before every revision round
     ```
4. **Audit experiment code before drafting or syncing**:
   - Whenever experiment code or config exists, run:
     ```bash
     python3 <skill-dir>/scripts/audit_packet.py --code <experiment-dir> [--irb <irb-dir>]
     ```
   - This surfaces actual telemetry (`visibilitychange`/`blur`/`focus`, mouse/dwell tracking, audio/chimes, chat, timers, `localStorage`), retake locks, skip/opt-out controls, pay/bonus text, and placeholders so the IRB never contradicts what the code does.

## 1. Draft a new Exempt packet (`draft`)

1. Read [references/amendment-proofing.md](references/amendment-proofing.md) and [references/consent-formats.md](references/consent-formats.md).
2. **Run a short PI decision gate before writing.** Ask only what the study docs and PI profile leave open — normally at most four calls:
   - **Duration tier & pay ceiling** (anchor vs. buffered ceiling, base hourly rate, performance bonus / wait-time pay / disconnect protection if multiplayer).
   - **Task scope & flexibility** (specific stimuli vs. umbrella description with one representative sample so routine tuning stays inside the approved envelope).
   - **Consent format & optional survey superset** (short survey opener vs. electronic information sheet vs. full institutional template; which optional survey blocks stay in the superset pool).
   - **Enrollment cap & study team** (`N` with pilot + dropout/matchmaking headroom; PI-only vs. student/team investigators who need current CITI certificates).
3. **Write the synchronized packet** from one canonical set of numbers, disclosures, and consent copy:
   - `irb/eHIRB-Application-Draft.md`: every portal section in exact order, following the institution guide (for JHU HIRB: Sections 1, Screening 1.0–1.1, 3–10, 14, 15).
   - `irb/sources/`: canonical markdown files (`consent.md`, `recruitment.md`, `tasks-and-questions.md`) with YAML frontmatter.
   - Build clean `.docx` files into `irb/attachments/` with:
     ```bash
     uv run <skill-dir>/scripts/build_docx.py <irb-dir>/sources/*.md --out <irb-dir>/attachments/
     ```
     (Pass `--var APP_NO=PENDING_HIRB_NUMBER` or set variables in frontmatter / a shared `vars.yaml`.)
   - `irb/README.md`: short index of files, portal upload mapping (e.g., 7.1.3 funding PDF, 8.2.0 consent, 9.6.0 tasks/survey, 14.14.0 recruitment), and a submission checklist.
   - **Sync live experiment config** (if present and requested): update the consent page, opt-out button, survey optionality (`required: false` / "Prefer not to answer"), open-text no-PII reminder, and debrief pay wording so the live study matches `Consent-Statement.docx` verbatim on every material point.
4. **Verify before handing over** (Section 5 below).

## 2. Sync and audit with experiment changes (`sync`)

Use when the study design, `experiment.yaml`, or workspace code changed.

1. Run `python3 <skill-dir>/scripts/audit_packet.py --irb <irb-dir> --code <experiment-dir>`.
2. Classify each difference against [references/amendment-proofing.md](references/amendment-proofing.md):
   - **In-envelope**: calibration or UI polish already covered by the protocol's stated bounds (no IRB change needed; note why).
   - **Pre-submission sync**: study not yet submitted — update all four synchronized surfaces (application `.md`, consent, recruitment/tasks, live experiment), rebuild `.docx`, and re-audit.
   - **Amendment required**: study is already approved/acknowledged and the change crosses an approved boundary (higher risk, new data/telemetry, higher `N`, lower hourly rate, deception, new population, materially different task). Flag explicitly and draft an amendment summary instead of silently altering approved text.

## 3. Revise for an IRB review round (`revise`)

1. **Archive first.** Copy the current application `.md` and `attachments/*` into `irb/archive/` with a `YYYY-MM-DD` date prefix before editing anything.
2. **Log verbatim feedback.** Create `irb/reviews/YYYY-MM-DD.md` grouped by portal section (`## General Information`, `## 8`, `## 14`, `## 15`, etc.), pasting the reviewer's exact comments followed by a `Reply:` block for each item.
3. **Draft terse, concrete replies** that state: (a) what changed, (b) the exact section/attachment updated, and (c) confirmation of any required institutional policy. Never argue with a reviewer over clerical formatting; do clarify politely if a reviewer misread a technical detail (e.g., human review of AI outputs vs. AI tool validation).
4. **Apply every promised edit across ALL four synchronized surfaces** (portal `.md`, consent attachment, tasks/recruitment attachments, and live experiment config/code), rebuild `.docx` attachments, and run the checks in Section 5. Most multi-round loops happen when a fix in Section 8.1 isn't mirrored in 8.2 and Section 9.
5. **Distill new institutional rules.** If the reviewer raised a general policy or gotcha not yet in `references/institutions/<id>.md`, offer to append it (with zero personal/study-specific details).

## 4. Stamp IRB number or closeout (`stamp`, `closeout`)

- **Stamp (`stamp <IRB_ID>`):** Replace `PENDING_HIRB_NUMBER` across `eHIRB-Application-Draft.md`, `sources/`, rebuilt `attachments/*.docx`, live experiment config/consent, and preregistration if present. Update `irb/README.md`.
- **Closeout (`closeout <determination.pdf>`):** Read the determination letter and record in `irb/README.md` (and `CONTEXT.md` if present):
  - IRB number, review type, acknowledgement/approval date, expiration date,
  - Progress Report due date (typically **6 weeks before expiration** — flag clearly, since research and analysis must stop if missed),
  - Approved max `N`, study team members, and exact approved attachment filenames.

## 5. Pre-handoff checks

Run both checks on every new packet and every review-response revision before reporting back:

1. **Automated audit:**
   ```bash
   python3 <skill-dir>/scripts/audit_packet.py --irb <irb-dir> [--code <experiment-dir>]
   ```
   Fix every `FAIL`; inspect and resolve or explain every `WARN`.
2. **Fresh-context checkers:** Run the two checkers in [references/checkers.md](references/checkers.md) in parallel (fresh subagents, not forks, passing file paths only):
   - **Four-way sync & code-truth checker** (application ↔ consent ↔ recruitment/tasks ↔ live code).
   - **Institutional landmine checker** (checks every rule in `references/institutions/<id>.md`).
   Verify each finding against the files before applying. Report back briefly: files created/updated, audit results, decisions left to the PI, and the exact portal upload checklist.

## Never

- Write personal PI details (name, email, phone, grant numbers, CITI filenames, student names) into this skill repo.
- Leave an IRB claim that contradicts the live experiment code (especially hidden logging, audio, chat, demographics, or pay math).
- Claim a full validated scale (e.g., NASA-TLX) when items or anchors were modified; label it as a modified questionnaire.
- Leave consent wording mismatched across application `8.1`, attachment `8.2`, recruitment `14.14`, and live study opener `9.6`.
- Overwrite a submitted packet during a review round without archiving it in `archive/` first.
- Invent CITI dates, funding numbers, IRB IDs, or click Submit in a portal on the PI's behalf.
