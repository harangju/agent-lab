#!/usr/bin/env python3
"""Find handwritten markup in a PDF and save zoomed crops to read it from.

Usage:
    python3 -I find_ink.py PAPER.pdf OUT_DIR [--dpi 300] [--pages 2-15,19]

For every page it reports where the ink is, then writes to OUT_DIR:
    page-NN.png        the whole page at 110 dpi, for orientation
    page-NN-cK.png     each ink region at --dpi, padded, for reading
    unflagged-A-B.png  every page NOT flagged, 4 to a sheet at 80 dpi, so
                       you can check by eye that nothing was missed
    ink.json           pages, regions (PDF points) and how each was found

Ink is found one of two ways, and which one ran is reported:
    annotations   the page has ink/stamp/freetext annotations (iOS Markup,
                  Preview, Acrobat). Regions come from rendering with and
                  without annotations and diffing, since iOS Markup stores a
                  whole page of strokes as one page-sized Stamp.
    colour        only when the PDF has no annotations at all: saturated
                  pixels, for ink flattened into the page. Coloured figures
                  and logos show up too, so look before you trust them.

Needs PyMuPDF (`pip install pymupdf`) and numpy.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    import numpy as np
except ImportError as e:  # pragma: no cover
    sys.exit(f"missing dependency: {e}. pip install pymupdf numpy")

INK_ANNOTS = {"Ink", "Stamp", "FreeText", "Text", "Line", "Polygon",
              "PolyLine", "Square", "Circle", "Highlight", "Underline",
              "StrikeOut", "Squiggly", "Caret"}
PAD = 18  # points of context around each region
LOW_DPI = 72


def parse_pages(spec, n):
    if not spec:
        return list(range(1, n + 1))
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return [p for p in out if 1 <= p <= n]


def pix_array(page, dpi, annots=True):
    pm = page.get_pixmap(dpi=dpi, annots=annots, colorspace=fitz.csRGB, alpha=False)
    return np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, 3).astype(int)


def mask_regions(mask, scale, gap=12):
    """Group ink pixels into row bands, then column spans within each band."""
    rows = np.nonzero(mask.any(axis=1))[0]
    if rows.size == 0:
        return []
    bands, start, prev = [], rows[0], rows[0]
    for r in rows[1:]:
        if r - prev > gap:
            bands.append((start, prev))
            start = r
        prev = r
    bands.append((start, prev))
    rects = []
    for y0, y1 in bands:
        cols = np.nonzero(mask[y0:y1 + 1].any(axis=0))[0]
        rects.append(fitz.Rect(cols.min() * scale, y0 * scale,
                               (cols.max() + 1) * scale, (y1 + 1) * scale))
    return [r for r in rects if r.width * r.height > 20]


def merge(rects, slack=PAD):
    rects = [fitz.Rect(r) for r in rects]
    changed = True
    while changed:
        changed = False
        out = []
        for r in rects:
            for o in out:
                if (r + (-slack, -slack, slack, slack)).intersects(o):
                    o |= r
                    changed = True
                    break
            else:
                out.append(r)
        rects = out
    return rects


def find_on_page(page, doc_has_annots):
    annots = [a for a in page.annots() or [] if a.type[1] in INK_ANNOTS]
    kinds = sorted({a.type[1] for a in annots})
    scale = 72 / LOW_DPI
    if annots:
        # Diff with and without annotations to localise the strokes. iOS Markup
        # stores a whole page of ink as one page-sized Stamp, so its rect alone
        # says nothing about where the notes are.
        diff = np.abs(pix_array(page, LOW_DPI, True) - pix_array(page, LOW_DPI, False)).sum(axis=2) > 60
        rects = mask_regions(diff, scale) if diff.sum() > 30 else []
        return "annotations", rects or [a.rect for a in annots], kinds
    if doc_has_annots:
        return None, [], []  # ink lives in annotations here; colour is figures
    rgb = pix_array(page, LOW_DPI, True)
    sat = (rgb.max(axis=2) - rgb.min(axis=2)) > 70
    if sat.sum() > 30:
        return "colour", mask_regions(sat, scale), []
    return None, [], []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--pages", default="")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = []
    doc_has_annots = any(a.type[1] in INK_ANNOTS for pg in doc for a in pg.annots() or [])
    if not doc_has_annots:
        print("no annotations: looking for coloured ink burned into the page "
              "(figures and logos will show up too)")
    for pno in parse_pages(args.pages, doc.page_count):
        page = doc[pno - 1]
        how, rects, kinds = find_on_page(page, doc_has_annots)
        if not rects:
            continue
        rects = merge([r & page.rect for r in rects])
        rects.sort(key=lambda r: (round(r.y0 / 20), r.x0))
        page.get_pixmap(dpi=110).save(out / f"page-{pno:02d}.png")
        regions = []
        for k, r in enumerate(rects, 1):
            clip = (r + (-PAD, -PAD, PAD, PAD)) & page.rect
            # Widen narrow clips to full text width so the marked passage shows.
            if clip.width < page.rect.width * 0.5:
                clip.x0, clip.x1 = page.rect.x0 + 20, page.rect.x1 - 20
            page.get_pixmap(dpi=args.dpi, clip=clip).save(out / f"page-{pno:02d}-c{k}.png")
            regions.append([round(v, 1) for v in clip])
        report.append({"page": pno, "found_by": how, "annot_types": kinds,
                       "regions": regions})
        print(f"p.{pno:>3}  {how:<12} {len(regions)} region(s)  {' '.join(kinds)}")
    # Backstop: every page the detector did not flag goes onto 4-up contact
    # sheets, so a quick look can catch ink it missed (pencil, black ink
    # flattened into the page, ink on a mixed PDF).
    flagged = {r["page"] for r in report}
    rest = [p for p in parse_pages(args.pages, doc.page_count) if p not in flagged]
    sheets = []
    for i in range(0, len(rest), 4):
        group = rest[i:i + 4]
        pms = [doc[p - 1].get_pixmap(dpi=80) for p in group]
        w, h = max(pm.width for pm in pms), max(pm.height for pm in pms)
        sheet = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 2 * w, 2 * h), False)
        sheet.clear_with(255)
        for k, pm in enumerate(pms):
            pm.set_origin((k % 2) * w, (k // 2) * h)
            sheet.copy(pm, pm.irect)
        name = f"unflagged-{group[0]:02d}-{group[-1]:02d}.png"
        sheet.save(out / name)
        sheets.append({"file": name, "pages": group})
    (out / "ink.json").write_text(json.dumps(
        {"pdf": str(Path(args.pdf).resolve()), "pages": doc.page_count,
         "inked": report, "unflagged_sheets": sheets}, indent=1))
    if not report:
        print("no ink found. Render a few pages and look before trusting this.")
    else:
        print(f"{len(report)} of {doc.page_count} pages have ink -> {out}")
    if sheets:
        print(f"{len(rest)} unflagged pages on {len(sheets)} contact sheet(s) "
              "(unflagged-*.png): look at every one before trusting the list")


if __name__ == "__main__":
    main()
