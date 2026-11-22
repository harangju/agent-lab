"""Antigravity `run_workflow` script: Stage 4 Manuscript Lint, Code-Verified /lab Panel & Gate 4 Card.

Enforces fresh phase-scoped execution for Stage 4:
  1. Runs `lint_manuscript.py` (style, word cap, citations, number provenance,
     unresolved @comments, missing figures) and optional `pytest` suite.
  2. Fans out all five /lab personas in parallel with strict JSON schemas,
     requiring Methodologist and Skeptic to spot-check code and locked results.
  3. Synthesizes confirmed bugs vs. unresolved PI cruxes via a fresh Lead agent.
  4. Emits `gate4-review.json` and renders a Gate 4 HTML decision card.

Invoke via `run_workflow(ScriptPath=".../stage4_review_workflow.py", Args={...})`:
    Args:
      project          (str)        Project display name
      manuscript       (str)        Path to main manuscript (e.g. "notes/paper.md")
      max_words        (int, opt)   Venue word-count cap
      results_globs    (list[str])  Glob(s) for locked results/*.json
      code_paths       (list[str])  Key analysis/simulation scripts for code verification
      bib              (str, opt)   Path to .bib file
      check_md_refs    (bool, opt)  Check markdown ## References (default: True if no bib)
      lint_config      (str, opt)   Optional JSON config for lint_manuscript.py
      test_cmd         (str, opt)   Optional test command (e.g. "pytest -q")
      gate_card_out    (str, opt)   Output HTML path (default: "results/gate4-review.html")
      skill_dir        (str, opt)   Path to the research skill directory (auto-resolved if omitted)
"""

import json
import subprocess
from pathlib import Path

workspace = Path.cwd()


def resolve_skill_dir() -> Path:
    if args.get("skill_dir"):
        return Path(args["skill_dir"]).expanduser().resolve()
    if "__file__" in globals():
        return Path(globals()["__file__"]).resolve().parent.parent
    for candidate in (
        workspace / ".agents/skills/research",
        Path.home() / ".gemini/config/skills/research",
        Path.home() / ".agents/skills/research",
        Path.home() / ".claude/skills/research",
    ):
        if (candidate / "scripts/lint_manuscript.py").exists():
            return candidate.resolve()
    raise FileNotFoundError("Could not locate research skill directory; pass Args={'skill_dir': '...'}.")


skill_dir = resolve_skill_dir()
lint_script = skill_dir / "scripts" / "lint_manuscript.py"
pilot_scan = skill_dir / "scripts" / "pilot_scan.py"
agent_model = args.get("model") or "inherit"

project = args.get("project", workspace.name)
manuscript = args.get("manuscript", "notes/paper.md")
max_words = args.get("max_words")
results_globs = args.get("results_globs") or ["results/**/*.json"]
code_paths = args.get("code_paths") or ["scripts/"]
bib = args.get("bib")
check_md_refs = bool(args.get("check_md_refs", not bool(bib)))
lint_config = args.get("lint_config")
test_cmd = args.get("test_cmd")
gate_card_out = workspace / (args.get("gate_card_out") or "results/gate4-review.html")

# ── Phase 1: Deterministic lint & optional test suite ───────────────────────
phase("1. Manuscript lint, provenance & test suite")

lint_cmd = ["python3", str(lint_script), manuscript, "--format", "json"]
if max_words is not None:
    lint_cmd.extend(["--max-words", str(max_words)])
if lint_config:
    lint_cmd.extend(["--config", lint_config])
if bib:
    lint_cmd.extend(["--bib", bib])
if check_md_refs:
    lint_cmd.append("--check-md-refs")
if results_globs:
    lint_cmd.extend(["--results", *results_globs])

lint_proc = subprocess.run(lint_cmd, cwd=workspace, capture_output=True, text=True)
if lint_proc.returncode == 2:
    raise RuntimeError(f"lint_manuscript.py failed: {lint_proc.stderr}")
lint_report = json.loads(lint_proc.stdout)
log(
    f"Lint: words={lint_report['word_count']}/{lint_report.get('max_words')}, "
    f"errors={lint_report['errors']}, warnings={lint_report['warnings']}, "
    f"provenance={lint_report['numbers_matched']}/{lint_report['numbers_checked']}, "
    f"unresolved_comments={lint_report.get('unresolved_comments', 0)}"
)

test_passed = None
test_detail = "Not configured."
if test_cmd:
    tproc = subprocess.run(test_cmd, shell=True, cwd=workspace, capture_output=True, text=True)
    test_passed = tproc.returncode == 0
    tail = (tproc.stdout + "\n" + tproc.stderr).strip().splitlines()[-3:]
    test_detail = f"Exit {tproc.returncode}: " + " | ".join(tail)
    log(f"Tests: {'PASS' if test_passed else 'FAIL'} ({test_detail})")

# ── Phase 2: Code-verified /lab 5-persona review panel in parallel ──────────
phase("2. Code-verified /lab review panel")

persona_schema = {
    "type": "object",
    "required": [
        "persona",
        "readiness",
        "verified_against_code",
        "confirmed_bugs",
        "major_critiques",
        "summary",
    ],
    "properties": {
        "persona": {"type": "string"},
        "readiness": {"type": "string", "enum": ["ready", "minor_revisions", "major_revisions"]},
        "verified_against_code": {"type": "boolean"},
        "confirmed_bugs": {"type": "array", "items": {"type": "string"}},
        "major_critiques": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
}

personas = [
    (
        "Skeptic",
        "Novelty & prior-work overlap. Spot-check claims against actual scripts/results before accepting them, and check whether the core contribution is genuinely new vs. nearest neighbors.",
        True,
    ),
    (
        "Methodologist",
        "Rigor, identification, and code/data accuracy. You MUST open and spot-check the locked results JSONs and analysis scripts before reporting—do not critique from prose alone. Flag verifiable bugs separately from framing debates.",
        True,
    ),
    (
        "Visionary",
        "Impact, venue fit, and non-obvious cargo. Ask whether the hook delivers quantified, falsifiable cargo worthy of the target venue.",
        False,
    ),
    (
        "Newcomer",
        "Clarity, jargon, and structural flow. Flag anywhere a smart outside reader gets lost, encounters unexplained jargon, or hits a weak topic sentence.",
        False,
    ),
    (
        "Connector",
        "Cross-field integration and unifying principles. Identify missed bridges to adjacent literatures that strengthen (not bloat) the argument.",
        False,
    ),
]


abs_manuscript = str((workspace / manuscript).resolve())
abs_context = str((workspace / "CONTEXT.md").resolve())
abs_results_globs = [str(workspace / g) if not Path(g).is_absolute() else g for g in results_globs]
abs_code_paths = [str((workspace / p).resolve()) for p in code_paths]


def make_persona_prompt(name: str, mandate: str, must_check_code: bool) -> str:
    code_req = (
        f"MANDATORY: Spot-check the locked result files ({abs_results_globs}) and scripts ({abs_code_paths}) "
        "to confirm numbers and logic before raising or dismissing a critique. Set verified_against_code=true only if you read code/data directly."
        if must_check_code
        else "Read the manuscript and CONTEXT.md directly; spot-check results/scripts if your critique depends on a number."
    )
    return f"""You are the {name} persona in a Stage 4 /lab manuscript review for '{project}'.
Mandate: {mandate}
{code_req}

Read:
- Manuscript: {abs_manuscript}
- Context: {abs_context} (if present)
- Linter summary: words={lint_report['word_count']}/{lint_report.get('max_words')}, errors={lint_report['errors']}, warnings={lint_report['warnings']}

Do NOT write or edit any files. Return a concise, argued JSON verdict via `finish`."""


panel_results = await parallel(
    personas,
    lambda p: agent(
        make_persona_prompt(p[0], p[1], p[2]),
        schema=persona_schema,
        role=f"/lab {p[0]}",
        type_name="self",
        model=agent_model,
    ),
)

# ── Phase 3: Fresh Lead Synthesizer separates auto-fixes from PI cruxes ─────
phase("3. Synthesize confirmed bugs vs. PI cruxes")

synth_schema = {
    "type": "object",
    "required": ["bluf", "recommendation", "verifiable_fixes", "pi_cruxes", "anomalies"],
    "properties": {
        "bluf": {"type": "string", "description": "At most 3 plain sentences."},
        "recommendation": {"type": "string"},
        "verifiable_fixes": {"type": "array", "items": {"type": "string"}},
        "pi_cruxes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "label", "tradeoff"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "tradeoff": {"type": "string"},
                },
            },
        },
        "anomalies": {"type": "array", "items": {"type": "string"}},
    },
}

synth_prompt = f"""You are the Research Lead synthesizing a Stage 4 Gate 4 review for '{project}'.
Linter JSON summary: {json.dumps({k: lint_report[k] for k in ['word_count', 'max_words', 'errors', 'warnings', 'numbers_checked', 'numbers_matched', 'unresolved_comments']}, indent=2)}
Linter top findings: {json.dumps(lint_report['findings'][:20], indent=2)}
Tests: {test_detail}
/lab Panel Verdicts:
{json.dumps(panel_results, indent=2)}

Produce a crisp synthesis:
1. `bluf`: <= 3 plain sentences giving readiness, headline bug count, and the single biggest crux.
2. `verifiable_fixes`: concrete bugs/lint errors verified against code or data that can be fixed mechanically before the PI craft pass.
3. `pi_cruxes`: 2-3 high-stakes framing, scope, or persona-contradiction calls that require PI judgment (each with id like 'Option A'/'Crux 1', label, tradeoff).
4. `anomalies`: any code/prose mismatch, unverified numbers, or persona contradictions.
5. `recommendation`: one crisp sentence.

Do NOT edit files. Return strict JSON via `finish`."""

synthesis = await agent(synth_prompt, schema=synth_schema, role="Lead Gate 4 Synthesizer", type_name="self", model=agent_model)

# ── Phase 4: Emit Gate 4 Decision Card ──────────────────────────────────────
phase("4. Emit Gate 4 Decision Card")

checks = [
    {
        "name": "Style & Word Budget",
        "status": "pass" if lint_report["errors"] == 0 else "fail",
        "detail": f"{lint_report['word_count']} words (cap: {lint_report.get('max_words') or 'none'}); {lint_report['errors']} errors, {lint_report['warnings']} warnings.",
    },
    {
        "name": "Number Provenance",
        "status": "pass" if lint_report["numbers_checked"] == lint_report["numbers_matched"] else "warn",
        "detail": f"{lint_report['numbers_matched']}/{lint_report['numbers_checked']} empirical numbers matched locked JSONs.",
    },
    {
        "name": "Inline @comments",
        "status": "pass" if lint_report.get("unresolved_comments", 0) == 0 else "warn",
        "detail": f"{lint_report.get('unresolved_comments', 0)} unresolved inline @comment(s).",
    },
    {
        "name": "Test Suite",
        "status": "not_run" if test_passed is None else ("pass" if test_passed else "fail"),
        "detail": test_detail,
    },
]
for p in panel_results:
    st = "pass" if p["readiness"] == "ready" else ("warn" if p["readiness"] == "minor_revisions" else "fail")
    code_tag = " [code-verified]" if p["verified_against_code"] else ""
    checks.append(
        {
            "name": f"/lab {p['persona']}{code_tag}",
            "status": st,
            "detail": f"{p['readiness']}: {p['summary']}",
        }
    )

confirmed_bugs = sum(len(p["confirmed_bugs"]) for p in panel_results)
gate_payload = {
    "project": project,
    "stage": "Stage 4 → Gate 4",
    "gate": "Gate 4: PI Craft Pass",
    "bluf": synthesis["bluf"],
    "recommendation": synthesis["recommendation"],
    "cost_usd_est": None,
    "runtime_min_est": None,
    "leak_count": lint_report["errors"] + confirmed_bugs,
    "checks": checks,
    "anomalies": synthesis["anomalies"],
    "verifiable_fixes": synthesis["verifiable_fixes"],
    "panel_results": panel_results,
    "crux_options": synthesis["pi_cruxes"],
}

gate_json_path = gate_card_out.with_suffix(".json")
gate_json_path.parent.mkdir(parents=True, exist_ok=True)
gate_json_path.write_text(json.dumps(gate_payload, indent=2) + "\n", encoding="utf-8")

subprocess.run(
    ["python3", str(pilot_scan), "render-card", "--gate-json", str(gate_json_path), "--out", str(gate_card_out)],
    check=True,
    cwd=workspace,
)

log(f"Gate 4 JSON: {gate_json_path}")
log(f"Gate 4 HTML: {gate_card_out}")
print(
    json.dumps(
        {
            "gate_json": str(gate_json_path),
            "gate_html": str(gate_card_out),
            "bluf": synthesis["bluf"],
            "verifiable_fixes": len(synthesis["verifiable_fixes"]),
            "recommendation": synthesis["recommendation"],
        },
        indent=2,
    )
)
