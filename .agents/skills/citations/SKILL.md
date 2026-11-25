---
name: citations
description: Fetch and update Google Scholar citation snapshots (profile yearly totals, per-paper by_year breakdowns, undated counts, h-index, and i10-index) into a local JSON/JSONL file. Use when updating citations, syncing a Google Scholar profile, or checking citation growth.
argument-hint: "[scholar user id or url] [citations jsonl path]"
---

# Citations

Update a local citations database (e.g., `citations.jsonl` or `kernel/citations.jsonl`) from a public Google Scholar profile, fetching only changed papers inside Chrome (or `/browser`) so Google Scholar's `view_citation` anti-bot check isn't tripped by headless scripts.

Paths like `scripts/...` are relative to this skill's folder (`<skill-dir>`). Resolve them to absolute paths when running commands.

## 1. Resolve Config

Locate the Scholar `profile` ID and target citations file in order:
1. Explicit user arguments (`user=<ID>`, file path).
2. Existing snapshot file in the repo (`kernel/citations.jsonl`, `citations.jsonl`, or `citations/*.jsonl`) — read `profile` from the latest entry.
3. `~/.config/agent-lab/citations-profile.json` (private local defaults, outside any public skill repo).

If neither `profile` nor target file can be found, ask the user once and offer to save defaults to `~/.config/agent-lab/citations-profile.json`.

## 2. Fetch Profile & Compute Delta

Run the helper script (uses `curl` so system TLS certs work cleanly and checks for any anti-bot gate):

```bash
python3 <skill-dir>/scripts/scholar_sync.py profile --user <ID> --citations <path> --out /tmp/scholar_profile.json --pbcopy
```

This does three things:
1. Fetches the public profile page (`pagesize=100`), parses `profileTotalsByYear` (aligning `.gsc_g_t` years with `.gsc_g_a` bars by `z-index` so zero-citation years are preserved as `0`), headline stats (`total`, `h_index`, `i10_index`), and each cited paper's `id`, `title`, and `total`.
   - If Google Scholar serves a CAPTCHA or `Verifying...` gate, **stop immediately and report the block**—never attempt to solve or bypass it.
2. Compares current paper totals against the latest local snapshot and prints which papers changed or are new.
3. If papers changed, builds a fast parallel (`Promise.all`) Chrome DevTools snippet targeting **only the changed/new papers** and copies it to the clipboard (`--pbcopy`).

If **no papers changed** and `profileTotalsByYear` matches, skip Step 3 and report that citations are already up to date.

## 3. Collect Changed Paper Histograms

Because `view_citation` triggers a `Verifying...` JS check on plain HTTP requests:

- **With `/browser` (Chrome remote debugging enabled):** Navigate to `https://scholar.google.com/citations?user=<ID>&hl=en&cstart=0&pagesize=100`, run the generated snippet (or read `.gsc_oci_g_a` / `.gsc_oci_g_al` for each changed paper), and stop immediately if a verification gate appears.
- **Without `/browser`:** Ask the user to open `https://scholar.google.com/citations?user=<ID>&hl=en&cstart=0&pagesize=100` in **Chrome** (not Safari, which lacks `copy()`), paste the clipboard snippet into DevTools Console, click the `Copy N papers (ok: true)` button that appears at the top-right, and paste (or say `pbpaste`).

## 4. Merge & Verify Snapshot

Merge the pasted delta (`--pbpaste` or `--papers-json <file>`) with `/tmp/scholar_profile.json` into `<path>`:

```bash
python3 <skill-dir>/scripts/scholar_sync.py merge --citations <path> --profile-json /tmp/scholar_profile.json --pbpaste
```

The script:
- Preserves existing `group` labels for known papers (default `"Other"` for new papers).
- Computes `undated = max(0, total - sum(by_year.values()))` per paper and stores `"undated"` only when `> 0`.
- Replaces an existing entry for today's date or appends a new snapshot line, sorted descending by `dated + undated`.
- Prints `dated`, `undated`, `grand`, `h-index`, `i10-index`, and flags any year where `sum(paper by_year)` differs from `profileTotalsByYear` (e.g., if an unchanged-total paper had a citation reclassified across years).

## Notes

- **Why not OpenAlex or Semantic Scholar?** Both have clean APIs, but their counts diverge from Google Scholar (unmerged preprint/journal DOIs, smaller/different citing corpus). Use them only when the user explicitly asks for OpenAlex/Semantic Scholar rather than Google Scholar.
