# Exempt Consent Formats & Required Disclosures

Pick **one** consent format during the PI decision gate and use the exact same text and disclosures across:
1. Application `8.1.0` (process description),
2. Attachment `8.2.0` (`Consent-Statement.docx`),
3. Study opener (`9.6.0` and live Qualtrics/Pairit consent screen), and
4. Recruitment material `14.14.0` (consistent summary of time, pay, tasks, eligibility, voluntary nature).

---

## Choosing a Format

| Format | Best for | Pros / Cons |
|---|---|---|
| **A. Short HIRB Survey Opener** | Pure anonymous online surveys (e.g., Qualtrics via Prolific, ≤15 min, no custom telemetry) | Cleanest for participants; uses HIRB's exact survey sentence. Too thin for custom web apps with telemetry, bonuses, or multiplayer interaction. |
| **B. Concise Electronic Information Sheet** | Short interactive web experiments (e.g., Pairit, 10–25 min) | Fits on one screen; clearly discloses tasks, pay/bonuses, telemetry, opt-out button, and contacts. Keep it aligned with required key elements. |
| **C. Full HIRB Written Consent Template (Adapted for Online)** | Longer/complex behavioral experiments (e.g., 20–40 min, bonuses, multiplayer chat, comprehension checks) | Mirrors every heading of the HIRB Revised Written Consent Form Template, minimizing reviewer pushback on Section 8. Replace signature block with agree/decline buttons. |

---

## Format A — Short HIRB Survey Opener

Exact HIRB base text (from eHIRB Section 8.2 note), extended with skip and no-PII reminders:

> By completing this survey or questionnaire, you are consenting to be in this research study. Your participation is voluntary, you may skip any question you are not comfortable answering, and you can stop the survey at any time. Please do not include personal information or incriminating information in open responses.

- Upload a short `Consent-Statement.docx` containing this exact text so `8.1.0`, `8.2.0`, and `9.6.0` match word-for-word.

---

## Format B — Concise Electronic Information Sheet

Include every element below on one clean screen (no signature required for Exempt studies):

1. **Institution & study identification:** University name, study title, PI name & email, IRB application number.
2. **Purpose & procedures:** Plain-language summary of what participants will do (including whether agents are simulated or teammates are human, and whether audio chimes or chat are used).
3. **Time & pay:** Expected duration (or ceiling), exact base pay, hourly rate, performance bonus / floor / wait-time / disconnect rules, and payout window via Prolific.
4. **Risks & voluntariness:** Minimal risks (mild fatigue, boredom, eye strain, time pressure), voluntary participation, stop anytime without penalty, skip any survey question (`required: false` / "Prefer not to answer").
5. **Data collected & NOT collected:** Enumerate every logged item faithfully (clicks, answers, timestamps, browser-tab visibility/focus, cursor dwell, chat, Prolific aggregate demographics) AND what is *not* collected (name, email, IP, location, audio/video/screen recording, eye tracking, biometrics). State Prolific ID separation/deletion and open-text/chat no-PII reminder.
6. **Contacts:** PI email + IRB phone/email.
7. **Age & explicit buttons:** Confirm 18+ and provide **both** `"I understand and agree to participate"` and `"I do not wish to participate"` (routing to a clean opt-out exit screen that records no task data).

---

## Format C — Full HIRB Written Consent Template (Online Adaptation)

Use the standard HIRB section headings in order (with running header `Date prepared: ... | PI: ... | Application No.: ...`):

1. Title block (`JOHNS HOPKINS UNIVERSITY` / `HOMEWOOD INSTITUTIONAL REVIEW BOARD (HIRB)` / `RESEARCH PARTICIPANT INFORMED CONSENT FORM`) + `Study Title`, `Application No.`, `Principal Investigator`
2. Opening voluntariness sentence
3. **Research Summary (Key Information)**
4. **Why is this research being done?** (include eligibility and target consented ceiling `N`)
5. **What will happen if you join this study?** (bulleted steps, simulated-agent / no-live-interaction or anonymous-team notice, audio chime mute note if applicable, open-text/chat no-PII reminder, no follow-up)
6. **How long will you be in the study?**
7. **What are the risks or discomforts of the study?** (include both task discomforts and confidentiality-breach harms)
8. **Are there benefits to being in the study?**
9. **What are your options if you do not want to be in the study?**
10. **Will it cost you anything to be in this study?**
11. **Will you be paid if you join this study?** (exact base + bonus + floor + wait-time/disconnect rules + Prolific timing + no SSN / no direct university payment)
12. **Can you leave the study early?**
13. **How will the confidentiality of your data be protected?** (HIRB/government review clause, bulleted protections matching `15.1.1`, 3-year retention + de-identified reproducibility archive if applicable)
14. **What is the Institutional Review Board (IRB) and how does it protect you?** (`410-516-6580` / `hirb@jhu.edu`)
15. **What should you do if you have questions about the study?**
16. **Your Agreement to Participate** (confirm 18+, read & understood, voluntarily agree; agree vs. `"I do not wish to participate"` button; no legal rights waived)

---

## Code-Synced Disclosures Checklist

Whenever the live experiment code contains any of the features below, disclose it explicitly in **consent**, **`8.1`**, **`9.5`**, and **`15.1.1`**:

- **Browser-tab focus / visibility logging** (`visibilitychange`, `blur`, `focus`) — explain why (e.g., measuring active reading time vs. tab switches) and note no screen recording or URLs outside the study are captured.
- **Cursor / hover / dwell timing** (`mouseenter`, `mouseleave`, `mousemove`) — distinguish element dwell time from full mouse-path recording.
- **Audio alerts / chimes** (`Audio`, `AudioContext`) — state it is a soft playback chime only (mutable), with **no microphone or audio recording**.
- **Prolific aggregate demographics** — state that standard non-identifying Prolific profile demographics (e.g., age, sex) may be exported for aggregate sample reporting.
- **Live participant text chat** — note anonymous role labels (`Participant A`, `Role 1`, etc.), explicit no-PII reminder inside the workspace, and pre-analysis redaction.
- **Matchmaking / partner disconnect** — state max wait time, wait-time pay, and that remaining participants are still paid if a teammate disconnects.
- **Comprehension checks** — clarify whether participants can retry/review without unpaid screen-out (Prolific policy prohibits unpaid screening after consent unless formally configured).
