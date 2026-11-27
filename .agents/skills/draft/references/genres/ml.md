# Paper-Type Playbook: ML, Systems & Interpretability

Load alongside `../STYLE.md` for conference and systems/ML papers (ICML, NeurIPS, ICLR, ACL, COLM). Combine with `general-science.md` for hybrid venues such as *Nature Machine Intelligence*.

## Structure & Headings
- **Abstract:** ~150–200 words, consistent present tense, concrete task/model scope, 1–2 anchored headline gains, and a concise closing takeaway (cut minor ablations and raw trial counts).
- **Introduction:** Distinct opening from the abstract; place a visual Figure 1 overview on pages 1–2; avoid closing with a rote `"Taken together, ..."` or `"Overall, ..."` paragraph unless target exemplars do so.
- **Experimental Setup:** Prefer parallel `\paragraph{}` blocks (*Models*, *Tasks / Benchmarks*, *Controls / Evaluation*) over deeply nested subsections when matching ICML/NeurIPS exemplars.
- **Standard, positive headings:** Use canonical venue phrasing (*Experimental Setup*, *Mechanistic Analysis*, *Benchmarks and Failure Modes*) rather than ad-hoc or negative headings (*Limit Tests*, *Scope Limits*, *When X Fails*). Avoid fragmenting Results into 7–8 tiny subsections (`4.1`–`4.8`).

## Prose & Terminology Micro-Rules
- **Canonical ML/interp vocabulary:** Use standard community terms (`test-time compute`, `KV cache`, `output layers`, `activation patching`, `recurrent passes`) rather than ad-hoc paraphrases (`compute savings`, `key-value memory`, `readout layers`, `causal prelude swap`).
- **Cut colloquial / vague verbs:** Replace informal verbs (`stall`, `hit`, `escape`, `boost`, `own`) with precise mechanistic verbs (`plateau`, `degrade`, `recover`, `improve`, `exceed`).
- **Concrete prompt example first:** Before describing a synthetic task or perturbation abstractly, show a 1–2 line verbatim input/output schematic so the reader sees the exact tokens the model sees.
- **No bare script symbols:** Never leave internal keys (`split_mid_row`), unintroduced math subscripts (`K_A`, `r=8`), or cryptic flags in prose, titles, or captions.

## Tables & Figures Micro-Rules
- **Figure 1 overview:** Make Figure 1 a crisp, zero-effort schematic (often native TikZ or vector SVG/PDF) contrasting the problem and mechanism on a verbatim example—keep tiny example boxes out of aggregate data plots.
- **Uniform benchmark tables:** Hold evaluation depth and control sets uniform across every row (never silently swap baselines per model). Pair official published benchmark formats with strict perturbation controls.
- **Readable headers & native typography:** Spell out headers (no opaque `H`, `M`, `N`, `Anch.`), add compact literal syntax cues where helpful (`Leading \n`, `Inline`, `Misaligned`), use `booktabs` at native conference font size, and avoid `\resizebox{\textwidth}{!}` shrinkage hacks.
- **Data figures:** Keep consistent panel grids across figures (e.g., 1×2 or 1×3), left-aligned `A.`/`B.`/`C.` panel titles, frameless grouped top legends (`frameon=False`), shared colors across problem vs. solution figures, and uniform `+` prefixes for additive interventions (`Base`, `+ Control`, `+ Method`).
- **TikZ spacing:** Put `\linespread{...}\selectfont` inside the TikZ node `font=` style option rather than inside node body text.

## Code & Replication Audit Hazards
- **Model/wrapper bugs:** Frozen backbones duplicated in `nn.ModuleList`, `wrapper.train()` flipping frozen weights out of `.eval()`, checkpoints saving full frozen weights instead of adapter state dicts, hook registration order breaking `.generate()`, missing `try/finally` hook cleanup.
- **Batching & eval leaks:** Missing `attention_mask`, right-vs-left padding drift vs. `batch=1` log-probabilities, multi-token words where single-token scoring is assumed, relaxed substring matching (`"1" in "1998"`, `"no" in "unknown"`).
- **Split & stimulus leaks:** Strided slicing (`items[::2]`) over alternating `[conflict, control]` lists putting all conflicts in calibration and controls in test; target-only visual scale/position cues; off-canvas rendered badges across seeds.
- **Cluster/SLURM hygiene:** Dozens of copy-pasted `.slurm` files that should share one parameterized launcher + `_env.sh`; missing per-job isolated `TMPDIR`/`TRITON_CACHE_DIR`/local `/tmp/miopen_*` (preventing NFS/Lustre SQLite locks and `$HOME` quota spills).
