# Amendment-Proofing (Flexible Exempt Drafting)

Once an IRB issues an Exempt determination, **no changes may be made to the protocol or consent form without board approval**. Over-specifying volatile tuning parameters before piloting forces unnecessary amendments. Draft honestly with calibrated bounds so routine tuning stays inside the approved protocol.

---

## 1. What to Keep Flexible (Safe Bounds)

1. **Duration & base pay ceiling:**
   - State a realistic **upper bound or range** (e.g., *"up to 20 minutes"*, *"approximately 15–20 minutes"*) paired with a floor hourly rate (*"at least $12.00/hour prorated base pay, plus performance bonus"*).
   - Keep the exact session duration and base pay synchronized on the live Prolific listing and consent screen at launch, staying at or below the approved duration ceiling and at or above the approved hourly rate.
2. **Task stimuli & umbrella description:**
   - Describe the **task class** rather than locking a single draft stimulus set when items are still being tuned (e.g., *"short simulated workplace documents, such as memos or summary briefs, with occasional planted factual discrepancies"*), and upload **one representative sample** plus the interaction mechanics in `Tasks-and-Questions.docx`.
   - Include a calibration sentence in Section `9.3`: *"Representative task instructions, sample stimuli, and survey items are uploaded in Section 9.6.0; minor timing, block-count, stimulus-wording, or payoff-weight calibrations may be refined after initial piloting within the same session-duration, compensation, and minimal-risk bounds."*
3. **Optional superset survey pool:**
   - Upload the **superset** of candidate post-study items in `Tasks-and-Questions.docx` (marking optional modules clearly, e.g., *"a subset of the following optional post-study items may be presented, taking no more than 3 minutes total"*).
   - Dropping an optional item during tuning does not increase burden or risk; adding a brand-new sensitive question after approval *would* require an amendment.
4. **Enrollment ceiling (`14.6.0`):**
   - Request enough total consented participants (`N`) to cover: **pilot(s) + confirmatory target + 20–30% attrition/opt-out/matchmaking-timeout buffer** (and explain the breakdown cleanly in `14.6.1`). Running fewer than the approved ceiling never needs an amendment; exceeding it does.
5. **Internal tuning knobs (keep at principle level in IRB):**
   - Exact task timing distributions, exact round/block counts, exact payoff weights (state the *structure*: bonus formula, any penalty rule, and the `$0.00` bonus floor so base pay is never reduced), and exact UI layout details.

---

## 2. What MUST Stay Exact (Never Blur)

- **Risk level and non-deception** (`1.6`, `10.1`, `15.1`): never introduce deception or sensitive/distressing topics under umbrella wording.
- **All collected data & telemetry** (`8.1`, `9.5`, `15.1.1`): every logged behavioral signal (clicks, timestamps, tab visibility/focus, cursor dwell, chat, Prolific demographics) must be disclosed honestly; never log something the consent says you will not collect.
- **Pay floor & bonus-floor guarantees** (`14.12`): never reduce base pay below the stated hourly floor or let error penalties eat into base pay.
- **Eligibility & populations** (`14.2`, `14.8`): never recruit minors, non-English speakers, or targeted vulnerable populations unless explicitly approved.
- **Study team** (`3.2`): anyone handling raw study data must be listed on the protocol with current CITI training.

---

## 3. Pre-Submission Sync vs. Post-Approval Amendment

When running `/irb sync` after code or design edits:

| Change | Before submission | After determination |
|---|---|---|
| Adjusting wait times, error rates, block count, or wording within approved duration/pay/task bounds | Update docs if stated specifically | **In-envelope** (no amendment; ensure live consent still states accurate session time & pay) |
| Dropping an optional item from the approved survey superset | Remove or keep marked optional | **In-envelope** |
| Adding a new telemetry field (e.g., tab-focus logging) or audio chime | Sync all 4 surfaces | **Amendment required** |
| Adding new survey questions not in `Tasks-and-Questions.docx` | Sync all 4 surfaces | **Amendment required** |
| Changing task domain outside stated umbrella, adding deception, adding chat, or raising `N` above approved cap | Sync all 4 surfaces | **Amendment required** |
| Adding a student/co-investigator | Add in `3.2` + CITI | **Amendment required** |
| Lowering effective hourly pay below stated floor or lengthening session past ceiling | Sync all 4 surfaces | **Amendment required** |
