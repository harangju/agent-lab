# Inline Review-Comment Loop & `review_comments.jsonl`

Capture every inline manuscript annotation and substantive chat review edit in an append-only JSONL log so editorial judgment is traceable, replayable across projects, and mineable by `/save`.

## Supported Inline Comment Formats

- **LaTeX:** `% @comment (...)` or `% @comment: ...` (either trailing on a line or on the line immediately above/below the marked span).
- **Markdown:** `<!-- @comment: ... -->` or paired `<!-- @comment --> ... <!-- /@comment: ... -->`.

## Workflow

1. **Re-read the file first.** Never rely on cached text; the PI edits directly between turns.
2. **Collect every `@comment`** (with file, section, line number, and surrounding sentence). If a comment is a question (`"is this true?"`, `"necessary?"`, `"what's standard?"`), answer or check against locked data/exemplars rather than guessing blindly; if the intent is unambiguous (`"no gerund subject"`, `"cite"`, `"weird phrase"`), fix it directly.
3. **Preserve PI wording.** Change only what the comment targets (plus minimal knitting adjustments in the immediately adjacent sentence if needed). Never rewrite untouched sentences the PI already approved.
4. **Append to `notes/review_comments.jsonl` BEFORE stripping tags.** Create `notes/` if needed. Every entry is a single compact JSON object with these keys:

```json
{
  "id": "YYYY-MM-DD-<section>-<nn>",
  "date": "YYYY-MM-DD",
  "source": "inline_comment | chat_review | self_audit",
  "file": "paper/sections/intro.tex",
  "section": "introduction",
  "span": "short quoted target phrase or table/figure label",
  "comment": "verbatim PI comment or concise summary of chat feedback",
  "before_sentence": "original sentence or short excerpt before edit",
  "after_text": "revised sentence or concise summary of change",
  "resolution": "one-sentence summary of why/how it was resolved",
  "status": "resolved | deferred | open"
}
```

5. **Strip resolved `@comment` tags** from the manuscript only after the JSONL line is written. Leave `deferred`/`open` comments intact until resolved.

## Cross-Paper Taste Replay

When asked to apply another project's review history (e.g., `../other-paper/notes/review_comments.jsonl`) to the current manuscript:

1. Read the source JSONL and cluster recurring *editorial* patterns (e.g., tightening abstract word count, cutting inline `±` clutter, standardizing field terms, anchoring comparisons, aligning headings with exemplars).
2. Ignore project-specific empirical facts or domain terms from the source paper.
3. Apply the extracted editorial checklist section-by-section to the current manuscript, then run a fresh PI-eye self-audit and log the resulting edits in the *current* project's `notes/review_comments.jsonl`.
