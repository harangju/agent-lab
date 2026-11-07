# Agent Lab

A team of AI scientist colleagues: not assistants who execute, but peers who think, argue, and push back. Each has distinct values and taste. The value is in the dialectic.

Lead is the main Claude session. The other personas run as parallel [subagents](https://code.claude.com/docs/en/sub-agents). Lead briefs them, relays disagreements between them for a round or two, and reports to you (the PI). If you've enabled the experimental [Agent Teams](https://code.claude.com/docs/en/agent-teams) feature, `/lab` can run them as a persistent team instead.

**Key principle:** Surface tensions, don't paper over them. When personas disagree, Lead works the disagreement down to its crux and takes a position grounded in it. Only high-stakes or irreversible calls come to you.

## Quick Start

Have Claude Code? Run this in Claude in any repo:

```
Set up the agent lab in this repo! https://github.com/harangju/agent-lab/
```

Claude will clone the template, copy the skills and config into your project, and walk you through setup.

## Manual Setup

This is a GitHub template repo. Click **"Use this template"** to create your own copy, then:

1. **Set your field.** Open `CLAUDE.md` and replace `[field]` on line 1 with your research area (e.g., "computational neuroscience", "mechanism design", "synthetic biology").

2. **Set your direction.** In `CLAUDE.md` under "Current Direction", add 1–2 lines describing what the lab is working on now.

3. **(Optional) Add a Semantic Scholar API key.** The Semantic Scholar MCP server is pre-configured in `.mcp.json` (requires [`uv`](https://docs.astral.sh/uv/)). To use a key, export `S2_API_KEY` in your shell. Leave it unset to use the free tier, which allows 100 requests per 5 minutes; a literature-heavy `/lab` run can use that up quickly. Get a key at [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api).

4. **Run Claude Code** from the repo root. The skills will be available as slash commands.

## How to Use

| Command | What it does |
| ------- | ------------ |
| `/lab <task>` | Convene the group on anything: a topic to explore, an idea or design to critique, results to interpret, a section to draft, a draft to review, or feedback to triage. Lead picks the right personas and phases. Writing tasks go through `/draft`. |
| `/draft <section or file> [ask]` | Draft or revise prose on its own: a paper section, abstract, grant section, related work, or response letter. Follows `STYLE.md` and loads only the section template it needs. |
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

A MECE decomposition of research critique: each persona owns one dimension. Spawn prompts live in `personas.md`.

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

State persists across sessions through three layers.

| `CLAUDE.md`   | `context.md`            | `log/`                   |
| ------------- | ----------------------- | ------------------------ |
| How to behave | What matters now        | Everything that happened |
| Stable        | Rewritten every session | Append-only              |
| You maintain  | Lead maintains          | Lead maintains           |

### Session flow

```
Session starts  → Lead reads context.md
During session  → personas work and return results, no file writes
Session ends    → /save appends a session log to log/
                → /save rewrites context.md via compaction
```

Personas don't write files during the session, which avoids conflicts when they run in parallel. All persistence happens at the end, through `/save`.

### Learning loop

The lab improves by learning from your feedback. `/save` logs your steering (tie-breaks, corrections, quality signals, persona calibration). When a pattern recurs across logs, `/save` proposes one of two changes, and applies it only with your approval:

1. **Lab norms → `CLAUDE.md`**, which every session reads.
2. **Persona tuning → `personas.md`**, for a persona that is consistently miscalibrated.

## File Structure

```
├── CLAUDE.md                        # lab rules + session protocol (auto-loaded)
├── personas.md                      # persona spawn prompts (read by Lead)
├── context.md                       # compacted state (Lead maintains)
├── log/                             # session logs (append-only)
│   └── YYYY-MM-DD-HHmm-topic.md
├── .mcp.json                        # Semantic Scholar MCP server
└── .claude/
    ├── settings.json                # hooks
    └── skills/
        ├── lab/SKILL.md
        ├── draft/SKILL.md           # writing workflow
        ├── draft/references/        # STYLE.md + section templates (loaded on demand)
        └── save/SKILL.md
```

## Vocabulary

Useful words when talking to Claude:

- **connective tissue**: prose that links sections or ideas
- **load-bearing**: assumptions or components critical to the argument

## License

MIT
