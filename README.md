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

3. **(Optional) Add a Semantic Scholar API key.** The Semantic Scholar MCP server is pre-configured in `.claude/settings.json`. Replace `your-api-key-here` with your key, or remove the `env` block to use the free tier. Free tier is 100 requests / 5 min — a `/sprint` can burn through this quickly. Get a key at [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api).

4. **Run Claude Code** from the repo root. The skills will be available as slash commands.

## How to Use

Pick the workflow that matches your stage:

| You have...          | Run...                   |
| -------------------- | ------------------------ |
| A topic, no idea yet | `/sprint [topic]`        |
| An idea              | `/review-idea [idea]`    |
| A design             | `/review-design`         |
| Results              | `/review-results`        |
| A draft              | `/review-draft [path]`   |
| Reviewer comments    | `/review-rr`             |
| A talk to prep       | `/presentation`          |

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

Three workflow types. Sprint for exploration, Review for everything with a presenter, Presentation for sequential talk prep.

```
Explore → Design → Execute → Analyze → Write
                                          ↓
                                       Iterate
                                      ↗  ↑  ↖
                              Draft    Present  R&R
                              Review   Review   Review
```

Bootstrapping: Sprint → Review (idea) → Review (design). Revision can loop back to earlier stages.

### Sprint

Parallel exploration. No presenter — everyone searches independently and synthesizes.

### Review

Present → critique → debate → synthesize. One template, parameterized by what's being reviewed.

| Skill             | What's reviewed          | Personas                                           | Output                          |
| ----------------- | ------------------------ | -------------------------------------------------- | ------------------------------- |
| `/review-idea`    | New idea                 | All 6                                              | Go/no-go + refined direction    |
| `/review-design`  | Method plan              | Lead, Methodologist, Skeptic, Connector            | Validated design                |
| `/review-results` | Results + interpretation | Lead, Methodologist, Skeptic, Visionary, Connector | Interpretation + story          |
| `/review-draft`   | Manuscript               | All 6                                              | Structured feedback             |
| `/review-rr`      | Reviews + manuscript     | Lead, Methodologist, Skeptic, Visionary, Newcomer  | Revision plan + response letter |

### Presentation

Sequential section-by-section review with live defense. Structurally different from Review — teammates react as they go, catching "you lost me at section 2."

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
        ├── sprint/SKILL.md
        ├── review-idea/SKILL.md
        ├── review-design/SKILL.md
        ├── review-results/SKILL.md
        ├── review-draft/SKILL.md
        ├── review-rr/SKILL.md
        ├── presentation/SKILL.md
        └── reflect/SKILL.md
```

## License

MIT
