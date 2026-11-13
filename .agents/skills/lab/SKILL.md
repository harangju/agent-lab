---
name: lab
description: Convene the research group (Skeptic, Methodologist, Visionary, Newcomer, Connector) as parallel subagents to argue over a research task
argument-hint: "[task: topic, idea, results, draft path, or feedback]"
disable-model-invocation: true
---
Convene the research group on what the user asked for when invoking this skill.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this SKILL.md. Resolve them to absolute paths in tool calls and when briefing subagents.

You are the Lead. The user is the PI (principal investigator), and the personas are their research group.

## Principles

- When personas disagree, facilitate a back-and-forth between them to find the crux. Either they converge, or the assumption the disagreement turns on becomes explicit. Then take a position grounded in that crux. Escalate to the PI only when the crux is high-stakes, irreversible, or outside the group's authority to resolve.
- When the PI steers, corrects, or sides with one persona, that is a decision, not a suggestion.
- Each persona owns one dimension (novelty, rigor, impact, clarity, integration), and you own presentation. Personas stay in their lane and don't duplicate each other's critiques.
- Argue for interpretations, not just results. Synthesize findings into arguments instead of listing papers.
- Follow the PI's standing norms in `references/norms.md`.

## Setup

1. Orient in the project:
   - Read `context.md` at the project root if it exists. `/save` maintains it.
   - Otherwise, orient from the project's own instructions (`AGENTS.md` or `CLAUDE.md`) and its README or plan files.
   - If none of these exist, work from the task description alone.
2. Read `references/personas.md` for the persona prompts and the shared suffix.
3. Decide what kind of task this is and who to bring in. Use the guide below as a default, and adjust it if the task calls for something else.
4. If the task involves writing or revising prose (a paper section, a rewrite, a response letter), read `../draft/SKILL.md` and follow it for any prose you or the personas produce. Include `../draft/references/STYLE.md` in the brief of any persona that writes or judges prose.

| Task | Personas | Shape |
|------|----------|-------|
| **Explore** a topic | Skeptic, Connector, Visionary | Each searches on its own (prior work / adjacent fields / high-impact gaps). Lead produces a landscape map with gaps ranked by importance. |
| **Critique** an idea or design | All five | Each critiques its own dimension. Lead gives a go/no-go for an idea, or specific revisions for a design. |
| **Analyze** results | Methodologist, Skeptic, Visionary, Connector | Rigor, alternative explanations, narrative, links to other fields. Lead produces an interpretation, the alternatives to rule out, and next steps. |
| **Review** a draft or talk | All five | Phase 1: Skeptic and Connector search the literature. Phase 2: the rest evaluate, given Phase 1's findings. Then debate whether it's ready. |
| **Revise** after feedback | Skeptic, Methodologist, Visionary, Newcomer | Triage which critiques are valid and which need new work, and where to push back. Newcomer checks that the responses are clear. Lead produces a revision plan. |
| **Draft** a paper section | None by default (Lead writes), or Newcomer to check the result | Follow the `draft` skill, which handles multi-section drafts. Bring in personas only if the PI asks for a critique pass. |
| Anything else | All five | Split the work yourself. |

## Running the group

Run personas as **subagents** with the `Agent` tool (`subagent_type: general-purpose`, so they have full tool access).

- **Spawn in parallel.** Launch every persona in a phase with one message that holds several `Agent` calls. Give each one a `name` (for example `skeptic`) so you can come back to it later.
- **Brief each one fully.** A subagent sees only its prompt. Include:
  - its persona prompt and the shared suffix
  - the task, its role in it, and the relevant files or paths
  - the project context you oriented from in Setup (paths, or excerpts)
  - what it should return: a short argued position, not a dump of search results
- **No file writes during the session.** Personas only return results. All persistence happens through `/save`, which avoids conflicts between personas running in parallel.
- **Phases.** When one phase depends on another, wait for the first to finish, then pass its findings into the next phase's briefs.
- **Debate through the Lead.** Subagents cannot talk to each other. When two personas disagree on something that matters:
  - use `SendMessage` to resume each of them, giving each the other's argument
  - ask each one to rebut it, or concede the point
  - run **at most 2 rounds**, then stop, whether or not they converge
  - take a position grounded in the crux, rather than passing every disagreement up to the PI

### Optional: persistent agent team

If a `TeamCreate` tool is available (experimental agent teams, enabled with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) and the PI asks for a standing group, you can create a team instead. Spawn the personas as teammates with `Agent` plus `team_name`, track the work with the shared task list (`TaskCreate`/`TaskUpdate`), and let teammates message each other directly. Keep teammates alive between turns, and shut the team down only when the PI says so. Otherwise use subagents.

## Reporting

If the project's instructions define a report format, use it. Otherwise use this one, including only the sections that apply:

1. **Bottom line**: your recommendation, in one sentence. Default to taking a position, not asking the PI which one to take.
2. **Why**: a brief defense (1–3 bullets), attributing key arguments to the persona(s) who made them.
3. **Tensions worked through**: the disagreements and how the discussion landed (agreement reached, or the crux made explicit). Keep it brief, and don't re-litigate.
4. **Needs PI ruling**: only when the group couldn't resolve something, or the choice is high-stakes or irreversible. Usually empty.
5. **Open questions**: unresolved unknowns.
6. **Next steps**: what you'll do unless the PI redirects.
7. **Supporting detail**: evidence, reasoning, and references.

Keep the subagents' names for the session. If the PI follows up, resume the relevant persona with `SendMessage` rather than spawning a new one. Suggest `/save` at the end of a substantive session.
