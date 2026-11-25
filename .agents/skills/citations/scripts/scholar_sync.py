#!/usr/bin/env python3
"""Fetch Google Scholar profile deltas and merge per-paper yearly citations."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path


UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def norm_title(s: str) -> str:
    return re.sub(r"[‐‑‒–—−]", "-", s).strip().lower()


def fetch_html(url: str) -> str:
    return subprocess.check_output(["curl", "-sL", "-A", UA, url]).decode("utf-8", errors="replace")


def is_gated(body: str) -> bool:
    head = body[:2500].lower()
    return "<title>verifying...</title>" in head or "captcha" in head or "gs_captcha" in body.lower()


def parse_profile(body: str) -> dict:
    # Align .gsc_g_t years with .gsc_g_a bars via z-index so 0-count years are preserved.
    hist_m = re.search(r'<div class="gsc_md_hist_b">(.*?)</div>\s*</div>', body, re.S)
    profile_totals: dict[str, int] = {}
    if hist_m:
        hist_html = hist_m.group(1)
        years = re.findall(r'class="gsc_g_t"[^>]*>(\d{4})<', hist_html)
        bars = re.findall(r'<a[^>]*class="gsc_g_a"[^>]*style="([^"]*)"[^>]*><span class="gsc_g_al">(\d+)</span>', hist_html)
        by_z: dict[int, int] = {}
        for style, val in bars:
            zm = re.search(r"z-index:\s*(\d+)", style)
            if zm:
                by_z[int(zm.group(1))] = int(val)
        n = len(years)
        for idx, y in enumerate(years):
            profile_totals[y] = by_z.get(n - idx, 0)

    stats_raw = [int(x) for x in re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', body)]
    stats = {
        "total": stats_raw[0] if len(stats_raw) > 0 else None,
        "h_index": stats_raw[2] if len(stats_raw) > 2 else None,
        "i10_index": stats_raw[4] if len(stats_raw) > 4 else None,
    }

    papers = []
    for row in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', body, re.S):
        tm = re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', row, re.S)
        cm = re.search(r'class="gsc_a_ac gs_ibl"[^>]*>(\d*)</a>', row)
        hm = re.search(r'href="(/citations\?view_op=view_citation[^"]+)"', row)
        cnt_s = cm.group(1).strip() if cm else ""
        if not cnt_s:
            continue
        href = html.unescape(hm.group(1)) if hm else ""
        idm = re.search(r"citation_for_view=[^:]+:([^&]+)", href)
        papers.append({
            "id": idm.group(1) if idm else "",
            "title": html.unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else "",
            "total": int(cnt_s),
            "href": href,
        })

    return {"profileTotalsByYear": profile_totals, "stats": stats, "papers": papers}


def load_snapshots(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix == ".json":
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def build_console_snippet(changed_ids: list[str]) -> str:
    ids_json = json.dumps(changed_ids)
    return (
        "(() => {\n"
        f"  const target = new Set({ids_json});\n"
        "  const rows = [...document.querySelectorAll('tr.gsc_a_tr')].map(r => {\n"
        "    const a = r.querySelector('.gsc_a_at'), c = r.querySelector('.gsc_a_c a');\n"
        "    const href = a?.getAttribute('href') || '';\n"
        "    const id = href.match(/citation_for_view=[^:]+:([^&]+)/)?.[1];\n"
        "    return { id, title: a?.textContent.trim(), href, total: +(c?.textContent.trim() || 0) };\n"
        "  }).filter(r => r.total > 0 && target.has(r.id));\n"
        "  Promise.all(rows.map(async r => {\n"
        "    const doc = new DOMParser().parseFromString(await (await fetch(r.href)).text(), 'text/html');\n"
        "    const by_year = {};\n"
        "    doc.querySelectorAll('.gsc_oci_g_a').forEach(a => {\n"
        "      const y = (a.getAttribute('href') || '').match(/as_ylo=(\\d{4})/)?.[1];\n"
        "      if (y) by_year[y] = +a.querySelector('.gsc_oci_g_al').textContent.trim();\n"
        "    });\n"
        "    return { id: r.id, title: r.title, total: r.total, by_year, ok: !!doc.querySelector('#gsc_oci_title') };\n"
        "  })).then(papers => {\n"
        "    const out = JSON.stringify(papers);\n"
        "    const btn = document.createElement('button');\n"
        "    btn.textContent = `Copy ${papers.length} papers (ok: ${papers.every(p => p.ok)})`;\n"
        "    btn.style.cssText = 'position:fixed;top:12px;right:12px;z-index:99999;padding:10px 14px;background:#111;color:#fff;border:0;border-radius:8px;font:bold 13px sans-serif;cursor:pointer;';\n"
        "    btn.onclick = () => navigator.clipboard.writeText(out).then(() => { btn.textContent = 'Copied!'; });\n"
        "    document.body.appendChild(btn);\n"
        "  });\n"
        "})();"
    )


def cmd_profile(args: argparse.Namespace) -> int:
    url = f"https://scholar.google.com/citations?user={args.user}&hl=en&cstart=0&pagesize=100"
    body = fetch_html(url)
    if is_gated(body):
        print("BLOCKED: Google Scholar returned an anti-bot verification/CAPTCHA page.", file=sys.stderr)
        return 2

    prof = parse_profile(body)
    prof["user"] = args.user
    prof["date"] = args.date

    if args.out:
        Path(args.out).write_text(json.dumps(prof, indent=2, ensure_ascii=False), encoding="utf-8")

    snaps = load_snapshots(Path(args.citations)) if args.citations else []
    latest = snaps[-1] if snaps else None
    old_by_title = {}
    if latest:
        for p in latest.get("papers", []):
            old_by_title[norm_title(p["title"])] = sum(p.get("by_year", {}).values()) + int(p.get("undated", 0) or 0)

    changed = []
    for p in prof["papers"]:
        prev_tot = old_by_title.get(norm_title(p["title"]), 0)
        if p["total"] != prev_tot:
            changed.append((prev_tot, p))

    print(f"Profile {args.user} ({args.date}): stats={prof['stats']}, cited_papers={len(prof['papers'])}")
    print("profileTotalsByYear:", prof["profileTotalsByYear"])
    if not changed:
        print("Changed papers: 0 (all paper totals match latest snapshot)")
        return 0

    print(f"Changed/new papers ({len(changed)}):")
    for prev_tot, p in changed:
        print(f"  {prev_tot:>3} -> {p['total']:>3} ({p['total'] - prev_tot:+d}) | {p['id']} | {p['title']}")

    snippet = build_console_snippet([p["id"] for _, p in changed if p["id"]])
    if args.pbcopy:
        subprocess.run(["pbcopy"], input=snippet, text=True, check=True)
        print("Copied Chrome DevTools console snippet to clipboard via pbcopy.")
    else:
        print("\n--- Chrome DevTools Console Snippet ---\n" + snippet)
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    cit_path = Path(args.citations)
    snaps = load_snapshots(cit_path)
    prev = snaps[-1] if snaps else None
    prof = json.loads(Path(args.profile_json).read_text(encoding="utf-8"))

    if args.pbpaste:
        raw_papers = subprocess.check_output(["pbpaste"]).decode("utf-8")
    elif args.papers_json:
        raw_papers = Path(args.papers_json).read_text(encoding="utf-8")
    else:
        raw_papers = sys.stdin.read()

    fetched = json.loads(raw_papers)
    if isinstance(fetched, dict) and "papers" in fetched:
        fetched = fetched["papers"]

    failed = [p.get("title") for p in fetched if not p.get("ok", True)]
    if failed:
        print(f"ERROR: Some fetched papers did not pass #gsc_oci_title check: {failed}", file=sys.stderr)
        return 2

    prev_map = {norm_title(p["title"]): p for p in (prev or {}).get("papers", [])}
    fetched_map = {norm_title(p["title"]): p for p in fetched}

    merged_papers = []
    for prof_p in prof["papers"]:
        key = norm_title(prof_p["title"])
        old_p = prev_map.get(key, {})
        new_p = fetched_map.get(key)
        by_year = {str(y): int(c) for y, c in (new_p["by_year"] if new_p else old_p.get("by_year", {})).items() if int(c) > 0}
        by_year = dict(sorted(by_year.items(), key=lambda kv: int(kv[0])))
        dated_sum = sum(by_year.values())
        undated = max(0, prof_p["total"] - dated_sum) if new_p else max(0, int(old_p.get("undated", 0) or 0))
        rec = {
            "title": old_p.get("title", prof_p["title"]),
            "group": old_p.get("group", "Other"),
            "by_year": by_year,
        }
        if undated > 0:
            rec["undated"] = undated
        merged_papers.append(rec)

    merged_papers.sort(key=lambda p: sum(p["by_year"].values()) + p.get("undated", 0), reverse=True)

    date_str = prof.get("date") or args.date
    snap = {
        "date": date_str,
        "profile": prof["user"],
        "source": "Google Scholar",
        "note": args.note,
        "profileTotalsByYear": prof["profileTotalsByYear"],
        "papers": merged_papers,
    }

    out_snaps = [s for s in snaps if s.get("date") != date_str]
    out_snaps.append(snap)
    cit_path.parent.mkdir(parents=True, exist_ok=True)
    with cit_path.open("w", encoding="utf-8") as f:
        for s in out_snaps:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    # Verification summary
    year_sums = collections.Counter()
    for p in merged_papers:
        for y, c in p["by_year"].items():
            year_sums[y] += c
    dated = sum(year_sums.values())
    undated = sum(p.get("undated", 0) for p in merged_papers)
    totals = sorted([sum(p["by_year"].values()) + p.get("undated", 0) for p in merged_papers], reverse=True)
    h = sum(1 for i, c in enumerate(totals) if c >= i + 1)
    i10 = sum(1 for c in totals if c >= 10)
    print(f"Saved {date_str} to {cit_path}: papers={len(merged_papers)}, dated={dated}, undated={undated}, grand={dated+undated}, h={h}, i10={i10}")
    mismatches = {
        y: (year_sums[y], prof["profileTotalsByYear"].get(y, 0))
        for y in sorted(set(year_sums) | set(prof["profileTotalsByYear"]))
        if year_sums[y] != prof["profileTotalsByYear"].get(y, 0)
    }
    if mismatches:
        print("Year-sum vs profileTotalsByYear diffs (unchanged-total paper reclassification?):", mismatches)
    return 0


def main() -> int:
    today = dt.date.today().isoformat()
    ap = argparse.ArgumentParser(description="Sync Google Scholar citations into JSONL.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_prof = sub.add_parser("profile", help="Fetch profile, compute delta, emit Chrome snippet.")
    p_prof.add_argument("--user", required=True, help="Google Scholar user ID")
    p_prof.add_argument("--citations", help="Existing citations JSON/JSONL file for delta")
    p_prof.add_argument("--out", help="Write parsed profile JSON here")
    p_prof.add_argument("--date", default=today, help="Snapshot date (YYYY-MM-DD)")
    p_prof.add_argument("--pbcopy", action="store_true", help="Copy Chrome snippet via pbcopy")

    p_merge = sub.add_parser("merge", help="Merge fetched delta papers into citations JSONL.")
    p_merge.add_argument("--citations", required=True, help="Target citations JSONL file")
    p_merge.add_argument("--profile-json", required=True, help="Path from `profile --out`")
    p_merge.add_argument("--papers-json", help="Path to fetched delta papers JSON")
    p_merge.add_argument("--pbpaste", action="store_true", help="Read fetched delta papers from clipboard")
    p_merge.add_argument("--date", default=today, help="Fallback snapshot date")
    p_merge.add_argument("--note", default="", help="Optional snapshot note")

    args = ap.parse_args()
    if args.cmd == "profile":
        return cmd_profile(args)
    return cmd_merge(args)


if __name__ == "__main__":
    raise SystemExit(main())
