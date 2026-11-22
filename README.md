# Agent Lab

A team of AI scientist colleagues: not assistants who execute, but peers who think, argue, and push back. Each has distinct values and taste. The value is in the dialectic.

Lead is the main Claude session. The other personas run as parallel [subagents](https://code.claude.com/docs/en/sub-agents). Lead briefs them, relays disagreements between them for a round or two, and reports to you (the PI). If you've enabled the experimental [Agent Teams](https://code.claude.com/docs/en/agent-teams) feature, `/lab` can run them as a persistent team instead.

**Key principle:** Surface tensions, don't paper over them. When personas disagree, Lead works the disagreement down to its crux and takes a position grounded in it. Only high-stakes or irreversible calls come to you.

## Install

The lab is three [Agent Skills](https://agentskills.io) (`/lab`, `/draft`, `/save`), written for Claude Code. Other agents that read the format can load them too, but `/lab`, `/fan-out`, `/research`, and the `/referee` checkers work best with subagents. Three more sit alongside the lab: `/research` orchestrates a full stage-gated research loop from a starting question to a verified manuscript, `/fan-out` schedules a batch of independent work, and `/referee` turns a paper you marked up by hand into a transcription of your notes and a terse referee report in your voice. Install them once, at user level, and they work in every project. Nothing goes into your project's repo except the session state `/save` writes (`CONTEXT.md` and `log/`).

Quickest: in Claude Code, say

```
Install the agent lab skills from https://github.com/harangju/agent-lab/ into ~/.agents/skills and ~/.claude/skills
```

Manual install. To get updates with `git pull`, clone the repo and symlink the skills in:

```bash
git clone https://github.com/harangju/agent-lab.git ~/agent-lab
mkdir -p ~/.agents/skills ~/.claude/skills
for s in lab draft save fan-out referee research; do
  ln -s ~/agent-lab/.agents/skills/$s ~/.agents/skills/$s   # cross-client location
  ln -s ~/agent-lab/.agents/skills/$s ~/.claude/skills/$s   # Claude Code
done
```

To keep your own edits (personas, norms, `STYLE.md`) private, copy the folders with `cp -R` instead of symlinking them. This is a public repo, so anything you commit to a clone goes public when you push.

**Paper search (recommended).** The personas use two tools when they're connected:

- [Semantic Scholar](https://www.semanticscholar.org/product/api) for exact paper lookup and citation graphs
- [Consensus](https://consensus.app) for question-level literature search

Add Semantic Scholar at user scope (requires [`uv`](https://docs.astral.sh/uv/)):

```bash
claude mcp add --transport stdio --scope user semantic-scholar -- uvx semantic-scholar-fastmcp
```

The free tier allows 100 requests per 5 minutes, which a literature-heavy `/lab` run can use up. With a key, add `--env SEMANTIC_SCHOLAR_API_KEY=<your key>` right after `add`. Connect Consensus from claude.ai's connector settings.

## How to Use

| Command | What it does |
| ------- | ------------ |
| `/lab [task]` | Convene the group on anything: a topic to explore, an idea or design to critique, results to interpret, a section to draft, a draft to review, or feedback to triage. Lead picks the right personas and phases. Writing tasks go through `/draft`. |
| `/draft [section or file] [ask]` | Draft or revise prose on its own: a paper section, abstract, grant section, related work, or response letter. Follows `STYLE.md` and loads only the section template it needs. |
| `/save [topic]` | Checkpoint: append a session log, rewrite `CONTEXT.md`, and propose standing rules when your feedback keeps recurring. |
| `/fan-out [batch]` | Schedule a batch of independent work so you review once. Lead splits it across parallel workers, brings the pieces together, checks them, and hands you one review page. |
| `/research [question or resume]` | Run a six-stage research loop from a starting question to a verified manuscript, composing `/lab`, `/draft`, `/save`, and `/fan-out` with automated 1-seed pilots, raw-log inspection, style/provenance linting, and five PI decision gates. |

Examples:

```
/research does double-blind peer review change acceptance gaps across subfields?
/research resume
/lab explore how LLM agents coordinate without a shared memory
/lab critique this design: notes/plan.md
/lab review drafts/intro.md
/draft results section from notes/results.md
/fan-out the five open items in TODO.md
```

### Writing

`/draft` keeps everything in its own `references/` folder:

- **`STYLE.md`** holds the sentence, punctuation, content, grammar, and composition rules, your voice and phrasing, the response-letter rules, and the hard constraints. Edit it to match your own voice. A `STYLE.md` in the project you're writing in, such as a paper's or a grant's, adds to it and wins on conflicts.
- **Section templates**, loaded one at a time as a task needs them: abstract (Nature summary paragraph), introduction, theory, related work, results (paragraph and full section), discussion, methods, grant section, and response letter, plus paragraph and narrative structure.

Let them argue. Steer the debate as PI: break ties, redirect, ask follow-ups. Follow-ups go back to the same personas, who keep their context.

### Fan-out

`/fan-out` is about scheduling, not critique. Hand it a batch of independent work, such as five grant sections, a list of open questions, or a release's worth of fixes. Lead then:

1. Proposes a split and waits for your go. No two workers own the same thing, and every rule the pieces share gets one owner.
2. Runs the workers in parallel. A worker can be a side session, a subagent, or a `/lab` or `/draft` run.
3. Brings the pieces together, checks them the way you would, and fixes what breaks where they meet.
4. Hands you one review page. Each change gets a Before and a Now, shown as a visual (screenshots, a chart, a table or an illustration), plus a tag saying whether Lead saw it working.

You review once, at the end. Fixes from your review go on the same page.

## Personas

A MECE decomposition of research critique: each persona owns one dimension. Spawn prompts live in `.agents/skills/lab/references/personas.md`.

| Persona | Dimension | Asks | Prevents |
|---------|-----------|------|----------|
| **Lead** (you're talking to it) | Presentation | Briefs the group, works disagreements to a crux, presents the argument | Weak framing, unclear narrative |
| **Skeptic** | Novelty | "Has this been done? What's actually new?" | Wasting time on existing work |
| **Methodologist** | Rigor | "Is this sound? Would it generalize?" | Publishing claims you can't defend |
| **Visionary** | Impact | "So what? Who cares? Think bigger." | Working on incremental stuff that won't matter |
| **Newcomer** | Clarity | "You lost me. Explain it simply." | Jargon-heavy work that nobody reads |
| **Connector** | Integration | "How does this relate to X in [other field]?" | Missing complementary work, thinking in silos |

**Natural tensions:**
- Visionary wants to swing big → Methodologist asks if the methods support it
- Visionary says "Nature material" → Skeptic asks what's actually new
- Methodologist wants more experiments → Visionary asks if it's worth the time
- Connector draws links to adjacent fields → Skeptic asks if those links are real
- Newcomer says the framing is unclear → Lead defends, others weigh in on whether the confusion reveals a real gap

## Context Management

The lab keeps its rules in the skills and its state in your project.

| In the skills (all projects) | `CONTEXT.md` (per project) | `log/` (per project) |
| ---------------------------- | -------------------------- | -------------------- |
| How to behave: principles, report format, personas, norms, style | What matters now | Everything that happened |
| Stable; you approve changes | Rewritten by every `/save` | Append-only |

Your project's own `AGENTS.md` or `CLAUDE.md` still applies as usual. If a project has no `CONTEXT.md` (or `context.md`) yet, the Lead orients from those files and the project's README or plan.

### Session flow

```
Session starts  → Lead reads CONTEXT.md (or context.md / the project's own docs)
During session  → personas work and return results, no file writes
Session ends    → /save appends a session log to log/
                → /save rewrites CONTEXT.md via compaction
```

Personas don't write files during the session, which avoids conflicts when they run in parallel. All persistence happens at the end, through `/save`.

### Learning loop

`/save` logs your steering (tie-breaks, corrections, quality signals, persona calibration). When a pattern recurs across logs, `/save` proposes a standing rule routed to the file that governs it, and applies it only with your approval:

1. **Agent workflow, coding, or communication → `AGENTS.md` / `CLAUDE.md`** (or user-level agent rules if cross-project).
2. **Writing or formatting → `STYLE.md`** (project-level, or `draft/references/STYLE.md` across projects).
3. **`/lab` deliberation norms → `lab/references/norms.md`**, which every `/lab` run follows.
4. **`/lab` persona tuning → `lab/references/personas.md`**, for a persona that is consistently miscalibrated.

A research lesson or decision specific to one project goes in that project's `CONTEXT.md` instead.

## File Structure

```
.agents/skills/               # .claude/skills is a symlink to this
├── lab/
│   ├── SKILL.md                 # Lead protocol, principles, report format
│   └── references/
│       ├── personas.md          # persona spawn prompts
│       └── norms.md             # your standing lab norms
├── draft/
│   ├── SKILL.md                 # writing workflow
│   └── references/              # STYLE.md + section templates (loaded on demand)
├── save/SKILL.md                # session log + CONTEXT.md compaction
├── fan-out/
│   ├── SKILL.md                 # split, integrate, check, hand over one review
│   ├── template.html            # the review page
│   └── references/code.md       # extra steps when the batch is code
└── referee/
    ├── SKILL.md                 # marked-up PDF → comments.md → review → revisions
    ├── scripts/find_ink.py      # locate handwriting and save zoomed crops
    └── references/              # formats.md (comments + review), voice.md, checkers.md
└── research/
    ├── SKILL.md                 # stage-gated research orchestrator (Stages 0–6, including R&R)
    ├── template.html            # PI gate decision card
    ├── references/              # gates.md (schemas + S-tier checks), scaffold.md, revision.md
    └── scripts/                 # lint_manuscript.py, pilot_scan.py, pilot_workflow.py, stage4_review_workflow.py, checkpoint.py
```

In each project, `/save` creates:

```
CONTEXT.md                       # compacted state
log/YYYY-MM-DD-HHmm-topic.md     # session logs (append-only)
```

## Vocabulary

Useful words when talking to Claude:

- **connective tissue**: prose that links sections or ideas
- **load-bearing**: assumptions or components critical to the argument

## License

MIT
