"""Resumable stage-2 batch controller.

Modes:
  --plan     show pending steps and runtime estimate without executing Kira
  --status   show checkpoint summary
  --run      execute pending baseline/boundary steps sequentially

The controller stops immediately on a failed command.  If a family's boundary
audit reports that a union reduction is needed, it records that condition and
stops cleanly so the generic union stage can be added/adjusted without losing
previous completed work.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from three_loop.integral_family_classification import ROOT
import three_loop.master_basis_api as master_basis_api
from three_loop.master_basis_batch import (
    AUDIT_DIR,
    BatchStep,
    append_runtime,
    build_queue,
    estimate_queue,
    execution_families,
    family_steps,
    load_checkpoint,
    save_checkpoint,
    update_checkpoint,
)


def _fmt(seconds: float) -> str:
    seconds = max(0, int(seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)
    if days:
        return f"{days}d {hours:02d}h {minutes:02d}m"
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {sec:02d}s"
    return f"{sec}s"


def _cache_registry_once() -> None:
    print("building canonical registry once ...", flush=True)
    cached = master_basis_api._global_registry()
    master_basis_api._global_registry = lambda: cached
    print("canonical registry ready", flush=True)


def _bat() -> Path:
    return ROOT / "run_three_loop_master_basis_seed.bat"


def _run_step(step: BatchStep) -> int:
    cmd = [str(_bat()), step.family, step.seed.tag, step.solver]
    print("\n=== RUN", step.key, "===", flush=True)
    start = time.perf_counter()
    update_checkpoint(step, status="running")
    proc = subprocess.run(cmd, cwd=ROOT, shell=True)
    elapsed = time.perf_counter() - start
    spec = master_basis_api.build_family_spec(step.family)
    append_runtime({
        "family": step.family,
        "phase": step.phase,
        "phase_class": "baseline" if step.phase == "baseline" else "boundary",
        "seed": step.seed.tag,
        "solver": step.solver,
        "elapsed_s": elapsed,
        "topology": spec.topology_family,
        "unique_physical": spec.unique_physical_count,
        "auxiliary_count": spec.auxiliary_count,
        "top_sector": spec.top_sector,
        "exit_code": proc.returncode,
    })
    update_checkpoint(
        step,
        status="pass" if proc.returncode == 0 else "fail",
        elapsed_s=elapsed,
        detail=f"exit_code={proc.returncode}",
    )
    print(f"=== END {step.key}: exit={proc.returncode} elapsed={_fmt(elapsed)} ===", flush=True)
    return int(proc.returncode)


def _boundary_audit_path(family: str, baseline_tag: str) -> Path:
    return AUDIT_DIR / f"three_loop_{family.lower()}_firefly_{baseline_tag}_boundary_aggregate_audit.json"


def _run_boundary_audit(family: str, baseline_tag: str) -> tuple[int, dict]:
    cmd = [
        sys.executable,
        "-m",
        "examples.three_loop_master_basis_boundary_audit",
        "--family", family,
        "--baseline-seed", baseline_tag,
        "--solver", "firefly",
    ]
    proc = subprocess.run(cmd, cwd=ROOT)
    path = _boundary_audit_path(family, baseline_tag)
    payload = {}
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    return int(proc.returncode), payload


def show_plan(start_family: str | None) -> None:
    queue = build_queue(start_family=start_family)
    estimate = estimate_queue(queue)
    print("QEDCalc master-basis batch plan")
    print(f"pending executable seed steps: {estimate['step_count']}")
    for row in estimate["steps"]:
        est = row["estimate"]
        print(
            f"  {row['family']:12s} {row['phase']:10s} {row['seed_tag']:8s} "
            f"{row['solver']:8s}  median~{_fmt(est['median_s'])} "
            f"range~{_fmt(est['low_s'])}..{_fmt(est['high_s'])}"
        )
    print("estimated remaining seed-compute wall time:")
    print(f"  low    {_fmt(estimate['total_low_s'])}")
    print(f"  median {_fmt(estimate['total_median_s'])}")
    print(f"  high   {_fmt(estimate['total_high_s'])}")
    print("note: union/final-boundary rescue time is not included until a family proves unstable")


def show_status() -> None:
    cp = load_checkpoint()
    rows = list(cp.get("steps", {}).values())
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    print("QEDCalc master-basis batch status")
    print("checkpoint:", ROOT / "output" / "three_loop_integral_family_audit" / "three_loop_master_basis_batch_checkpoint.json")
    print("step status counts:", counts)
    failed = [row for row in rows if row.get("status") in {"fail", "needs_union"}]
    for row in failed[-10:]:
        print(f"  {row.get('key')}: {row.get('status')} {row.get('detail','')}")


def run_batch(start_family: str | None) -> int:
    families = execution_families()
    if start_family:
        if start_family not in families:
            raise SystemExit(f"start family is not pending: {start_family}")
        families = families[families.index(start_family):]

    for index, family in enumerate(families, start=1):
        spec = master_basis_api.build_family_spec(family)
        baseline = spec.baseline_seed
        print(f"\n##### FAMILY {index}/{len(families)} {family} baseline={baseline.tag} #####", flush=True)
        steps = family_steps(family)
        queue_keys = {step.key for step in build_queue(start_family=family)}
        for step in steps:
            if step.key not in queue_keys:
                print(f"SKIP existing/pass: {step.key}", flush=True)
                continue
            code = _run_step(step)
            if code:
                print(f"STOP: {step.key} failed; fix API/config and rerun with --run --start-family {family}")
                return code

        code, audit = _run_boundary_audit(family, baseline.tag)
        if code:
            print(f"STOP: boundary audit failed for {family}")
            return code
        if audit.get("union_reduction_needed"):
            synthetic = BatchStep(family, "union-needed", baseline, "firefly")
            update_checkpoint(
                synthetic,
                status="needs_union",
                detail=str(audit.get("union_target_file") or "union reduction required"),
            )
            print(
                f"STOP CLEANLY: {family} requires union reduction. "
                "All previous results are checkpointed; add/fix generic union stage, then resume here."
            )
            return 20
        print(f"FAMILY {family}: one-axis stable; ready for final-basis promotion audit", flush=True)

    print("All scheduled baseline/boundary families completed without a union stop.")
    return 0


def main() -> None:
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--status", action="store_true")
    mode.add_argument("--run", action="store_true")
    p.add_argument("--start-family")
    args = p.parse_args()

    _cache_registry_once()
    if args.plan:
        show_plan(args.start_family)
        return
    if args.status:
        show_status()
        return
    raise SystemExit(run_batch(args.start_family))


if __name__ == "__main__":
    main()
