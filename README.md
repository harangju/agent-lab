# Agent Lab

A team of AI scientist colleagues: not assistants who execute, but peers who think, argue, and push back. Each has distinct values and taste. The value is in the dialectic.

Lead is the main Claude session. The other personas run as parallel [subagents](https://code.claude.com/docs/en/sub-agents). Lead briefs them, relays disagreements between them for a round or two, and reports to you (the PI). If you've enabled the experimental [Agent Teams](https://code.claude.com/docs/en/agent-teams) feature, `/lab` can run them as a persistent team instead.

**Key principle:** Surface tensions, don't paper over them. When personas disagree, Lead works the disagreement down to its crux and takes a position grounded in it. Only high-stakes or irreversible calls come to you.

## Install

The lab is three Claude Code skills (`/lab`, `/draft`, `/save`). Install them once, at user level, and they work in every project. Nothing goes into your project's repo except the session state `/save` writes (`context.md` and `log/`).

Quickest: in Claude Code, say

```
Install the agent lab skills from https://github.com/harangju/agent-lab/ into ~/.claude/skills
```

Manual install. To get updates with `git pull`, clone the repo and symlink the skills in:

```bash
git clone https://github.com/harangju/agent-lab.git ~/agent-lab
mkdir -p ~/.claude/skills
for s in lab draft save; do ln -s ~/agent-lab/.claude/skills/$s ~/.claude/skills/$s; done
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
| `/save [topic]` | Checkpoint: append a session log, rewrite `context.md`, and propose lab norms when your feedback keeps recurring. |

Examples:

```
/lab explore how LLM agents coordinate without a shared memory
/lab critique this design: notes/plan.md
/lab review drafts/intro.md
/draft results section from notes/results.md
```

### Writing

`/draft` keeps everything in its own `references/` folder:

- **`STYLE.md`** holds the sentence, punctuation, content, grammar, and composition rules, your voice and phrasing, the response-letter rules, and the hard constraints. Edit it to match your own voice. A `STYLE.md` in the project you're writing in, such as a paper's or a grant's, adds to it and wins on conflicts.
- **Section templates**, loaded one at a time as a task needs them: abstract (Nature summary paragraph), introduction, theory, related work, results (paragraph and full section), discussion, methods, grant section, and response letter, plus paragraph and narrative structure.

Let them argue. Steer the debate as PI: break ties, redirect, ask follow-ups. Follow-ups go back to the same personas, who keep their context.

## Personas

A MECE decomposition of research critique: each persona owns one dimension. Spawn prompts live in `.claude/skills/lab/references/personas.md`.

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

| In the skills (all projects) | `context.md` (per project) | `log/` (per project) |
| ---------------------------- | -------------------------- | -------------------- |
| How to behave: principles, report format, personas, norms, style | What matters now | Everything that happened |
| Stable; you approve changes | Rewritten by every `/save` | Append-only |

Your project's own `AGENTS.md` or `CLAUDE.md` still applies as usual. If a project has no `context.md` yet, the Lead orients from those files and the project's README or plan.

### Session flow

```
Session starts  → Lead reads context.md (or the project's own docs)
During session  → personas work and return results, no file writes
Session ends    → /save appends a session log to log/
                → /save rewrites context.md via compaction
```

Personas don't write files during the session, which avoids conflicts when they run in parallel. All persistence happens at the end, through `/save`.

### Learning loop

The lab improves by learning from your feedback. `/save` logs your steering (tie-breaks, corrections, quality signals, persona calibration). When a pattern recurs across logs, `/save` proposes one of two changes, and applies it only with your approval:

1. **Lab norms → `lab/references/norms.md`**, which every `/lab` run follows.
2. **Persona tuning → `lab/references/personas.md`**, for a persona that is consistently miscalibrated.

A lesson that's specific to one project goes in that project's `context.md` instead.

## File Structure

```
.claude/skills/
├── lab/
│   ├── SKILL.md                 # Lead protocol, principles, report format
│   └── references/
│       ├── personas.md          # persona spawn prompts
│       └── norms.md             # your standing lab norms
├── draft/
│   ├── SKILL.md                 # writing workflow
│   └── references/              # STYLE.md + section templates (loaded on demand)
└── save/SKILL.md                # session log + context.md compaction
```

In each project, `/save` creates:

```
context.md                       # compacted state
log/YYYY-MM-DD-HHmm-topic.md     # session logs (append-only)
```

## Vocabulary

Useful words when talking to Claude:

- **connective tissue**: prose that links sections or ideas
- **load-bearing**: assumptions or components critical to the argument

## License

MIT
