# Johns Hopkins University — Homewood IRB (eHIRB) Exempt Guide

Institution-specific field map, boilerplate, and reviewer landmines for **Exempt** online behavioral and survey studies (e.g., Prolific + Qualtrics or Pairit).

- **IRB Office:** Homewood Institutional Review Board (HIRB), Johns Hopkins University
- **Public Contact:** `(410) 516-6580` / `hirb@jhu.edu` / `https://homewoodirb.jhu.edu/`
- **Portal:** JHU eHIRB (`New Application` → `Exempt`, Minimal risk)
- **Typical Exempt Categories:** Category 2 (surveys/questionnaires, anonymous or low-risk) and Category 3 (benign behavioral interventions with adults, prospective agreement).

---

## 1. Portal Section Map (Copy-Paste Order)

Mirror these exact section numbers in `eHIRB-Application-Draft.md`:

| Section | Portal Heading | Key Fields & Exempt Defaults |
|---|---|---|
| **1** | General Information | `1.0` PI + CITI date/certs; `2.0` Full Study Title; `3.0` New; `3.1` Exempt; `5.0` Brief summary (objectives, procedures, population); `6.0` Minimal |
| **1 (Screening)** | Screening Information | `1.0` Is subject AI/ML? (`Yes` only if study is about AI/ML; `No` for pre-programmed simulated agents with static stimuli); `1.1` Device/algorithm/app developed or validated? (**`No`** for human-oversight / behavioral studies — see Landmine #2) |
| **3** | Research Personnel | `1.0` Student research project? (`Yes` → `1.1` PI supervision plan; `No` if PI-only); `2.0` Team Members table (JHU affiliates must log into eHIRB once before appearing; upload CITI for each) |
| **4** | Conflict of Interest | `1.0` `No` (unless a reportable COI exists) |
| **5** | Clinical Trials | `1.0` `No`; `6.0` blank (unless registered) |
| **6** | Research Sites | `1.0` Non-Hopkins collaboration? (`No` unless collaborating); `2.0` `[x] Internet/email`; `3.0` KSAS/WSE lab? (`No` for online-only) |
| **7** | Support Information | `1.0` **Currently funded** whenever participants are paid (see Landmine #1); `1.1` Funding source + grant/account #; `1.2` `[x] Monetary`; `1.3` Upload funding award PDF; `2.0` State Prolific direct payment + JHU payment procedures confirmation |
| **8** | Informed Consent and Assent | `1.0` Process: where/when, no time limit, disclosures, how understanding is assessed (click agree / opt-out button / optional non-punitive comprehension check), English-only; `2.0` Upload `Consent-Statement.docx`; `2.1` blank if English-only; `3.0` Future contact `No`; `4.0` Auth in consent `No` |
| **9** | Protocol Information | `1.0` Checkboxes: `[x] Survey/Questionnaire`, plus `[x] Intervention or testing: ... behavioral ...` for experiments, plus `[x] AI/ML` only if applicable; `2.0` Purpose/goals; `3.0` Design/methodology; `4.0` Importance of knowledge; `5.0` Step-by-step procedures with time breakdown & exact list of recorded vs. non-recorded data; `6.0` Upload `Tasks-and-Questions.docx` (or full survey PDF); `7.0` Audio/video/photo `No` |
| **10** | Deception | `1.0` `No` (for non-deceptive exempt studies; briefly explain why — e.g., participants are told agents are simulated / rounds vary without revealing exact sequence) |
| **14** | Recruitment and Participants | `1.0` `[x] PI` (+ Student Investigator/Team if applicable); `2.0` `[x] None` (no vulnerable populations directly recruited); `4.0` `[x] Male` `[x] Female`; `5.0` Population, Prolific recruitment, and **fraud-prevention steps**; `6.0` Total consented ceiling `N`; `6.1` Power/pilot/dropout justification; `7.0` Anti-coercion (voluntary, anonymous, fair Prolific rate); `8.0` Inclusion + Prolific verification; `9.0` Exclusion (prescreening + analysis exclusions); `10.0` No participant costs; `11.0` `Yes` → **`Other`** (Prolific, not cash) + JHU payment procedures confirmation; `12.0` Exact base pay, hourly rate, bonus/wait-time/disconnect rules, payout timing, no SSN/tax info; `13.0` `Yes`; `14.0` Upload `Recruitment-Material_Prolific.docx` |
| **15** | Risk, Benefits and Confidentiality | `1.0` Minimal discomforts + **explicit harms** of confidentiality breach (see Landmine #3); `1.1` **Mitigations** only (voluntary/skip, no direct IDs, Prolific ID separation/deletion, open-text/chat PII warning + redaction, encrypted JHU OneDrive, no media); `2.0` Benefits to participants (none beyond compensation); `3.0` Benefits to society; `4.0` Identifiable data `No`; `7.0` Encrypted JHU OneDrive, password-protected computers, no raw files on local laptops/mobile; `8.0` Stored on laptops/mobile? `No` (must match `7.0`!); `9.0` Who collects/stores/accesses; `10.0` Retain ≥3 years post-completion per JHU policy, then permanently delete raw exports (note if de-identified dataset archived for reproducibility); `13.0` JHMI/SOM PII/PHI? `No`; `16.0` Confidentiality confirmation `Yes` |

### Portal Upload Checklist

- **Section 7.1.3:** Funding award PDF (required whenever participants are paid)
- **Section 8.2.0:** `attachments/Consent-Statement.docx`
- **Section 9.6.0:** `attachments/Tasks-and-Questions.docx` (or full survey PDF)
- **Section 14.14.0:** `attachments/Recruitment-Material_Prolific.docx`
- **Note:** Only the PI can click **Submit** in eHIRB (`Validate` → `Finish` → `Submit`).

---

## 2. Known HIRB Reviewer Landmines (Prevent on Round 1)

Every item below has triggered real HIRB revision requests on past exempt Prolific studies:

1. **Any participant payment ⇒ `7.1` must be "Currently funded".**
   - Even small Prolific studies count as funded remuneration. Upload the funding/award PDF in `7.1.3`.
   - Select **`Other`** (never Cash/ClinCard/Gift Cards/PaymentWorks) in `14.11.0`, explain electronic payment via Prolific, and include the exact confirmation in **both `7.2.0` and `14.11.0`**:
     > *"The investigators will follow the Johns Hopkins University approved Procedures for Paying Research Participants."*
   - In `14.12.0`, state the exact base dollar amount, implied hourly rate (at least Prolific's fair floor, typically ≥$12/hr), any bonus/wait-time/disconnect rules, payout window (e.g., within 24–48 hours), and explicitly state: *"No Social Security number or tax-identifying information is collected from participants, and Johns Hopkins University does not issue payment to participants directly."*

2. **AI Screening Trap (`Screening 1.1`).**
   - Setting `Screening 1.1` ("Will a device/algorithm/app be developed and/or validated through this study?") to `Yes` prompts reviewers to demand the specific AI tool, how it works, and how participant data validate it — plus matching consent language.
   - For behavioral / human-oversight studies where participants inspect AI-generated or simulated outputs and no AI model is trained or validated on participant data, set **`1.1 = No`**. If the study uses pre-programmed simulated agents with static pre-generated items, `1.0` can also be `No` with a one-line explanation.

3. **Strict split between `15.1.0` (Harms) and `15.1.1` (Mitigations).**
   - `15.1.0` **must explicitly enumerate concrete harms** of a breach of confidentiality or loss of privacy: (1) identification of respondents (e.g., if personal details were typed in open text/chat), (2) reputational harm or embarrassment, (3) emotional distress from unauthorized disclosure, and (4) misuse of information by third parties.
   - Put *all* procedural safeguards (Prolific ID handling, disabled IP tracking, OneDrive encryption, skip options, redaction) in **`15.1.1`**, not `15.1.0`.

4. **Four-way consent & platform parity (`8.1` ↔ `8.2` ↔ `9.6`/live app ↔ `14.14`).**
   - Reviewers compare `8.1.0`, the uploaded file in `8.2.0`, the opener inside `9.6.0` / the live study, and the Prolific script in `14.14.0`. If `8.1` describes a one-sentence opener while `8.2` uploads a multi-page form (or `9.6` has a third version), HIRB will return the application.
   - Explicitly distinguish **recruitment platform** (Prolific) from **hosting platform** (Qualtrics or Pairit) in `8.1`, `9.5`, and `15.1.1`.

5. **Survey fraud-prevention disclosure (`14.5` / `14.8–14.9`).**
   - Paid online surveys/experiments trigger HIRB's fraud-prevention guidance (`Fraud-Prevention-Regarding-Use-of-Survey-Instruments.pdf`). Proactively include concrete measures in `14.5`: Prolific approval rate (≥95% or ≥98%), minimum prior submissions, verified country residency, duplicate prevention (`allowRetake: false` + Prolific deduping), comprehension/attention checks (note whether non-punitive), timing/engagement monitoring, and screening open-ended text for non-substantive or automated responses.

6. **Required Prolific recruitment components (`14.14.0`).**
   - HIRB treats a Prolific listing as recruitment material. Upload `Recruitment-Material_Prolific.docx` containing all required elements:
     1. Explicit statement that it is a **research study**
     2. **PI name** and **Johns Hopkins University** affiliation
     3. **HIRB application number** (or placeholder to stamp) and review attribution
     4. **Purpose** of the study
     5. **Eligibility criteria** (18+, U.S., English, device)
     6. **Procedures** (what participants will do; single session, no follow-up)
     7. **Time commitment**
     8. **Exact compensation** (base + bonus/wait-time if any, payout timing)
     9. **Voluntary participation** and right to withdraw
     10. **Contacts** (PI email + HIRB `410-516-6580` / `hirb@jhu.edu`)
     11. **Prescreening filters** listed separately at the bottom

7. **Open-text & chat PII warning + "Prefer not to answer".**
   - Every survey item should allow skipping (e.g., `required: false` or a `"Prefer not to answer"` choice), and `15.1.1` must cite this as a discomfort mitigation.
   - Any free-text field or multiplayer chat must include an explicit instruction *"not to include personal information or incriminating information"* (or names/employer) in **both** consent and on the prompt itself, plus pre-analysis screening and redaction in `15.1.1`.

8. **Storage consistency (`15.7.0` vs `15.8.0`).**
   - If `15.8.0` ("stored on laptops or other mobile devices") is **`No`**, `15.7.0` and `15.1.1` must say data are stored *exclusively* on encrypted JHU-approved cloud storage (JHU OneDrive) and accessed via password-protected computers *without storing raw files locally on laptops or mobile devices*.

9. **Modified instruments naming (`9.3` / `9.5` / `9.6`).**
   - If you shorten or alter a validated instrument (e.g., 5 of 6 NASA-TLX items on a 1–7 scale), describe it as a *"modified workload and task-experience questionnaire (adapted from NASA-TLX)"* rather than claiming the full validated instrument.

10. **CITI course specificity (`1.0` / `3.2`).**
    - PI and every team member must hold current **Social & Behavioral Research – Basic/Refresher** CITI certificates uploaded to their eHIRB profiles (other CITI tracks are rejected).

11. **Post-determination progress report.**
    - Exempt determinations expire (typically after 2 years) and require a **Progress Report at least 6 weeks prior to the expiration date**; if missed, all research *including data analysis* must stop immediately.
