#!/usr/bin/env python3
"""Primary-source BibTeX verifier and arXiv metadata fetcher.

Zero-dependency Python 3 CLI that:
  1. Parses .bib files (with nested-brace handling) and optionally scans modular
     .tex files (following \\input / \\include) for citation coverage & URLs.
  2. Runs deterministic BibTeX hygiene checks (missing fields, duplicates,
     unbraced post-question-mark/colon title capitals, arXiv-only venues).
  3. Queries primary bibliographic APIs (arXiv API, Crossref, OpenAlex) to catch
     hallucinated/missing authors, fabricated title prefixes, year errors, and
     superseded arXiv preprints.
  4. Fetches exact metadata + abstract for a single arXiv ID/URL (`--arxiv`).

Usage:
    python3 verify_bib.py paper/ref.bib --tex paper/nmi/main.tex --format text
    python3 verify_bib.py paper/ref.bib --offline --format json
    python3 verify_bib.py --arxiv https://arxiv.org/abs/2504.10786
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

USER_AGENT = "agent-lab-verify-bib/1.0 (mailto:research@example.org)"
ARXIV_ID_RE = re.compile(r"(?:arxiv\.org/(?:abs|pdf|html)/|arXiv:)?(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE)
OLD_ARXIV_RE = re.compile(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:)?([a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)", re.IGNORECASE)


@dataclass
class BibEntry:
    key: str
    entry_type: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class Issue:
    severity: str  # "error" | "warn" | "info"
    key: str
    rule: str
    message: str


def strip_braces(text: str) -> str:
    return re.sub(r"[{}]", "", text).strip()


def normalize_text(text: str) -> str:
    s = strip_braces(text).lower()
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def extract_surnames(author_field: str) -> list[str]:
    """Extract lowercase author surnames from a BibTeX author string."""
    if not author_field:
        return []
    parts = re.split(r"\s+and\s+", author_field.strip(), flags=re.IGNORECASE)
    surnames: list[str] = []
    for raw in parts:
        raw = strip_braces(raw).strip()
        if not raw or raw.lower() == "others":
            continue
        if "," in raw:
            surname = raw.split(",", 1)[0].strip()
        else:
            tokens = raw.split()
            surname = tokens[-1] if tokens else ""
        norm = re.sub(r"[^a-z]", "", surname.lower())
        if norm:
            surnames.append(norm)
    return surnames


def parse_bib(text: str) -> list[BibEntry]:
    """Parse BibTeX entries cleanly, respecting nested braces and quoted values."""
    entries: list[BibEntry] = []
    n = len(text)
    i = 0

    while i < n:
        at = text.find("@", i)
        if at == -1:
            break
        line_no = text.count("\n", 0, at) + 1
        m = re.match(r"@([A-Za-z]+)\s*([{(])", text[at:])
        if not m:
            i = at + 1
            continue
        entry_type = m.group(1).lower()
        open_ch = m.group(2)
        close_ch = "}" if open_ch == "{" else ")"
        pos = at + m.end()

        # Find matching closing delimiter for the entry
        depth = 1
        start_body = pos
        while pos < n and depth > 0:
            ch = text[pos]
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
            pos += 1
        body = text[start_body : pos - 1]
        i = pos

        if entry_type in {"comment", "preamble", "string"}:
            continue

        comma = body.find(",")
        if comma == -1:
            continue
        key = body[:comma].strip()
        rest = body[comma + 1 :]
        fields = _parse_bib_fields(rest)
        entries.append(BibEntry(key=key, entry_type=entry_type, line=line_no, fields=fields))

    return entries


def _parse_bib_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    n = len(body)
    i = 0
    while i < n:
        while i < n and body[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        m = re.match(r"([A-Za-z0-9_\-]+)\s*=\s*", body[i:])
        if not m:
            # Skip to next comma/newline
            nxt = body.find("\n", i)
            i = n if nxt == -1 else nxt + 1
            continue
        fname = m.group(1).lower()
        i += m.end()
        if i >= n:
            break

        if body[i] == "{":
            depth = 1
            i += 1
            start = i
            while i < n and depth > 0:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                i += 1
            val = body[start : i - 1]
        elif body[i] == '"':
            i += 1
            start = i
            depth = 0
            while i < n:
                ch = body[i]
                if ch == "{":
                    depth += 1
                elif ch == "}" and depth > 0:
                    depth -= 1
                elif ch == '"' and depth == 0 and (i == start or body[i - 1] != "\\"):
                    break
                i += 1
            val = body[start:i]
            i += 1
        else:
            start = i
            while i < n and body[i] not in ",\r\n":
                i += 1
            val = body[start:i]

        fields[fname] = re.sub(r"\s+", " ", val).strip()
    return fields


def expand_tex_files(tex_path: Path, seen: set[Path] | None = None) -> str:
    """Read a .tex file and recursively inline \\input{...} and \\include{...}."""
    resolved = tex_path.resolve()
    if seen is None:
        seen = set()
    if resolved in seen or not resolved.exists():
        return ""
    seen.add(resolved)
    text = resolved.read_text(encoding="utf-8", errors="replace")
    base = resolved.parent

    def _replace(match: re.Match[str]) -> str:
        rel = match.group(1).strip()
        cand = (base / rel) if rel.endswith(".tex") else (base / f"{rel}.tex")
        if cand.exists():
            return expand_tex_files(cand, seen)
        return match.group(0)

    # Strip full-line comments before following \input so commented inputs aren't expanded
    lines = []
    for ln in text.splitlines():
        if ln.lstrip().startswith("%"):
            continue
        lines.append(re.sub(r"(?<!\\)%.*$", "", ln))
    cleaned = "\n".join(lines)
    return re.sub(r"\\(?:input|include)\{([^}]+)\}", _replace, cleaned)


def extract_tex_citations_and_urls(tex_paths: list[Path]) -> tuple[set[str], list[str]]:
    cited: set[str] = set()
    urls: list[str] = []
    for tp in tex_paths:
        body = expand_tex_files(tp)
        for m in re.finditer(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", body):
            for k in m.group(1).split(","):
                k = k.strip()
                if k:
                    cited.add(k)
        for m in re.finditer(r"\\(?:url|href)\{(https?://[^}]+)\}", body):
            urls.append(m.group(1).strip())
    return cited, sorted(set(urls))


def extract_arxiv_id(entry: BibEntry) -> str | None:
    for field_name in ("eprint", "journal", "booktitle", "howpublished", "url", "note", "doi"):
        val = entry.fields.get(field_name, "")
        if not val:
            continue
        if field_name == "doi" and "arxiv" not in val.lower():
            continue
        m = ARXIV_ID_RE.search(val)
        if m:
            return re.sub(r"v\d+$", "", m.group(1))
        if "arxiv" in val.lower() or field_name == "eprint":
            m2 = OLD_ARXIV_RE.search(val)
            if m2:
                return re.sub(r"v\d+$", "", m2.group(1))
    return None


def check_local_hygiene(entries: list[BibEntry], cited_keys: set[str] | None) -> list[Issue]:
    issues: list[Issue] = []
    seen_keys: set[str] = set()
    seen_dois: dict[str, str] = {}
    seen_arxiv: dict[str, str] = {}

    for e in entries:
        if e.key in seen_keys:
            issues.append(Issue("error", e.key, "duplicate-key", f"Duplicate BibTeX key '{e.key}' (line {e.line})."))
        seen_keys.add(e.key)

        for req in ("title", "year"):
            if not e.fields.get(req):
                issues.append(Issue("error", e.key, "missing-field", f"Missing required field '{req}'."))
        if not e.fields.get("author") and not e.fields.get("editor"):
            issues.append(Issue("error", e.key, "missing-field", "Missing both 'author' and 'editor'."))

        title = e.fields.get("title", "")
        # Flag unbraced capital after '?' or ':' in BibTeX title (lowercased by many styles)
        if re.search(r"[?:]\s+[A-Z](?:[a-z]|\b)", title):
            issues.append(
                Issue(
                    "warn",
                    e.key,
                    "title-case-brace",
                    f"Unbraced capital after '?' or ':' in title: {title[:90]}",
                )
            )

        doi = e.fields.get("doi", "").strip().lower()
        if doi:
            if doi in seen_dois:
                issues.append(Issue("warn", e.key, "duplicate-doi", f"Same DOI as '{seen_dois[doi]}': {doi}"))
            else:
                seen_dois[doi] = e.key

        aid = extract_arxiv_id(e)
        if aid:
            if aid in seen_arxiv:
                issues.append(Issue("warn", e.key, "duplicate-arxiv", f"Same arXiv ID as '{seen_arxiv[aid]}': {aid}"))
            else:
                seen_arxiv[aid] = e.key

    if cited_keys is not None:
        bib_keys = {e.key for e in entries}
        for k in sorted(cited_keys - bib_keys):
            issues.append(Issue("error", k, "missing-bib-entry", f"Cited in TeX but missing from .bib: '{k}'."))
        for k in sorted(bib_keys - cited_keys):
            issues.append(Issue("warn", k, "uncited-bib-entry", f"Present in .bib but never cited in TeX: '{k}'."))

    return issues


def _http_get_text(url: str, timeout: float = 15.0) -> str:
    curl = shutil.which("curl")
    if curl:
        proc = subprocess.run(
            [curl, "-fsSL", "--max-time", str(int(timeout)), "-A", USER_AGENT, url],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"curl exited {proc.returncode}")
        return proc.stdout
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_arxiv_record(arxiv_id_or_url: str) -> dict[str, Any] | None:
    m = ARXIV_ID_RE.search(arxiv_id_or_url) or OLD_ARXIV_RE.search(arxiv_id_or_url)
    aid = m.group(1) if m else arxiv_id_or_url.strip()
    aid = re.sub(r"v\d+$", "", aid)
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(aid)}"
    xml_text = _http_get_text(url)
    root = ET.fromstring(xml_text)
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        return None
    title_el = entry.find("a:title", ns)
    if title_el is None or not (title_el.text or "").strip():
        return None
    title = re.sub(r"\s+", " ", (title_el.text or "").strip())
    summary = re.sub(r"\s+", " ", (entry.findtext("a:summary", default="", namespaces=ns) or "").strip())
    published = (entry.findtext("a:published", default="", namespaces=ns) or "")[:4]
    authors = [
        re.sub(r"\s+", " ", (a.findtext("a:name", default="", namespaces=ns) or "").strip())
        for a in entry.findall("a:author", ns)
    ]
    journal_ref = (entry.findtext("x:journal_ref", default="", namespaces=ns) or "").strip()
    doi = (entry.findtext("x:doi", default="", namespaces=ns) or "").strip()
    return {
        "source": "arxiv",
        "arxiv_id": aid,
        "title": title,
        "authors": authors,
        "year": published,
        "journal_ref": journal_ref,
        "doi": doi,
        "abstract": summary,
    }


def fetch_crossref_record(doi: str | None, title: str, first_surname: str) -> dict[str, Any] | None:
    if doi:
        clean_doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi.strip(), flags=re.IGNORECASE)
        url = f"https://api.crossref.org/works/{urllib.parse.quote(clean_doi, safe='')}"
        data = json.loads(_http_get_text(url))
        item = data.get("message")
        if item:
            return _parse_crossref_item(item)
    if not title:
        return None
    q = urllib.parse.urlencode({"query.title": strip_braces(title), "rows": 3})
    url = f"https://api.crossref.org/works?{q}"
    data = json.loads(_http_get_text(url))
    items = data.get("message", {}).get("items", [])
    norm_target = normalize_text(title)
    for item in items:
        rec = _parse_crossref_item(item)
        if _title_similarity(norm_target, normalize_text(rec["title"])) >= 0.80:
            if not first_surname or any(first_surname in s for s in extract_surnames(" and ".join(rec["authors"]))):
                return rec
    return None


def _parse_crossref_item(item: dict[str, Any]) -> dict[str, Any]:
    titles = item.get("title") or [""]
    authors = []
    for a in item.get("author") or []:
        fam = a.get("family", "")
        giv = a.get("given", "")
        name = f"{giv} {fam}".strip() or a.get("name", "")
        if name:
            authors.append(name)
    year = ""
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (item.get(k) or {}).get("date-parts") or []
        if parts and parts[0]:
            year = str(parts[0][0])
            break
    container = (item.get("container-title") or [""])[0]
    return {
        "source": "crossref",
        "title": titles[0],
        "authors": authors,
        "year": year,
        "venue": container,
        "volume": item.get("volume", ""),
        "issue": item.get("issue", ""),
        "page": item.get("page", ""),
        "doi": item.get("DOI", ""),
    }


def fetch_openalex_record(title: str) -> dict[str, Any] | None:
    if not title:
        return None
    q = urllib.parse.urlencode({"search": strip_braces(title), "per-page": 3})
    url = f"https://api.openalex.org/works?{q}"
    data = json.loads(_http_get_text(url))
    norm_target = normalize_text(title)
    for w in data.get("results", []):
        w_title = w.get("title") or ""
        if _title_similarity(norm_target, normalize_text(w_title)) >= 0.80:
            authors = [
                (au.get("author") or {}).get("display_name", "")
                for au in (w.get("authorships") or [])
                if (au.get("author") or {}).get("display_name")
            ]
            loc = w.get("primary_location") or {}
            src = (loc.get("source") or {}).get("display_name", "")
            return {
                "source": "openalex",
                "title": w_title,
                "authors": authors,
                "year": str(w.get("publication_year") or ""),
                "venue": src,
                "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            }
    return None


def _title_similarity(a: str, b: str) -> float:
    ta = set(a.split())
    tb = set(b.split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def compare_entry_with_record(entry: BibEntry, rec: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    bib_title = normalize_text(entry.fields.get("title", ""))
    rec_title = normalize_text(rec.get("title", ""))
    if bib_title and rec_title and bib_title != rec_title:
        sim = _title_similarity(bib_title, rec_title)
        sev = "error" if sim < 0.90 else "warn"
        issues.append(
            Issue(
                sev,
                entry.key,
                "title-mismatch",
                f"Title differs from {rec['source']} ({sim:.2f} overlap): bib='{strip_braces(entry.fields.get('title',''))}' vs primary='{rec['title']}'",
            )
        )

    bib_surnames = extract_surnames(entry.fields.get("author", ""))
    rec_surnames = extract_surnames(" and ".join(rec.get("authors", [])))
    if bib_surnames and rec_surnames:
        if bib_surnames[0] != rec_surnames[0]:
            issues.append(
                Issue(
                    "error",
                    entry.key,
                    "first-author-mismatch",
                    f"First author differs from {rec['source']}: bib='{bib_surnames[0]}' vs primary='{rec_surnames[0]}'.",
                )
            )
        if "others" not in entry.fields.get("author", "").lower():
            missing = [s for s in rec_surnames if s not in bib_surnames]
            extra = [s for s in bib_surnames if s not in rec_surnames]
            if extra:
                issues.append(
                    Issue(
                        "error",
                        entry.key,
                        "extra-or-wrong-author",
                        f"Author(s) in bib not found in {rec['source']}: {extra} (primary={rec_surnames[:8]}).",
                    )
                )
            elif missing and len(rec_surnames) <= 12:
                issues.append(
                    Issue(
                        "warn",
                        entry.key,
                        "missing-authors",
                        f"Author(s) missing vs {rec['source']}: {missing}.",
                    )
                )

    bib_year = re.sub(r"[^0-9]", "", entry.fields.get("year", ""))[:4]
    rec_year = re.sub(r"[^0-9]", "", str(rec.get("year", "")))[:4]
    if bib_year and rec_year and bib_year != rec_year:
        issues.append(
            Issue(
                "warn",
                entry.key,
                "year-mismatch",
                f"Year differs from {rec['source']}: bib={bib_year} vs primary={rec_year}.",
            )
        )

    # Check if an arXiv entry now has a published peer-reviewed venue
    venue_text = (entry.fields.get("journal", "") + " " + entry.fields.get("booktitle", "")).lower()
    is_arxiv_cited = "arxiv" in venue_text or entry.entry_type == "misc"
    pub_venue = rec.get("journal_ref") or rec.get("venue") or ""
    if is_arxiv_cited and pub_venue and "arxiv" not in pub_venue.lower() and "corr" not in pub_venue.lower():
        issues.append(
            Issue(
                "warn",
                entry.key,
                "published-venue-available",
                f"Cited as preprint/misc, but {rec['source']} lists published venue: '{pub_venue}'.",
            )
        )

    return issues


def check_url_status(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    curl = shutil.which("curl")
    if curl:
        proc = subprocess.run(
            [curl, "-sSIL", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", str(int(timeout)), "-A", USER_AGENT, url],
            capture_output=True,
            text=True,
        )
        code = proc.stdout.strip()
        if code in ("403", "405"):
            proc = subprocess.run(
                [curl, "-sSL", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", str(int(timeout)), "-A", USER_AGENT, url],
                capture_output=True,
                text=True,
            )
            code = proc.stdout.strip()
        if code.isdigit() and 200 <= int(code) < 400:
            return True, f"HTTP {code}"
        return False, f"HTTP {code or proc.stderr.strip()}"
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            try:
                req_get = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req_get, timeout=timeout) as resp:
                    return True, f"HTTP {resp.status}"
            except Exception as e2:
                return False, str(e2)
        return False, f"HTTP {e.code}"
    except Exception as exc:
        return False, str(exc)


def verify_entries_online(entries: list[BibEntry], delay: float = 0.35) -> tuple[list[Issue], dict[str, dict[str, Any]]]:
    issues: list[Issue] = []
    records: dict[str, dict[str, Any]] = {}
    for idx, entry in enumerate(entries):
        if idx > 0 and delay > 0:
            time.sleep(delay)
        rec: dict[str, Any] | None = None
        aid = extract_arxiv_id(entry)
        doi = entry.fields.get("doi")
        title = entry.fields.get("title", "")
        surnames = extract_surnames(entry.fields.get("author", ""))
        first_s = surnames[0] if surnames else ""

        api_errors: list[str] = []
        if aid:
            try:
                rec = fetch_arxiv_record(aid)
            except Exception as exc:
                api_errors.append(f"arXiv: {exc}")
        if rec is None or (aid and not rec.get("journal_ref")):
            try:
                cr = fetch_crossref_record(doi, title, first_s)
                if cr:
                    if rec and not rec.get("journal_ref") and cr.get("venue"):
                        rec["venue"] = cr["venue"]
                    elif rec is None:
                        rec = cr
            except Exception as exc:
                api_errors.append(f"Crossref: {exc}")
        if rec is None:
            try:
                rec = fetch_openalex_record(title)
            except Exception as exc:
                api_errors.append(f"OpenAlex: {exc}")

        if rec is None:
            if api_errors:
                issues.append(Issue("info", entry.key, "api-lookup-error", f"Primary API lookup error: {'; '.join(api_errors)}"))
            else:
                issues.append(
                    Issue("warn", entry.key, "unverified-online", "No exact match in arXiv/Crossref/OpenAlex; verify manually.")
                )
            continue

        records[entry.key] = {k: v for k, v in rec.items() if k != "abstract"}
        issues.extend(compare_entry_with_record(entry, rec))

    return issues, records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify BibTeX entries against primary APIs or fetch an arXiv record.")
    parser.add_argument("bib", type=Path, nargs="?", help="Path to .bib file.")
    parser.add_argument("--tex", type=Path, nargs="*", default=[], help="Main .tex file(s) to check citation coverage & URLs.")
    parser.add_argument("--keys", nargs="*", default=[], help="Optional subset of BibTeX keys to verify.")
    parser.add_argument("--offline", action="store_true", help="Run local hygiene & TeX coverage checks only (no network).")
    parser.add_argument("--check-urls", action="store_true", help="Also verify HTTP reachability of URLs in .bib and .tex.")
    parser.add_argument("--delay", type=float, default=0.35, help="Delay between API calls in seconds (default: 0.35).")
    parser.add_argument("--arxiv", type=str, default=None, help="Fetch metadata + abstract for one arXiv ID or URL and exit.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args(argv)

    if args.arxiv:
        rec = fetch_arxiv_record(args.arxiv)
        if rec is None:
            print(f"Error: could not fetch arXiv record for '{args.arxiv}'.", file=sys.stderr)
            return 2
        if args.format == "json":
            print(json.dumps(rec, indent=2))
        else:
            print(f"Title:   {rec['title']}")
            print(f"Authors: {', '.join(rec['authors'])}")
            print(f"Year:    {rec['year']} | arXiv: {rec['arxiv_id']}")
            if rec.get("journal_ref"):
                print(f"Venue:   {rec['journal_ref']}")
            print(f"\nAbstract:\n{rec['abstract']}")
        return 0

    if not args.bib or not args.bib.exists():
        print("Error: provide an existing .bib file (or --arxiv <id>).", file=sys.stderr)
        return 2

    entries = parse_bib(args.bib.read_text(encoding="utf-8", errors="replace"))
    if args.keys:
        key_set = set(args.keys)
        entries = [e for e in entries if e.key in key_set]

    cited_keys: set[str] | None = None
    urls: list[str] = []
    if args.tex:
        cited_keys, urls = extract_tex_citations_and_urls(args.tex)

    issues = check_local_hygiene(entries, cited_keys)
    records: dict[str, dict[str, Any]] = {}
    if not args.offline:
        online_issues, records = verify_entries_online(entries, delay=args.delay)
        issues.extend(online_issues)

    if args.check_urls and not args.offline:
        for e in entries:
            if e.fields.get("url"):
                urls.append(e.fields["url"])
        for u in sorted(set(urls)):
            ok, detail = check_url_status(u)
            if not ok:
                issues.append(Issue("error", "URL", "broken-url", f"URL check failed ({detail}): {u}"))

    errors = sum(1 for x in issues if x.severity == "error")
    warnings = sum(1 for x in issues if x.severity == "warn")
    report = {
        "bib": str(args.bib),
        "entries_checked": len(entries),
        "verified_online": len(records),
        "errors": errors,
        "warnings": warnings,
        "passed": errors == 0,
        "issues": [asdict(x) for x in issues],
        "records": records,
    }

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["passed"] else "FAIL"
        print(
            f"[{status}] {args.bib} | entries: {len(entries)} | matched online: {len(records)} "
            f"| errors: {errors} | warnings: {warnings}"
        )
        for iss in issues:
            print(f"  {iss.severity.upper():<5} [{iss.key}] ({iss.rule}) {iss.message}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
