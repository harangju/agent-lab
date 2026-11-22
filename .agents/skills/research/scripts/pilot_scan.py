#!/usr/bin/env python3
"""Deterministic 1-seed pilot log scanner, prompt SHA-256 pinner, and Gate Card renderer.

Zero-dependency Python 3 helper used by /research (and pilot_workflow.py) to:
  1. Hash prompt/config files (SHA-256) to verify reproducibility pins.
  2. Scan raw .jsonl / .log trajectories for engineering leaks:
     - JSON parse errors
     - Empty or truncated responses (finish_reason == "length", max_tokens cutoff)
     - Unhandled exceptions / stack traces / API errors
     - Suspected ceiling (>= 0.95) or floor (<= 0.05) metric flags
  3. Extract verbatim raw trajectory excerpts for Trajectory Inspector & Gate 3.
  4. Render an HTML Gate Decision Card from template.html.

Usage:
    python3 pilot_scan.py scan --logs "results/pilot/*.jsonl" --prompts prompts/*.txt
    python3 pilot_scan.py render-card --gate-json gate3.json --out results/gate3.html
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "template.html"

ERROR_PATTERNS = [
    re.compile(r"\bTraceback \(most recent call last\)", re.IGNORECASE),
    re.compile(r"\b(?:JSONDecodeError|SyntaxError|KeyError|ValueError|RuntimeError|TimeoutError)\b"),
    re.compile(r"\b(?:rate[ _-]?limit|429 Too Many Requests|502 Bad Gateway|503 Service Unavailable)\b", re.IGNORECASE),
    re.compile(r"\b(?:parse[ _-]?error|schema[ _-]?validation[ _-]?failed|invalid json)\b", re.IGNORECASE),
]

TRUNCATION_KEYS = {"finish_reason", "stop_reason"}
TRUNCATION_VALUES = {"length", "max_tokens", "max_output_tokens", "truncated"}
METRIC_HINT_KEYS = {"accuracy", "score", "success", "pass_rate", "rate", "solved", "correct"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def expand_globs(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for pat in patterns:
        matches = glob.glob(pat, recursive=True)
        candidates = [Path(m) for m in sorted(matches)] if matches else ([Path(pat)] if Path(pat).exists() else [])
        for p in candidates:
            rp = p.resolve()
            if p.is_file() and rp not in seen:
                seen.add(rp)
                paths.append(p)
    return paths


def inspect_record(obj: Any, leaks: dict[str, list[str]], metrics: dict[str, list[float]], loc: str) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in TRUNCATION_KEYS and str(v).lower() in TRUNCATION_VALUES:
                leaks["truncation"].append(f"{loc}: {k}={v}")
            if kl in {"error", "exception", "parse_error"} and v not in (None, "", False, 0):
                leaks["errors"].append(f"{loc}: {k}={str(v)[:160]}")
            if kl in {"response", "content", "output", "text", "assistant"} and isinstance(v, str) and not v.strip():
                leaks["empty_output"].append(f"{loc}: empty '{k}'")
            if kl in METRIC_HINT_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool):
                fv = float(v)
                if 0.0 <= fv <= 1.0:
                    metrics.setdefault(kl, []).append(fv)
            inspect_record(v, leaks, metrics, loc)
    elif isinstance(obj, list):
        for item in obj:
            inspect_record(item, leaks, metrics, loc)
    elif isinstance(obj, str):
        for pat in ERROR_PATTERNS:
            if pat.search(obj):
                leaks["errors"].append(f"{loc}: matched /{pat.pattern}/")
                break


def scan_pilot(
    log_paths: list[Path],
    prompt_paths: list[Path] | None = None,
    max_excerpts: int = 3,
    excerpt_chars: int = 600,
) -> dict[str, Any]:
    prompt_pins = {str(p): sha256_file(p) for p in (prompt_paths or [])}

    leaks: dict[str, list[str]] = {
        "json_parse": [],
        "truncation": [],
        "empty_output": [],
        "errors": [],
    }
    metrics: dict[str, list[float]] = {}
    excerpts: list[dict[str, str]] = []
    total_records = 0

    for p in log_paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if not lines:
            leaks["empty_output"].append(f"{p.name}: file is empty")
            continue

        if p.suffix.lower() == ".jsonl":
            for lineno, line in enumerate(lines, start=1):
                total_records += 1
                loc = f"{p.name}:L{lineno}"
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    leaks["json_parse"].append(f"{loc}: {exc.msg}")
                    continue
                inspect_record(obj, leaks, metrics, loc)
                if len(excerpts) < max_excerpts:
                    excerpts.append({"source": loc, "snippet": line[:excerpt_chars]})
        elif p.suffix.lower() == ".json":
            total_records += 1
            try:
                obj = json.loads(text)
                inspect_record(obj, leaks, metrics, p.name)
                if len(excerpts) < max_excerpts:
                    excerpts.append({"source": p.name, "snippet": text[:excerpt_chars]})
            except json.JSONDecodeError as exc:
                leaks["json_parse"].append(f"{p.name}: {exc.msg}")
        else:
            total_records += len(lines)
            for lineno, line in enumerate(lines, start=1):
                for pat in ERROR_PATTERNS:
                    if pat.search(line):
                        leaks["errors"].append(f"{p.name}:L{lineno}: matched /{pat.pattern}/")
                        break
            if len(excerpts) < max_excerpts:
                excerpts.append({"source": p.name, "snippet": text[:excerpt_chars]})

    ceiling_floor_flags: list[str] = []
    metric_summary: dict[str, dict[str, float]] = {}
    for k, vals in metrics.items():
        if not vals:
            continue
        mean_val = sum(vals) / len(vals)
        metric_summary[k] = {"n": float(len(vals)), "mean": round(mean_val, 4), "min": min(vals), "max": max(vals)}
        if mean_val >= 0.95:
            ceiling_floor_flags.append(f"Possible ceiling effect on '{k}': mean={mean_val:.3f} (n={len(vals)})")
        elif mean_val <= 0.05:
            ceiling_floor_flags.append(f"Possible floor effect on '{k}': mean={mean_val:.3f} (n={len(vals)})")

    leak_count = sum(len(v) for v in leaks.values())
    return {
        "files_scanned": [str(p) for p in log_paths],
        "total_records": total_records,
        "prompt_pins": prompt_pins,
        "leak_count": leak_count,
        "leaks": leaks,
        "metric_summary": metric_summary,
        "ceiling_floor_flags": ceiling_floor_flags,
        "excerpts": excerpts,
        "clean": leak_count == 0,
    }


def render_gate_card(gate_data: dict[str, Any], template_path: Path = TEMPLATE_PATH) -> str:
    tpl = template_path.read_text(encoding="utf-8")
    tpl = re.sub(r"<!--.*?-->\s*", "", tpl, count=1, flags=re.DOTALL)

    anomalies = gate_data.get("anomalies") or []
    leak_count = int(gate_data.get("leak_count", 0))
    checks = gate_data.get("checks") or []
    has_fail = any(c.get("status") == "fail" for c in checks) or leak_count > 0

    if has_fail:
        status_class, status_label = "fail", "Blocked — Action Required"
    elif anomalies:
        status_class, status_label = "warn", "Anomaly Flagged"
    else:
        status_class, status_label = "pass", "Ready for PI Sign-Off"

    cost = gate_data.get("cost_usd_est")
    cost_str = f"${cost:.2f}" if isinstance(cost, (int, float)) else "N/A"
    runtime = gate_data.get("runtime_min_est")
    runtime_str = f"{runtime:.1f} min" if isinstance(runtime, (int, float)) else "N/A"

    if anomalies:
        items_html = "".join(f"<li>{html.escape(str(a))}</li>" for a in anomalies)
        anomaly_section = (
            '<section class="anomaly-banner">'
            '<span class="eyebrow" style="color:inherit;">Anomaly Circuit-Breaker</span>'
            f"<ul>{items_html}</ul></section>"
        )
    else:
        anomaly_section = ""

    checks_rows = []
    for c in checks:
        st = str(c.get("status", "not_run"))
        if st not in {"pass", "warn", "fail", "not_run"}:
            st = "not_run"
        checks_rows.append(
            f"<tr><td><b>{html.escape(str(c.get('name', '')))}</b></td>"
            f"<td><span class=\"pill {st}\">{html.escape(st.upper())}</span></td>"
            f"<td>{html.escape(str(c.get('detail', '')))}</td></tr>"
        )

    visual_path = gate_data.get("visual_path")
    if visual_path:
        vp = html.escape(str(visual_path))
        visual_section = (
            '<section class="visual">'
            '<span class="eyebrow">Evidence Visual</span>'
            f'<img src="{vp}" alt="Gate visual">'
            f'<p style="font-size:.88rem;color:var(--muted);">Source: <code>{vp}</code></p>'
            "</section>"
        )
    else:
        visual_section = ""

    excerpts = gate_data.get("excerpts") or []
    if excerpts:
        blocks = []
        for ex in excerpts:
            src = html.escape(str(ex.get("source", "log")))
            snip = html.escape(str(ex.get("snippet", "")))
            blocks.append(f'<div style="display:flex;flex-direction:column;gap:6px;"><span class="eyebrow">{src}</span><pre>{snip}</pre></div>')
        excerpts_section = (
            '<section style="display:flex;flex-direction:column;gap:12px;">'
            '<span class="eyebrow">Raw Trajectory Sample</span>'
            "<h2>Verbatim Log Excerpts</h2>"
            + "".join(blocks)
            + "</section>"
        )
    else:
        excerpts_section = ""

    rec = str(gate_data.get("recommendation", ""))
    crux_cards = []
    for opt in gate_data.get("crux_options") or []:
        oid = html.escape(str(opt.get("id", "")))
        label = html.escape(str(opt.get("label", "")))
        tradeoff = html.escape(str(opt.get("tradeoff", "")))
        is_rec = bool(opt.get("recommended")) or (oid and oid.lower() in rec.lower())
        cls = "card recommended" if is_rec else "card"
        badge = ' <span class="pill pass">Recommended</span>' if is_rec else ""
        crux_cards.append(
            f'<div class="{cls}"><h3>{oid}: {label}{badge}</h3><p>{tradeoff}</p></div>'
        )

    replacements = {
        "{{Project}}": html.escape(str(gate_data.get("project", "Research Project"))),
        "{{Stage}}": html.escape(str(gate_data.get("stage", "Stage 2 → Stage 3"))),
        "{{Date}}": html.escape(str(gate_data.get("date", date.today().isoformat()))),
        "{{GateTitle}}": html.escape(str(gate_data.get("gate", "Gate 3: Pilot Sign-Off"))),
        "{{StatusClass}}": status_class,
        "{{StatusLabel}}": status_label,
        "{{CostEstimate}}": html.escape(cost_str),
        "{{RuntimeEstimate}}": html.escape(runtime_str),
        "{{LeakCount}}": str(leak_count),
        "{{Bluf}}": html.escape(str(gate_data.get("bluf", ""))),
        "{{Recommendation}}": html.escape(rec),
        "{{AnomalySection}}": anomaly_section,
        "{{ChecksRows}}": "\n".join(checks_rows),
        "{{VisualSection}}": visual_section,
        "{{ExcerptsSection}}": excerpts_section,
        "{{CruxCards}}": "\n".join(crux_cards),
    }
    for k, v in replacements.items():
        tpl = tpl.replace(k, v)
    return tpl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan pilot raw logs and render Gate Decision Cards.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Scan raw logs and compute prompt SHA-256 pins.")
    p_scan.add_argument("--logs", nargs="+", required=True, help="Log files or globs (.jsonl, .json, .log).")
    p_scan.add_argument("--prompts", nargs="*", default=[], help="Prompt/config files to SHA-256 pin.")
    p_scan.add_argument("--max-excerpts", type=int, default=3, help="Number of verbatim raw excerpts to include.")
    p_scan.add_argument("--out", type=Path, default=None, help="Optional JSON output path.")

    p_card = sub.add_parser("render-card", help="Render an HTML Gate Decision Card from JSON.")
    p_card.add_argument("--gate-json", type=Path, required=True, help="Path to gate JSON payload.")
    p_card.add_argument("--out", type=Path, required=True, help="Output HTML file path.")
    p_card.add_argument("--template", type=Path, default=TEMPLATE_PATH, help="HTML template path.")

    args = parser.parse_args(argv)

    if args.cmd == "scan":
        log_paths = expand_globs(args.logs)
        prompt_paths = expand_globs(args.prompts)
        if not log_paths:
            print("Error: no log files matched --logs", file=sys.stderr)
            return 2
        result = scan_pilot(log_paths, prompt_paths, max_excerpts=args.max_excerpts)
        payload = json.dumps(result, indent=2)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload + "\n", encoding="utf-8")
        print(payload)
        return 0 if result["clean"] else 1

    if args.cmd == "render-card":
        data = json.loads(args.gate_json.read_text(encoding="utf-8"))
        rendered = render_gate_card(data, template_path=args.template)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
        print(f"Wrote gate card: {args.out}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
