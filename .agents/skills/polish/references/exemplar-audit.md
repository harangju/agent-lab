# Venue-Exemplar Structural Audit

Real published papers from the target venue outrank generic writing templates on abstract length, tense, intro closings, section structure, headings, and typography.

## 1. Locate Exemplars

Search in this order (never hardcode personal paths inside shared skills):

1. **Project-local:** `exemplars/` or `lit/` in the current repository.
2. **User-level private config:** `~/.config/agent-lab/exemplars.json`, formatted as:
   ```json
   {
     "index": "/absolute/path/to/lit/index.md",
     "root": "/absolute/path/to/lit",
     "venues": {
       "nmi": ["nmi", "nature-machine-intelligence"],
       "icml": ["icml", "ml-exemplar"],
       "neurips": ["neurips", "ml-exemplar"]
     }
   }
   ```
   Read the `index` markdown table to pick 3–6 papers matching the current project's target venue and genre (prefer `.tex` sources or extracted notes like `notes/<venue>-abstracts.md` when available, then PDFs).
3. If neither exists, ask the PI once for 3–5 target-venue exemplars (or a local path to save into `~/.config/agent-lab/exemplars.json`).

## 2. Benchmark Against 3–6 Exemplars

Check every dimension explicitly—do not guess from memory:

| Dimension | What to verify against the exemplars |
| --- | --- |
| **Abstract** | Hard word/character cap (e.g., NMI ≤150 words; ICML ~150–200 words), consistent tense (present vs. past), concrete example inclusion, hourglass closing sentence, zero minor robustness details. |
| **Title** | Lead with the core concept, drop filler prefixes (`"How..."`) or forced metaphors unless standard for that venue, keep crisp length, ensure clear separation from prior co-authored papers. |
| **Introduction** | Distinct opening from abstract, exact closing move (e.g., whether exemplars close with a significance sentence vs. `"Taken together"` / `"Overall"`—usually avoid rote `"Taken together"`), roadmap length, whether Figure 1 sits on page 1–2 as a visual overview. |
| **Section structure** | Typical number of top-level sections and subsections (avoid over-fragmenting into 4.1–4.8 when exemplars group into 2–3 focused sections or clean `\paragraph{}` lead-ins). |
| **Experimental Setup** | Parallel `\paragraph{}` blocks (Models, Benchmarks/Tasks, Evaluation/Controls) vs. numbered subsections; standard benchmark sample sizes (`N`) and citations. |
| **Figures & Tables** | Whether exemplars lead with a Figure 1 overview diagram, how tables format headers/rules (`booktabs`, no `\resizebox`), and how captions structure bold titles + walkthroughs. |
| **LaTeX Template** | Official venue style file, double-blind vs. single-blind rules, line numbers, page/figure limits, and clean compilation with zero overfull boxes. |

## 3. Report & Apply

- Present concrete exemplar deltas first (e.g., *"All 6 NMI exemplars are ≤150 words in present tense and omit `"We hypothesize..."` openings"*).
- Apply mechanical alignment edits (word caps, tense, standard subsection layout, closing stems) directly when asked; flag major structural cuts (e.g., moving a study to SI/Appendix) for PI sign-off.
