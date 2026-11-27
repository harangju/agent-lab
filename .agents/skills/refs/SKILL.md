---
name: refs
description: Verify every BibTeX reference and in-text citation against primary bibliographic APIs (arXiv, Crossref, OpenAlex, proceedings) and live URLs, or run a fast arXiv paper relevance and scoop check against project CONTEXT.md. Use when verifying paper references, auditing bibliography accuracy, checking citations, or evaluating whether a new arXiv paper is relevant or scoops the project.
argument-hint: "[verify <bib> [--tex <tex>] | check <arxiv-url-or-id>]"
---
Verify paper references and citations, or evaluate a candidate paper's relevance/scoop risk, as requested by the user.

Paths like `references/...` and `scripts/...` are relative to this skill's folder, the one holding this `SKILL.md`. Resolve them to absolute paths in tool calls and when briefing subagents.

*(Note: this skill verifies a manuscript's bibliography and evaluates related papers. For syncing a personal Google Scholar citation profile, use `/citations`.)*

## Mode 1 — Full Bibliography & Citation Verification (`verify` — default)

Never trust LLM-generated BibTeX entries or memory. Verify every entry against primary bibliographic records and verify every in-text citation context.

### Step 1: Run automated primary-source check
```bash
python3 <skill-dir>/scripts/verify_bib.py <paper.bib> [--tex <main.tex>] [--check-urls] --format json > /tmp/bib_audit.json
```
The script:
1. Parses every BibTeX entry and expands `\input{...}` / `\include{...}` across modular `.tex` files to find missing or uncited keys and extracted URLs.
2. Checks deterministic BibTeX hygiene: missing fields, duplicate keys/DOIs/arXiv IDs, unbraced capitals after `?` or `:` in titles, and stale arXiv entries.
3. Queries **arXiv API**, **Crossref**, and **OpenAlex** to compare author lists (catching hallucinated or dropped authors), exact titles (catching fabricated prefixes), publication years, and published peer-reviewed venues (NeurIPS/ICML/ICLR/ACL/Nature) that superseded an arXiv preprint.
4. Optionally verifies live HTTP reachability for web URLs and Hugging Face checkpoints (`--check-urls`).

### Step 2: Inspect every flagged entry & verify proceedings details
- For any entry flagged with a mismatch or unresolved by APIs (e.g., PMLR/NeurIPS/OpenReview page ranges, book editions, technical reports, blog posts), verify directly against the official publisher/proceedings record via web search.
- Never silently drop an author or guess page numbers/issue numbers.

### Step 3: Audit every in-text citation context
- Group all in-text `\cite*` occurrences by section (use parallel subagents for papers with >30 citations).
- For every citation, verify that the cited paper **actually supports the specific empirical or theoretical claim made in that sentence** (catch swapped keys, wrong attribution, wrong author order, or citations attached to the wrong phenomenon).

### Step 4: Fix, recompile, and log
1. Apply all verified fixes to `.bib` and `.tex` files.
2. Recompile every manuscript PDF target (`tectonic` or `pdflatex`/`bibtex`) and confirm **zero undefined citations or cross-reference warnings**.
3. Append a concise summary entry to `notes/review_comments.jsonl` (if the project uses it) and report exact counts: entries checked, factual/metadata errors fixed, mis-citations fixed, and URLs/checkpoints verified. Do not commit unless asked.

---

## Mode 2 — Quick arXiv Relevance & Scoop Check (`check <url-or-id>`)

When the PI drops an arXiv link or paper URL asking *"is this relevant?"* or *"are we scooped?"*:

1. Read `CONTEXT.md` (core RQ, mechanism, nearest neighbors, falsifiable claim).
2. Fetch the paper's exact metadata and abstract immediately:
   ```bash
   python3 <skill-dir>/scripts/verify_bib.py --arxiv <arxiv-url-or-id>
   ```
   If the abstract leaves overlap ambiguous, inspect the full paper text/PDF or web summary before judging.
3. Reply with a standalone **2–3 sentence verdict** (unless asked to expand):
   - Clear classification: **Scooped / Direct Overlap**, **Cite & Differentiate**, or **Not Relevant / Skip**.
   - Exact one-line contrast between their mechanism/finding and ours.
   - Concrete action recommendation (e.g., skip, add one contrast sentence in Related Work, or inspect a specific section).

## Never

- Declare references verified based on memory or key-existence linting alone.
- Invent DOIs, page ranges, author names, or venue acceptances without a primary record.
- Leave an arXiv preprint cited as `arXiv` when a verified peer-reviewed proceedings/journal version exists (unless citing an arXiv-only version intentionally).
