---
name: fan-out
description: Schedule a batch of independent work so the user reviews once. Split it across parallel workers, integrate and check the results yourself, and hand back one review package. Use when the user hands over a list of work, such as code fixes, doc or grant sections, research questions or drafts, and wants it done in parallel and reviewed in one pass.
---

# Fan out

You are the lead. Workers do the pieces. You split the work, bring it back together, check it, and hand the user one package. This is scheduling: the user's attention is the scarce thing. They should review once, at the end, and only see finished work you have already checked.

Follow the project's own rules (AGENTS.md, CLAUDE.md, a STYLE.md) for how its work is built, run and published. This skill does not override them.

**If the batch is code, also read [references/code.md](references/code.md).**

## Workers

- **Side sessions** for pieces that take a while, write files, or that the user might want to open on their own.
- **Subagents** for short pieces whose results you need in this turn.
- A worker can run another skill, such as `/lab` to argue out a question or `/draft` to write a section. Fan-out schedules the work; it doesn't care what kind of work it is.

## 1. Propose the split, then wait

Before starting anything, show the user:

- **The workers**, as a table: one row each, with the items it covers. Split so no two workers own the same thing, whether that's files, doc sections, or questions.
- **Shared rules and who owns them.** List everything more than one worker depends on, such as a deadline, a term, a number, a name, a format, or a claim that shows up in several places. Give each one owner. Write the exact rule into every brief that touches it.
- **Specs, not finished work**, for any item that needs a decision before it can be done.
- **What you'll leave out**: items that need the user's call. List them as open questions. Don't guess.
- **Your defaults**, numbered, so the user can change one by its number.
- **What stays untouched**, like production or a submitted draft.

Wait for a clear go-ahead.

> The worst bug in the first run came from a shared rule with no owner. The app and web showed the refund day as the deadline, and the emails showed the day before. Each worker followed its own reading of the spec. Both were reasonable, and they disagreed.

## 2. Start the workers

Each brief says:

- the items it covers and what it owns
- the shared rules it must follow, word for word
- what it should check itself, and what to leave for you (anything that needs the whole batch together)
- to report what it did, what it checked, and what it couldn't check

Do any specs yourself while the workers run.

## 3. While they work

- **Capture "before"** for everything the batch will change: screenshots of screens and pages, and the data behind every number, figure or claim, so you can redraw it next to "now" on the same scale. You can't get it back once the work lands.
- **Start the review page now** from [template.html](template.html), and fill it in as you go.
- Keep a short **status file** with the workers, where each one's work is, what's integrated, what's checked, and what's open. A long run will compact your context. The review page and the status file are what survive it.

## 4. Integrate and check

- Bring every piece into one place: a branch, a doc, a folder.
- Check it the way the user would: use the app, read the doc from start to finish, rerun the analysis.
- **Look where the pieces meet.** Check every shared rule from step 1 everywhere it shows up. Most problems surface here.
- Fix what breaks yourself. Don't send it back to a worker.

## 5. Hand over the package

- **The work, in one place**: a PR, a doc, or a folder.
- **One review page**, made from [template.html](template.html). Keep its structure and look, replace every `{{placeholder}}`, and delete the example items. Group it in the order the user will go through it. For each change:
  - **Before:** what the user saw before, with a concrete example.
  - **Now:** what they see instead, with the same example.
  - **A visual** of before and now. See [Visuals](#visuals).
  - **Same** (optional): something nearby that didn't change.
  - **Try** (optional): the shortest path to see it.
  - **Checked:** *Seen working*, *Partly seen*, or *Not seen*. Be honest about which.
- **Found while checking**: problems you found and haven't fixed, written as Before and Now, so the user can say "fix both".
- **Not checked**: what you couldn't check, and why.
- **Needs your call**: the open questions from step 1, plus any new ones.

Close with a short message that links the work and the page and says what's left for the user.

## 6. After review

The user's fixes go into the same place, on the same page. Add a **"Fixed after review"** section, and strike the items in "Found while checking" as you fix them. Don't start a new package.

## Visuals

Show every change; don't only tell it. Start from a visual, without waiting to be asked, and fall back to words alone only when there's truly nothing to draw.

Pick the visual that shows the change:

| What changed | Show it as |
|---|---|
| A screen or a page | Before and now screenshots, side by side, taken from the same place |
| A number, like an estimate, a rate or a count | One chart with before and now on the same axes |
| Many numbers | A small table with before, now, and the difference |
| A mechanism, a design or a plan | An illustration or diagram, before and now |
| Prose | The old and new text side by side |

- **One combined figure beats two pictures** whenever before and now share axes. Overlay them so the move is the first thing you see.
- **Build visuals from the real results**: the actual screenshots, the actual data files. Use the same scale for before and now, and put the sample size and the source in a note. Never draw what *should* happen.
- **Keep them plain.** Give each figure one plain headline that says what changed. The writing rules below apply to figures too: no code names in the labels, and the stats go in a note, not on the figure.
- Draw charts and illustrations as inline SVG on the review page, using the page's colors, so they work in light and dark mode.

## Writing for the reviewer

Everything the user reads, including the review page, a PR description and your messages, follows these rules:

- **Describe what the reader sees or does, in plain words**: in the app, on the page, in the result. Leave function names, file names and phrases like "the server works out…" out of the main text. If a detail of how it works matters, put it in a small note under the change.
- **Write every change as a separate Before line and Now line, with a concrete example.**
  - Before: The app said Dec 8, the email said Dec 7.
  - Now: Both say Dec 7.
- **Show it and say it.** Every Before and Now pair gets a visual, and words that stand on their own without it.
- **Add a Same line when something nearby didn't change**, so the reviewer doesn't assume it did. For example: "Same: saving the shipping address still overwrites your return address."
- **Before publishing, check every sentence.** If it describes how the work was done instead of what the reader sees, rewrite it.
- Say what you saw, not what should happen. "I saw Dec 7 on the Home banner" beats "the banner will show the correct date".
- Keep "not checked" in plain view. Don't bury it in a footnote.
