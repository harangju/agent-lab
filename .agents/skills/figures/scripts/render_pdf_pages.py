#!/usr/bin/env python3
"""Render manuscript PDF pages to PNGs for visual QA inspection.

Uses `pdftoppm` when available, falling back to PyMuPDF (`fitz`).
Prints generated PNG paths so an agent can inspect them directly with `read_file`.

Usage:
    python3 render_pdf_pages.py paper/main.pdf --out /tmp/fig_qa --pages 1,3-5
    python3 render_pdf_pages.py paper/main.pdf --out /tmp/fig_qa --figures
    python3 render_pdf_pages.py paper/main.pdf --out /tmp/fig_qa --all --dpi 200
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def parse_page_spec(spec: str, max_page: int) -> list[int]:
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            lo = max(1, int(lo_s))
            hi = min(max_page, int(hi_s))
            pages.update(range(lo, hi + 1))
        else:
            p = int(part)
            if 1 <= p <= max_page:
                pages.add(p)
    return sorted(pages)


def get_pdf_page_count(pdf_path: Path) -> int:
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        proc = subprocess.run([pdfinfo, str(pdf_path)], capture_output=True, text=True)
        if proc.returncode == 0:
            m = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.MULTILINE)
            if m:
                return int(m.group(1))
    try:
        import fitz  # type: ignore

        with fitz.open(pdf_path) as doc:
            return len(doc)
    except Exception as exc:
        raise RuntimeError(f"Could not determine page count (install poppler/pdftoppm or PyMuPDF): {exc}") from exc


def detect_figure_pages(pdf_path: Path, total_pages: int) -> list[int]:
    """Identify pages likely containing figures or tables via page text scan."""
    fig_re = re.compile(r"\b(?:Figure|Fig\.|Table|Extended Data Fig\.)\s+\d+", re.IGNORECASE)
    found: list[int] = []
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        for p in range(1, total_pages + 1):
            proc = subprocess.run(
                [pdftotext, "-f", str(p), "-l", str(p), str(pdf_path), "-"],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0 and fig_re.search(proc.stdout):
                found.append(p)
        return found or list(range(1, min(total_pages, 3) + 1))

    try:
        import fitz  # type: ignore

        with fitz.open(pdf_path) as doc:
            for idx, page in enumerate(doc, start=1):
                if fig_re.search(page.get_text("text")) or page.get_images():
                    found.append(idx)
        return found or list(range(1, min(total_pages, 3) + 1))
    except Exception:
        return list(range(1, total_pages + 1))


def render_pages(pdf_path: Path, out_dir: Path, pages: list[int], dpi: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = pdf_path.stem
    outputs: list[Path] = []
    pdftoppm = shutil.which("pdftoppm")

    if pdftoppm:
        for p in pages:
            prefix = out_dir / f"{stem}_p{p:02d}"
            subprocess.run(
                [pdftoppm, "-png", "-r", str(dpi), "-f", str(p), "-l", str(p), "-singlefile", str(pdf_path), str(prefix)],
                check=True,
                capture_output=True,
                text=True,
            )
            outputs.append(prefix.with_suffix(".png"))
        return outputs

    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Neither `pdftoppm` nor PyMuPDF (`fitz`) is available.") from exc

    scale = dpi / 72.0
    mat = fitz.Matrix(scale, scale)
    with fitz.open(pdf_path) as doc:
        for p in pages:
            pix = doc[p - 1].get_pixmap(matrix=mat, alpha=False)
            out_path = out_dir / f"{stem}_p{p:02d}.png"
            pix.save(str(out_path))
            outputs.append(out_path)
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG for visual QA.")
    parser.add_argument("pdf", type=Path, help="Path to compiled manuscript PDF.")
    parser.add_argument("--out", type=Path, default=Path("/tmp/fig_qa"), help="Output directory for PNGs.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pages", type=str, help="Comma/range page spec, e.g. '1,3-5'.")
    group.add_argument("--figures", action="store_true", help="Auto-detect pages containing Figure/Table references.")
    group.add_argument("--all", action="store_true", help="Render every page.")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI (default: 200).")
    args = parser.parse_args(argv)

    if not args.pdf.exists():
        print(f"Error: PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    total = get_pdf_page_count(args.pdf)
    if args.pages:
        pages = parse_page_spec(args.pages, total)
    elif args.all:
        pages = list(range(1, total + 1))
    else:
        pages = detect_figure_pages(args.pdf, total)

    if not pages:
        print("Error: no valid pages selected.", file=sys.stderr)
        return 2

    outputs = render_pages(args.pdf, args.out, pages, args.dpi)
    print(f"Rendered {len(outputs)}/{total} page(s) from {args.pdf} at {args.dpi} DPI:")
    for path in outputs:
        print(f"  {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
