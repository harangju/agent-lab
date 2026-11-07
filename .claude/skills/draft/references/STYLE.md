# Style

These are the shared writing rules for all prose: papers, grants, notes, response letters, and web pages. Apply them whenever you draft or edit a sentence. The PI maintains this file. If a project has its own STYLE.md, or a writing section in AGENTS.md, that file's rules win on conflicts.

## Sentences

1. **Make the subject a strong keyword.** Lead with a key noun of the work, not a generic noun phrase, and prefer the work's own terms as grammatical subjects. The subject is the link that connects one sentence to the next.
2. **Keep the subject short.** Don't pile a list into the grammatical subject ("X, Y, Z, A, and B [verb]" reads as a dump). Put a short subject up front ("we", "the revision", "the paper") and move the specifics into the predicate or a parenthetical.
   - **Prefer subject extraposition over gerund subjects.** Don't lead with a heavy gerund as the subject. Use an anticipatory "it" and put the action in an infinitive at the end.
     - ❌ "Bolting agents onto old processes rarely delivers."
     - ✅ "It rarely delivers to bolt agents onto old processes."
   - Also avoid opening a sentence with a participle used as an adjective ("Communicating agents can deviate..."). It is syntactically ambiguous, because the reader first parses it as a heavy gerund subject ("the act of communicating with agents").
3. **Use an active, concrete verb.** Don't use the passive where an action verb will do. Match the verb to what actually happened. Prefer simple standard verbs that do real work ("test", "measure", "compare", "build", "map", "show", "keep") over ornate or vague ones ("leverage", "illuminate", "operationalize", "facilitate", "interrogate").
4. **Narrate when appropriate.** When the prose walks the reader through a move (a definition, a test, a turn in the argument), say what you are doing, in plain sequence. Narration orients the reader. It doesn't decorate.
5. **Don't use a verb that doubles as a noun.** Noun-verb ambiguity confuses. Avoid "partitions", "splits", "breaks", "cuts", and "spreads"; prefer "decomposes", "severs", or "computes". But don't swap simple verbs for stiff, thesaurus words ("elevate" for "raise", "ceases" for "stops") unless the result sounds completely natural. Simple, clear verbs always win.
6. **Be standard, not corny.** No cute, dramatic, or ornamental word choices. No inflated phrasing ("synergistic", "revolutionary").
7. **Vary sentence length.** A key finding deserves a short sentence of its own. After a long, complex sentence, follow with a short one. LLMs default to uniform medium-length sentences, so break the pattern on purpose.

## Punctuation

1. **No em dashes.** Use a comma, a period, or parentheses.
2. **Avoid explanatory colons in prose; split into two sentences instead.** A colon that delivers something just named (a list, or an item named and then given) is fine. Split a colon when the clause after it explains or justifies a claim instead of delivering something named.
3. **Use semicolons sparingly, if at all.** Instead of colons and semicolons, use connective prose: and, but, while, because, meaning, namely. Vary the connectors in parallel structures.

## Content

1. **No invented jargon or arbitrary labels.** Don't coin a term and then lean on it to explain something. Use words a reader already knows.
2. **Introduce and define every substantial word.** Before a key term carries weight, give the reader a plain handle for it. Don't drop a loaded word cold. Italicize a key term on first use, and use it consistently after that.
3. **Connect those words in a logical chain.** Once a word is on the table, reuse it as the bridge to the next idea, so each sentence picks up a term the previous one made available. Keep the transitions natural and conversational, though. Don't repeat words mechanically or write formulaic sentences just to satisfy this rule.
4. **De-hedge.** State the claim. Keep substantive caveats that narrow a factual claim, and cut meta-qualifiers that label the contribution as narrow. The test is whether a qualifier narrows the fact or the framing of the fact: a qualifier that narrows the fact stays, and one that narrows the framing goes. Qualify without announcing that you are qualifying.
5. **Never frontload limitations.**
6. **Frame the design with confidence, not defensively.** Keep 100% scientific accuracy and respect the boundaries of the experiments, but present design choices as strong and deliberate. Sound like you are confidently explaining a strong design, not defending a weak one.
7. **Be specific.** In Results, use exact numbers and anchor comparisons: "reduced error by 12% (from 34% to 22%)", not "significantly reduced error". Don't write "the model" when you mean BERT, or "in most cases" when you have the count.
8. **In journal revisions, never refer to the reviewer or editor in the manuscript.**
9. **Name a contrast with concrete opposites.** When a sentence turns on a reversal or tension, name both poles in concrete terms ("an asset in human-human teams, a liability in human-AI teams") instead of a vague motion verb ("accelerating", "shifting", "widening"). Give the consequence its own sentence so the claim lands.
10. **Make topic sentences skimmable.** A reader who scans only the first sentence of each paragraph should still get the argument. So name the subject in the topic sentence. Don't open a paragraph with a backward demonstrative ("This finding...", "These results...") that sends the reader back to the previous paragraph to work out what it means. Anywhere in a paragraph, attach a noun to "this" ("this result shows", not "this shows").

## Grammar

1. **The possessive singular adds 's.** Charles's friend, the boss's desk. The exceptions are ancient names (Jesus') and fixed forms like "for conscience' sake".
2. **Use the Oxford comma.** In a series of three or more, put a comma after every term except the last: red, white, and blue.
3. **Set off parenthetic expressions with commas.** If the matter is genuinely parenthetic, it needs both commas. Restrictive matter takes none.
4. **Put a comma before a conjunction joining two independent clauses** (and, but, for, or, nor). Leave it out when the conjunction joins a compound predicate that shares one subject.
5. **No comma splices and no sentence fragments.** Join independent clauses with a semicolon, a period, or a conjunction, never a bare comma. Don't break one sentence into two with a period.

## Composition

1. **Omit needless words.** Every word must tell. Cut "the fact that", "there is/are", "in order to", and "due to the fact that". This rule subsumes most of the others.
2. **Put statements in positive form.** Assert what is, not what is not: "He usually came late" beats "He was not often on time." Reserve "not" for genuine denial.
3. **Express coordinate ideas in parallel form.** Match the grammatical structure across the items in a series or a comparison.
4. **Keep related words together.** Put the subject next to its verb, and each modifier next to what it modifies. Position governs the relationship.
5. **Put the emphatic words at the end.** The end of the sentence is the place of stress, so end on the word you want the reader to keep.
6. **Treat the paragraph as the unit of composition.** One topic per paragraph, signaled by its topic sentence (see Content 10).
7. **Signpost a new line of reasoning.** When a paragraph opens a new analysis or question, its topic sentence narrates the turn: why this question now, and what it tests or explains ("To explain why X holds, we examined Y"; "We then asked how much of the effect runs through Y"). Don't drop a new analysis on the reader cold. They should know what question the paragraph answers before the numbers arrive. Signposts (topic-sentence stems and discourse markers) tell readers where they are in the story, so keep that job when you revise: rewrite the claim a signpost introduces, but don't bury, demote, or cut the signpost itself.
8. **End each paragraph by interpreting the evidence.** The final sentence, especially in Results, should interpret the findings just presented or motivate the move to the next analysis. Tell the reader what the evidence means. Don't end on a raw number or an uninterpreted fact, and don't introduce an unmotivated new term in the closing sentence just to set up the next paragraph.
9. **Let parallel syntax show the relationship.** Show opposing or matching relationships through word choice and grammatical structure, not meta-commentary ("this is a mirror image", "these are opposites"). For example, don't write "In a mirror image of the first experiment, where we increased the temperature, we decreased the temperature in the second experiment." Write "In the first experiment, we increased the temperature. In the second, we decreased it."
10. **No two pieces share the same opening.** The abstract and the introduction, and any parallel sections, must start with different subjects and framings.

## Voice and phrasing

Match the PI's voice. Use these stems as models, but internalize the patterns rather than repeating them verbatim.

- **Reporting findings:** "We found that...", "These results suggest/indicate/demonstrate that...", "This pattern aligns with..."
- **Transitions:**
  - "Taken together, ..." synthesizes several findings into one claim.
  - "Having established X, we now examine Y" bridges two sections.
  - "We begin by examining..." opens a Results section.
  - "Most importantly, ..." marks the argument's center of gravity.
  - "Critically, ..." flags the single most important point.
- **Contrasts:** "In contrast, ...", "Conversely, ...", "Unlike [prior approach], ...", or a balanced "[X], while [Y]" ("human-AI teams produced higher text quality, while human-human teams produced higher image quality").
- **Gaps:** "We currently lack...", "It is unclear how...", "[Prior work] tends to [limitation], which [consequence]."
- **Contributions:** "To address these gaps, we...", "The core contribution is...", "This study extends X to Y."
- **Causal chains:** "[X], in turn, [Y]"; ", in part, because..."
- **Theory closers:** "We therefore examine whether *[italicized research question]*."
- **Hedges, only when the evidence warrants one:** "may [verb]", "suggests that...", "With that caveat in mind, ..."

## Response letters

1. Answer the reviewer's request fully in the response itself. Don't make them read the paper, or another reply, to understand what you did.
2. Name the analyses, tables, and text changes, and say where each one now appears.
3. Use signposting. Overwhelm the reviewer with concrete work done, not rhetoric.
4. `\revision` blocks quote the manuscript, so keep them accurate. Keep `\reviewer` text unchanged.

## Hard constraints

- Never claim a mechanism that the data reject.
- Never upgrade suggestive evidence into proof.
- Never invent findings. Read enough of the surrounding text to know the actual claims, numbers, and constraints.
- Treat a question from the PI as a question, not as an instruction to rewrite everything. When the ask is ambiguous, align on intent first, then edit.
