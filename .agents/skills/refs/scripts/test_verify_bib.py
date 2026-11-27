#!/usr/bin/env python3
"""Unit tests for /refs verify_bib.py (offline, deterministic)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import verify_bib


SAMPLE_BIB = r"""
@inproceedings{vaswani2017attention,
  title={Attention Is All You Need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki},
  booktitle={Advances in Neural Information Processing Systems},
  year={2017}
}

@article{geiping2025huginn,
  title={Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach},
  author={Geiping, Jonas and McLeish, Sean},
  journal={arXiv preprint arXiv:2502.05171},
  eprint={2502.05171},
  year={2025}
}
"""


class TestVerifyBib(unittest.TestCase):
    def test_parse_bib_and_arxiv_extraction(self) -> None:
        entries = verify_bib.parse_bib(SAMPLE_BIB)
        self.assertEqual([e.key for e in entries], ["vaswani2017attention", "geiping2025huginn"])
        self.assertEqual(verify_bib.extract_arxiv_id(entries[1]), "2502.05171")
        self.assertIsNone(verify_bib.extract_arxiv_id(entries[0]))

    def test_local_hygiene_catches_case_and_tex_coverage(self) -> None:
        entries = verify_bib.parse_bib(SAMPLE_BIB)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sec.tex").write_text(r"We cite \citep{vaswani2017attention,missing2026}.", encoding="utf-8")
            (root / "main.tex").write_text(r"\input{sec}", encoding="utf-8")
            cited, _ = verify_bib.extract_tex_citations_and_urls([root / "main.tex"])

        issues = verify_bib.check_local_hygiene(entries, cited)
        rules = {(i.key, i.rule) for i in issues}
        self.assertIn(("geiping2025huginn", "title-case-brace"), rules)
        self.assertIn(("missing2026", "missing-bib-entry"), rules)
        self.assertIn(("geiping2025huginn", "uncited-bib-entry"), rules)

    def test_compare_entry_catches_author_title_and_venue_drift(self) -> None:
        entry = verify_bib.parse_bib(SAMPLE_BIB)[1]
        primary = {
            "source": "arxiv",
            "title": "Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach",
            "authors": ["Jonas Geiping", "Sean McLeish", "Neel Jain"],
            "year": "2025",
            "journal_ref": "NeurIPS 2025",
        }
        issues = verify_bib.compare_entry_with_record(entry, primary)
        rules = {i.rule for i in issues}
        self.assertIn("missing-authors", rules)
        self.assertIn("published-venue-available", rules)

        bad_entry = verify_bib.BibEntry(
            key="fake2025",
            entry_type="article",
            line=1,
            fields={
                "title": "Ouro: Scaling Latent Loops",
                "author": "Doe, Jane and Fake, Person",
                "year": "2024",
            },
        )
        issues2 = verify_bib.compare_entry_with_record(bad_entry, primary)
        rules2 = {i.rule for i in issues2}
        self.assertIn("title-mismatch", rules2)
        self.assertIn("first-author-mismatch", rules2)
        self.assertIn("extra-or-wrong-author", rules2)
        self.assertIn("year-mismatch", rules2)


if __name__ == "__main__":
    unittest.main()
