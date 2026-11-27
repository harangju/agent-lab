# Paper-Type Playbook: Management, Information Systems & Empirical Econ

Load alongside `../STYLE.md` for quantitative social-science, business, and archival empirical venues (*Management Science*, *Information Systems Research*, *MIS Quarterly*, *Journal of Marketing Research*, empirical economics/strategy journals).

## Structure & Headings
- **Stakes & institutional context first:** Open with the real economic, organizational, or market phenomenon and why it matters economically or managerially before introducing the dataset or estimator.
- **Claim-clustered Related Work / Theory:** Group prior work by theoretical mechanism or empirical debate (never author-by-author summaries), steelman the nearest alternative explanation, and state the exact empirical or theoretical wedge your study owns.
- **Explicit identification before results:** Lay out the institutional setting, source of variation, estimand, and identifying assumptions cleanly before presenting main estimates.
- **Disciplined Results arc:** Follow a standard empirical progression—*Main Effects* → *Mechanisms & Heterogeneity* → *Robustness & Alternative Explanations*—then translate effect sizes into concrete economic/managerial magnitudes in Discussion.

## Prose & Terminology Micro-Rules
- **Match causal verbs to identification:** Reserve causal verbs (`causes`, `increases`, `reduces`) for cleanly identified designs (RCTs, DiD with validated pre-trends, RDD, credible IV); use precise associational phrasing (`is associated with`, `predicts`, `correlates with`) for observational specifications.
- **Economic magnitude alongside significance:** Always anchor estimates against the baseline mean or standard deviation (e.g., *"a 4.2 percentage-point increase, or 14% of the control mean"*), never bare `p < 0.01` or significance stars alone.
- **Steelman alternative explanations:** Name the sharpest threats to validity (selection, omitted variables, spillovers, measurement error, reverse causality) directly and explain which specific test rules out each threat.
- **Positive, crisp prose:** Keep econometrics explanations concrete—explain *why* a fixed effect or control enters the regression in plain economic terms rather than listing variable names cold.

## Tables & Figures Micro-Rules
- **Progressive specification tables:** Structure main regression tables left-to-right from parsimonious baseline → progressive fixed effects and controls → preferred full specification. Report standard errors in parentheses, clustering level, fixed-effect indicators (`Yes`/`No`), sample size (`N`), baseline DV mean, and $R^2$ (or pseudo-$R^2$) consistently in every column.
- **Summary statistics & balance:** Include a clean descriptive statistics table (mean, SD, min/median/max, `N`) and, for quasi-experiments or RCTs, a covariate-balance table.
- **Event-study & heterogeneity plots:** Show pre-treatment periods with 95% CIs, clearly mark the reference period and treatment onset, and keep y-axis units identical across subgroup panels to prevent visual distortion.
- **Script-exported tables only:** Emit LaTeX regression tables directly from reproducible analysis scripts (`fixest`/`etable`, `esttab`, `statsmodels`/Python) rather than hand-typing coefficients or stars.

## Code & Replication Audit Hazards
- **Identification & specification bugs:** Post-treatment variables accidentally included as controls ("bad controls"), wrong SE clustering level (observation vs. firm/user/market), staggered-adoption DiD bias left unchecked, or mismatched sample restrictions across columns without documenting why `N` changed.
- **Data-pipeline leaks:** Many-to-many joins silently inflating row counts, inconsistent winsorization/trimming thresholds across tables, missing-value imputation altering denominators, or date/timezone misalignment across merged archival panels.
- **Table ↔ Text drift:** Verify every coefficient, standard error, sample size, and percentage-of-mean calculation quoted in the text matches the exact exported LaTeX table and locked results file.
