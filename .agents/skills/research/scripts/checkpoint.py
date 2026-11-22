#!/usr/bin/env python3
"""Automated stage checkpoint helper for /research and /save.

Handles the mechanical half of /save + git hygiene:
  1. Appends an immutable entry to `log/YYYY-MM-DD-HHmm-<slug>.md` (never edits existing text).
  2. Updates `CONTEXT.md` (or existing `context.md`) with:
     - Optional updated `**Stage:**` header line
     - Optional newly confirmed dead ends under `## Confirmed Dead Ends`
     - Appended link under `## Session Logs`
  3. Optionally runs a verification command (e.g. `pytest -q`) and, if `--commit`
     is passed and tests pass, commits staged workspace changes cleanly.

Usage:
    python3 checkpoint.py --topic gate2-mechanism --summary "Toy invariants pass" \
        --stage "Stage 2 (Pilot-First Engine)" --dead-end "Model X hits 100% ceiling on trivial seed"
    python3 checkpoint.py --topic stage3-sweep --body-file /tmp/notes.md --test-cmd "pytest -q"
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "checkpoint"


def resolve_context_path(root: Path) -> Path:
    upper = root / "CONTEXT.md"
    lower = root / "context.md"
    if lower.exists() and not upper.exists():
        return lower
    return upper


def append_log_entry(
    root: Path,
    topic: str,
    body: str,
    *,
    now: datetime | None = None,
    log_file: Path | None = None,
) -> Path:
    ts = now or datetime.now()
    log_dir = root / "log"
    log_dir.mkdir(parents=True, exist_ok=True)

    if log_file is not None:
        target = log_file if log_file.is_absolute() else root / log_file
    else:
        fname = f"{ts.strftime('%Y-%m-%d-%H%M')}-{slugify(topic)}.md"
        target = log_dir / fname

    header_time = ts.strftime("%Y-%m-%d %H:%M")
    if target.exists():
        chunk = f"\n\n## Update ({header_time})\n\n{body.strip()}\n"
        with target.open("a", encoding="utf-8") as f:
            f.write(chunk)
    else:
        content = f"# {header_time} — {topic}\n\n{body.strip()}\n"
        target.write_text(content, encoding="utf-8")

    return target


def update_context(
    context_path: Path,
    log_rel_path: str,
    *,
    stage: str | None = None,
    dead_ends: list[str] | None = None,
    today: str | None = None,
) -> None:
    date_str = today or datetime.now().strftime("%Y-%m-%d")
    if not context_path.exists():
        lines = [
            "# Project Context",
            "",
            f"**Stage:** {stage or 'Stage 0 (Seed & Frame)'}",
            f"**Last updated:** {date_str}",
            "",
            "## Confirmed Dead Ends",
            "*(Never retry these without stating what materially changed.)*",
            "- None yet.",
            "",
            "## Session Logs",
            f"- `{log_rel_path}`",
            "",
        ]
        text = "\n".join(lines)
    else:
        text = context_path.read_text(encoding="utf-8")

        if stage:
            if re.search(r"^\*\*Stage:\*\*.*$", text, re.MULTILINE):
                text = re.sub(r"^\*\*Stage:\*\*.*$", f"**Stage:** {stage}", text, count=1, flags=re.MULTILINE)
            else:
                text = re.sub(r"^(# .+)$", rf"\1\n\n**Stage:** {stage}", text, count=1, flags=re.MULTILINE)

        if re.search(r"^\*\*Last updated:\*\*.*$", text, re.MULTILINE):
            text = re.sub(
                r"^\*\*Last updated:\*\*.*$", f"**Last updated:** {date_str}", text, count=1, flags=re.MULTILINE
            )

        # Append log link under Session Logs / Session logs (avoid duplicates)
        log_bullet = f"- `{log_rel_path}`"
        if log_rel_path not in text:
            m_sec = re.search(r"^(##\s+Session\s+[Ll]ogs\s*)$", text, re.MULTILINE)
            if m_sec:
                insert_pos = m_sec.end()
                # Find end of this section (next ## or EOF)
                m_next = re.search(r"^##\s+", text[insert_pos:], re.MULTILINE)
                sec_end = insert_pos + m_next.start() if m_next else len(text)
                prefix = text[:sec_end].rstrip()
                suffix = text[sec_end:]
                text = f"{prefix}\n{log_bullet}\n" + ("\n" + suffix.lstrip("\n") if suffix.strip() else "")
            else:
                text = text.rstrip() + f"\n\n## Session Logs\n{log_bullet}\n"

    # Append any new confirmed dead ends
    if dead_ends:
        m_de = re.search(r"^(##\s+Confirmed\s+Dead\s+Ends\s*)$", text, re.MULTILINE)
        new_bullets = [f"- {d.strip()}" for d in dead_ends if d.strip() and d.strip() not in text]
        if new_bullets:
            if m_de:
                insert_pos = m_de.end()
                m_next = re.search(r"^##\s+", text[insert_pos:], re.MULTILINE)
                sec_end = insert_pos + m_next.start() if m_next else len(text)
                sec_body = text[insert_pos:sec_end]
                sec_body = re.sub(r"^\s*-\s*None yet\.\s*$", "", sec_body, flags=re.MULTILINE)
                prefix = text[:insert_pos] + sec_body.rstrip()
                suffix = text[sec_end:]
                joined = "\n".join(new_bullets)
                text = f"{prefix}\n{joined}\n" + ("\n" + suffix.lstrip("\n") if suffix.strip() else "")
            else:
                joined = "\n".join(new_bullets)
                text = text.rstrip() + f"\n\n## Confirmed Dead Ends\n{joined}\n"

    context_path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append session log, update CONTEXT.md, and optionally test & commit.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root directory.")
    parser.add_argument("--topic", required=True, help="Short checkpoint topic (used for heading and filename slug).")
    parser.add_argument("--summary", default="", help="Markdown body for the log entry.")
    parser.add_argument("--body-file", type=Path, default=None, help="Read log entry body from a markdown file.")
    parser.add_argument("--log-file", type=Path, default=None, help="Existing log file to append to instead of creating a new one.")
    parser.add_argument("--stage", default=None, help="Updated Stage line for CONTEXT.md.")
    parser.add_argument("--dead-end", action="append", default=[], help="Confirmed dead end to append to CONTEXT.md (repeatable).")
    parser.add_argument("--test-cmd", default=None, help="Optional shell command to verify before committing.")
    parser.add_argument("--commit", default=None, help="Optional git commit message (only runs if tests pass and paths are dirty).")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    body = args.body_file.read_text(encoding="utf-8") if args.body_file else args.summary
    if not body.strip():
        print("Error: provide --summary or --body-file.", file=sys.stderr)
        return 2

    log_path = append_log_entry(root, args.topic, body, log_file=args.log_file)
    rel_log = log_path.relative_to(root).as_posix()
    ctx_path = resolve_context_path(root)
    update_context(ctx_path, rel_log, stage=args.stage, dead_ends=args.dead_end)

    print(f"Log updated: {rel_log}")
    print(f"Context updated: {ctx_path.relative_to(root).as_posix()}")

    if args.test_cmd:
        proc = subprocess.run(args.test_cmd, shell=True, cwd=root)
        if proc.returncode != 0:
            print(f"Verification failed (exit {proc.returncode}); skipping commit.", file=sys.stderr)
            return proc.returncode

    if args.commit:
        status = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True)
        if not status.stdout.strip():
            print("Working tree clean; nothing to commit.")
            return 0
        # Stage only the checkpoint files unless already staged; never blind `git add -A` on untracked junk
        subprocess.run(["git", "add", rel_log, ctx_path.relative_to(root).as_posix()], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", args.commit], cwd=root, check=True)
        print(f"Committed checkpoint: {args.commit}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
