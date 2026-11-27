#!/usr/bin/env python3
"""Manuscript style, citation, and number-provenance linter.

Zero-dependency Python 3 CLI designed for scholarly Markdown and LaTeX manuscripts.
Checks prose against agent-lab STYLE.md defaults (plus optional project config),
enforces venue word caps, validates citations, detects unresolved @comments,
checks embedded figure paths, and cross-checks numeric claims against locked
results/*.json files.

Usage:
    python3 lint_manuscript.py notes/paper.md
    python3 lint_manuscript.py paper/main.tex --bib paper/ref.bib --results results/*.json
    python3 lint_manuscript.py notes/paper.md --config notes/lint.json --bib lit/refs.bib --format json
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_BANNED_PHRASES: list[str] = [
    r"\bthe fact that\b",
    r"\bdue to the fact that\b",
    r"\bin order to\b",
    r"\bsynergistic\b",
    r"\brevolutionary\b",
    r"\bleverage[sd]?\b",
    r"\bleveraging\b",
    r"\butilize[sd]?\b",
    r"\butilizing\b",
    r"\boperationalize[sd]?\b",
    r"\bfacilitate[sd]?\b",
    r"\billuminate[sd]?\b",
]

DEFAULT_AMBIGUOUS_VERBS: list[str] = [
    "splits",
    "breaks",
    "cuts",
    "spreads",
    "partitions",
]

NON_GERUND_ING_WORDS: set[str] = {
    "during",
    "nothing",
    "everything",
    "something",
    "anything",
    "morning",
    "evening",
    "spring",
    "string",
    "king",
    "ring",
    "thing",
    "wing",
    "ceiling",
    "pending",
    "barring",
    "notwithstanding",
    "following",
    "according",
}

BACKWARD_OPENERS_RE = re.compile(
    r"^(This\s+(?:finding|result|pattern|effect|difference|trend|gap|evidence|work|study|paper|analysis|shows|suggests|demonstrates|indicates)|"
    r"These\s+(?:findings|results|patterns|effects|differences|trends|data|numbers|estimates))\b"
)

BARE_THIS_RE = re.compile(
    r"\b[Tt]his\s+(shows|suggests|demonstrates|indicates|proves|means|implies|reveals|confirms|reflects)\b"
)

EXPLANATORY_COLON_RE = re.compile(r"(?<!http)(?<!https):[ \t]+([a-z][a-zA-Z0-9,\- ]{12,})")
GERUND_OPENER_RE = re.compile(r"(?:^|[.!?]\s+)([A-Z][a-z]{3,}ing)\s+([a-z]+)")

# Context prefixes right before a number that denote structural labels, not empirical values
STRUCTURAL_PREFIX_RE = re.compile(
    r"\b(?:Fig(?:ure)?\.?|Table|Tab\.?|Study|Experiment|Exp\.?|Round|Phase|Stage|Gate|"
    r"Section|Sec\.?|Equation|Eq\.?|Theorem|Prop(?:osition)?\.?|Lemma|Corollary|"
    r"Appendix|Supplement(?:ary)?|SI|Note|Model|Arm|Seed|Step|Box|Panel|S|Part|Chapter)\s*$",
    re.IGNORECASE,
)


@dataclass
class Finding:
    severity: str  # "error" or "warn"
    rule: str
    line: int
    message: str
    excerpt: str = ""


def load_config(config_path: Path | None) -> dict[str, Any]:
    if not config_path:
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def strip_non_prose_preserve_lines(text: str) -> tuple[list[str], int | None]:
    """Return prose lines (1-indexed alignment via list index + 1) with
    YAML frontmatter, fenced code, display math, HTML comments, tables,
    and References section blanked out, plus the 1-indexed line where
    References starts (if any).
    """
    raw_lines = text.splitlines()
    out: list[str] = []
    n = len(raw_lines)
    i = 0

    # Skip YAML frontmatter at top of file
    if n > 0 and raw_lines[0].strip() == "---":
        out.append("")
        i = 1
        while i < n and raw_lines[i].strip() != "---":
            out.append("")
            i += 1
        if i < n:
            out.append("")
            i += 1

    in_fence = False
    in_math = False
    in_comment = False
    refs_line: int | None = None

    while i < n:
        line = raw_lines[i]
        stripped = line.strip()

        if refs_line is None and re.match(r"^#{1,3}\s+References\b", stripped, re.IGNORECASE):
            refs_line = i + 1

        if refs_line is not None:
            out.append("")
            i += 1
            continue

        # HTML comments (single or multi-line)
        if in_comment:
            if "-->" in line:
                in_comment = False
            out.append("")
            i += 1
            continue
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            out.append("")
            i += 1
            continue

        # Fenced code blocks
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append("")
            i += 1
            continue
        if in_fence:
            out.append("")
            i += 1
            continue

        # Display math blocks
        if stripped.startswith("$$"):
            if stripped == "$$" or not stripped.endswith("$$") or len(stripped) == 2:
                in_math = not in_math
            out.append("")
            i += 1
            continue
        if in_math:
            out.append("")
            i += 1
            continue

        # Markdown tables, horizontal rules, image-only lines, blockquotes? Keep blockquotes as prose.
        if stripped.startswith("|") or re.match(r"^[-*_]{3,}$", stripped) or re.match(r"^!\[.*\]\(.*\)$", stripped):
            out.append("")
            i += 1
            continue

        # Remove inline HTML comments on prose lines
        cleaned = re.sub(r"<!--.*?-->", "", line)
        out.append(cleaned)
        i += 1

    return out, refs_line


LATEX_SKIP_ENVS: set[str] = {
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "eqnarray",
    "eqnarray*",
    "table",
    "table*",
    "tabular",
    "tabular*",
    "tabularx",
    "tikzpicture",
    "verbatim",
    "lstlisting",
    "minted",
    "algorithm",
    "algorithmic",
    "thebibliography",
}

LATEX_HEADING_RE = re.compile(r"^\\(?:part|chapter|section|subsection|subsubsection)\*?\{")


def expand_latex_inputs(manuscript_path: Path, seen: set[Path] | None = None, root_dir: Path | None = None) -> str:
    """Recursively expand \\input{...} and \\include{...} in a LaTeX manuscript."""
    resolved = manuscript_path.resolve()
    if seen is None:
        seen = set()
    if root_dir is None:
        root_dir = resolved.parent
    if resolved in seen or not resolved.exists():
        return ""
    seen.add(resolved)
    text = resolved.read_text(encoding="utf-8", errors="replace")
    cur_dir = resolved.parent
    out_lines: list[str] = []

    for line in text.splitlines():
        if line.lstrip().startswith("%"):
            out_lines.append(line)
            continue
        m = re.match(r"^\s*\\(?:input|include)\{([^}]+)\}\s*(?:%.*)?$", line)
        if m:
            rel = m.group(1).strip()
            candidates = []
            for base in (cur_dir, root_dir):
                candidates.append(base / rel)
                if not rel.endswith(".tex"):
                    candidates.append(base / f"{rel}.tex")
            found = next((c for c in candidates if c.exists()), None)
            if found is not None:
                out_lines.append(expand_latex_inputs(found, seen, root_dir))
                continue
        out_lines.append(line)
    return "\n".join(out_lines)


def strip_latex_non_prose_preserve_lines(text: str) -> tuple[list[str], int | None]:
    """Return LaTeX prose lines (1-indexed alignment) with preamble, comments,
    equations, tables, TikZ blocks, and bibliography blanked out.
    """
    raw_lines = text.splitlines()
    out: list[str] = []
    has_begin_doc = any(r"\begin{document}" in ln for ln in raw_lines)
    in_doc = not has_begin_doc
    skip_env_stack: list[str] = []
    in_display_math = False
    refs_line: int | None = None

    for idx, line in enumerate(raw_lines):
        lineno = idx + 1
        if not in_doc:
            if r"\begin{document}" in line:
                in_doc = True
            out.append("")
            continue

        # Strip unescaped LaTeX comments
        no_comment = re.sub(r"(?<!\\)%.*$", "", line)
        stripped = no_comment.strip()

        if refs_line is None and re.search(r"\\(?:bibliography|printbibliography)\b|\\begin\{thebibliography\}", stripped):
            refs_line = lineno
        if r"\end{document}" in stripped:
            out.append("")
            refs_line = refs_line or lineno
            continue
        if refs_line is not None:
            out.append("")
            continue

        # Track skipped environments (equations, tables, tikz, verbatim, etc.)
        begins = re.findall(r"\\begin\{([^}]+)\}", stripped)
        ends = re.findall(r"\\end\{([^}]+)\}", stripped)
        entered_skip = False
        for env in begins:
            if env in LATEX_SKIP_ENVS:
                skip_env_stack.append(env)
                entered_skip = True
        if skip_env_stack:
            for env in ends:
                if skip_env_stack and skip_env_stack[-1] == env:
                    skip_env_stack.pop()
            out.append("")
            continue
        if entered_skip:
            out.append("")
            continue

        # Display math \[ ... \] or $$ ... $$
        if r"\[" in stripped or stripped.startswith("$$"):
            if not (r"\]" in stripped or (stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 2)):
                in_display_math = True
            out.append("")
            continue
        if in_display_math:
            if r"\]" in stripped or "$$" in stripped:
                in_display_math = False
            out.append("")
            continue

        # Skip pure structural/layout command lines
        if (
            not stripped
            or re.match(
                r"^\\(?:begin|end|centering|raggedright|vspace|hspace|label|includegraphics|graphicspath|"
                r"maketitle|tableofcontents|clearpage|newpage|appendix|noindent|smallskip|medskip|bigskip|"
                r"toprule|midrule|bottomrule|bibliographystyle|setcounter|renewcommand|newcommand|def|"
                r"title|author|affil|icml\w+|date|keywords)\b",
                stripped,
            )
            and not LATEX_HEADING_RE.match(stripped)
        ):
            out.append("")
            continue

        # Mark LaTeX section headers with '#' prefix so downstream heading checks recognize them
        if LATEX_HEADING_RE.match(stripped):
            out.append("# " + re.sub(r"^\\[a-zA-Z]+\*?\{(.*)\}$", r"\1", stripped))
            continue

        out.append(no_comment)

    return out, refs_line


def clean_inline_markup(line: str, is_latex: bool = False) -> str:
    """Strip inline code, inline math, URLs, markdown links, and LaTeX commands for prose checks."""
    s = re.sub(r"`[^`]*`", " ", line)
    s = re.sub(r"\$[^$]*\$", " ", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"https?://\S+", " ", s)
    if is_latex:
        s = re.sub(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{[^}]*\}", " ", s)
        s = re.sub(r"\\(?:ref|eqref|autoref|cref|Cref|label|url|pageref)\{[^}]*\}", " ", s)
        s = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", s)
        s = re.sub(r"\\(?:textbf|textit|emph|texttt|textsc|textrm|textsf|underline|paragraph|caption|footnote)\*?\{([^{}]*)\}", r"\1", s)
        s = re.sub(r"\\(?:textbf|textit|emph|texttt|textsc|textrm|textsf|underline|paragraph|caption|footnote)\*?\{([^{}]*)\}", r"\1", s)
        s = re.sub(r"\\%", "%", s)
        s = re.sub(r"\\&", "&", s)
        s = re.sub(r"~", " ", s)
        s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", s)
        s = re.sub(r"[{}]", "", s)
    return s


def count_words(prose_lines: list[str], exclude_headings: bool = True, is_latex: bool = False) -> int:
    total = 0
    for line in prose_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if exclude_headings and stripped.startswith("#"):
            continue
        cleaned = clean_inline_markup(stripped, is_latex=is_latex)
        cleaned = re.sub(r"<!--.*?-->", "", cleaned)
        # Drop Pandoc citations like [@smith2024; @jones2025] from word count? Keep conservative standard word split
        words = re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", cleaned)
        total += len(words)
    return total


def check_style(
    prose_lines: list[str],
    banned_patterns: list[str],
    ambiguous_verbs: list[str],
    is_latex: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []
    compiled_banned = [(pat, re.compile(pat, re.IGNORECASE)) for pat in banned_patterns]
    ambiguous_re = (
        re.compile(r"\b(" + "|".join(re.escape(w) for w in ambiguous_verbs) + r")\b", re.IGNORECASE)
        if ambiguous_verbs
        else None
    )

    prev_blank = True
    for idx, raw_line in enumerate(prose_lines):
        lineno = idx + 1
        stripped = raw_line.strip()
        if not stripped:
            prev_blank = True
            continue

        is_heading = stripped.startswith("#")
        is_list_item = bool(re.match(r"^(?:[-*+]|\d+\.)\s+", stripped))
        cleaned = clean_inline_markup(stripped, is_latex=is_latex)

        # 1. Em dashes (hard STYLE.md rule; in LaTeX also catch '---' without spaces, allowing '--' en dashes)
        has_em_dash = "\u2014" in cleaned or bool(re.search(r"(?<=\s)---?(?=\s)", cleaned))
        if is_latex and re.search(r"(?<!-)---(?!-)", cleaned):
            has_em_dash = True
        if has_em_dash:
            findings.append(
                Finding(
                    severity="error",
                    rule="em-dash",
                    line=lineno,
                    message="Em dash found; use a comma, period, or parentheses.",
                    excerpt=stripped[:120],
                )
            )

        # 2. Banned / ornate / filler phrases
        for pat_str, regex in compiled_banned:
            for m in regex.finditer(cleaned):
                findings.append(
                    Finding(
                        severity="error",
                        rule="banned-phrase",
                        line=lineno,
                        message=f"Banned or filler phrase '{m.group(0)}' (pattern: {pat_str}).",
                        excerpt=stripped[:120],
                    )
                )

        if not is_heading:
            # 3. Backward demonstrative paragraph opener
            if prev_blank and not is_list_item:
                text_start = re.sub(r"^>\s*", "", cleaned).strip()
                m_back = BACKWARD_OPENERS_RE.match(text_start)
                if m_back:
                    findings.append(
                        Finding(
                            severity="error",
                            rule="backward-opener",
                            line=lineno,
                            message=(
                                f"Paragraph opens with backward demonstrative '{m_back.group(0)}'; "
                                "name the concrete subject in the topic sentence."
                            ),
                            excerpt=stripped[:120],
                        )
                    )

            # 4. Bare 'this <verb>' without noun
            for m_this in BARE_THIS_RE.finditer(cleaned):
                findings.append(
                    Finding(
                        severity="error",
                        rule="bare-this",
                        line=lineno,
                        message=f"Attach a noun after 'this' instead of '{m_this.group(0)}'.",
                        excerpt=stripped[:120],
                    )
                )

            # 5. Explanatory colons inside narrative sentences (skip bold lead-ins and line-ending list colons)
            if ":" in cleaned and not cleaned.rstrip().endswith(":"):
                no_leadin = re.sub(r"^\*\*[^*]+\*\*:\s*", "", cleaned)
                no_leadin = re.sub(r"^(?:Note|Caution|Tip|Example|Summary|Methods|Results|Discussion):\s*", "", no_leadin)
                m_col = EXPLANATORY_COLON_RE.search(no_leadin)
                if m_col:
                    findings.append(
                        Finding(
                            severity="warn",
                            rule="explanatory-colon",
                            line=lineno,
                            message="Possible explanatory colon in narrative prose; consider splitting into two sentences.",
                            excerpt=stripped[:120],
                        )
                    )

            # 6. Gerund / participle sentence opener heuristic
            for m_ger in GERUND_OPENER_RE.finditer(cleaned):
                word = m_ger.group(1)
                if word.lower() not in NON_GERUND_ING_WORDS:
                    findings.append(
                        Finding(
                            severity="warn",
                            rule="gerund-opener",
                            line=lineno,
                            message=f"Sentence starts with '{word} {m_ger.group(2)}'; check for heavy gerund subject or ambiguous participle.",
                            excerpt=stripped[:120],
                        )
                    )

            # 7. Ambiguous noun-verb words
            if ambiguous_re:
                for m_amb in ambiguous_re.finditer(cleaned):
                    findings.append(
                        Finding(
                            severity="warn",
                            rule="ambiguous-verb",
                            line=lineno,
                            message=f"Noun-verb ambiguous word '{m_amb.group(0)}'; consider an unambiguous verb if used as a verb.",
                            excerpt=stripped[:120],
                        )
                    )

            # 8. Unanchored 'significantly' without numbers in the same sentence
            for sent in re.split(r"(?<=[.!?])\s+", cleaned):
                if re.search(r"\bsignificant(?:ly)?\b", sent, re.IGNORECASE) and not re.search(r"\d", sent):
                    findings.append(
                        Finding(
                            severity="warn",
                            rule="unanchored-significant",
                            line=lineno,
                            message="'significant(ly)' used without an anchored number in the sentence.",
                            excerpt=sent[:120],
                        )
                    )

        prev_blank = False

    return findings


def check_citations_bib(full_text: str, bib_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    bib_text = bib_path.read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_text))

    # Pandoc citations [@key; @key2] or standalone @key (not email) and LaTeX \cite{k1,k2}
    cited_keys: dict[str, int] = {}
    for lineno, line in enumerate(full_text.splitlines(), start=1):
        # LaTeX \cite / \citep / \citet
        for m in re.finditer(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", line):
            for k in m.group(1).split(","):
                k = k.strip()
                if k:
                    cited_keys.setdefault(k, lineno)
        # Pandoc [@key] or @key not preceded by word char (avoids emails)
        for m in re.finditer(r"(?<![\w.])@([A-Za-z][A-Za-z0-9_:\-]*\d{2,4}[A-Za-z0-9_:\-]*)", line):
            cited_keys.setdefault(m.group(1), lineno)

    for key, lineno in sorted(cited_keys.items(), key=lambda x: x[1]):
        if key not in bib_keys:
            findings.append(
                Finding(
                    severity="error",
                    rule="missing-citation",
                    line=lineno,
                    message=f"Citation '@{key}' not found in {bib_path.name}.",
                )
            )

    for key in sorted(bib_keys - set(cited_keys)):
        findings.append(
            Finding(
                severity="warn",
                rule="uncited-bib-entry",
                line=1,
                message=f"BibTeX entry '{key}' in {bib_path.name} is never cited.",
            )
        )

    return findings


def check_numbered_md_refs(full_text: str, refs_line: int | None) -> list[Finding]:
    """Verify citations against a markdown ## References section.

    Supports both numbered citations ([1], (1, 2–4)) and author-year citations
    (Smith, 2024; Smith & Jones, 2024; Smith et al., 2024).
    """
    if refs_line is None:
        return []
    lines = full_text.splitlines()
    body = lines[: refs_line - 1]
    ref_block = lines[refs_line - 1 :]

    defined_entries: list[tuple[int, str]] = []
    for line in ref_block:
        m = re.match(r"^\s*(?:\[(\d+)\]|(\d+)\.)\s+(.+)$", line)
        if m:
            defined_entries.append((int(m.group(1) or m.group(2)), m.group(3).strip()))
    if not defined_entries:
        return []

    defined_nums = {num for num, _ in defined_entries}
    cited_nums: dict[int, int] = {}
    # Match both bracketed [1, 2–4] and Science-style parenthetical (1, 2–4) citations
    cite_re = re.compile(r"(?:\[(\d+(?:\s*[,–\-]\s*\d+)*)\]|\((\d+(?:\s*[,–\-]\s*\d+)*)\))")
    for lineno, line in enumerate(body, start=1):
        cleaned = clean_inline_markup(line)
        for m in cite_re.finditer(cleaned):
            spec = m.group(1) or m.group(2)
            # For parenthetical matches, skip standalone 4-digit years like (2024)
            if m.group(2) and re.fullmatch(r"(?:19|20)\d{2}", spec.strip()):
                continue
            for part in spec.split(","):
                part = part.strip()
                rng = re.match(r"^(\d+)\s*[–\-]\s*(\d+)$", part)
                if rng:
                    lo, hi = int(rng.group(1)), int(rng.group(2))
                    if hi - lo <= 50:
                        for n in range(lo, hi + 1):
                            cited_nums.setdefault(n, lineno)
                elif part.isdigit():
                    cited_nums.setdefault(int(part), lineno)

    # If the body uses author-year style (no numbered citations found), verify by author surname + year
    if not cited_nums:
        body_text = "\n".join(clean_inline_markup(ln) for ln in body)
        findings: list[Finding] = []
        for num, entry in defined_entries:
            # Extract leading surname token (before comma or initials) and 4-digit year
            m_yr = re.search(r"\b((?:19|20)\d{2})\b", entry)
            m_au = re.match(r"^([A-Z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+)?)\s*(?:,|\()", entry)
            if not m_yr or not m_au:
                continue
            surname = m_au.group(1).split()[-1]
            year = m_yr.group(1)
            if not re.search(rf"\b{re.escape(surname)}\b[^\n()]*?\b{year}\b", body_text):
                findings.append(
                    Finding(
                        severity="warn",
                        rule="uncited-reference",
                        line=refs_line,
                        message=f"Reference [{num}] ({surname}, {year}) does not appear to be cited in main text.",
                    )
                )
        return findings

    findings = []
    for num, lineno in sorted(cited_nums.items(), key=lambda x: x[1]):
        if num not in defined_nums:
            findings.append(
                Finding(
                    severity="error",
                    rule="missing-ref-number",
                    line=lineno,
                    message=f"In-text reference [{num}] is not defined under References.",
                )
            )
    for num in sorted(defined_nums - set(cited_nums)):
        findings.append(
            Finding(
                severity="warn",
                rule="uncited-reference",
                line=refs_line,
                message=f"Reference [{num}] is listed under References but never cited in main text.",
            )
        )
    return findings


def collect_json_scalars(obj: Any, out: set[float]) -> None:
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        val = float(obj)
        if math.isfinite(val):
            out.add(val)
            out.add(abs(val))
            # Common percentage representation of proportions stored in [0, 1] or [-1, 1]
            if -1.0 <= val <= 1.0:
                out.add(val * 100.0)
                out.add(abs(val) * 100.0)
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_json_scalars(v, out)
    elif isinstance(obj, list):
        for item in obj:
            collect_json_scalars(item, out)


def number_matches_pool(num_str: str, val: float, pool: set[float], rel_tol: float) -> bool:
    """Check whether a reported number matches any locked JSON scalar up to
    the printed decimal precision (rounding half-unit tolerance) or rel_tol.
    """
    clean = num_str.replace(",", "").rstrip("%")
    if "." in clean:
        decimals = len(clean.split(".", 1)[1])
        round_tol = 0.51 * (10.0 ** (-decimals))
    else:
        round_tol = 0.51  # integer rounding (e.g. 42.3% reported as 42%)

    abs_tol = max(round_tol, abs(val) * rel_tol)
    for candidate in pool:
        if abs(candidate - val) <= abs_tol:
            return True
    return False


def check_number_provenance(
    prose_lines: list[str],
    result_paths: list[Path],
    rel_tol: float = 0.005,
    strict_numbers: bool = False,
    is_latex: bool = False,
) -> tuple[list[Finding], int, int]:
    """Cross-check empirical numbers in prose against locked JSON scalars.

    Returns (findings, checked_count, matched_count).
    """
    pool: set[float] = set()
    for p in result_paths:
        data = json.loads(p.read_text(encoding="utf-8"))
        collect_json_scalars(data, pool)

    findings: list[Finding] = []
    checked = 0
    matched = 0
    num_re = re.compile(r"(?<![A-Za-z0-9_.\-])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(%)?(?![A-Za-z0-9_])")
    severity = "error" if strict_numbers else "warn"

    for idx, raw_line in enumerate(prose_lines):
        lineno = idx + 1
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cleaned = clean_inline_markup(stripped, is_latex=is_latex)
        # Mask bracketed [1, 2, 15-18] and parenthetical (1, 2–4) numbered citations
        cleaned = re.sub(r"\[\d+(?:\s*[,–\-]\s*\d+)*\]", " ", cleaned)
        cleaned = re.sub(r"\(\d{1,3}(?:\s*[,–\-]\s*\d{1,3})*\)", " ", cleaned)

        for m in num_re.finditer(cleaned):
            raw_num = m.group(1)
            is_pct = bool(m.group(2))
            prefix = cleaned[max(0, m.start() - 25) : m.start()]
            if STRUCTURAL_PREFIX_RE.search(prefix):
                continue

            val = float(raw_num.replace(",", ""))
            is_int = "." not in raw_num

            # Skip years (1900-2099) and small narrative counts (<10) unless decimal or percent
            if is_int and not is_pct:
                if 1900 <= val <= 2099:
                    continue
                if val < 10:
                    continue

            checked += 1
            if number_matches_pool(raw_num + ("%" if is_pct else ""), val, pool, rel_tol):
                matched += 1
            else:
                token = raw_num + ("%" if is_pct else "")
                findings.append(
                    Finding(
                        severity=severity,
                        rule="unverified-number",
                        line=lineno,
                        message=f"Number '{token}' not matched in locked JSON results.",
                        excerpt=stripped[:120],
                    )
                )

    return findings, checked, matched


def expand_paths(patterns: list[str]) -> list[Path]:
    out: list[Path] = []
    for pat in patterns:
        matches = glob.glob(pat, recursive=True)
        if matches:
            out.extend(Path(m) for m in sorted(matches))
        else:
            p = Path(pat)
            if p.exists():
                out.append(p)
    return out


def check_inline_comments(full_text: str, forbid_comments: bool = False) -> tuple[list[Finding], int]:
    """Detect unresolved inline review comments in Markdown (<!-- @comment -->) or LaTeX (% @comment ...)."""
    findings: list[Finding] = []
    count = 0
    severity = "error" if forbid_comments else "warn"
    md_pat = re.compile(r"<!--\s*/?@comment\b[^>]*-->", re.IGNORECASE)
    tex_pat = re.compile(r"(?<!\\)%\s*@comment\b.*", re.IGNORECASE)
    for lineno, line in enumerate(full_text.splitlines(), start=1):
        md_matches = list(md_pat.finditer(line))
        opens = [m for m in md_matches if not m.group(0).lstrip("<!- ").startswith("/")]
        n_md = len(opens) if opens else len(md_matches)
        n_tex = len(tex_pat.findall(line))
        n_here = n_md + n_tex
        if n_here:
            count += n_here
            findings.append(
                Finding(
                    severity=severity,
                    rule="unresolved-comment",
                    line=lineno,
                    message=f"{n_here} unresolved inline @comment marker(s) found.",
                    excerpt=line.strip()[:120],
                )
            )
    return findings, count


def check_figure_links(full_text: str, manuscript_path: Path, is_latex: bool = False) -> list[Finding]:
    """Verify that local markdown image embeds or LaTeX \\includegraphics targets resolve to existing files."""
    findings: list[Finding] = []
    base_dir = manuscript_path.resolve().parent

    if is_latex:
        search_dirs = [base_dir]
        for gp in re.findall(r"\\graphicspath\{((?:\s*\{[^}]+\}\s*)+)\}", full_text, re.DOTALL):
            for sub in re.findall(r"\{([^}]+)\}", gp):
                search_dirs.append((base_dir / sub).resolve())
        inc_re = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
        exts = ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg")
        for lineno, line in enumerate(full_text.splitlines(), start=1):
            no_comment = re.sub(r"(?<!\\)%.*$", "", line)
            for m in inc_re.finditer(no_comment):
                raw_target = m.group(1).strip()
                if "\\" in raw_target:
                    continue  # macro path
                exists = False
                for d in search_dirs:
                    for ext in exts:
                        cand = (d / f"{raw_target}{ext}").resolve()
                        if cand.exists():
                            exists = True
                            break
                    if exists:
                        break
                if not exists:
                    findings.append(
                        Finding(
                            severity="error",
                            rule="missing-figure",
                            line=lineno,
                            message=f"Embedded LaTeX figure not found: '{raw_target}'.",
                            excerpt=line.strip()[:120],
                        )
                    )
        return findings

    in_fence = False
    img_re = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    for lineno, line in enumerate(full_text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in img_re.finditer(line):
            raw_target = m.group(1).strip().split()[0].strip("<>")
            if raw_target.startswith(("http://", "https://", "data:")):
                continue
            if raw_target.startswith("file://"):
                candidate = Path(raw_target[len("file://") :])
            else:
                candidate = (base_dir / raw_target).resolve()
            if not candidate.exists():
                findings.append(
                    Finding(
                        severity="error",
                        rule="missing-figure",
                        line=lineno,
                        message=f"Embedded figure not found: '{raw_target}'.",
                        excerpt=stripped[:120],
                    )
                )
    return findings


def lint_manuscript(
    manuscript_path: Path,
    *,
    config_path: Path | None = None,
    max_words: int | None = None,
    bib_path: Path | None = None,
    check_md_refs: bool = False,
    result_paths: list[Path] | None = None,
    extra_banned: list[str] | None = None,
    rel_tol: float = 0.005,
    strict: bool = False,
    strict_numbers: bool = False,
    forbid_comments: bool = False,
) -> dict[str, Any]:
    cfg = load_config(config_path)
    is_latex = manuscript_path.suffix.lower() == ".tex"
    if is_latex:
        full_text = expand_latex_inputs(manuscript_path)
        prose_lines, refs_line = strip_latex_non_prose_preserve_lines(full_text)
    else:
        full_text = manuscript_path.read_text(encoding="utf-8")
        prose_lines, refs_line = strip_non_prose_preserve_lines(full_text)

    effective_max_words = max_words if max_words is not None else cfg.get("max_words")
    banned_patterns = list(DEFAULT_BANNED_PHRASES)
    for term in cfg.get("banned_terms", []):
        banned_patterns.append(term if any(ch in term for ch in r"\[]()*+?|^$") else rf"\b{re.escape(term)}\b")
    for term in extra_banned or []:
        banned_patterns.append(rf"\b{re.escape(term)}\b")

    ambiguous_verbs = cfg.get("ambiguous_verbs", DEFAULT_AMBIGUOUS_VERBS)

    findings: list[Finding] = []
    word_count = count_words(prose_lines, is_latex=is_latex)
    if effective_max_words is not None and word_count > int(effective_max_words):
        findings.append(
            Finding(
                severity="error",
                rule="word-count",
                line=1,
                message=f"Main text word count ({word_count}) exceeds budget ({effective_max_words}).",
            )
        )

    findings.extend(check_style(prose_lines, banned_patterns, ambiguous_verbs, is_latex=is_latex))
    comment_findings, unresolved_comments = check_inline_comments(
        full_text, forbid_comments=(forbid_comments or strict)
    )
    findings.extend(comment_findings)
    findings.extend(check_figure_links(full_text, manuscript_path, is_latex=is_latex))

    if bib_path:
        findings.extend(check_citations_bib(full_text, bib_path))
    if check_md_refs and not is_latex:
        findings.extend(check_numbered_md_refs(full_text, refs_line))

    num_checked = 0
    num_matched = 0
    if result_paths:
        num_findings, num_checked, num_matched = check_number_provenance(
            prose_lines, result_paths, rel_tol=rel_tol, strict_numbers=strict_numbers, is_latex=is_latex
        )
        findings.extend(num_findings)

    if strict:
        for f in findings:
            if f.severity == "warn":
                f.severity = "error"

    findings.sort(key=lambda f: (0 if f.severity == "error" else 1, f.line, f.rule))
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warn")

    return {
        "file": str(manuscript_path),
        "word_count": word_count,
        "max_words": effective_max_words,
        "numbers_checked": num_checked,
        "numbers_matched": num_matched,
        "unresolved_comments": unresolved_comments,
        "errors": errors,
        "warnings": warnings,
        "passed": errors == 0,
        "findings": [asdict(f) for f in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint scholarly markdown manuscripts for style, citations, and number provenance.")
    parser.add_argument("manuscript", type=Path, help="Path to markdown manuscript.")
    parser.add_argument("--config", type=Path, default=None, help="Optional JSON lint config (max_words, banned_terms, ambiguous_verbs).")
    parser.add_argument("--max-words", type=int, default=None, help="Main-text word count cap.")
    parser.add_argument("--bib", type=Path, default=None, help="BibTeX file to verify citations against.")
    parser.add_argument("--check-md-refs", action="store_true", help="Verify numbered [1] or author-year citations against ## References.")
    parser.add_argument("--results", nargs="*", default=[], help="Locked JSON result files (paths or globs) for number provenance.")
    parser.add_argument("--banned", nargs="*", default=[], help="Additional banned literal terms.")
    parser.add_argument("--rel-tol", type=float, default=0.005, help="Relative tolerance for number provenance matching (default: 0.005).")
    parser.add_argument("--strict", action="store_true", help="Treat all warnings (including unresolved @comments) as errors.")
    parser.add_argument("--strict-numbers", action="store_true", help="Treat unmatched numbers as errors.")
    parser.add_argument("--forbid-comments", action="store_true", help="Treat unresolved inline @comment markers as errors (Gate 5 check).")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args(argv)

    if not args.manuscript.exists():
        print(f"Error: file not found: {args.manuscript}", file=sys.stderr)
        return 2

    res_paths = expand_paths(args.results)
    report = lint_manuscript(
        args.manuscript,
        config_path=args.config,
        max_words=args.max_words,
        bib_path=args.bib,
        check_md_refs=args.check_md_refs,
        result_paths=res_paths,
        extra_banned=args.banned,
        rel_tol=args.rel_tol,
        strict=args.strict,
        strict_numbers=args.strict_numbers,
        forbid_comments=args.forbid_comments,
    )

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["passed"] else "FAIL"
        cap_str = f" / {report['max_words']}" if report["max_words"] else ""
        print(
            f"[{status}] {report['file']} | words: {report['word_count']}{cap_str} | "
            f"errors: {report['errors']} | warnings: {report['warnings']} | "
            f"@comments: {report['unresolved_comments']}"
        )
        if report["numbers_checked"]:
            print(
                f"Provenance: {report['numbers_matched']}/{report['numbers_checked']} "
                f"empirical numbers matched locked JSONs"
            )
        for f in report["findings"]:
            tag = "ERR " if f["severity"] == "error" else "WARN"
            print(f"  {tag} L{f['line']:<4} [{f['rule']}] {f['message']}")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
