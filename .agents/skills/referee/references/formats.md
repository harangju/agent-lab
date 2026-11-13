# Formats

Use these when the project has no earlier `comments.md` or review to copy. If it does, copy those instead.

## `comments.md`

```markdown
# <ID> — Transcribed Comments & Relevant Sections

- **Title:** <title>
- **Journal:** <venue, track or special issue>
- **Manuscript ID:** <ID>

Handwriting appears on PDF pp. 2–9 and 14 only; later pages have no notes.

---

## Abstract

### PDF p. 2 (Manuscript p. 1 of 38)
**Relevant Section:**
> ... We show that **<u>platform design</u>** shapes how sellers **<u>respond
> to competition</u>** ... a passage long enough to show what every mark
> refers to, with "..." for cuts and ~~strikethrough~~ for words the user
> crossed out.

**Handwritten Comments & Markings:**
- Under *"platform design"*: **"which part of the design?"**
- Left margin, arrow to *"respond to competition"*: **"how measured?"**
- Checkmark (**✓**) at the end of this paragraph
- Below the keywords: **"abstract overclaims — major or minor depending on the rest"**

---

## 1. Introduction

### PDF p. 3 (Manuscript p. 2 of 38)
...

---

## Notes on unannotated sections (for the review)

- **Design:** ...
- **Definitions the review relies on:** ...
- **What the paper concedes:** ...
```

Rules:

- Use one `###` block per page, under a `##` heading named for the paper's own section. A page that spans two sections gets a block under each.
- If the PDF has line numbers instead of page numbers, use them in the block header, as in `### PDF p. 2 (Lines 19–40)`. They help you find things, but they never go into the review.
- Give each note's position: under, above, left/right margin, top of page, with an arrow to, or circled. Then quote the anchor phrase in italics and the note in bold quotes.
- Transcribe a figure or table note against its caption.
- A general note at the top of a page gets its own block: `### PDF p. 14 (...) — Top of page (general reflection)`.

## Review

Use the venue's template. If the repo has none, use the journal's file in `venues/` if there is one (for example, [venues/misq.md](venues/misq.md)). If not, use this:

```markdown
# Review: <ID>

## Summary

<What they did and found, with key numbers, in 3–5 sentences. One line on what is good.>

## Major Comments

1. **<One-sentence claim of the problem.>** <What the paper does. Why it's a problem. A direct question, or what would fix it.>

2. **...**

## Minor Comments

1. <One to three sentences.>

2. ...

## Recommendation

## Confidential Comments to the Editor
```

Venue forms vary. Management Science opens with question prompts that sit above the detailed comments. ISR puts a score table first. PNAS has a single "comments for the author" box. For these and MISQ, see [venues/](venues/). Keep the template's headings and boilerplate exactly as they are, and fill in only the answer slots.
