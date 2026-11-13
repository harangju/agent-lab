---
name: referee
description: Turn a manuscript PDF the user marked up by hand (iPad/Apple Pencil, Preview, Acrobat) into a transcription of every note and a terse referee report in their voice, then revise it with them. Use when the user drops an annotated paper PDF and asks to transcribe their notes, draft a review from their markup, review a revised manuscript in a second round, or work on it "the same way as the others".
argument-hint: "[path to the marked-up PDF] [tone or instructions]"
---
Referee from markup: $ARGUMENTS

The user reads the paper on paper (or an iPad) and writes in the margins. Your job is to get every note off the page, turn the notes into a review that sounds like them, and then make the small revisions they ask for. The review is theirs: their points, their judgement, their voice. You transcribe, organize, check, and tighten.

There are three deliverables, in this order, and the user usually checks in between:

1. **`comments.md`**, a faithful transcription of every handwritten note next to the passage it marks.
2. **The review**, built from those notes on the venue's template.
3. **Revisions**, in a loop, until they commit.

## 0. Set up

1. Read the project's own conventions first: `CLAUDE.md`/`AGENTS.md`, a venue `template.md`, and one or two finished reviews and `comments.md` files from earlier manuscripts. **The repo's existing files are the format spec.** Match their folder layout, file names, headings, and section order exactly. If the user says "like the others in X", open those. If the repo has nothing for this venue, check `references/venues/` for a file on the journal, such as [misq.md](references/venues/misq.md). It has the journal's form fields, its recommendation scale, and a template. The order of precedence is the repo's files, then the venue file, then the generic template in formats.md.
2. Put the manuscript in its own folder the way the repo already does (typically `<venue>/<ID>/` holding the PDF, `comments.md`, and `<ID>.md` copied from the venue template). Use `git mv` for files that are already tracked. If there's no precedent, use that layout.
3. Extract the paper text once, to your scratchpad, for quoting and fact-checking later:
   `pdftotext -layout paper.pdf $SCRATCH/paper.txt`
4. Work out the page offset (PDF page N is often manuscript page N−1 because of a cover page) and the total manuscript pages. Every note gets both numbers.
5. If this is a revised manuscript, also read the user's round-1 review and the authors' response letter.

## 1. Find the ink

Run the helper. It finds every page with markup and saves zoomed crops of each inked region:

```bash
python3 -I ${CLAUDE_SKILL_DIR}/scripts/find_ink.py paper.pdf $SCRATCH/ink
```

- Annotated PDFs (iOS Markup stores a whole page of strokes as one page-sized Stamp) are localized by rendering with and without annotations and diffing. If the PDF has no annotations, it falls back to coloured pixels, which also catches figures, so look at those pages before trusting them.
- Read `page-NN.png` for orientation, then every `page-NN-cK.png` crop. For anything you can't read, re-render tighter and sharper with `pdftoppm -r 600 -f N -l N -x X -y Y -W W -H H` (pixel coordinates at that DPI), or PyMuPDF `get_pixmap(dpi=600, clip=rect)`.
- **Check the misses.** The detector can miss pencil, black ink flattened into the page, or a PDF where only some pages are annotated. So every page it did *not* flag goes onto `unflagged-*.png` contact sheets, four pages each. Look at every sheet. If any page shows a mark, render that page at 300 dpi and read it like the others. Don't skip this even when the flagged list looks complete.
- Also note what has no ink: say which pages carry notes ("Handwriting appears on PDF pp. 2–9 and 14 only").

## 2. Transcribe into `comments.md`

**Every single mark counts.** That includes checkmarks, "good", "?", underlines with no words, arrows, crossed-out words, and notes the user wrote to themselves ("could be major or minor"). The user has said "all my comments matter." Don't summarize, merge, or tidy their words. Keep their spelling, casing, and profanity.

Follow the format in [references/formats.md](references/formats.md) unless the repo's own earlier `comments.md` files differ. If they differ, theirs win. In short: group by paper section, one block per page, the marked passage quoted with the marked phrases in bold-underline, then each note anchored to the phrase it sits under or beside.

- Where a reading is uncertain, give your best reading and flag it: `**"cool"** [or "coal"?]`. Never silently guess.
- End with **Notes on unannotated sections**: a short list of facts from the pages the user didn't mark that the review will need, such as design details, sample sizes, definitions, and what the paper concedes. Keep it factual, not evaluative.

Before moving on, recount: the number of inked regions you read should match the notes you wrote down.

## 3. Draft the review

Copy the venue template and fill it from the notes. Read [references/voice.md](references/voice.md) first and follow it for every sentence. If the project has its own memory or style notes on review voice, those win.

- **Summary.** A few plain sentences: what they did and what they found, with the key numbers. Then one line of what's good, if the user's notes say so.
- **Major comments.** Cluster the notes into a handful of problems, usually 3–5. Each one opens with a bold one-sentence claim, followed by a few sentences: what the paper does, why it's a problem, and what would fix it, ideally as a direct question.
- **Minor comments.** Numbered, one to three sentences each. Wording, definitions, notation, missing details.
- **Second round.** Open with a line on whether each round-1 major was resolved, then the new issues from the notes. An unresolved point the notes don't raise goes under possible additions.
- **Source.** Every comment traces to the user's notes. Points you came up with yourself go in your chat message as "possible additions", not into the draft. The user adds the ones they want.
- **Tone.** Use the tone the user asks for. "Scathing but respectful" means confused-reader framing ("I don't follow how…", "It's unclear what…"), giving the authors the benefit of the doubt while every point still lands.
- **Leave the user's calls blank.** That means scores, the recommendation, and confidential comments to the editor, unless the user asks you to fill them or their notes state them.
- **Length.** Draft about a third as long as feels natural. "Make sure you don't add too much detail" is the standing instruction.

### Check before you hand it over

Do these before the user sees the draft; they will ask for them anyway.

1. **Coverage, yourself.** Walk `comments.md` top to bottom. Each substantive note should land in a comment or be dropped on purpose. List what you dropped and why in your message. This check needs the notes, so it stays with you.
2. **Independent checkers.** Run the three checkers in [references/checkers.md](references/checkers.md) in parallel, each in fresh context with only the files it needs:
   - **Accuracy** checks every factual claim in the review against `paper.txt`. A review that is wrong about the paper hurts the user. In a second round, it also checks the response letter's claims against the revised paper.
   - **Author rebuttal** writes the authors' best reply to each comment ("we did that in Section X", "that's standard"). This is the fairness check.
   - **Voice** checks every sentence against voice.md.

   You drafted the review from the notes, so you read the paper the way the notes do. Fresh checkers catch what that reading misses.
3. **Weigh the findings.** They are claims, not edits. Check each against `paper.txt` before acting. Fix confirmed errors, narrow comments a rebuttal partly answers, and apply voice rewrites. If a rebuttal sinks a whole point, flag it rather than drop it, because the point is the user's. checkers.md has the details.

Then report back briefly: where the files are, how many notes you transcribed, the majors in one line each, anything dropped, the checks (what was flagged, changed, and rejected), possible additions, and uncertain readings.

## 4. Revise with the user

Most of the session is this loop. The user's turns are short ("tldr", "is #3 fair?", "drop minor 4", "way too verbose", "commit and push").

- **Re-read the file before every edit.** The user edits the review directly between turns. Keep their edits and wording verbatim unless they ask you to change them. Change only what they asked about.
- **"Is this fair / accurate / true?"** Check it against `paper.txt` and give a verdict per comment first (fair / partly / wrong, with one line of why), then the suggested fix. For a reading not anchored on yours, you can also run the rebuttal checker on just that comment. Don't apply the fix until they say so, unless they already asked you to.
- **"tldr" / "explain #2".** Give a few lines in plain language. Don't edit anything.
- **Restructuring.** When they say what a comment should argue ("it's two points: …"), rebuild it around their points in their order. Don't keep your old framing.
- **Deletions.** Renumber after any deletion, and fix cross-references ("see Major 2").
- **When they correct your voice** ("don't cite lines", "seems AI written"), fix it everywhere in the file, not only where they pointed. Then offer to add the rule to voice.md or to the project's memory so it sticks.
- **Strategy questions** ("would this ever fit the journal?", "can I give major revision now and reject next round?"). Answer candidly, as a colleague would. It's their call, so don't edit the recommendation on your own.
- **Second opinions.** When they paste or point to another model's, session's, or person's review or edits, treat every point as a claim. Check each one against the paper as if you hadn't seen it, then say where it's right, where it's wrong, and what it missed. Hold your own earlier claims to the same standard, and say so plainly when the evidence reverses one.

## 5. Commit

Only when asked. Use one commit per request, with a message naming the manuscript and what changed ("Transcribe notes and draft <ID> review", "Trim <ID> review and remove parentheticals"). Proofs are often large PDFs, so if an HTTPS push times out (HTTP 408), retry with `git -c http.postBuffer=524288000 -c http.lowSpeedLimit=0 -c http.lowSpeedTime=999999 push`. Confirm the push with `git ls-remote origin` against `HEAD`, not the exit code.

## Never

- Cite line numbers in the review.
- Invent a note the user didn't write, or a finding the paper doesn't contain.
- Act on a checker's, another model's, or the authors' claim without checking it against the paper.
- Rewrite the user's own wording when they only asked about something else.
- Fill in scores, recommendations, or editor comments on your own initiative.
