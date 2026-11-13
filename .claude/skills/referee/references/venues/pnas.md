# PNAS

Manuscript IDs look like `PNAS-2026-31615`. Submissions usually come with a separate SI PDF (`*_SI.pdf`). Read the SI too, because definitions and robustness checks often live only there.

## Form fields

Only one field has been seen:

- **Comments for the author** (required). Its boilerplate reads, in full:
  > PNAS reserves the right to edit review comments that may impede constructive discussion of a manuscript or reveal confidential information. Authors will not know your identity unless you purposefully sign your comments.
  >
  > Please provide your comments to questions four and five above.

The box refers to "questions four and five above", so the form has at least five questions before it. They haven't been seen. Don't guess what they are, and leave them for the user. If the user shows the full form, record them here.

## Notes

- PNAS PDFs have **line numbers**, so the blocks in `comments.md` use `### PDF p. N (Lines A–B)` instead of manuscript page numbers. Line numbers still never go into the review.
- Brief Reports are short. Keep the review short too: about 5 majors and a few minors at most.
- The user's PNAS review uses `###` for Major and Minor comments, nested under the single author box.

## Review file

Use this only when the repo has no template or earlier review for this venue. If it has either, follow that instead.

Start with `# PNAS Review — <ID>`, then `## Comments for the author *`, followed by the boilerplate above, word for word. Then add one summary paragraph, `### Major comments`, and `### Minor comments`. Leave out Recommendation and Confidential headings unless the user shows the form has those fields.
