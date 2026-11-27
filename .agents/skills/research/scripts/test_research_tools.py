#!/usr/bin/env python3
"""Unit tests for the /research skill scripts (lint_manuscript, pilot_scan, pilot_workflow, checkpoint).

Run with:
    python3 -m unittest discover -s . -p "test_*.py" -v
"""

from __future__ import annotations

import ast
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import checkpoint
import lint_manuscript
import pilot_scan


class TestLintManuscript(unittest.TestCase):
    def test_clean_manuscript_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ms = root / "paper.md"
            res = root / "results.json"
            bib = root / "refs.bib"

            res.write_text(json.dumps({"accuracy": 0.842, "n_teams": 120, "delta": 14.5}), encoding="utf-8")
            bib.write_text("@article{smith2024,\n  title={Coordination},\n  author={Smith}\n}\n", encoding="utf-8")
            ms.write_text(
                "---\ntitle: Sample\n---\n\n"
                "# Main Text\n\n"
                "Agent teams reached 84.2% accuracy across 120 teams [@smith2024].\n"
                "The treatment raised scores by 14.5 points (Figure 1, 2024).\n\n"
                "```python\n# em dash — in code block should be ignored\n```\n\n"
                "| Col A | Col B |\n|---|---|\n| 99999 | ignored |\n\n"
                "## References\n\n"
                "1. Smith (2024) — em dash in references ignored.\n",
                encoding="utf-8",
            )

            report = lint_manuscript.lint_manuscript(
                ms, max_words=100, bib_path=bib, result_paths=[res], strict=True
            )
            self.assertTrue(report["passed"], msg=json.dumps(report, indent=2))
            self.assertEqual(report["errors"], 0)
            self.assertEqual(report["warnings"], 0)
            self.assertEqual(report["numbers_checked"], 3)
            self.assertEqual(report["numbers_matched"], 3)

    def test_catches_style_citations_wordcap_and_unverified_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ms = root / "paper.md"
            res = root / "results.json"
            bib = root / "refs.bib"
            cfg = root / "lint.json"

            res.write_text(json.dumps({"accuracy": 0.75}), encoding="utf-8")
            bib.write_text("@article{cited2024,\n  title={A}\n}\n@article{unused2023,\n  title={B}\n}\n", encoding="utf-8")
            cfg.write_text(json.dumps({"max_words": 20, "banned_terms": ["magicbox"]}), encoding="utf-8")

            ms.write_text(
                "This finding shows that teams leverage magicbox — and this proves it works [@cited2024; @missing2025].\n\n"
                "Scaling agents improves accuracy: teams reach 91.3% on the benchmark.\n"
                "The effect grew significantly across cohorts.\n"
                "During testing, the model splits inputs.\n",
                encoding="utf-8",
            )

            report = lint_manuscript.lint_manuscript(
                ms, config_path=cfg, bib_path=bib, result_paths=[res], strict_numbers=True
            )
            rules = {f["rule"] for f in report["findings"]}
            self.assertFalse(report["passed"])
            self.assertIn("word-count", rules)
            self.assertIn("em-dash", rules)
            self.assertIn("banned-phrase", rules)
            self.assertIn("backward-opener", rules)
            self.assertIn("bare-this", rules)
            self.assertIn("gerund-opener", rules)
            self.assertIn("explanatory-colon", rules)
            self.assertIn("ambiguous-verb", rules)
            self.assertIn("unanchored-significant", rules)
            self.assertIn("missing-citation", rules)
            self.assertIn("uncited-bib-entry", rules)
            self.assertIn("unverified-number", rules)
            # Ensure "During testing" was NOT flagged as a gerund opener
            gerund_msgs = [f["message"] for f in report["findings"] if f["rule"] == "gerund-opener"]
            self.assertTrue(all("During" not in m for m in gerund_msgs))

    def test_numbered_markdown_references(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ms = Path(td) / "paper.md"
            ms.write_text(
                "Teams coordinate faster [1, 3] and align early (4–5) in 2024.\n\n"
                "## References\n\n"
                "1. Ref One.\n"
                "2. Ref Two.\n"
                "4. Ref Four.\n"
                "5. Ref Five.\n",
                encoding="utf-8",
            )
            report = lint_manuscript.lint_manuscript(ms, check_md_refs=True)
            missing = [f["message"] for f in report["findings"] if f["rule"] == "missing-ref-number"]
            uncited = [f["message"] for f in report["findings"] if f["rule"] == "uncited-reference"]
            self.assertEqual(len(missing), 1)
            self.assertIn("[3]", missing[0])
            self.assertEqual(len(uncited), 1)
            self.assertIn("[2]", uncited[0])

    def test_author_year_markdown_references(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ms = Path(td) / "paper.md"
            ms.write_text(
                "Prior studies examine coordination (Simon, 1962; March, Schulz, & Zhou, 2000).\n\n"
                "## References\n\n"
                "1. Simon, H. A. (1962). The architecture of complexity.\n"
                "2. March, J. G., Schulz, M., & Zhou, X. (2000). The dynamics of rules.\n"
                "3. Unused, A. (2021). Never mentioned.\n",
                encoding="utf-8",
            )
            report = lint_manuscript.lint_manuscript(ms, check_md_refs=True)
            uncited = [f["message"] for f in report["findings"] if f["rule"] == "uncited-reference"]
            self.assertEqual(len(uncited), 1)
            self.assertIn("Unused", uncited[0])

    def test_inline_comments_and_missing_figures(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fig_ok = root / "fig1.svg"
            fig_ok.write_text("<svg></svg>", encoding="utf-8")
            ms = root / "paper.md"
            ms.write_text(
                "Teams measure <!-- @comment -->overhead<!-- /@comment: tighten --> cleanly.\n\n"
                "![Good](fig1.svg)\n"
                "![Missing](fig_missing.svg)\n"
                "![Remote](https://example.com/plot.png)\n",
                encoding="utf-8",
            )
            rep_warn = lint_manuscript.lint_manuscript(ms)
            self.assertEqual(rep_warn["unresolved_comments"], 1)
            rules_sev = {(f["rule"], f["severity"]) for f in rep_warn["findings"]}
            self.assertIn(("unresolved-comment", "warn"), rules_sev)
            self.assertIn(("missing-figure", "error"), rules_sev)
            # Existing fig1.svg and external URL must not trigger missing-figure
            missing_msgs = [f["message"] for f in rep_warn["findings"] if f["rule"] == "missing-figure"]
            self.assertEqual(len(missing_msgs), 1)
            self.assertIn("fig_missing.svg", missing_msgs[0])

            rep_forbid = lint_manuscript.lint_manuscript(ms, forbid_comments=True)
            rules_sev_strict = {(f["rule"], f["severity"]) for f in rep_forbid["findings"]}
            self.assertIn(("unresolved-comment", "error"), rules_sev_strict)


class TestPilotScanAndWorkflow(unittest.TestCase):
    def test_scan_clean_and_leaky_logs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompt = root / "sys.txt"
            prompt.write_text("You are a test agent.\n", encoding="utf-8")

            clean_log = root / "clean.jsonl"
            clean_log.write_text(
                json.dumps({"seed": 1, "finish_reason": "stop", "content": "OK", "accuracy": 0.62}) + "\n",
                encoding="utf-8",
            )
            clean_res = pilot_scan.scan_pilot([clean_log], [prompt])
            self.assertTrue(clean_res["clean"])
            self.assertEqual(clean_res["leak_count"], 0)
            self.assertEqual(len(clean_res["prompt_pins"]), 1)
            self.assertEqual(clean_res["ceiling_floor_flags"], [])

            leaky_log = root / "leaky.jsonl"
            leaky_log.write_text(
                "{not valid json}\n"
                + json.dumps({"finish_reason": "length", "content": "", "accuracy": 0.99})
                + "\n"
                + json.dumps({"content": "Traceback (most recent call last): Boom"})
                + "\n",
                encoding="utf-8",
            )
            leaky_res = pilot_scan.scan_pilot([leaky_log], [prompt])
            self.assertFalse(leaky_res["clean"])
            self.assertEqual(len(leaky_res["leaks"]["json_parse"]), 1)
            self.assertEqual(len(leaky_res["leaks"]["truncation"]), 1)
            self.assertEqual(len(leaky_res["leaks"]["empty_output"]), 1)
            self.assertEqual(len(leaky_res["leaks"]["errors"]), 1)
            self.assertEqual(len(leaky_res["ceiling_floor_flags"]), 1)

    def test_render_gate_card_replaces_placeholders_and_escapes_html(self) -> None:
        gate_data = {
            "project": "Test <Proj>",
            "stage": "Stage 2 → Stage 3",
            "gate": "Gate 3: Pilot Sign-Off",
            "date": "2026-11-21",
            "bluf": "Pilot passed cleanly with <0> leaks.",
            "recommendation": "Option A",
            "cost_usd_est": 12.5,
            "runtime_min_est": 8.0,
            "leak_count": 0,
            "checks": [{"name": "Log Scan", "status": "pass", "detail": "0 leaks"}],
            "anomalies": ["Ceiling check: <none>"],
            "excerpts": [{"source": "seed1.jsonl:L1", "snippet": "{\"ok\": true}"}],
            "crux_options": [
                {"id": "Option A", "label": "Approve sweep", "tradeoff": "Costs $12.50", "recommended": True}
            ],
        }
        rendered = pilot_scan.render_gate_card(gate_data)
        self.assertNotIn("{{", rendered)
        self.assertIn("Test &lt;Proj&gt;", rendered)
        self.assertIn("$12.50", rendered)
        self.assertIn("8.0 min", rendered)
        self.assertIn("Anomaly Circuit-Breaker", rendered)

    def test_pilot_workflow_valid_top_level_await_syntax(self) -> None:
        for fname in ("pilot_workflow.py", "stage4_review_workflow.py"):
            wf_path = SCRIPTS_DIR / fname
            src = wf_path.read_text(encoding="utf-8")
            compile(src, str(wf_path), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)


class TestCheckpoint(unittest.TestCase):
    def test_append_only_log_and_context_updates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            t1 = datetime(2026, 11, 21, 14, 30)
            log1 = checkpoint.append_log_entry(root, "Gate 1 Charter", "Initial charter locked.", now=t1)
            self.assertTrue(log1.exists())
            self.assertIn("# 2026-11-21 14:30 — Gate 1 Charter", log1.read_text(encoding="utf-8"))

            # Continuing the same log file must append, never overwrite
            t2 = datetime(2026, 11, 21, 15, 0)
            checkpoint.append_log_entry(root, "Gate 1 Charter", "Added nearest neighbor.", now=t2, log_file=log1)
            log_text = log1.read_text(encoding="utf-8")
            self.assertIn("Initial charter locked.", log_text)
            self.assertIn("## Update (2026-11-21 15:00)", log_text)
            self.assertIn("Added nearest neighbor.", log_text)

            ctx = checkpoint.resolve_context_path(root)
            rel = log1.relative_to(root).as_posix()
            checkpoint.update_context(
                ctx,
                rel,
                stage="Stage 1 (Theory & Toy Proof)",
                dead_ends=["Naive baseline fails on empty graph"],
                today="2026-11-21",
            )
            ctx_text = ctx.read_text(encoding="utf-8")
            self.assertIn("**Stage:** Stage 1 (Theory & Toy Proof)", ctx_text)
            self.assertIn("- Naive baseline fails on empty graph", ctx_text)
            self.assertNotIn("- None yet.", ctx_text)
            self.assertIn(f"- `{rel}`", ctx_text)

            # Second update preserves existing dead end and avoids duplicate log link
            checkpoint.update_context(
                ctx,
                rel,
                stage="Stage 2 (Pilot-First Engine)",
                dead_ends=["Naive baseline fails on empty graph", "Prompt v1 leaks JSON"],
                today="2026-11-21",
            )
            ctx_text2 = ctx.read_text(encoding="utf-8")
            self.assertIn("**Stage:** Stage 2 (Pilot-First Engine)", ctx_text2)
            self.assertEqual(ctx_text2.count(rel), 1)
            self.assertIn("- Prompt v1 leaks JSON", ctx_text2)


class TestLatexLinting(unittest.TestCase):
    def test_modular_latex_clean_and_catches_errors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sections").mkdir()
            (root / "figs").mkdir()
            (root / "figs" / "fig1.pdf").write_bytes(b"%PDF-1.4\n")
            res = root / "results.json"
            res.write_text(json.dumps({"acc": 0.842, "delta": 14.5}), encoding="utf-8")
            bib = root / "ref.bib"
            bib.write_text("@article{smith2024,\n  title={Test},\n  author={Smith}\n}\n", encoding="utf-8")

            (root / "sections" / "intro.tex").write_text(
                "\\section{Introduction}\n"
                "Models reach 84.2\\% accuracy across 8B--675B scales \\citep{smith2024}.\n"
                "\\begin{figure}[t]\n"
                "\\includegraphics{fig1}\n"
                "\\end{figure}\n"
                "\\begin{table}[t]\n"
                "\\begin{tabular}{cc} 99999 & ignored \\\\ \\end{tabular}\n"
                "\\end{table}\n",
                encoding="utf-8",
            )
            main_tex = root / "main.tex"
            main_tex.write_text(
                "\\documentclass{article}\n"
                "\\graphicspath{{figs/}}\n"
                "\\begin{document}\n"
                "\\input{sections/intro}\n"
                "\\bibliography{ref}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            clean = lint_manuscript.lint_manuscript(
                main_tex, bib_path=bib, result_paths=[res], strict=True, forbid_comments=True
            )
            self.assertTrue(clean["passed"], msg=json.dumps(clean, indent=2))
            self.assertEqual(clean["unresolved_comments"], 0)
            self.assertEqual(clean["numbers_matched"], 1)

            # Inject LaTeX em-dash, % @comment, and missing figure
            (root / "sections" / "intro.tex").write_text(
                "\\section{Introduction}\n"
                "Models fail---badly---here \\citep{smith2024}. % @comment (fix em dash)\n"
                "\\includegraphics{missing_fig}\n",
                encoding="utf-8",
            )
            dirty = lint_manuscript.lint_manuscript(
                main_tex, bib_path=bib, forbid_comments=True
            )
            rules = {f["rule"] for f in dirty["findings"]}
            self.assertFalse(dirty["passed"])
            self.assertIn("em-dash", rules)
            self.assertIn("unresolved-comment", rules)
            self.assertIn("missing-figure", rules)
            self.assertEqual(dirty["unresolved_comments"], 1)


if __name__ == "__main__":
    unittest.main()
