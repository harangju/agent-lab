# Paper-Type Playbook: Nature, Science & General-Interest Journals

Load alongside `../STYLE.md` for broad interdisciplinary journals (*Nature*, *Science*, *Nature Human Behaviour*, *Nature Machine Intelligence*, *PNAS*). Often combined with `ml.md` or `behavioral.md`.

## Structure & Headings
- **Strict abstract budgets:** Check exact journal caps before drafting (*Nature Machine Intelligence* ≤150 words; *Science* ≤125 words; *Nature* ~200 words; *PNAS* ≤250 words). Cut secondary robustness checks, raw trial totals, and minor implementation details from the abstract.
- **Accessible opening & hourglass closing:** Open the abstract and introduction in plain language understandable to a scientist outside the immediate subfield (zero unexplained niche jargon), narrow to the exact falsifiable gap, and close with one broad scientific takeaway that zooms back out cleanly.
- **Main Text vs. Methods / SI split:** Keep the Main Text focused on the core question, headline mechanism, and decisive validation. Move technical derivations, secondary baselines, hyperparameter sweeps, and exhaustive per-model tables cleanly to Methods, Extended Data, or Supplementary Information.
- **Claim-style Results headers (where journal exemplars use them):** State each Results subsection's finding as a crisp declarative takeaway rather than a vague topic label (*"Top-down feedback restores global consistency"* beats *"Results of Study 3"*).

## Prose & Terminology Micro-Rules
- **Zero curse of knowledge:** Knit every new concept piece-by-piece from established terms; define any subfield-specific architecture, cognitive term, or metric plainly before it carries analytical weight.
- **Consistent present tense (check exemplars):** Many *Nature*-family papers use consistent present tense in the abstract and for general mechanisms, switching cleanly to past tense only when narrating specific completed procedures. Match the target journal's published exemplars.
- **Prose diet:** Keep narrative paragraphs focused on 1–2 anchored headline contrasts; avoid stacked parentheticals, inline `±` clusters, and throat-clearing meta-commentary.
- **Confident, non-defensive framing:** State scope boundaries cleanly in Discussion without frontloading limitations in the abstract or intro.

## Tables & Figures Micro-Rules
- **Visual storytelling for skimmers:** A reader who looks only at Figures 1–5 and their bold caption titles should grasp the entire arc—problem, mechanism, main result, and real-world generality.
- **Figure budget discipline:** Respect strict main-figure caps (typically 4–6 main figures). Merge closely related panels onto clean multi-panel plates and move extra diagnostics to Extended Data / SI rather than exceeding the limit.
- **Concrete real-world examples:** Pair aggregate quantitative charts with crisp, representative visual or text examples (vetted for print legibility and appropriateness) so non-specialists immediately see what the phenomenon looks like.
- **Print-scale legibility:** Multi-panel full-width plates shrink aggressively in two-column journal layouts—inspect rendered PDF pages directly to ensure every embedded label, curve, and example stays readable.

## Code & Replication Audit Hazards
- **Main Text ↔ Extended Data ↔ SI parity:** After moving sections or robustness checks to SI/Extended Data, re-verify every cross-reference (`Supplementary Table S3`, `Extended Data Fig. 2`) and confirm no stale numbers remain from earlier drafts.
- **Caption threshold verification:** Verify every qualitative claim in figure titles/subtitles (e.g., `"remains below 40%"`, `"across all models"`) directly against the locked JSON plotted in that figure.
- **Public release readiness:** Keep heavy reference PDFs out of git, ensure every table and figure regenerates cleanly from committed scripts + locked results, and verify code/data availability statements match the public repository URL.
