# Agent Lab

A team of AI scientist colleagues — not assistants who execute, but peers who think, argue, and push back. Each has distinct values and taste. The value is in the dialectic.

Built on [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams). Lead is the team lead; other personas are teammates. You (the PI) steer through Lead. Coordination, messaging, and task management are handled by Agent Teams natively.

**Key principle:** Surface tensions, don't force consensus. Disagreements are logged, not resolved. You break ties.

## Quick Start

Have Claude Code? Run this in any repo:

```
claude "Set up the agent lab in this repo! https://github.com/harangju/agent-lab/"
```

Claude will clone the template, copy the skills and config into your project, and walk you through setup.

## Manual Setup

This is a GitHub template repo. Click **"Use this template"** to create your own copy, then:

1. **Set your field.** Open `CLAUDE.md` and replace `[field]` on line 1 with your research area (e.g., "computational neuroscience", "mechanism design", "synthetic biology").

2. **Set your direction.** In `CLAUDE.md` under "Current Direction", add 1–2 lines describing what the lab is working on now.

3. **(Optional) Add a Semantic Scholar API key.** The Semantic Scholar MCP server is pre-configured in `.claude/settings.json`. Replace `your-api-key-here` with your key, or remove the `env` block to use the free tier. Free tier is 100 requests / 5 min — an `/explore` can burn through this quickly. Get a key at [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api).

4. **Run Claude Code** from the repo root. The skills will be available as slash commands.

## How to Use

Pick the skill that matches your stage:

| You have...          | Run...                   |
| -------------------- | ------------------------ |
| A topic, no idea yet | `/explore [topic]`       |
| An idea or design    | `/plan [idea/design]`    |
| Results              | `/analyze [results]`     |
| A draft or talk      | `/write [path]`          |
| Feedback to address  | `/revise [feedback]`     |

Let them argue. Steer the debate as PI — break ties, redirect, ask follow-ups.

## Personas

MECE decomposition of research critique. Each persona owns one dimension. Lead is the team lead (presents, defends, handles persistence); others are teammates. Spawn prompts live in `personas.md`.

| Persona | Dimension | Asks | Prevents |
|---------|-----------|------|----------|
| **Lead** (team lead) | Presentation | Steel-mans the argument, defends it, handles persistence | Weak framing, unclear narrative |
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

## Workflows

Skills map to the research pipeline. Each skill is a stage where the group argues about your work.

```
explore → plan → [execute] → analyze → write
                                         ↓
                                       revise ←→ (loops back to any stage)
```

Bootstrapping: explore → plan. Revision can loop back to earlier stages.

### Explore

Parallel exploration. No presenter — everyone searches independently and synthesizes. `/explore [topic]`

### Plan

Present → critique → debate. Covers both early ideas (go/no-go) and concrete designs (methodology review). `/plan [idea or design]`

### Analyze

Present results → argue over interpretation → build narrative. The group debates what the results mean, not just whether they're correct. `/analyze [results]`

### Write

Phased critique of any written artifact — manuscript, talk, poster. Phase 1: extract argument + search literature. Phase 2: evaluate by dimension. Phase 3: debate readiness. `/write [path]`

### Revise

Triage incoming feedback — reviewer comments, collaborator notes, PI comments — and plan revision. The group debates what to concede vs. push back on, then produces a revision plan. `/revise [feedback]`

### Reflect

Meta-learning. Synthesizes PI feedback from `log/` into candidate lab norms and persona calibration suggestions. `/reflect`

## Context Management

State persists across sessions through three layers.

| `CLAUDE.md`   | `context.md`            | `log/`                   |
| ------------- | ----------------------- | ------------------------ |
| How to behave | What matters now        | Everything that happened |
| Stable        | Rewritten every session | Append-only              |
| You maintain  | Lead maintains          | Lead maintains           |

### Session flow

```
Session starts  → agents read context.md
During session  → agents work and return results, no file writes
Session ends    → Lead appends session log to log/
                → Lead rewrites context.md via compaction
```

Agents don't write files during the session — avoids conflicts when running in parallel. All persistence happens at the end through Lead.

### Learning loop

The lab improves by learning from your feedback. Two levels:

**1. Lab norms → `CLAUDE.md`** (all personas read)

Your steering — tie-breaks, corrections, quality signals — gets logged to `log/` with everything else. Periodically run `/reflect` to synthesize recurring patterns into Lab Norms.

**2. Persona tuning → `personas.md`** (per-persona)

When a specific persona is consistently miscalibrated, update its spawn prompt in `personas.md` directly.

## File Structure

```
├── CLAUDE.md                        # lab rules + session protocol (auto-loaded)
├── personas.md                      # spawn prompts (read by Lead on demand)
├── context.md                       # compacted state (Lead maintains)
├── log/                             # session logs (Lead appends)
│   └── YYYY-MM-DD-HHmm.md
└── .claude/
    ├── settings.json                # MCP config, permissions
    └── skills/
        ├── explore/SKILL.md
        ├── plan/SKILL.md
        ├── analyze/SKILL.md
        ├── write/SKILL.md
        ├── revise/SKILL.md
        └── reflect/SKILL.md
```

## License

MIT
