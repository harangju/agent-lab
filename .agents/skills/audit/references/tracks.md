# Parallel Audit Track Briefs (Universal Core)

Brief all four read-only audit subagents in parallel. Require every finding to include exact `file:line` references and a clear **Bucket A** (safe mechanical cleanup / zero-impact fix) vs. **Bucket B** (affects locked data, stimuli, or reported manuscript numbers—needs PI decision) classification.

**Also pass the matching genre playbook from `../../draft/references/genres/`** (`ml.md`, `behavioral.md`, `general-science.md`, or `management-econ.md`) so subagents check the concrete failure modes specific to this paper type.

## Track 1 — Core Package, Data Pipeline & Stimuli
- **Look for:**
  - Dead code, unused modules, and duplicated helpers or wrappers that can be consolidated cleanly without breaking saved artifacts or public interfaces.
  - Silent pipeline, modeling, or evaluation bugs: data leakage, mis-aligned joins/merges, wrong grouping/clustering, batching/masking bugs, metric edge cases, or unguarded state cleanup.
  - Stimulus/instrument defects (for experimental or synthetic tasks): inadvertent confounds, visual clipping, broken cross-condition parity, or mismatch between live study code and reported design.

## Track 2 — Experiment, Analysis & Compute Scripts
- **Look for:**
  - Superseded pilot/v1/archive scripts, dead scripts still imported by active runners (promote shared utilities into the core package), and hardcoded output paths that risk overwriting runs.
  - Split, randomization, exclusion, and estimation bugs: non-stratified or leaked train/test splits, inconsistent outlier/exclusion rules, silently swallowed fallbacks, or misconfigured cluster/scheduler launchers.
  - Copy-pasted launcher/runner boilerplate that can be consolidated into parameterized scripts with clean cache/temp isolation.

## Track 3 — Figures, Tables & Paper-vs-Data Replication
- **Look for:**
  - Re-run every offline analysis, merge, figure, and table script and diff against committed `results/`, `paper/tables/`, and figures.
  - Cross-check **every number in the manuscript** (Abstract, Results prose, Tables, Figure captions/subtitles, SI/Appendix) directly against locked `results/` files—flag any stale number, rounding slip, or caption claim contradicted by data.
  - Flag superseded result files, orphaned figure/table scripts, and unreferenced assets.

## Track 4 — Repo Hygiene, Tests, Builds & Git Bloat
- **Look for:**
  - Run offline unit tests (`pytest` / R tests), syntax/lint checks (`py_compile`, `bash -n`), and manuscript compilation (`tectonic` / `pdflatex`).
  - Check dependency manifests (`pyproject.toml` / `requirements.txt`), stale READMEs, stray bytecode/scratch files, and large binary files committed to git (such as reference PDFs that belong outside the repo).
