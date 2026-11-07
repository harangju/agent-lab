# Paragraph and narrative structure

Read this for any multi-paragraph drafting. Sentence-level rules live in `STYLE.md`.

## Paragraph Structure

Every paragraph (except in Abstract and Methods) follows this skeleton:

1. **Topic sentence.** State the paragraph's claim or point. A reader skimming only topic sentences should get the paper's argument.
   - ✓ Verify: Does this sentence make a claim, not just announce a topic? "The model fails on long sequences" not "We now discuss sequence length."

2. **Support** (2–4 sentences). Give evidence, reasoning, or elaboration that backs the topic sentence. Each supporting sentence should connect to the claim, not to each other in a chain.
   - ✓ Verify: Could you delete any supporting sentence without weakening the claim? If yes, delete it.

3. **Transition / setup** (0–1 sentence). Connect to the next paragraph. Bridge the gap once: either at the end of this paragraph or the start of the next, not both. Redundant bridging stutters.
   - ✓ Verify: Does the last sentence point forward? Does the next paragraph's topic sentence follow naturally?

**Paragraph-level checks:**
- One point per paragraph. If you find yourself writing "Additionally" or "Furthermore" mid-paragraph, you probably need a new paragraph.
- Length varies by section: 3–6 sentences in Results blocks, up to 8–12 in Theory/Discussion where arguments need room to develop. If a paragraph feels long, check whether it's still on one point.
- The topic sentence does the heavy lifting. If the paragraph still makes sense with only its topic sentence, the structure is right.
- **Curse of knowledge** (Pinker): You know things the reader doesn't. After writing each paragraph, re-read it as if you are a smart researcher in an adjacent field who has never seen this specific work. Flag any term, acronym, or assumption that such a reader would not understand without context. Define or gloss it on first use. The Introduction and Discussion are where this matters most. Results can assume the reader has read the setup.
- **"So what?" and "Who cares?"** (Schimel): Every paragraph should pass both tests. "So what?" asks why the paragraph matters for the argument. "Who cares?" asks who in the audience needs it. If a paragraph fails either test, cut it or connect it to the main thread.

## Narrative Structure

The paper is a story (Schimel). The research question is the protagonist, the gap is the conflict, and the findings are the resolution. If you can't tell the paper's story in three sentences (what was unknown, what you did, what you found), the structure is broken. Every section serves this arc: the Introduction sets up the conflict, Theory sharpens it, Methods describe the approach, Results resolve it, Discussion interprets what the resolution means.

These patterns operate above the paragraph level. Apply them when planning section order and paragraph sequence.

**Within paragraphs, sentence architecture varies by section:**
- Introduction evidence paragraphs: Claim → evidence cascade (each from a different domain) → meta-evidence capstone
- Introduction gap paragraphs: Concede prior work → critique via accumulation (stack negations) → declare gap
- Theory paragraphs: Mechanism → contrast/inversion → italicized research question
- Results paragraphs: Bridge from prior result → brief method → quantified finding → restrained interpretation (the four-beat pattern)
- Discussion paragraphs: Finding → literature link → extension or reframing

**Across paragraphs, escalate specificity:**
- Each paragraph takes the previous paragraph's endpoint and drills deeper. The last sentence of paragraph N sets up the first sentence of paragraph N+1.
- Make transitions explicit, and never rely on implicit connections. Name the prior section's contribution and the next section's role: "Having established [X], we now examine [Y]." "Our findings on [X] raise an important question about [Y]."
- ✓ Verify: Read only the first and last sentence of each paragraph in sequence. Does the argument flow?

**Across the paper, preview and then deliver:**
- The reader should never be surprised. The Introduction previews all major findings. Each section opener summarizes what follows. Privilege comprehension over suspense.
- Track key terms (italicized on first use) across the entire paper. A concept introduced in the Introduction should recur in Theory, be measured in Results, and be interpreted in Discussion.
- One thread runs through the entire paper. State it in the abstract's last sentence, preview it in the Introduction, and restate it in the Conclusion.

**Ordering by increasing complexity:**
- Present findings in order of increasing novelty and increasing cost: confirmed effects first (easy to absorb), mixed effects second, novel or counterintuitive effects last.
- Group concepts in triads (rule of three) where possible (mechanisms, effects, contributions).
