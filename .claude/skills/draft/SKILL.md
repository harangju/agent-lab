---
name: draft
description: Draft a paper section using rhetorical structure templates
---
Draft this paper section: $ARGUMENTS

Read `context.md` for current research state. If a manuscript draft exists, read it for context. Identify which section is requested (abstract, introduction, results, discussion, methods). If multiple sections or "all" is requested, spawn one subagent per section in parallel — each gets only its own template.

For each section, follow the **move → write → verify** loop: draft the move, then check it against the verify step before moving on. Do not draft the next move until the current one passes.

Apply the style rules and paragraph structure below to every sentence and paragraph you write. These are non-negotiable — check each paragraph against them before moving on.

---

## Style Rules

Follow standard scientific prose conventions (active voice, parallel construction, present tense for established facts, past tense for your results). The rules below target LLM-specific failure modes — check every sentence against them.

**Characters as subjects, actions as verbs** (Williams)
- The sentence's grammatical subject should be the person or thing doing the action. The verb should be that action. "The committee decided" not "A decision was reached by the committee." "We analyzed" not "An analysis was performed." This kills nominalizations and passive voice in one move.
- ✓ Verify: In each sentence, is the subject a real character (we, participants, the model) doing a real action (measured, increased, predicts)? Or is the subject an abstraction (analysis, decision, investigation) with a weak verb (was performed, was made, was conducted)?

**Sentence rhythm**
- Vary sentence length. Short sentences punch. Longer sentences develop an idea, add nuance, or build a chain of reasoning. A key finding deserves a short sentence on its own. LLMs default to uniform medium-length sentences — fight this.
- After a long complex sentence, follow with a short one. After several medium sentences, break the pattern.

**Specificity**
- Be as specific as the context warrants. In Results, use exact numbers: "3-fold increase" not "significant increase." In Introduction/Discussion, broader language is fine when you genuinely mean the class rather than ducking a specific name you could give.
- Avoid false vagueness — abstract language when the specific thing is available. "The model" when you mean BERT. "In most cases" when you have the count.
- In Results, anchor numbers and comparisons. "Reduced error by 12% (from 34% to 22%)" not "reduced error by 12%."

**Economy**
- Cut throat-clearing. Delete "It is worth noting that," "Interestingly," "It should be mentioned that." Start with the content.
- Cut hedging unless epistemically necessary. "X increases Y" not "X appears to potentially increase Y." Hedge only when the evidence genuinely warrants it — then hedge precisely ("in 3 of 5 conditions, X increased Y").
- Positive form. Say what is, not what isn't. "The method has limitations" not "The method is not without limitations." "We ignored X" not "We did not consider X."

**Precision**
- Never dangle "this." Always attach a noun: "This result shows" not "This shows." "This pattern suggests" not "This suggests."
- Italicize key terms on first introduction. Use consistently thereafter.

---

## Voice and Phrasing

Match the PI's writing voice. Use these constructions as models — don't parrot them, but internalize the patterns.

**Reporting findings:**
- "We found [that] ..." — the primary construction for results
- "These results suggest/indicate/demonstrate that ..."
- "This pattern aligns with / is consistent with ..."

**Transitions:**
- "Taken together, ..." / "Together, ..." — synthesize multiple findings into one claim
- "Having established [X], we now examine ..." — bridge between sections
- "We begin by examining ..." — open a results section
- "Most importantly, ..." — signal the argument's center of gravity
- "Critically, ..." — flag the single most important piece
- "Broadly, ..." — high-level takeaway before specifics
- "In light of this evidence, ..." — pivot from prior work to your claim

**Contrasts:**
- "In contrast, ..." / "Conversely, ..." — juxtapose conditions or findings
- "Unlike [prior approach], ..." — explicit comparison to prior work
- "Yet ..." — lighter, mid-sentence contrast
- "[X], while [Y]" — balanced parallel contrast: "human-AI teams produced higher text quality, while human-human teams produced higher image quality"

**Gaps and problems:**
- "we currently lack ..." / "it is unclear how ..."
- "Our lack of evidence on [X] exists, in part, because ..."
- "[Prior work] tend(s) to [limitation], which [consequence]"
- "These innovations are meaningful because [X], yet the existing scientific literature studies none of them."

**Contributions:**
- "To address these gaps, we ..."
- "This represents a fundamental departure from ..."
- "The core contribution is ..."
- "This study extends [X] to [Y]"

**Causal chaining:**
- "[X], in turn, [Y]" — link mechanisms in a pathway
- ", in part, because" — partial causal attribution

**Rhetorical emphasis:**
- "[X] is not merely [Y]; [Z]" — upgrade importance: "recognition is not merely perceptual but consequential"
- "This creates a tension: ..." — name a trade-off explicitly
- Tricolon lists (rule of three) for mechanisms, effects, contributions

**Theory section closers:**
- "We therefore examine whether *[italicized research question]*." — close each theory subsection with a testable prediction

**Hedging (when warranted):**
- "may [verb]" — dominant hedge in Theory/Discussion
- "suggests that ..." — cautious inference from data
- "possibly / perhaps because ..." — speculative explanation
- "With that caveat in mind, ..." — acknowledge limitation, then proceed

---

## Paragraph Structure

Every paragraph (except in Abstract and Methods) follows this skeleton:

1. **Topic sentence** — the paragraph's claim or point. A reader skimming only topic sentences should get the paper's argument.
   - ✓ Verify: Does this sentence make a claim, not just announce a topic? "The model fails on long sequences" not "We now discuss sequence length."

2. **Support** (2–4 sentences) — evidence, reasoning, or elaboration that backs the topic sentence. Each supporting sentence should connect to the claim, not to each other in a chain.
   - ✓ Verify: Could you delete any supporting sentence without weakening the claim? If yes, delete it.

3. **Transition / setup** (0–1 sentence) — connect to the next paragraph. Bridge the gap once: either at the end of this paragraph or the start of the next, not both. Redundant bridging stutters.
   - ✓ Verify: Does the last sentence point forward? Does the next paragraph's topic sentence follow naturally?

**Paragraph-level checks:**
- One point per paragraph. If you find yourself writing "Additionally" or "Furthermore" mid-paragraph, you probably need a new paragraph.
- Length varies by section: 3–6 sentences in Results blocks, up to 8–12 in Theory/Discussion where arguments need room to develop. If a paragraph feels long, check whether it's still on one point.
- The topic sentence does the heavy lifting. If the paragraph still makes sense with only its topic sentence, the structure is right.
- **Curse of knowledge** (Pinker): You know things the reader doesn't. After writing each paragraph, re-read it as if you are a smart researcher in an adjacent field who has never seen this specific work. Flag any term, acronym, or assumption that such a reader would not understand without context. Define or gloss it on first use. The Introduction and Discussion are where this matters most — Results can assume the reader has read the setup.
- **"So what?" and "Who cares?"** (Schimel): Every paragraph should pass both tests. "So what?" — why does this matter for the argument? "Who cares?" — who in the audience needs this? If a paragraph fails either test, cut it or connect it to the main thread.

---

## Narrative Structure

The paper is a story (Schimel). The research question is the protagonist, the gap is the conflict, and the findings are the resolution. If you can't tell the paper's story in three sentences — what was unknown, what you did, what you found — the structure is broken. Every section serves this arc: the Introduction sets up the conflict, Theory sharpens it, Methods describe the approach, Results resolve it, Discussion interprets what the resolution means.

These patterns operate above the paragraph level. Apply them when planning section order and paragraph sequence.

**Within paragraphs — sentence architecture varies by section:**
- Introduction evidence paragraphs: Claim → evidence cascade (each from a different domain) → meta-evidence capstone
- Introduction gap paragraphs: Concede prior work → critique via accumulation (stack negations) → declare gap
- Theory paragraphs: Mechanism → contrast/inversion → italicized research question
- Results paragraphs: Bridge from prior result → brief method → quantified finding → restrained interpretation (the four-beat pattern)
- Discussion paragraphs: Finding → literature link → extension or reframing

**Across paragraphs — escalating specificity:**
- Each paragraph takes the previous paragraph's endpoint and drills deeper. The last sentence of paragraph N sets up the first sentence of paragraph N+1.
- Make transitions explicit — never rely on implicit connections. Name the prior section's contribution and the next section's role: "Having established [X], we now examine [Y]." "Our findings on [X] raise an important question about [Y]."
- ✓ Verify: Read only the first and last sentence of each paragraph in sequence. Does the argument flow?

**Across the paper — preview then deliver:**
- The reader should never be surprised. The Introduction previews all major findings. Each section opener summarizes what follows. Privilege comprehension over suspense.
- Track key terms (italicized on first use) across the entire paper. A concept introduced in the Introduction should recur in Theory, be measured in Results, and be interpreted in Discussion.
- One thread runs through the entire paper. State it in the abstract's last sentence, preview it in the Introduction, and restate it in the Conclusion.

**Ordering by increasing complexity:**
- Present findings in order of increasing novelty and increasing cost: confirmed effects first (easy to absorb), mixed effects second, novel or counterintuitive effects last.
- Group concepts in triads (rule of three) where possible — mechanisms, effects, contributions.

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

The Introduction funnels from broad context to this paper. In long-form introductions (e.g., management, social science), Moves 3–5 expand after occupying the niche: describe the approach, preview findings, and state the contribution. In short-form introductions (e.g., natural sciences), Move 3 is a single paragraph.

**Move 1: Establish territory** (1–2 paragraphs)
Claim importance — why this field/topic matters. Review prior work — what has been established. Set the stage for the gap. Use evidence cascades: multiple findings from different domains, ending with the strongest (meta-evidence or review).
- ✓ Verify: Are citations selective (key papers, not exhaustive lists)? Would the reader agree this topic matters?

**Move 2: Establish niche** (1–2 paragraphs)
Identify the gap — what's missing, unresolved, or contested. This is the pivot. Signal it: "However, ...", "Despite this, ...", "It remains unclear ..." Layer gaps if needed: first a methods gap, then a deeper understanding gap ("Furthermore, we currently lack...").
- ✓ Verify: Can you state the gap in one sentence? Is it specific, not "more research is needed"? Does each gap paragraph's critique use accumulation (stacking what prior work doesn't do)?

**Move 3: Occupy the niche** (1+ paragraphs)
State what this paper does — "To address these gaps, we ..." Preview the approach, the key innovation, and the main finding.
- ✓ Verify: Does this directly address the gap from Move 2? Would a reader know what to expect in the rest of the paper?

**Move 4: Preview findings** (1–2 paragraphs, long-form only)
Summarize the main outcomes, then the mechanisms. Use "Most importantly, ..." to signal the core contribution. The reader should know the punchline before entering Theory/Results.
- ✓ Verify: Does the preview cover both what you found and why it matters?

**Move 5: Contribution statement** (1 paragraph, long-form only)
Position the paper against existing work. "Our work contributes to ... by presenting ..." / "The core contribution is ..."
- ✓ Verify: Does this echo Move 1 (territory) and preview the Discussion's closing?

**Final check:** Read Moves 1–5 in sequence. Is there a clear funnel from broad → gap → this paper → findings → contribution?

---

## Theory / Literature Review (building block + capstone)

Use when the paper has a dedicated Theory or Literature Review section between Introduction and Methods. Skip if the Introduction already covers theory (common in natural sciences).

**Move 1: Foundation** (1 subsection)
Establish the theoretical framework — the vocabulary and distinctions the rest of the section will use. End with a roadmap sentence listing the mechanisms or constructs to be examined: "We examine how these differences manifest in three mechanisms: [A], [B], and [C]."
- ✓ Verify: Does this subsection define all key terms? Does the roadmap match the subsequent subsection structure?

**Move 2: Mechanisms** (1 subsection per mechanism, in parallel)
Each subsection develops one mechanism. Within each:
1. Establish the construct in existing theory (what's known about this mechanism in general)
2. Apply it to the paper's context (how it operates here)
3. Close with an italicized research question: "We therefore examine whether *[testable proposition]*."

Use a descriptive-then-consequential pattern: first ask whether the pattern exists, then ask whether it affects outcomes.
- ✓ Verify: Does each subsection end with an italicized research question? Does each question build on the previous subsection's logic?

**Move 3: Moderator / Capstone** (1 subsection, depends on Move 2)
The final mechanism depends on the earlier ones. Its opening sentence should reference the previous subsections explicitly: "The [A] and [B] patterns described above assume that [C]." This creates a building block + capstone structure.
- ✓ Verify: Does the capstone's research question link all mechanisms into a single causal chain?

**Final check:** Read all italicized research questions in sequence. Do they build from descriptive → consequential → conditional? Do they map to the Results subsections?

---

## Results

One subsection per major finding. Build sequentially — each block sets up the next.

**Macro arc — What → So What → How → Why:**
Order subsections to build a causal narrative. First, present the outcomes (what happened). Then, validate them (does it matter in the real world?). Then, describe the process differences (how did collaboration differ?). Finally, link process to outcomes (why did these patterns emerge?). This creates a mystery — outcomes first, then the mechanisms that explain them.

Within each phase, order findings by increasing novelty: confirmed/intuitive effects first, mixed effects second, novel/counterintuitive effects last.

Use explicit transitions between subsections: "Our findings on [X] raise an important question about [Y]." "Having established [X], we now examine [Y]." "To address why [X], we [Y]."

**Per result block, repeat this loop:**

**Move 0: Claim header** (bold)
State the finding as a claim in the header itself. E.g., "**Collaborating with AI agents increases individual-level productivity.**" A reader skimming only headers should get the paper's story.
- ✓ Verify: Is this a claim, not a topic? "X increases Y" not "Effects of X on Y."

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

**Synthesizing paragraph** (after 2–3 related blocks):
Use "Taken together, ..." to synthesize multiple findings into a single interpretive claim. This is where new conceptual labels emerge from the data (e.g., "delegation workflow").

**Final check:** Read all claim headers in sequence. Do they tell the paper's story? Does the narrative build to the core contribution?

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
