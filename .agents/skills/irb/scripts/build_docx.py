#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-docx>=1.1",
#     "pyyaml>=6.0",
# ]
# ///
"""Build clean, IRB-formatted Word (.docx) attachments from canonical Markdown files.

Usage:
    uv run scripts/build_docx.py sources/*.md --out attachments/
    uv run scripts/build_docx.py sources/consent.md --out attachments/ --vars sources/vars.yaml --var APP_NO=HIRB00012345

Supported Markdown frontmatter (YAML between --- lines):
    output: Consent-Statement.docx            # Output filename (default: <input-stem>.docx)
    header: "Date prepared: {{DATE}} | PI: {{PI}} | Application No.: {{APP_NO}}"
    title:                                    # Centered bold 12pt title lines at top
      - UNIVERSITY NAME
      - INSTITUTIONAL REVIEW BOARD
      - RESEARCH PARTICIPANT INFORMED CONSENT FORM
    font: Calibri                             # Default: Calibri
    font_size: 11                             # Default: 11

Supported Markdown body syntax:
    # Heading / ## Section Heading            # Bold 11pt section heading
    ### Subheading                            # Bold 11pt subheading
    - Bullet item / * Bullet item             # Word List Bullet
    1. Numbered item                          # Word List Number
    > Blockquote                              # Indented italic paragraph
    | Col 1 | Col 2 |                         # Markdown pipe table
    **bold**, *italic*, `code`                # Inline formatting
    {{VAR_NAME}}                              # Substituted from frontmatter / --vars / --var
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

VAR_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
INLINE_RE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_text = "\n".join(lines[1:i])
                body = "\n".join(lines[i + 1 :]).lstrip("\n")
                meta = yaml.safe_load(fm_text) or {}
                if not isinstance(meta, dict):
                    raise ValueError("Frontmatter must be a YAML mapping")
                return meta, body
    return {}, text


def substitute_vars(text: str, variables: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return str(variables[key]) if key in variables else match.group(0)

    return VAR_RE.sub(repl, text)


def add_inline_runs(paragraph, text: str) -> None:
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos : m.start()])
        token = m.group(0)
        if token.startswith("**") and token.endswith("**"):
            r = paragraph.add_run(token[2:-2])
            r.bold = True
        elif token.startswith("*") and token.endswith("*"):
            r = paragraph.add_run(token[1:-1])
            r.italic = True
        elif token.startswith("`") and token.endswith("`"):
            r = paragraph.add_run(token[1:-1])
            r.font.name = "Courier New"
            r.font.size = Pt(10)
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def parse_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def build_one(
    md_path: Path,
    out_dir: Path,
    shared_vars: dict[str, str],
    cli_vars: dict[str, str],
    allow_unresolved: bool,
) -> Path:
    raw = md_path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)

    # Merge variables: shared_vars < frontmatter scalars < cli_vars
    variables: dict[str, str] = dict(shared_vars)
    for k, v in meta.items():
        if isinstance(v, (str, int, float)) and k not in {"output", "header", "font", "font_size"}:
            variables[str(k)] = str(v)
    variables.update(cli_vars)

    # Resolve header, title lines, and body
    header_text = substitute_vars(str(meta.get("header", "")), variables)
    raw_titles = meta.get("title", [])
    if isinstance(raw_titles, str):
        raw_titles = [raw_titles]
    title_lines = [substitute_vars(str(t), variables) for t in raw_titles]
    body = substitute_vars(body, variables)

    unresolved = sorted(set(VAR_RE.findall(header_text + "\n" + "\n".join(title_lines) + "\n" + body)))
    if unresolved and not allow_unresolved:
        raise ValueError(
            f"{md_path}: unresolved template variable(s): {', '.join(unresolved)} "
            "(pass --var KEY=VALUE or --vars file.yaml)"
        )

    doc = Document()
    font_name = str(meta.get("font", "Calibri"))
    font_size = float(meta.get("font_size", 11))
    normal = doc.styles["Normal"]
    normal.font.name = font_name
    normal.font.size = Pt(font_size)

    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    if header_text.strip():
        hp = section.header.paragraphs[0]
        hp.text = header_text.strip()
        if hp.runs:
            hp.runs[0].font.name = font_name
            hp.runs[0].font.size = Pt(9)

    for t in title_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        r.bold = True
        r.font.size = Pt(12)
    if title_lines:
        doc.add_paragraph()

    lines = body.splitlines()
    i = 0
    para_buf: list[str] = []

    def flush_para() -> None:
        nonlocal para_buf
        if not para_buf:
            return
        text = " ".join(s.strip() for s in para_buf).strip()
        para_buf = []
        if text:
            p = doc.add_paragraph()
            add_inline_runs(p, text)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped == "---":
            flush_para()
            doc.add_paragraph()
            i += 1
            continue

        # Markdown pipe table
        if "|" in stripped and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
            flush_para()
            headers = parse_table_row(line)
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                rows.append(parse_table_row(lines[i]))
                i += 1
            ncols = len(headers)
            table = doc.add_table(rows=1 + len(rows), cols=ncols)
            table.style = "Table Grid"
            for c_idx, h_text in enumerate(headers):
                cell_p = table.rows[0].cells[c_idx].paragraphs[0]
                r = cell_p.add_run(h_text)
                r.bold = True
            for r_idx, row in enumerate(rows, start=1):
                for c_idx in range(min(ncols, len(row))):
                    cell_p = table.rows[r_idx].cells[c_idx].paragraphs[0]
                    add_inline_runs(cell_p, row[c_idx])
            doc.add_paragraph()
            continue

        hm = HEADING_RE.match(stripped)
        if hm:
            flush_para()
            level = len(hm.group(1))
            htext = hm.group(2).strip()
            p = doc.add_paragraph()
            r = p.add_run(htext)
            r.bold = True
            r.font.size = Pt(12 if level == 1 else font_size)
            i += 1
            continue

        bm = BULLET_RE.match(line)
        if bm:
            flush_para()
            p = doc.add_paragraph(style="List Bullet")
            add_inline_runs(p, bm.group(1).strip())
            i += 1
            continue

        nm = NUMBERED_RE.match(line)
        if nm:
            flush_para()
            p = doc.add_paragraph(style="List Number")
            add_inline_runs(p, nm.group(1).strip())
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            q_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35)
            add_inline_runs(p, " ".join(q_lines))
            for r in p.runs:
                r.italic = True
            continue

        # Treat lines starting with "**Label:**" as standalone labeled paragraphs
        if re.match(r"^\*\*[^*]+:\*\*\s*", stripped):
            flush_para()
            p = doc.add_paragraph()
            add_inline_runs(p, stripped)
            i += 1
            continue

        para_buf.append(line)
        i += 1

    flush_para()

    out_name = substitute_vars(str(meta.get("output", md_path.stem + ".docx")), variables)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_name
    doc.save(out_path)
    return out_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build IRB-formatted .docx files from Markdown.")
    ap.add_argument("inputs", nargs="+", type=Path, help="Input Markdown file(s)")
    ap.add_argument("--out", "-o", type=Path, required=True, help="Output directory for .docx files")
    ap.add_argument("--vars", type=Path, default=None, help="Optional YAML file of shared template variables")
    ap.add_argument(
        "--var",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override or define a template variable (repeatable)",
    )
    ap.add_argument(
        "--allow-unresolved",
        action="store_true",
        help="Do not fail if {{VAR}} placeholders remain unresolved",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    shared_vars: dict[str, str] = {}
    if args.vars:
        loaded = yaml.safe_load(args.vars.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            print(f"Error: {args.vars} must contain a YAML mapping", file=sys.stderr)
            return 2
        shared_vars = {str(k): str(v) for k, v in loaded.items()}

    cli_vars: dict[str, str] = {}
    for item in args.var:
        if "=" not in item:
            print(f"Error: --var must be KEY=VALUE, got {item!r}", file=sys.stderr)
            return 2
        k, v = item.split("=", 1)
        cli_vars[k.strip()] = v

    for md_path in args.inputs:
        if not md_path.exists():
            print(f"Error: input not found: {md_path}", file=sys.stderr)
            return 2
        out_path = build_one(md_path, args.out, shared_vars, cli_vars, args.allow_unresolved)
        print(f"Saved: {out_path} ({out_path.stat().st_size:,} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
