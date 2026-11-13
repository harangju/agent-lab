# Checkers

Three checkers read the first full draft with fresh context, so they don't inherit your reading of the notes. Each one gets only the files its job needs and returns findings. None of them edits anything.

## When to run them

- **Once, on the first full draft,** after your own coverage pass and before you report back.
- **On "is #N fair?"** you may run the rebuttal checker on just that comment.
- **Not on every revision.** The user's turns in the revise loop are short ("drop minor 4"), and checkers slow them down.

Spawn all three in one message so they run in parallel. Use fresh subagents, not forks: a fork carries your context, which is the bias the checkers are there to avoid. Pass file paths, not pasted text. If you can't spawn subagents, run the three checks yourself in this order, re-reading the paper for each one.

Fill in the `{…}` slots. `{paper}` is `$SCRATCH/paper.txt`, and `{pdf}` is the manuscript PDF, for tables and figures that `pdftotext` garbles.

## Accuracy

```
You are checking a referee report for factual accuracy. You did not write it.

Read the review at {review} and the manuscript text at {paper}. Use the PDF at {pdf} for tables, figures, and anything the text extraction garbles.

Find every factual claim the review makes about the paper: numbers, sample sizes, section, table, and figure references, and statements of what the paper does, reports, defines, assumes, or never does. Check each one against the paper.

Return one line per claim:
- the claim, quoted from the review in 15 words or fewer
- HOLDS, PARTLY, WRONG, or CAN'T TELL
- the evidence: a short quote from the paper with its section or page. For a claim that the paper lacks something, say what you searched for and where.

Judge facts only, not tone or whether the critique is fair. Do not edit any file.
```

In a second round, add this paragraph before the last line: "Also read the authors' response letter at {response_letter}. For each claim it makes about what changed, check the revised paper and rate the claim the same way."

## Author rebuttal

```
You are the authors of the manuscript at {pdf} (text at {paper}). You have just received the referee report at {review}.

For each numbered comment, major and minor, write the strongest honest reply you would put in a response letter. Point to where the paper already handles the point, or say why it is standard practice, mistaken, or out of scope. Do not concede just to be polite, and do not claim analyses the paper does not contain.

Then rate each comment:
- LANDS: your reply defeats the comment, or nearly does.
- PARTLY: your reply answers part of it. Say which part survives.
- STANDS: you have no good reply.

Return, for each comment: its number, the rating, your reply in one to three sentences, and the quote and location in the paper that your reply relies on. Do not edit any file.
```

## Voice

```
You are checking the wording of a referee report. Read the voice rules at {voice}{, the project's style notes at {project_style}}{, and one or two of the user's finished reviews at {examples} for the voice to match}. Then read the review at {review}.

Flag every sentence that breaks a rule. For each one, give the sentence quoted, the rule it breaks, and a rewrite that keeps its meaning and every fact. Also flag any comment that runs over the length limits. If the same pattern repeats, list every instance.

Judge wording only. Do not check facts against the paper, add points, or soften the substance. Do not edit any file.
```

## Weighing what comes back

Checker findings are claims, not edits. A checker can misread the paper the way a second-opinion reviewer can, so check each finding against `paper.txt` yourself before you act on it.

- **Accuracy, WRONG or PARTLY, confirmed:** fix the comment or cut the false part. The review must not be wrong about the paper.
- **Rebuttal, LANDS or PARTLY, confirmed:** narrow the comment to what survives, or ask about the point instead of asserting it. If the reply sinks the whole point, don't drop it. The point is the user's, so flag it in your message with the authors' likely reply.
- **Voice:** apply the rewrites that keep the meaning, and fix the same pattern anywhere else in the file.
- **Rejected findings:** keep a one-line reason for each.

In your report back, add a short **Checks** list with what each checker flagged, what you changed, what you rejected and why, and any point a rebuttal sank.
