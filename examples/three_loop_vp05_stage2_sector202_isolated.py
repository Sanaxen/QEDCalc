"""Guarded, isolated VP05 sector202 three-candidate r7s5d3 diagnostic.

One exact sector only; NEVER restarts saved sector206/234 jobs or overwrites
the Step93 exact-source proof. A retained initiate-only master list is NOT
a proof of mathematical r8s5d3/r8s6d2 boundary closure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from examples import three_loop_vp05_sector202_reuse_audit as evidence
from examples import three_loop_vp05_stage2_non202_batch as prior
from examples import three_loop_vp05_stage2_continuation_batch as guard
from examples import three_loop_vp05_stage2_sector_inventory as inventory
from examples.three_loop_master_basis_candidate_closure import _read_integrals
from three_loop.master_basis_api import Seed, build_family_spec, export_kira_project, find_or_infer_masters

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FAMILY = "VP05_full"
SECTOR = 202
REQUESTED_SEED = "r8s5d3"
EFFECTIVE = Seed(7, 5, 3)
TARGETS = tuple("VP05_full[" + ",".join(str(v) for v in row) + "]"
                for row in evidence.gap.TARGETS)
ACK = "EXECUTE_VP05_ISOLATED_SECTOR202_R7S5D3"
TAG = "VP05_SECTOR202_ISOLATED "
MANIFEST = "vp05_sector202_r7s5d3_manifest.json"
MANDATORY = guard.MANDATORY
PREFERRED = guard.PREFERRED
MONITOR = guard.MONITOR
FILES = guard.FILES
MAX_SECONDS = 5400
RAM_WARN, RAM_STOP = 18, 22
SWAP_WARN, SWAP_STOP = 4, 8
INTERVAL = 5


def project_for(run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", run_id):
        raise ValueError("run_id must be 1-32 ASCII letters/digits/_/-")
    return OUTPUT / ("vp05_stage2_sector202_r7s5d3_" + run_id)


def digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Missing or linked pinned file: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or linked manifest: " + str(path))
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise RuntimeError("Invalid JSON object: " + str(path))
    return value


def scope() -> dict:
    """Reopen all no202 + Step93 protected evidence before mutation or run."""
    report = evidence.inspect()
    if (report.get("status") != "VP05_SECTOR202_EVIDENCE_REUSED_FRONTIER_OPEN"
        or report.get("canonical_candidate_masters") != 63
        or report.get("sector202_all_three_targets_proven") is not False
        or report.get("global_63_master_basis_proven") is not False
        or report.get("sector202_local_effective_boundary") != EFFECTIVE.tag):
        raise RuntimeError("Protected sector202 evidence scope changed")
    rows = report.get("remaining_sector_groups", [])
    row = next((r for r in rows if r.get("sector") == SECTOR), None)
    if (row is None or row.get("candidate_count") != len(TARGETS)
        or row.get("targets") != list(TARGETS)
        or len(rows) != 7 or sum(r.get("candidate_count", 0) for r in rows) != 23):
        raise RuntimeError("Canonical three target obligations unexpectedly changed")
    # Existing r8s5d3 standard project must not secretly have a valid result
    # that makes this separate pilot redundant.
    old = inventory.analyze_sector(Seed(8, 5, 3), SECTOR, list(TARGETS))
    if (old.get("matching_local_master_inventory") is True
        or old.get("restricted_exact_sector_audit_match") is True
        or old.get("candidate_count") != 3
        or old.get("targets") != list(TARGETS)):
        raise RuntimeError("Unexpected existing same-seed sector202 evidence; review first")
    if SECTOR.bit_count() != 4 or min(8, SECTOR.bit_count() + 3) != EFFECTIVE.r:
        raise RuntimeError("Wrong effective exact-sector r limit")
    return {"sector": SECTOR, "targets": list(TARGETS),
            "requested_seed": REQUESTED_SEED, "effective_seed": EFFECTIVE.tag,
            "existing_standard_project": old.get("project"),
            "step93_target_b_exact_identity_reused_for_context_only": True,
            "step93_equivalence_to_this_new_kira_job_proven": False}


def status(run_id: str, info: dict) -> dict:
    directory = project_for(run_id)
    out = {"project": str(directory), "sector": SECTOR, "run_id": run_id,
           "effective_seed": EFFECTIVE.tag, "target_count": 3,
           "global_closure_proven": False}
    if directory.is_symlink():
        raise RuntimeError("Linked pilot project refused")
    if not directory.exists():
        return {**out, "state": "not_prepared", "candidate_retained": False}
    if not directory.is_dir():
        raise RuntimeError("Pilot path exists and is not a directory")
    saved = read(directory / MANIFEST)
    if (saved.get("status") != "VP05_SECTOR202_ISOLATED_PREPARED"
        or saved.get("run_id") != run_id
        or saved.get("family") != FAMILY or saved.get("sector") != SECTOR
        or saved.get("requested_seed") != REQUESTED_SEED
        or saved.get("effective_seed") != EFFECTIVE.tag
        or saved.get("targets") != info["targets"]
        or set(saved.get("input_sha256", {})) != set(FILES)):
        raise RuntimeError("Pinned pilot input/manifest mismatch")
    for name, sha in saved["input_sha256"].items():
        if digest(directory / name) != sha:
            raise RuntimeError("Pilot input changed: " + name)
    for name in (MANDATORY, PREFERRED):
        if _read_integrals(directory / name, FAMILY) != info["targets"]:
            raise RuntimeError("Target input differs from protected manifest")
    final = directory / "monitored_exit.json"
    if final.is_symlink():
        raise RuntimeError("Linked monitor result refused")
    if final.is_file():
        outcome = read(final)
        success = (outcome.get("reason") == "kira_exit"
                   and outcome.get("success") is True
                   and outcome.get("kira_returncode") == 0)
        master_source, retained = None, False
        if success:
            try:
                master_source, masters, _ = find_or_infer_masters(
                    directory, FAMILY, mandatory_targets=info["targets"])
                retained = set(masters) == set(info["targets"])
            except (RuntimeError, ValueError, OSError):
                retained = False
        guarded = (outcome.get("success") is False
                   and outcome.get("kira_returncode") == -15
                   and outcome.get("reason") in ("ram_stop", "swap_stop", "time_stop"))
        state = ("completed_local_retained" if retained else
                 "guard_stopped_" + outcome["reason"] if guarded else
                 "finished_needs_review")
        return {**out, "state": state, "candidate_retained": bool(retained),
                "master_source": str(master_source) if master_source else None,
                "monitor_result": outcome}
    interrupted = any((directory / name).exists() for name in (
        "console_output.log", "monitored_kira.log", "monitored_metrics.jsonl",
        "tmp", "results", "sectormappings"))
    return {**out, "state": "interrupted_manual_review" if interrupted else "prepared",
            "candidate_retained": False}


def audit(run_id: str) -> dict:
    info = scope()
    state = status(run_id, info)
    resources = guard.read_resource_peaks(project_for(run_id)) if state["state"] != "not_prepared" else {}
    return {"status": "VP05_SECTOR202_DIAGNOSTIC_READ_ONLY",
            "run_id": run_id, "pilot": state, "resources": resources,
            "target_exponents": [list(v) for v in evidence.gap.TARGETS],
            "max_seconds": MAX_SECONDS, "ram_warn_stop_gib": [RAM_WARN, RAM_STOP],
            "swap_warn_stop_gib": [SWAP_WARN, SWAP_STOP],
            "previously_retained_other_sectors": 19,
            "sector206_234_preserved": True,
            "r8s5d3_full_closure_proven": False,
            "r8s6d2_full_closure_proven": False,
            "kira_executed": False, "files_modified": False}


def prepare(run_id: str) -> dict:
    info = scope()
    before = status(run_id, info)
    if before["state"] == "prepared":
        return {"status": "VP05_SECTOR202_PREPARED_REUSED_NO_KIRA",
                "project": before["project"], "new_project_created": False,
                "files_modified": False, "kira_executed": False}
    if before["state"] != "not_prepared":
        raise RuntimeError("Existing project must not be overwritten or restarted: "
                           + before["state"])
    directory = project_for(run_id)
    if not OUTPUT.is_dir():
        raise RuntimeError("Output directory absent")
    monitor = ROOT / "scripts" / MONITOR
    if monitor.is_symlink() or not monitor.is_file():
        raise RuntimeError("Pinned Kira monitoring script absent")
    spec = build_family_spec(FAMILY)
    if spec.baseline_seed.tag != "r8s3d0":
        raise RuntimeError("Unexpected VP05 family baseline")
    directory.mkdir(parents=False, exist_ok=False)
    export_kira_project(spec, directory, seed=EFFECTIVE, solver="masters",
                        mandatory_file=MANDATORY, preferred_masters_file=PREFERRED,
                        reduce_sectors=[SECTOR], top_level_sectors=[SECTOR],
                        clean=False)
    for name in (MANDATORY, PREFERRED):
        (directory / name).write_text("\n".join(info["targets"]) + "\n",
                                       encoding="utf-8", newline="\n")
    shutil.copyfile(monitor, directory / MONITOR)
    manifest = {"status": "VP05_SECTOR202_ISOLATED_PREPARED",
                "run_id": run_id, "family": FAMILY, "sector": SECTOR,
                "requested_seed": REQUESTED_SEED,
                "effective_seed": EFFECTIVE.tag, "targets": info["targets"],
                "input_sha256": {name: digest(directory / name) for name in FILES},
                "proof_of_standard_family_closure": False,
                "protected_projects_overwritten": False}
    (directory / MANIFEST).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    after = status(run_id, info)
    if after["state"] != "prepared":
        raise RuntimeError("Prepared project not hash-verified; preserve for review")
    return {"status": "VP05_SECTOR202_PREPARE_PASS_NO_KIRA",
            "project": str(directory), "new_project_created": True,
            "existing_projects_overwritten": False, "kira_executed": False}


def execute(run_id: str, acknowledge: str) -> dict:
    if acknowledge != ACK:
        raise ValueError("Exact execute acknowledgement is required")
    if os.name != "nt":
        raise RuntimeError("Kira execution is supported only on Windows + WSL")
    info = scope()
    before = status(run_id, info)
    if before["state"] != "prepared":
        raise RuntimeError("No automatic retry or restart: " + before["state"])
    # Keep both process and memory gates from the no202a guard that passed.
    guard._no_other_kira()
    resources = prior.wsl_resource_preflight()
    project = project_for(run_id)
    if shutil.disk_usage(project).free < 10 * 1024**3:
        raise RuntimeError("Less than 10 GiB free disk")
    console = project / "console_output.log"
    if console.exists() or console.is_symlink():
        raise RuntimeError("Existing Kira console log must not be overwritten")
    command = ["wsl.exe", "--cd", str(project), "python3", MONITOR,
               "--max-seconds", str(MAX_SECONDS),
               "--warn-gib", str(SWAP_WARN), "--stop-gib", str(SWAP_STOP),
               "--interval", str(INTERVAL),
               "--ram-warn-gib", str(RAM_WARN),
               "--ram-stop-gib", str(RAM_STOP)]
    print("START isolated VP05 sector202 " + str(project), flush=True)
    with console.open("x", encoding="utf-8") as stream:
        process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    after = status(run_id, info)
    result = {"status": ("VP05_SECTOR202_THREE_LOCAL_CANDIDATES_RETAINED_NOT_CLOSURE"
                         if process.returncode == 0 and after["state"] == "completed_local_retained"
                         else "VP05_SECTOR202_GUARD_STOP_PRESERVED_NOT_PROOF"
                         if after["state"].startswith("guard_stopped_")
                         else "VP05_SECTOR202_EXECUTION_REVIEW_REQUIRED"),
              "run_id": run_id, "wsl_returncode": process.returncode,
              "pilot": after, "resource_preflight": resources,
              "resources": guard.read_resource_peaks(project),
              "previously_retained_other_sectors": 19,
              "sector206_234_preserved": True, "global_stage2_closure_proven": False,
              "r8s6d2_closure_proven": False, "promotion_ready_created": False}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "prepare", "audit", "run"))
    parser.add_argument("--run-id", default="sec202a")
    parser.add_argument("--acknowledge", default="")
    args = parser.parse_args()
    if args.mode in ("plan", "audit"):
        result = audit(args.run_id)
    elif args.mode == "prepare":
        result = prepare(args.run_id)
    else:
        result = execute(args.run_id, args.acknowledge)
    print(TAG + json.dumps(result, ensure_ascii=False), flush=True)
    if args.mode == "run" and result["status"] != "VP05_SECTOR202_THREE_LOCAL_CANDIDATES_RETAINED_NOT_CLOSURE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
