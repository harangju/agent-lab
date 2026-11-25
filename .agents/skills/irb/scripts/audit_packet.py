#!/usr/bin/env python3
"""Audit an Exempt IRB packet and/or experiment codebase for sync and compliance issues.

Standard library only (Python 3.11+).

Usage:
    python3 scripts/audit_packet.py --irb notes/human/irb --code notes/human/pairit
    python3 scripts/audit_packet.py --irb irb/
    python3 scripts/audit_packet.py --code experiment/
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
    "archive",
    ".next",
}
CODE_EXTS = {".yaml", ".yml", ".html", ".htm", ".js", ".ts", ".tsx", ".jsx", ".py", ".json"}
MAX_FILE_BYTES = 500_000

PLACEHOLDER_PATTERNS = [
    r"\bPENDING_HIRB_NUMBER\b",
    r"\bREPLACE_WITH_PROLIFIC_CODE\b",
    r"\bHIRB000XXXXX\b",
    r"\{\{[A-Za-z0-9_]+\}\}",
    r"\bTBD\b",
    r"\bTODO\b",
]

# Code signals -> (label, regex, disclosure keywords expected in IRB/consent, denial regex)
TELEMETRY_SIGNALS: list[tuple[str, str, list[str], str | None]] = [
    (
        "tab_focus_logging",
        r"visibilitychange|document\.hidden|addEventListener\s*\(\s*['\"](?:blur|focus)['\"]|tab_switch|focus_loss|blur_count",
        ["tab focus", "tab-focus", "focus timestamp", "visibility", "tab switch", "away from the window"],
        r"no\s+tab|not\s+collect[^.\n]{0,80}focus",
    ),
    (
        "cursor_dwell_tracking",
        r"addEventListener\s*\(\s*['\"](?:mousemove|pointermove|mouseenter|mouseleave)['\"]|onMouseMove|dwell_ms|cursor_dwell|hover_time",
        ["cursor", "hover", "dwell", "mouse"],
        r"no\s+mouse|not\s+collect[^.\n]{0,80}(?:cursor|mouse\s+dwell)",
    ),
    (
        "audio_chime_playback",
        r"\bnew\s+Audio\s*\(|AudioContext|webkitAudioContext|createOscillator|playChime",
        ["chime", "audio alert", "sound alert", "mutable", "mute"],
        None,
    ),
    (
        "media_or_location_api",
        r"getUserMedia|MediaRecorder|navigator\.geolocation",
        ["audio recording", "video recording", "location", "geolocation"],
        r"no\s+(?:audio|video|location|geolocation)",
    ),
    (
        "live_chat_or_multiplayer",
        r"chat_messages|sendChat|matchmaking|wait_room|ws://|wss://|WebSocket",
        ["chat", "team", "matchmaking", "teammate"],
        r"no\s+(?:live\s+)?interaction\s+with\s+other",
    ),
    (
        "browser_storage",
        r"\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b",
        [],
        None,
    ),
]


@dataclass
class Finding:
    level: str  # PASS, WARN, FAIL, INFO
    category: str
    message: str


def extract_docx_text(path: Path) -> str:
    parts: list[str] = []
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        for member in sorted(zf.namelist()):
            if member == "word/document.xml" or (
                member.startswith("word/header") and member.endswith(".xml")
            ):
                root = ET.fromstring(zf.read(member))
                for para in root.findall(".//w:p", ns):
                    t = "".join(node.text or "" for node in para.findall(".//w:t", ns))
                    if t.strip():
                        parts.append(t)
    return "\n".join(parts)


def load_irb_surfaces(irb_dir: Path) -> dict[str, tuple[Path, str]]:
    surfaces: dict[str, tuple[Path, str]] = {}
    if not irb_dir.exists():
        return surfaces

    # Top-level application markdown(s)
    for md in sorted(irb_dir.glob("*.md")):
        if md.name.lower() == "readme.md":
            continue
        surfaces[f"app:{md.name}"] = (md, md.read_text(encoding="utf-8", errors="replace"))

    # Source markdowns
    sources_dir = irb_dir / "sources"
    if sources_dir.is_dir():
        for md in sorted(sources_dir.glob("*.md")):
            surfaces[f"source:{md.name}"] = (md, md.read_text(encoding="utf-8", errors="replace"))

    # Built attachments (.docx)
    att_dir = irb_dir / "attachments"
    if att_dir.is_dir():
        for docx_path in sorted(att_dir.glob("*.docx")):
            try:
                surfaces[f"docx:{docx_path.name}"] = (docx_path, extract_docx_text(docx_path))
            except Exception as exc:
                surfaces[f"docx:{docx_path.name}"] = (docx_path, f"[ERROR reading docx: {exc}]")

    return surfaces


def iter_code_files(code_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(code_dir.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file() or path.suffix.lower() not in CODE_EXTS:
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        files.append(path)
    return files


def extract_numbers_summary(text: str) -> dict[str, set[str]]:
    dollars = set(re.findall(r"\$\d+(?:\.\d{2})?", text))
    # Capture duration phrases like "35 minutes", "15-20 minutes", "10–15 min"
    durations = {
        re.sub(r"\s+", " ", m.group(0).lower().replace("–", "-").replace("—", "-"))
        for m in re.finditer(r"\b\d+(?:\s*[-–—]\s*\d+)?\s*(?:minutes?|mins?)\b", text, re.I)
    }
    hirb_ids = set(re.findall(r"\bHIRB\d{5,}\b", text))
    return {"dollars": dollars, "durations": durations, "hirb_ids": hirb_ids}


def audit_code(code_dir: Path) -> tuple[list[Finding], dict[str, list[str]], dict[str, tuple[Path, str]]]:
    findings: list[Finding] = []
    detected: dict[str, list[str]] = {}
    config_surfaces: dict[str, tuple[Path, str]] = {}

    files = iter_code_files(code_dir)
    if not files:
        findings.append(Finding("WARN", "code", f"No readable code/config files found under {code_dir}"))
        return findings, detected, config_surfaces

    for f in files:
        rel = str(f.relative_to(code_dir))
        text = f.read_text(encoding="utf-8", errors="replace")

        if f.suffix.lower() in {".yaml", ".yml"} or "consent" in f.name.lower():
            config_surfaces[f"code:{rel}"] = (f, text)

        for label, pattern, _, _ in TELEMETRY_SIGNALS:
            hits = re.findall(pattern, text)
            if hits:
                detected.setdefault(label, []).append(f"{rel} ({len(hits)} hit(s))")

        # Experiment YAML-specific checks
        if f.name in {"experiment.yaml", "experiment.yml"}:
            if not re.search(r"allowRetake\s*:\s*false", text, re.I):
                findings.append(
                    Finding("WARN", "code-config", f"{rel}: `allowRetake: false` not found (check duplicate prevention)")
                )
            else:
                findings.append(Finding("PASS", "code-config", f"{rel}: `allowRetake: false` is enabled"))

            if not re.search(r"opt[_-]?out|do not wish to participate|decline", text, re.I):
                findings.append(
                    Finding("FAIL", "code-config", f"{rel}: no consent opt-out / decline path detected")
                )
            else:
                findings.append(Finding("PASS", "code-config", f"{rel}: consent opt-out / decline path found"))

            # Check if survey items force required: true
            if "type: survey" in text:
                survey_part = text.split("type: survey", 1)[1]
                if re.search(r"required\s*:\s*true", survey_part):
                    findings.append(
                        Finding("WARN", "code-config", f"{rel}: survey contains `required: true` (verify skip / Prefer not to answer)")
                    )
                else:
                    findings.append(Finding("PASS", "code-config", f"{rel}: survey items allow skipping"))

            for ph in PLACEHOLDER_PATTERNS:
                for m in re.finditer(ph, text):
                    findings.append(Finding("WARN", "placeholder", f"{rel}: unresolved token `{m.group(0)}`"))

    for label, locs in sorted(detected.items()):
        findings.append(Finding("INFO", "code-signal", f"Detected `{label}` in: {', '.join(locs)}"))

    return findings, detected, config_surfaces


def audit_irb(
    irb_surfaces: dict[str, tuple[Path, str]],
    detected_code_signals: dict[str, list[str]],
    code_config_surfaces: dict[str, tuple[Path, str]],
) -> list[Finding]:
    findings: list[Finding] = []

    if not irb_surfaces:
        findings.append(Finding("FAIL", "irb", "No IRB application markdown or .docx attachments found"))
        return findings

    app_texts = [txt for k, (_, txt) in irb_surfaces.items() if k.startswith("app:")]
    consent_texts = [
        txt for k, (_, txt) in irb_surfaces.items() if k.startswith("docx:") and "consent" in k.lower()
    ]
    recruit_texts = [
        txt for k, (_, txt) in irb_surfaces.items() if k.startswith("docx:") and "recruit" in k.lower()
    ]
    all_irb_text = "\n".join(txt for _, txt in irb_surfaces.values())
    app_text = "\n".join(app_texts)
    consent_text = "\n".join(consent_texts)

    # 1. Placeholders
    for name, (_, txt) in irb_surfaces.items():
        found_ph = sorted({m.group(0) for p in PLACEHOLDER_PATTERNS for m in re.finditer(p, txt)})
        if found_ph:
            findings.append(Finding("WARN", "placeholder", f"{name}: unresolved token(s): {', '.join(found_ph)}"))

    # 2. Cross-surface comparison (dollars, durations, HIRB IDs)
    combined_surfaces = dict(irb_surfaces)
    combined_surfaces.update(code_config_surfaces)
    summaries = {name: extract_numbers_summary(txt) for name, (_, txt) in combined_surfaces.items()}

    all_hirb_ids = set().union(*(s["hirb_ids"] for s in summaries.values())) if summaries else set()
    if len(all_hirb_ids) > 1:
        findings.append(
            Finding("FAIL", "sync", f"Multiple different HIRB IDs found across files: {sorted(all_hirb_ids)}")
        )
    elif len(all_hirb_ids) == 1:
        hirb_id = next(iter(all_hirb_ids))
        missing_id = [
            name
            for name, s in summaries.items()
            if hirb_id not in s["hirb_ids"] and not name.startswith("source:")
        ]
        if missing_id:
            findings.append(
                Finding("WARN", "sync", f"IRB ID `{hirb_id}` missing from: {', '.join(missing_id)}")
            )
        else:
            findings.append(Finding("PASS", "sync", f"IRB ID `{hirb_id}` consistent across surfaces"))

    # Print dollar & duration inventory per surface so mismatches are obvious
    dollar_rows = [f"{name}={sorted(s['dollars'])}" for name, s in summaries.items() if s["dollars"]]
    if dollar_rows:
        findings.append(Finding("INFO", "sync-pay", "Dollar amounts by surface: " + " | ".join(dollar_rows)))
    dur_rows = [f"{name}={sorted(s['durations'])}" for name, s in summaries.items() if s["durations"]]
    if dur_rows:
        findings.append(Finding("INFO", "sync-time", "Durations by surface: " + " | ".join(dur_rows)))

    # Flag if code experiment.yaml has dollar/duration values absent from app draft or consent
    if app_text:
        app_summary = extract_numbers_summary(app_text)
        for cname, csum in summaries.items():
            if not cname.startswith("code:"):
                continue
            extra_dollars = csum["dollars"] - app_summary["dollars"]
            if extra_dollars:
                findings.append(
                    Finding(
                        "FAIL",
                        "sync-pay",
                        f"{cname} mentions dollar amount(s) {sorted(extra_dollars)} not present in application draft",
                    )
                )
            extra_durs = csum["durations"] - app_summary["durations"]
            if extra_durs:
                findings.append(
                    Finding(
                        "WARN",
                        "sync-time",
                        f"{cname} mentions duration(s) {sorted(extra_durs)} not verbatim in application draft (verify within ceiling)",
                    )
                )

    # 3. Code telemetry vs IRB & live-consent disclosure checks
    if detected_code_signals and app_text:
        live_consent_text = "\n".join(
            txt for k, (_, txt) in code_config_surfaces.items() if "experiment.y" in k.lower() or "consent" in k.lower()
        )
        for label, pattern, keywords, denial_re in TELEMETRY_SIGNALS:
            if label not in detected_code_signals:
                continue
            locs = ", ".join(detected_code_signals[label])
            if denial_re and re.search(denial_re, all_irb_text, re.I):
                findings.append(
                    Finding(
                        "FAIL",
                        "code-vs-irb",
                        f"Code triggers `{label}` ({locs}), but IRB text appears to deny it (matched `{denial_re}`)",
                    )
                )
            if keywords:
                in_app = any(re.search(rf"\b{re.escape(kw)}", app_text, re.I) for kw in keywords)
                in_consent = (
                    any(re.search(rf"\b{re.escape(kw)}", consent_text, re.I) for kw in keywords)
                    if consent_text
                    else True
                )
                in_live = (
                    any(re.search(rf"\b{re.escape(kw)}", live_consent_text, re.I) for kw in keywords)
                    if live_consent_text
                    else True
                )
                if not in_app:
                    findings.append(
                        Finding(
                            "FAIL",
                            "code-vs-irb",
                            f"Code triggers `{label}` ({locs}), but application draft does not disclose any of {keywords}",
                        )
                    )
                if consent_text and not in_consent:
                    findings.append(
                        Finding(
                            "FAIL",
                            "code-vs-irb",
                            f"Code triggers `{label}` ({locs}), but Consent-Statement.docx does not disclose any of {keywords}",
                        )
                    )
                if live_consent_text and not in_live:
                    findings.append(
                        Finding(
                            "FAIL",
                            "code-vs-live-consent",
                            f"Code triggers `{label}` ({locs}), but live experiment config/consent does not disclose any of {keywords}",
                        )
                    )
                if in_app and in_consent and in_live:
                    findings.append(
                        Finding("PASS", "code-vs-irb", f"`{label}` disclosed across application, consent attachment, and live config")
                    )

    # 4. Institutional (JHU HIRB Exempt) landmine checks on application draft
    if app_text:
        # Payment => Funded + JHU payment procedures + no SSN
        paid = bool(re.search(r"Prolific|\$\d+", app_text))
        if paid:
            if re.search(r"Currently funded", app_text, re.I):
                findings.append(Finding("PASS", "hirb-funding", "Paid study marked 'Currently funded'"))
            else:
                findings.append(
                    Finding("FAIL", "hirb-funding", "Study pays participants but 'Currently funded' not found in Section 7")
                )

            proc_hits = len(re.findall(r"Procedures for Paying Research Participants", app_text, re.I))
            if proc_hits >= 2:
                findings.append(
                    Finding("PASS", "hirb-payment", "JHU Procedures for Paying Research Participants confirmed in both 7.2 and 14.11")
                )
            elif proc_hits == 1:
                findings.append(
                    Finding("WARN", "hirb-payment", "JHU Procedures for Paying Research Participants appears once (confirm in BOTH 7.2 and 14.11)")
                )
            else:
                findings.append(
                    Finding("FAIL", "hirb-payment", "Missing confirmation of JHU Procedures for Paying Research Participants (7.2 & 14.11)")
                )

            if re.search(r"Social Security|SSN", app_text, re.I):
                findings.append(Finding("PASS", "hirb-payment", "No-SSN / no direct university payment language present"))
            else:
                findings.append(
                    Finding("WARN", "hirb-payment", "Section 14.12 should explicitly state no SSN/tax info is collected")
                )

            if re.search(r"fraud", app_text, re.I):
                findings.append(Finding("PASS", "hirb-fraud", "Fraud-prevention measures addressed"))
            else:
                findings.append(
                    Finding("WARN", "hirb-fraud", "No fraud-prevention measures detected for paid online recruitment")
                )

        # Section 15.1.0 breach harms
        harm_hits = [
            kw
            for kw in ["reputational", "embarrassment", "distress", "misuse", "identification"]
            if re.search(kw, app_text, re.I)
        ]
        if len(harm_hits) >= 2:
            findings.append(Finding("PASS", "hirb-risk", f"Confidentiality-breach harms stated ({', '.join(harm_hits)})"))
        else:
            findings.append(
                Finding("WARN", "hirb-risk", "Section 15.1.0 may be missing explicit confidentiality-breach harms")
            )

        # Open-text / chat PII reminder
        if re.search(r"open-ended|free-text|open responses|text chat", app_text, re.I):
            if re.search(r"not to include[^.\n]{0,80}(?:personal|identifying|incriminating)", app_text, re.I):
                findings.append(Finding("PASS", "hirb-pii", "Open-text/chat no-PII warning found"))
            else:
                findings.append(
                    Finding("FAIL", "hirb-pii", "Open-text/chat present, but explicit no-PII warning not detected")
                )
            if re.search(r"redact", app_text, re.I):
                findings.append(Finding("PASS", "hirb-pii", "Pre-analysis PII redaction stated"))
            else:
                findings.append(Finding("WARN", "hirb-pii", "Open-text/chat present, but pre-analysis redaction not stated in 15.1.1"))

        # Modified NASA-TLX check
        if re.search(r"NASA-TLX", app_text, re.I) and not re.search(r"modified|adapted", app_text, re.I):
            findings.append(
                Finding("WARN", "hirb-scales", "`NASA-TLX` mentioned without `modified`/`adapted` (verify whether full validated 6-item 0-100 scale is used)")
            )

        # Screening 1.1 AI validation check
        s11 = re.search(
            r"device/algorithm/app be developed and/or validated.*?\n+\s*(Yes|No)\b",
            app_text,
            re.I | re.S,
        )
        if s11 and s11.group(1).lower() == "yes":
            findings.append(
                Finding("WARN", "hirb-ai", "Screening 1.1 is 'Yes' (validating an AI tool) — confirm consent describes the AI tool being validated")
            )

    # Recruitment required elements check
    if recruit_texts:
        rtxt = "\n".join(recruit_texts)
        missing_req = [
            label
            for label, pat in [
                ("research study label", r"research study"),
                ("voluntary", r"voluntary"),
                ("IRB contact", r"hirb@jhu\.edu|410-516-6580|IRB"),
                ("eligibility", r"18|eligib"),
                ("compensation", r"\$\d+|payment|paid"),
            ]
            if not re.search(pat, rtxt, re.I)
        ]
        if missing_req:
            findings.append(
                Finding("WARN", "hirb-recruitment", f"Recruitment attachment missing expected element(s): {', '.join(missing_req)}")
            )
        else:
            findings.append(Finding("PASS", "hirb-recruitment", "Recruitment attachment contains core required elements"))

    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit Exempt IRB packet and/or experiment code.")
    ap.add_argument("--irb", type=Path, default=None, help="Path to IRB packet directory")
    ap.add_argument("--code", type=Path, default=None, help="Path to experiment code/config directory")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any FAIL finding occurs")
    args = ap.parse_args(argv or sys.argv[1:])

    if not args.irb and not args.code:
        ap.error("Provide at least one of --irb or --code")

    all_findings: list[Finding] = []
    detected_signals: dict[str, list[str]] = {}
    code_configs: dict[str, tuple[Path, str]] = {}

    if args.code:
        code_findings, detected_signals, code_configs = audit_code(args.code)
        all_findings.extend(code_findings)

    if args.irb:
        irb_surfaces = load_irb_surfaces(args.irb)
        all_findings.extend(audit_irb(irb_surfaces, detected_signals, code_configs))

    counts = {"FAIL": 0, "WARN": 0, "PASS": 0, "INFO": 0}
    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}
    for f in sorted(all_findings, key=lambda x: (order.get(x.level, 9), x.category)):
        counts[f.level] = counts.get(f.level, 0) + 1
        print(f"[{f.level}] ({f.category}) {f.message}")

    print(
        f"\nSummary: {counts['FAIL']} FAIL, {counts['WARN']} WARN, "
        f"{counts['PASS']} PASS, {counts['INFO']} INFO"
    )
    if args.strict and counts["FAIL"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
