"""Antigravity `run_workflow` script: 1-Seed Pilot Inspector & Gate 3 Card Generator.

Runs a 1-seed pilot (or inspects existing pilot outputs), hashes prompt/config
pins, scans raw `.jsonl` logs deterministically via `pilot_scan.py`, spawns
fresh Trajectory Inspector and Anomaly Auditor agents with strict JSON schemas,
and renders a Gate 3 HTML decision card.

Invoke via `run_workflow(ScriptPath=".../pilot_workflow.py", Args={...})`:
    Args:
      project          (str)        Project display name
      hypothesis       (str)        Working hypothesis being tested
      pilot_cmd        (str, opt)   Shell command to run 1-seed pilot (omit if skip_run=True)
      skip_run         (bool, opt)  Skip running pilot_cmd and inspect existing logs (default: False)
      log_globs        (list[str])  Glob(s) for raw pilot logs (e.g. ["results/pilot/*.jsonl"])
      prompt_globs     (list[str])  Glob(s) for prompt/config files to SHA-256 pin
      sweep_multiplier (float)      Full sweep size / pilot size (e.g. 20 for 20 seeds)
      pilot_cost_usd   (float, opt) Measured pilot API/compute cost in USD
      gate_card_out    (str, opt)   Output HTML path (default: "results/gate3-pilot.html")
      skill_dir        (str, opt)   Path to the research skill directory (auto-resolved if omitted)
"""

import json
import subprocess
import time
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
        if (candidate / "scripts/pilot_scan.py").exists():
            return candidate.resolve()
    raise FileNotFoundError("Could not locate research skill directory; pass Args={'skill_dir': '...'}.")


skill_dir = resolve_skill_dir()
pilot_scan = skill_dir / "scripts" / "pilot_scan.py"
agent_model = args.get("model") or "inherit"

project = args.get("project", workspace.name)
hypothesis = args.get("hypothesis", "No hypothesis specified.")
pilot_cmd = args.get("pilot_cmd")
skip_run = bool(args.get("skip_run", False))
log_globs = args.get("log_globs") or ["results/pilot/*.jsonl"]
prompt_globs = args.get("prompt_globs") or []
sweep_multiplier = float(args.get("sweep_multiplier", 10.0))
pilot_cost_usd = args.get("pilot_cost_usd")
gate_card_out = workspace / (args.get("gate_card_out") or "results/gate3-pilot.html")

# ── Phase 1: Run 1-seed pilot & deterministic log scan ──────────────────────
phase("1. Run 1-seed pilot & scan raw logs")

pilot_runtime_sec = 0.0
pilot_exit_code = 0
if pilot_cmd and not skip_run:
    t0 = time.monotonic()
    proc = subprocess.run(pilot_cmd, shell=True, cwd=workspace, capture_output=True, text=True)
    pilot_runtime_sec = round(time.monotonic() - t0, 2)
    pilot_exit_code = proc.returncode
    log(f"Pilot command exited with {pilot_exit_code} in {pilot_runtime_sec}s")
    if pilot_exit_code != 0:
        log("Pilot stderr (tail):", proc.stderr[-1000:])
else:
    log("Skipping pilot execution; scanning existing logs.")

scan_cmd = ["python3", str(pilot_scan), "scan", "--logs", *log_globs]
if prompt_globs:
    scan_cmd.extend(["--prompts", *prompt_globs])

scan_proc = subprocess.run(scan_cmd, cwd=workspace, capture_output=True, text=True)
if scan_proc.returncode == 2:
    raise RuntimeError(f"pilot_scan.py failed: {scan_proc.stderr}")

scan_report = json.loads(scan_proc.stdout)
log(
    f"Scanned {len(scan_report['files_scanned'])} file(s), "
    f"{scan_report['total_records']} record(s), "
    f"{scan_report['leak_count']} deterministic leak(s)."
)

# ── Phase 2: Fresh Trajectory Inspector & Anomaly Auditor in parallel ───────
phase("2. Raw trajectory audit & anomaly check")

inspector_schema = {
    "type": "object",
    "required": ["engineering_leaks_found", "leaks", "behavior_summary", "trajectory_quality"],
    "properties": {
        "engineering_leaks_found": {"type": "integer"},
        "leaks": {"type": "array", "items": {"type": "string"}},
        "behavior_summary": {"type": "string", "description": "At most 2 short plain sentences."},
        "trajectory_quality": {"type": "string", "enum": ["clean", "minor_issues", "broken"]},
    },
}

auditor_schema = {
    "type": "object",
    "required": ["circuit_breaker_triggered", "anomalies", "competing_explanations", "signal_verdict"],
    "properties": {
        "circuit_breaker_triggered": {"type": "boolean"},
        "anomalies": {"type": "array", "items": {"type": "string"}},
        "competing_explanations": {"type": "array", "items": {"type": "string"}},
        "signal_verdict": {"type": "string", "enum": ["supports", "ambiguous", "contradicts", "invalid"]},
    },
}

abs_scanned_files = [str((workspace / f).resolve()) for f in scan_report["files_scanned"]]

inspector_prompt = f"""You are a Trajectory Inspector auditing a 1-seed pilot for project '{project}'.
Read the actual raw pilot files listed below—never rely on summaries alone.
Files: {abs_scanned_files}
Deterministic scan summary: {json.dumps({k: scan_report[k] for k in ['leak_count', 'leaks', 'total_records']}, indent=2)}

Inspect raw transcripts/records directly for:
1. Truncated generations, JSON/schema parse errors, empty outputs, or retries masking bugs.
2. Prompt leakage, instruction misunderstanding, or unintended tool loops.
3. Metric calculation bugs or silent fallbacks.

Return a strict JSON verdict via `finish`."""

auditor_prompt = f"""You are an Anomaly Auditor evaluating a 1-seed pilot for project '{project}'.
Working hypothesis: {hypothesis}
Deterministic metric summary: {json.dumps(scan_report['metric_summary'], indent=2)}
Ceiling/floor flags: {json.dumps(scan_report['ceiling_floor_flags'], indent=2)}
Files to spot-check: {abs_scanned_files}

Check whether the pilot signal is valid or whether an Anomaly Circuit-Breaker should fire.
Fire `circuit_breaker_triggered: true` if:
- pilot metrics hit a ceiling (>=95%) or floor (<=5%) that masks differences,
- pilot results contradict the working hypothesis, or
- instrumentation noise prevents interpreting the signal.

Always include at least three competing explanations when an anomaly exists:
(a) engineering/measurement artifact, (b) testbed difficulty/regime mismatch, (c) hypothesis is wrong or scoped differently.
Never suggest silently tweaking prompts to rescue an effect. Return strict JSON via `finish`."""

insp_result, audit_result = await parallel(
    [
        ("Trajectory Inspector", inspector_prompt, inspector_schema),
        ("Anomaly Auditor", auditor_prompt, auditor_schema),
    ],
    lambda item: agent(item[1], schema=item[2], role=item[0], type_name="self", model=agent_model),
)

# ── Phase 3: Assemble Gate 3 payload & render HTML card ─────────────────────
phase("3. Emit Gate 3 Decision Card")

total_leaks = scan_report["leak_count"] + int(insp_result["engineering_leaks_found"])
all_anomalies = list(scan_report["ceiling_floor_flags"]) + list(audit_result["anomalies"])
if pilot_exit_code != 0:
    all_anomalies.insert(0, f"Pilot command exited with non-zero code {pilot_exit_code}.")

cost_est = round(float(pilot_cost_usd) * sweep_multiplier, 2) if pilot_cost_usd is not None else None
runtime_min_est = round((pilot_runtime_sec * sweep_multiplier) / 60.0, 1) if pilot_runtime_sec else None

checks = [
    {
        "name": "1-Seed Pilot Execution",
        "status": "pass" if pilot_exit_code == 0 else "fail",
        "detail": f"Exit {pilot_exit_code}; {scan_report['total_records']} records across {len(scan_report['files_scanned'])} file(s).",
    },
    {
        "name": "Prompt SHA-256 Pins",
        "status": "pass" if scan_report["prompt_pins"] else "warn",
        "detail": f"{len(scan_report['prompt_pins'])} file(s) pinned." if scan_report["prompt_pins"] else "No prompt files passed for pinning.",
    },
    {
        "name": "Deterministic Log Scan",
        "status": "pass" if scan_report["leak_count"] == 0 else "fail",
        "detail": f"{scan_report['leak_count']} deterministic leak(s) detected.",
    },
    {
        "name": "Trajectory Inspector",
        "status": "pass" if insp_result["trajectory_quality"] == "clean" and insp_result["engineering_leaks_found"] == 0 else "fail",
        "detail": insp_result["behavior_summary"],
    },
    {
        "name": "Hypothesis & Anomaly Check",
        "status": "warn" if audit_result["circuit_breaker_triggered"] else "pass",
        "detail": f"Verdict: {audit_result['signal_verdict']}.",
    },
]

if total_leaks > 0:
    recommendation = "Option B (Fix leaks and re-run 1-seed pilot before scaling)."
    bluf = (
        f"1-seed pilot uncovered {total_leaks} engineering leak(s) across {scan_report['total_records']} records. "
        f"Full sweep is blocked until leaks reach zero. {insp_result['behavior_summary']}"
    )
elif audit_result["circuit_breaker_triggered"]:
    recommendation = "Option C (Halt and diagnose anomaly with PI before spending sweep budget)."
    bluf = (
        f"1-seed pilot ran with zero engineering leaks, but the Anomaly Circuit-Breaker fired "
        f"(signal: {audit_result['signal_verdict']}). Review competing explanations before scaling."
    )
else:
    recommendation = "Option A (Approve full sweep)."
    bluf = (
        f"1-seed pilot passed with 0 engineering leaks across {scan_report['total_records']} records "
        f"and signal verdict '{audit_result['signal_verdict']}'. {insp_result['behavior_summary']}"
    )

gate_payload = {
    "project": project,
    "stage": "Stage 2 → Stage 3",
    "gate": "Gate 3: Pilot → Sweep Sign-Off",
    "bluf": bluf,
    "recommendation": recommendation,
    "cost_usd_est": cost_est,
    "runtime_min_est": runtime_min_est,
    "leak_count": total_leaks,
    "prompt_pins": scan_report["prompt_pins"],
    "checks": checks,
    "anomalies": all_anomalies,
    "competing_explanations": audit_result["competing_explanations"],
    "excerpts": scan_report["excerpts"],
    "crux_options": [
        {
            "id": "Option A",
            "label": "Approve full sweep",
            "tradeoff": f"Proceeds to Stage 3 (est. cost: {f'${cost_est:.2f}' if cost_est is not None else 'N/A'}, est. runtime: {f'{runtime_min_est} min' if runtime_min_est is not None else 'N/A'}).",
            "recommended": total_leaks == 0 and not audit_result["circuit_breaker_triggered"],
        },
        {
            "id": "Option B",
            "label": "Fix leaks & re-pilot",
            "tradeoff": "Patches instrumentation/parse issues and reruns 1 clean seed before spending sweep budget.",
            "recommended": total_leaks > 0,
        },
        {
            "id": "Option C",
            "label": "Diagnose anomaly / adjust testbed",
            "tradeoff": "Runs a targeted 1-seed diagnostic to separate measurement error, task difficulty, and hypothesis failure.",
            "recommended": total_leaks == 0 and audit_result["circuit_breaker_triggered"],
        },
    ],
}

gate_json_path = gate_card_out.with_suffix(".json")
gate_json_path.parent.mkdir(parents=True, exist_ok=True)
gate_json_path.write_text(json.dumps(gate_payload, indent=2) + "\n", encoding="utf-8")

subprocess.run(
    ["python3", str(pilot_scan), "render-card", "--gate-json", str(gate_json_path), "--out", str(gate_card_out)],
    check=True,
    cwd=workspace,
)

log(f"Gate 3 JSON: {gate_json_path}")
log(f"Gate 3 HTML: {gate_card_out}")
print(json.dumps({"gate_json": str(gate_json_path), "gate_html": str(gate_card_out), "bluf": bluf, "recommendation": recommendation}, indent=2))
