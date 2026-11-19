"""Resume VP05 r8s5d3 next01 after a saved, RAM-guarded sector206 stop.

This tool is intentionally restricted to the *four already prepared* jobs
79,109,234,230. It verifies original Step93 proof and earlier archived sector
successes via the unchanged continuation controller. The preserved completed
sector205 project is reused, and the stopped sector206 project is never
restarted, cleaned, overwritten, or labelled mathematically unstable.

plan/audit: read-only. execute: explicit Windows acknowledgement; serial WSL
Kira with existing RAM/swap monitor, using only existing isolated project dirs.

NO family Stage-2 63-master closure, reduction coefficient proof, promotion,
or canonical-registry update is performed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from examples import three_loop_vp05_stage2_continuation_batch as base
from examples.three_loop_vp05_stage2_residual_forensics import project_profile

TAG = "VP05_AFTER206 "
RUN_ID = "next01"
SKIPPED = 206
PREVIOUS = 205
REMAINING = (79, 109, 234, 230)
ACK = "PRESERVE_SECTOR206_RUN_REMAINING_FOUR"
STATUS_ALL = "VP05_AFTER206_FOUR_LOCAL_PILOTS_RETAINED_206_STILL_UNRESOLVED"
STATUS_HALTED = "VP05_AFTER206_HALTED_REVIEW_REQUIRED"


def verified_scope() -> tuple[list[dict], list[dict]]:
    """Re-read pinned manifests, hash every input, and enforce the stop reason."""
    selected = base.sector_input_scope()
    if [item["sector"] for item in selected] != [
            PREVIOUS, SKIPPED, *REMAINING]:
        raise RuntimeError("Unexpected protected next01 sector manifest")
    rows = [base.status_one(RUN_ID, item) for item in selected]
    by_sector = {r["sector"]: r for r in rows}
    prior = by_sector[PREVIOUS]
    if (prior["state"] != "completed_local_retained"
        or prior.get("candidate_retained") is not True
        or prior.get("monitor_result", {}).get("kira_returncode") != 0
        or prior.get("monitor_result", {}).get("success") is not True):
        raise RuntimeError("Protected sector205 local success not independently verified")
    stopped = by_sector[SKIPPED]
    monitor = stopped.get("monitor_result") or {}
    if (stopped["state"] != "finished_needs_review"
        or monitor.get("reason") != "ram_stop"
        or monitor.get("success") is not False
        or monitor.get("kira_returncode") != -15):
        raise RuntimeError("Expected preserved sector206 RAM guard stop not verified")
    for sector in REMAINING:
        if by_sector[sector]["state"] not in (
                "prepared", "completed_local_retained"):
            raise RuntimeError(
                f"Sector{sector} missing, already interrupted, or changed; "
                "refusing to execute/overwrite")
    return selected, rows


def summarize_206() -> dict:
    """Bounded read-only inspection; partial Kira files are not proof."""
    selection, rows = verified_scope()
    stopped = next(row for row in rows if row["sector"] == SKIPPED)
    source = next(item for item in selection if item["sector"] == SKIPPED)
    directory = base.pilot_dir(RUN_ID, SKIPPED)
    details = project_profile(
        directory, expected_targets=source["targets"],
        mandatory_name=base.MANDATORY, preferred_name=base.PREFERRED)
    logs = details["log_files"]
    progress = [x["last_sector_progress"] for x in logs
                if x.get("last_sector_progress")]
    return {"sector": SKIPPED, "state": stopped["state"],
            "stop_reason": stopped["monitor_result"]["reason"],
            "wsl_returncode": stopped["monitor_result"]["kira_returncode"],
            "resources": base.read_resource_peaks(directory),
            "project_exists": details["project_exists"],
            "input_matches": details["mandatory_input_set_matches_expected"]
                             and details["preferred_input_set_matches_expected"],
            "master_file_present": details["metadata"]["masters"]["exists"]
                                    or details["metadata"]["masters_final"]["exists"],
            "partial_system_gz_count": details["metadata"]["system_equations"]["count"],
            "last_saved_kira_progress": progress[-1] if progress else None,
            "scientific_reduction_proven": False,
            "preserve_existing_evidence": True}


def plan() -> dict:
    selected, states = verified_scope()
    by_sector = {row["sector"]: row for row in states}
    return {
        "status": "VP05_AFTER206_REMAINING_FOUR_READ_ONLY",
        "run_id": RUN_ID, "requested_boundary_seed": base.SEED,
        "sector205": {"retained": True, "reused_without_rerun": True},
        "sector206": summarize_206(),
        "remaining": [{**by_sector[s], "resources": base.read_resource_peaks(
                     base.pilot_dir(RUN_ID, s))} for s in REMAINING],
        "remaining_candidates": sum(len(i["targets"]) for i in selected
                                    if i["sector"] in REMAINING),
        "per_sector_limit_seconds": base.MAX_SECTOR_SECONDS,
        "ram_warn_stop_gib": [base.RAM_WARN, base.RAM_STOP],
        "swap_warn_stop_gib": [base.SWAP_WARN, base.SWAP_STOP],
        "requires_explicit_execution_ack": ACK,
        "skip_206_is_not_a_pass": True, "global_closure_proven": False,
        "kira_executed": False, "files_modified": False}


def execute(*, acknowledge: str, max_total_seconds: int = 43200) -> dict:
    if acknowledge != ACK:
        raise ValueError("Exact acknowledgement required to skip blocked sector206")
    if os.name != "nt":
        raise RuntimeError("Kira execution must run from Windows with WSL")
    if not 30 <= max_total_seconds <= 43200:
        raise ValueError("max-total-seconds must be between 30 and 43200")
    selected, current = verified_scope()
    by_sector = {row["sector"]: row for row in current}
    by_target = {item["sector"]: item for item in selected}
    started = time.monotonic()
    completed = []
    for sector in REMAINING:
        before = by_sector[sector]
        if before["state"] == "completed_local_retained":
            completed.append({"sector": sector, "action": "reused_saved_local_pass"})
            continue
        remaining_seconds = max_total_seconds - (time.monotonic() - started)
        if remaining_seconds < 30:
            completed.append({"sector": sector, "action": "time_budget_exhausted"})
            break
        base._no_other_kira()
        directory = base.pilot_dir(RUN_ID, sector)
        log = directory / "console_output.log"
        if log.exists() or log.is_symlink():
            raise RuntimeError(
                "Refusing to overwrite existing console log: " + str(log))
        # Already prepared by prior next01; no new directory, job generation,
        # input rewrite, source checkpoint rewrite, or restart of sector206.
        args = ["wsl.exe", "--cd", str(directory), "python3", base.MONITOR,
                "--max-seconds", str(min(base.MAX_SECTOR_SECONDS,
                                          int(remaining_seconds))),
                "--warn-gib", str(base.SWAP_WARN),
                "--stop-gib", str(base.SWAP_STOP),
                "--interval", str(base.INTERVAL),
                "--ram-warn-gib", str(base.RAM_WARN),
                "--ram-stop-gib", str(base.RAM_STOP)]
        with log.open("x", encoding="utf-8") as stream:
            run = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT)
        after = base.status_one(RUN_ID, by_target[sector])
        completed.append({
            "sector": sector, "action": "executed",
            "wsl_returncode": run.returncode,
            "saved_state": after["state"],
            "monitor": after.get("monitor_result"),
            "resources": base.read_resource_peaks(directory)})
        if run.returncode != 0 or after["state"] != "completed_local_retained":
            break
    all_completed = (
        len(completed) == len(REMAINING)
        and all(row["action"] == "reused_saved_local_pass"
                or (row.get("action") == "executed"
                    and row.get("wsl_returncode") == 0
                    and row.get("saved_state") == "completed_local_retained")
                for row in completed))
    return {"status": STATUS_ALL if all_completed else STATUS_HALTED,
            "run_id": RUN_ID, "sector205_reused": True,
            "sector206_skipped_due_to_ram_stop": True,
            "sector206_still_unresolved": True,
            "four_sector_run_records": completed,
            "global_63_master_closure_proven": False,
            "formal_promotion_ready_created": False,
            "original_projects_deleted_or_replaced": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "audit", "run"))
    parser.add_argument("--acknowledge", default="")
    parser.add_argument("--max-total-seconds", type=int, default=43200)
    args = parser.parse_args()
    if args.mode in ("plan", "audit"):
        result = plan()
    else:
        result = execute(
            acknowledge=args.acknowledge,
            max_total_seconds=args.max_total_seconds)
    print(TAG + json.dumps(result, ensure_ascii=False), flush=True)
    if args.mode == "run" and result["status"] != STATUS_ALL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
