---
name: draft
description: Draft a paper section using rhetorical structure templates
---
Draft this paper section: $ARGUMENTS

Read `context.md` for current research state. If a manuscript draft exists, read it for context. Identify which section is requested (abstract, introduction, results, discussion, methods). If multiple sections or "all" is requested, spawn one subagent per section in parallel — each gets only its own template.

For each section, follow the **move → write → verify** loop: draft the move, then check it against the verify step before moving on. Do not draft the next move until the current one passes.

---

## Abstract (Nature summary paragraph format)

Target: 150–250 words. One paragraph. Every sentence has a job.

**Move 1: Basic introduction** (1–2 sentences)
Broad context, comprehensible to any scientist. What field? Why does it matter?
- ✓ Verify: Would a biologist, physicist, and economist all understand this?

**Move 2: Detailed background** (2–3 sentences)
Narrower context for scientists in related disciplines. What's known?
- ✓ Verify: Does this give enough context to understand the gap (Move 3)?

**Move 3: Problem statement** (1 sentence)
The specific gap this study addresses. Signal the pivot: "However, ..."
- ✓ Verify: Is the gap specific and falsifiable, not vague ("poorly understood")?

**Move 4: Main result** (1 sentence)
"Here we show ..." State the central finding.
- ✓ Verify: Does this directly address the gap in Move 3? Does it pass the So What test?

**Move 5: Result in context** (2–3 sentences)
What the main result reveals compared to previous knowledge. What's new or surprising?
- ✓ Verify: Is this comparison to prior work concrete, not generic?

**Move 6: Broader implications** (1–2 sentences)
What this means for the field.
- ✓ Verify: Does Move 1 set up a straight line to this sentence?

**Move 7: Broader perspective** (2–3 sentences, optional)
Accessible to any discipline. Include if important for general readership.
- ✓ Verify: Would this make a non-specialist care?

**Final check:** Read the full abstract aloud. Does it flow as one paragraph? Is it 150–250 words?

---

## Introduction (CARS model — Create a Research Space)

3–5 paragraphs total.

**Move 1: Establish territory** (1–2 paragraphs)
Claim importance — why this field/topic matters. Review prior work — what has been established. Set the stage for the gap.
- ✓ Verify: Are citations selective (key papers, not exhaustive lists)? Would the reader agree this topic matters?

**Move 2: Establish niche** (1 paragraph)
Identify the gap — what's missing, unresolved, or contested. This is the pivot. Signal it: "However, ...", "Despite this, ...", "It remains unclear ..."
- ✓ Verify: Can you state the gap in one sentence? Is it specific, not "more research is needed"?

**Move 3: Occupy the niche** (1 paragraph)
State what this paper does — "Here we ...", "In this study, we ..." Preview the approach (1 sentence). Preview the main finding (1 sentence).
- ✓ Verify: Does this directly address the gap from Move 2? Would a reader know what to expect in the rest of the paper?

**Final check:** Read Moves 1–3 in sequence. Is there a clear funnel from broad → gap → this paper?

---

## Results

One subsection per major finding. Build sequentially — each block sets up the next. The final block delivers the paper's main finding.

**Per result block, repeat this loop:**

**Move 1: Context** (1–2 sentences)
Why this experiment/analysis? Connect to the overall question or the previous result.
- ✓ Verify: If this is not the first block, does it follow logically from the previous interpretation?

**Move 2: Approach** (1–2 sentences)
What was done. Brief — details go in Methods.
- ✓ Verify: Is this short enough? Would a reader skim past it to the finding?

**Move 3: Finding** (2–4 sentences)
What was observed. Reference figures/tables. Lead with the main observation, then supporting details.
- ✓ Verify: Is every claim tied to a specific figure/table/statistic? Does the main observation come first?

**Move 4: Interpretation** (1–2 sentences)
What this means for the question. Keep it restrained — broader interpretation goes in Discussion.
- ✓ Verify: Is this interpretation supported by just this result (not jumping ahead)? Does it set up the next block?

**Final check:** Read all blocks in sequence. Does the narrative build to a climax? Is the main finding last?

---

## Discussion

5–7 paragraphs, inverted funnel (specific → broad).

**Move 1: Summary** (1 paragraph)
Restate the main finding(s) in plain language. Synthesize — don't repeat the Results.
- ✓ Verify: Is this a fresh restatement, not copy-paste from Results? No hedging?

**Move 2: Interpretation** (1–2 paragraphs)
What does it mean? Propose mechanism or explanation. Argue for your interpretation.
- ✓ Verify: Are you arguing for an interpretation, or just restating the result?

**Move 3: Context** (1–2 paragraphs)
How does this fit with existing literature? Agreement, disagreement, extension?
- ✓ Verify: Are comparisons to prior work specific (not "consistent with previous studies")? Use the Semantic Scholar MCP tool to verify claims about cited papers.

**Move 4: Limitations** (1 paragraph)
Honest, specific, constructive.
- ✓ Verify: For each limitation, did you note whether it threatens the main conclusion? Did you skip limitations already addressed in Methods?

**Move 5: Future directions** (2–3 sentences)
Specific next experiments or analyses.
- ✓ Verify: Are these concrete and actionable, not "further research is needed"?

**Move 6: Closing** (1–2 sentences)
Broader significance. End on the contribution, not the limitations.
- ✓ Verify: Does this echo the Introduction's opening, completing the arc?

**Final check:** Does the Discussion start specific (your result) and end broad (the field)? Is Move 1 the strongest sentence?

---

## Methods

Organized by technique or system, not chronologically.

**Per method subsection:**

**Move 1: What** — materials, systems, datasets, participants
- ✓ Verify: Are versions, sources, and identifiers specified?

**Move 2: How** — procedures in enough detail to reproduce. Reference established protocols; detail novel ones.
- ✓ Verify: Could a competent researcher in your field reproduce this from what's written?

**Move 3: Analysis** — data processing, software, parameters
- ✓ Verify: Are software versions and key parameters specified?

**Move 4: Statistics** — tests, thresholds, corrections, sample sizes
- ✓ Verify: Are multiple comparison corrections stated? Is the significance threshold explicit?

Write in past tense. If adapting a prior method, cite the original and describe your modifications.
