"""Resumable stage-2 batch controller.

Modes:
  --plan     show pending steps and runtime estimate without executing Kira
  --status   show checkpoint summary
  --run      execute pending families sequentially
  --resume   auto-detect the first unfinished family and continue

Run/plan/resume may be capped by --max-diagrams. Canonical families are atomic:
the controller never starts a family whose diagram count would exceed the cap.

For each pending family the controller reuses completed seed audits, runs any
missing FireFly baseline/boundary seeds, evaluates the one-axis boundary audit,
and automatically enters the mandatory-union/candidate-closure rescue path when
needed. Candidate closure is always followed by the no-rerun completion audit;
this intentionally handles Kira/FireFly runs that completed but did not emit a
human-readable equation for every selected non-master target.

A successfully proven family is written as a promotion-ready audit artifact.
Source-code registry promotion remains a separate reviewed Git change so a long
unattended computation never edits the executable canonical registry itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
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
    estimate_step,
    execution_families,
    family_steps,
    load_checkpoint,
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


def _bat(name: str = "run_three_loop_master_basis_seed.bat") -> Path:
    return ROOT / name


def _run_step(step: BatchStep) -> int:
    cmd = ["cmd.exe", "/d", "/c", str(_bat()), step.family, step.seed.tag, step.solver]
    est = estimate_step(step)
    eta = datetime.now().astimezone() + timedelta(seconds=est["median_s"])
    print("\n=== RUN", step.key, "===", flush=True)
    print(
        f"estimate: median~{_fmt(est['median_s'])} "
        f"range~{_fmt(est['low_s'])}..{_fmt(est['high_s'])} "
        f"median finish~{eta.strftime('%Y-%m-%d %H:%M %Z')}",
        flush=True,
    )
    start = time.perf_counter()
    update_checkpoint(step, status="running")
    proc = subprocess.run(cmd, cwd=ROOT)
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


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _single_audit(pattern: str) -> tuple[Path | None, dict]:
    hits = sorted(AUDIT_DIR.glob(pattern))
    if not hits:
        return None, {}
    # Prefer the newest artifact if a harmless older rerun artifact exists.
    path = max(hits, key=lambda item: item.stat().st_mtime)
    return path, _read_json(path)


def _run_bat_stage(
    family: str,
    baseline_tag: str,
    *,
    bat_name: str,
    phase: str,
    phase_class: str,
    tolerate_nonzero: bool = False,
) -> int:
    step = BatchStep(family, phase, master_basis_api.Seed(
        int(baseline_tag.split("s", 1)[0][1:]),
        int(baseline_tag.split("s", 1)[1].split("d", 1)[0]),
        int(baseline_tag.rsplit("d", 1)[1]),
    ), "firefly")
    cmd = ["cmd.exe", "/d", "/c", str(_bat(bat_name)), family, baseline_tag, "firefly"]
    print(f"\n=== RUN {family}:{phase} via {bat_name} ===", flush=True)
    start = time.perf_counter()
    update_checkpoint(step, status="running")
    proc = subprocess.run(cmd, cwd=ROOT)
    elapsed = time.perf_counter() - start
    spec = master_basis_api.build_family_spec(family)
    append_runtime({
        "family": family,
        "phase": phase,
        "phase_class": phase_class,
        "seed": baseline_tag,
        "solver": "firefly",
        "elapsed_s": elapsed,
        "topology": spec.topology_family,
        "unique_physical": spec.unique_physical_count,
        "auxiliary_count": spec.auxiliary_count,
        "top_sector": spec.top_sector,
        "exit_code": proc.returncode,
    })
    status = "pass" if proc.returncode == 0 else ("soft-fail" if tolerate_nonzero else "fail")
    update_checkpoint(step, status=status, elapsed_s=elapsed, detail=f"exit_code={proc.returncode}")
    print(
        f"=== END {family}:{phase}: exit={proc.returncode} elapsed={_fmt(elapsed)} ===",
        flush=True,
    )
    return int(proc.returncode)


def _record_promotion_ready(
    family: str,
    baseline_tag: str,
    *,
    basis_count: int,
    basis_source: str,
    proof_mode: str,
    proof_audit: str,
) -> Path:
    proposed = family.removesuffix("_full") + f"_final{basis_count}"
    path = AUDIT_DIR / f"three_loop_{family.lower()}_promotion_ready.json"
    payload = {
        "schema_version": 1,
        "stage": "master_basis_promotion_ready",
        "family": family,
        "baseline_seed": baseline_tag,
        "proposed_master_basis_id": proposed,
        "master_count": int(basis_count),
        "master_basis_source": basis_source,
        "proof_mode": proof_mode,
        "proof_audit": proof_audit,
        "audit_pass": True,
        "registry_promotion_pending_review": True,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    synthetic = BatchStep(
        family,
        "family-ready",
        master_basis_api.build_family_spec(family).baseline_seed,
        "firefly",
    )
    update_checkpoint(
        synthetic,
        status="pass",
        detail=f"{proposed}; proof={proof_mode}; artifact={path}",
    )
    print(f"PROMOTION READY: {family} -> {proposed}", flush=True)
    print(f"promotion-ready audit: {path}", flush=True)
    return path


def _run_union_rescue(family: str, baseline_tag: str) -> int:
    code = _run_bat_stage(
        family,
        baseline_tag,
        bat_name="run_three_loop_master_basis_union_reduction.bat",
        phase="union-reduction",
        phase_class="union",
    )
    if code:
        return code

    union_path, union = _single_audit(
        f"three_loop_{family.lower()}_firefly_{baseline_tag}_union_*_reduction_audit.json"
    )
    if not union_path or not union.get("audit_pass"):
        print(f"STOP: union reduction audit missing/failed for {family}", flush=True)
        return 21

    # The text-equation closure audit can return nonzero even when all Kira runs
    # completed successfully. Do not stop here; the no-rerun audit is the
    # authoritative completion check for this generic FireFly path.
    closure_code = _run_bat_stage(
        family,
        baseline_tag,
        bat_name="run_three_loop_master_basis_candidate_closure.bat",
        phase="candidate-closure",
        phase_class="closure",
        tolerate_nonzero=True,
    )
    if closure_code:
        print(
            f"{family}: candidate closure returned {closure_code}; "
            "running no-rerun completion audit before deciding failure.",
            flush=True,
        )

    reaudit_code = _run_bat_stage(
        family,
        baseline_tag,
        bat_name="run_three_loop_master_basis_candidate_closure_reaudit.bat",
        phase="candidate-closure-reaudit",
        phase_class="closure-audit",
    )
    if reaudit_code:
        print(f"STOP: authoritative no-rerun closure audit failed for {family}", flush=True)
        return reaudit_code

    reaudit_path, reaudit = _single_audit(
        f"three_loop_{family.lower()}_firefly_{baseline_tag}_candidate_*_closure_reaudit.json"
    )
    if (
        not reaudit_path
        or not reaudit.get("audit_pass")
        or not reaudit.get("stable_under_one_axis_extensions")
    ):
        print(f"STOP: stable closure proof artifact missing for {family}", flush=True)
        return 22

    count = int(union.get("candidate_master_count", 0))
    source = str(union.get("candidate_master_copy") or "")
    if count <= 0 or not source:
        print(f"STOP: invalid candidate basis metadata for {family}", flush=True)
        return 23

    _record_promotion_ready(
        family,
        baseline_tag,
        basis_count=count,
        basis_source=source,
        proof_mode="mandatory-union-plus-no-rerun-closure",
        proof_audit=str(reaudit_path),
    )
    return 0


def _promotion_ready_path(family: str) -> Path:
    return AUDIT_DIR / f"three_loop_{family.lower()}_promotion_ready.json"


def _family_is_ready(family: str) -> bool:
    payload = _read_json(_promotion_ready_path(family))
    if (
        payload.get("audit_pass")
        and payload.get("stage") == "master_basis_promotion_ready"
        and payload.get("family") == family
    ):
        return True

    baseline = master_basis_api.build_family_spec(family).baseline_seed
    step = BatchStep(family, "family-ready", baseline, "firefly")
    prior = load_checkpoint().get("steps", {}).get(step.key, {})
    return prior.get("status") == "pass"


def _select_families(
    start_family: str | None,
    max_diagrams: int | None,
    *,
    skip_ready: bool = True,
) -> tuple[list[str], int]:
    if max_diagrams is not None and max_diagrams <= 0:
        raise ValueError("max_diagrams must be a positive integer")

    families = list(execution_families())
    if start_family:
        if start_family not in families:
            raise ValueError(f"start family is not pending: {start_family}")
        families = families[families.index(start_family):]

    if skip_ready:
        families = [family for family in families if not _family_is_ready(family)]

    selected: list[str] = []
    diagrams = 0
    for family in families:
        count = len(master_basis_api.build_family_spec(family).diagrams)
        if max_diagrams is not None and diagrams + count > max_diagrams:
            break
        selected.append(family)
        diagrams += count
    return selected, diagrams


def _queue_for_families(families: list[str]) -> list[BatchStep]:
    if not families:
        return []
    allowed = set(families)
    queue = build_queue(start_family=families[0])
    return [step for step in queue if step.family in allowed]


def _auto_resume_family() -> str | None:
    families, _ = _select_families(None, None, skip_ready=True)
    return families[0] if families else None


def show_plan(start_family: str | None, max_diagrams: int | None) -> None:
    families, diagram_count = _select_families(start_family, max_diagrams)
    queue = _queue_for_families(families)
    estimate = estimate_queue(queue)
    print("QEDCalc master-basis batch plan")
    print(f"selected families: {len(families)}")
    print(f"selected diagrams: {diagram_count}" + (
        f" / max {max_diagrams}" if max_diagrams is not None else ""
    ))
    if max_diagrams is not None:
        print("diagram cap is strict; canonical families are atomic and are never split")
    if families:
        print(f"first family: {families[0]}")
        print(f"last family: {families[-1]}")
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
    print("note: union/candidate-closure rescue time is not included until a family proves unstable")


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
    next_family = _auto_resume_family()
    print("auto-resume family:", next_family or "none (all pending families are promotion-ready)")
    failed = [row for row in rows if row.get("status") in {"fail", "soft-fail", "needs_union"}]
    for row in failed[-10:]:
        print(f"  {row.get('key')}: {row.get('status')} {row.get('detail','')}")


def run_batch(
    start_family: str | None,
    max_diagrams: int | None,
    *,
    resume_mode: bool = False,
) -> int:
    if resume_mode and start_family is None:
        start_family = _auto_resume_family()
        if start_family is None:
            print("Nothing to resume: all currently pending families are promotion-ready.", flush=True)
            return 0
        print(f"AUTO RESUME: first unfinished family is {start_family}", flush=True)

    families, diagram_count = _select_families(start_family, max_diagrams)
    if not families:
        if max_diagrams is not None:
            print(
                f"No family fits within max-diagrams={max_diagrams} without splitting a canonical family.",
                flush=True,
            )
        else:
            print("No unfinished pending family remains.", flush=True)
        return 0

    initial_queue = _queue_for_families(families)
    initial_estimate = estimate_queue(initial_queue)
    finish = datetime.now().astimezone() + timedelta(seconds=initial_estimate["total_median_s"])
    print("QEDCalc unattended master-basis run", flush=True)
    print(
        f"selected families={len(families)} diagrams={diagram_count}" +
        (f" max_diagrams={max_diagrams}" if max_diagrams is not None else ""),
        flush=True,
    )
    print(f"first family={families[0]} last family={families[-1]}", flush=True)
    print(
        f"seed steps currently pending: {initial_estimate['step_count']} "
        f"median~{_fmt(initial_estimate['total_median_s'])} "
        f"range~{_fmt(initial_estimate['total_low_s'])}..{_fmt(initial_estimate['total_high_s'])}",
        flush=True,
    )
    print(
        f"seed-stage median finish~{finish.strftime('%Y-%m-%d %H:%M %Z')} "
        "(union/closure rescue time is added only when needed)",
        flush=True,
    )

    for index, family in enumerate(families, start=1):
        if _family_is_ready(family):
            print(f"SKIP promotion-ready family: {family}", flush=True)
            continue
        spec = master_basis_api.build_family_spec(family)
        baseline = spec.baseline_seed
        print(
            f"\n##### FAMILY {index}/{len(families)} {family} baseline={baseline.tag} #####",
            flush=True,
        )
        steps = family_steps(family)
        queue_keys = {step.key for step in build_queue(start_family=family)}
        for step in steps:
            if step.key not in queue_keys:
                print(f"SKIP existing/pass: {step.key}", flush=True)
                continue
            code = _run_step(step)
            if code:
                print(
                    f"STOP: {step.key} failed; fix API/config and rerun with "
                    f"--run --start-family {family}",
                    flush=True,
                )
                return code

        code, audit = _run_boundary_audit(family, baseline.tag)
        if code or not audit.get("audit_pass"):
            print(f"STOP: boundary audit failed for {family}", flush=True)
            return code or 24

        if audit.get("union_reduction_needed"):
            print(f"{family}: seed-dependent masters detected; entering union rescue.", flush=True)
            code = _run_union_rescue(family, baseline.tag)
            if code:
                return code
            continue

        if not audit.get("stable_under_one_axis_extensions"):
            print(
                f"STOP: {family} is neither stable nor marked for union reduction.",
                flush=True,
            )
            return 25

        count = int(audit.get("baseline_master_count", 0))
        source = str(audit.get("baseline_master_source") or "")
        if count <= 0 or not source:
            print(f"STOP: invalid stable baseline metadata for {family}", flush=True)
            return 26
        _record_promotion_ready(
            family,
            baseline.tag,
            basis_count=count,
            basis_source=source,
            proof_mode="stable-one-axis-baseline",
            proof_audit=str(_boundary_audit_path(family, baseline.tag)),
        )

    print(
        "All scheduled families reached promotion-ready status. "
        "Review promotion-ready audits, then update the executable registry in Git.",
        flush=True,
    )
    return 0


def main() -> None:
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--status", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--resume", action="store_true")
    p.add_argument("--start-family")
    p.add_argument("--max-diagrams", type=int)
    args = p.parse_args()

    _cache_registry_once()
    if args.plan:
        show_plan(args.start_family, args.max_diagrams)
        return
    if args.status:
        show_status()
        return
    raise SystemExit(
        run_batch(
            args.start_family,
            args.max_diagrams,
            resume_mode=bool(args.resume),
        )
    )


if __name__ == "__main__":
    main()
