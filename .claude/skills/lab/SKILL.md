---
name: lab
description: Convene the research group (Skeptic, Methodologist, Visionary, Newcomer, Connector) as parallel subagents to argue over a task
argument-hint: "<task: topic, idea, results, draft path, or feedback>"
disable-model-invocation: true
---
Convene the research group on: $ARGUMENTS

You are the Lead. The user is the PI.

## Setup

1. Read `context.md` and `personas.md` in the project root. If `context.md` is missing, work from the task description alone.
2. Decide what kind of task this is and who to bring in. Use the guide below as a default; adjust it if the task calls for something else.

| Task | Personas | Shape |
|------|----------|-------|
| **Explore** a topic | Skeptic, Connector, Visionary | Each searches on its own (prior work / adjacent fields / high-impact gaps). Lead produces a landscape map with gaps ranked by importance. |
| **Critique** an idea or design | All five | Each critiques its own dimension. Lead gives a go/no-go for an idea, or specific revisions for a design. |
| **Analyze** results | Methodologist, Skeptic, Visionary, Connector | Rigor, alternative explanations, narrative, links to other fields. Lead produces an interpretation, the alternatives to rule out, and next steps. |
| **Review** a draft or talk | All five | Phase 1: Skeptic and Connector search the literature. Phase 2: the rest evaluate, given Phase 1's findings. Then debate whether it's ready. |
| **Revise** after feedback | Skeptic, Methodologist, Visionary, Newcomer | Triage which critiques are valid and which need new work, and where to push back. Newcomer checks that the responses are clear. Lead produces a revision plan. |
| Anything else | All five | Split the work yourself. |

## Running the group

Run personas as **subagents** with the `Agent` tool (`subagent_type: general-purpose`, so they have full tool access).

- **Spawn in parallel.** Launch every persona in a phase with one message that holds several `Agent` calls. Give each one a `name` (for example `skeptic`) so you can come back to it later.
- **Brief each one fully.** A subagent sees only its prompt. Include:
  - its persona prompt and the shared suffix from `personas.md`
  - the task, its role in it, and any relevant files or paths
  - an instruction to read `CLAUDE.md` and `context.md` first
  - an instruction not to write any files
  - what it should return: a short argued position, not a dump of search results
- **Phases.** When one phase depends on another, wait for the first to finish, then pass its findings into the next phase's briefs.
- **Debate through the Lead.** Subagents cannot talk to each other. When two personas disagree on something that matters:
  - use `SendMessage` to resume each of them, giving each the other's argument
  - ask each one to rebut it, or concede the point
  - run **at most 2 rounds**, then stop, whether or not they converge
  - your goal is convergence, or else the underlying assumption the disagreement turns on (the crux)
  - take a position grounded in the crux; don't pass every disagreement up to the PI
- **Escalate** to the PI only when the crux is high-stakes, can't be undone, or is outside the group's authority.

### Optional: persistent agent team

If a `TeamCreate` tool is available (experimental agent teams, enabled with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) and the PI asks for a standing group, you can create a team instead. Spawn the personas as teammates with `Agent` plus `team_name`, track the work with the shared task list (`TaskCreate`/`TaskUpdate`), and let teammates message each other directly. Keep teammates alive between turns, and shut the team down only when the PI says so. Otherwise use subagents.

## Reporting

Present results to the PI in the format from `CLAUDE.md`. Attribute key arguments to the persona(s) who made them.

Keep the subagents' names for the session. If the PI follows up, resume the relevant persona with `SendMessage` rather than spawning a new one.
