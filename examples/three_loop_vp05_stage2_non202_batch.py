"""VP05 r8s5d3: preserve blocked 206/234 and run 202-free sectors.

Read-only plan/audit, exclusive preparation of FIVE new project directories,
and guarded, serial execution of SIX independent exact-sector candidate jobs:
230 (already prepared by next01), 126, 127, 229, 231, 237.

Sector202 is not a bitwise subsector of any selected top-level sector.
This removes that particular recursive sub-sector from these local jobs,
NOT a proof that any of them will run quickly or that the 63-master basis
is globally closed. The original stopped projects are NEVER modified.

After a guard stop, the stopped project's results are preserved and NOT
restarted. Further independent jobs may continue, but only after a
fresh WSL RAM/swap preflight and confirmation that no other Kira runs.
Unexpected failures / master-selection changes halt the entire batch.
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
import time

from examples import three_loop_vp05_stage2_continuation_batch as previous
from examples import three_loop_vp05_stage2_resume_after206 as follow
from examples import three_loop_vp05_stage2_sector_inventory as inventory
from examples.three_loop_master_basis_candidate_closure import _read_integrals
from three_loop.master_basis_api import Seed, build_family_spec, export_kira_project, find_or_infer_masters

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FAMILY = "VP05_full"
BOUNDARY = "r8s5d3"
SECTORS = (230, 126, 127, 229, 231, 237)
NEW_SECTORS = (126, 127, 229, 231, 237)
EXPECTED_COUNTS = (3, 2, 2, 6, 5, 5)
BLOCKED = (206, 234)
ACK = "EXECUTE_VP05_NO_SECTOR202_BATCH"
TAG = "VP05_NON202_BATCH "
MANDATORY = previous.MANDATORY
PREFERRED = previous.PREFERRED
MONITOR = previous.MONITOR
FILES = previous.FILES
MANIFEST = "vp05_non202_isolated_manifest.json"
MAX_SECTOR_SECONDS = 5400
MAX_TOTAL_SECONDS = 43200
RAM_WARN, RAM_STOP = 18, 22
SWAP_WARN, SWAP_STOP = 4, 8
INTERVAL_SECONDS = 5


def run_id_check(run_id: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", run_id):
        raise ValueError("Invalid run id; use 1-32 ASCII letters/digits/_/-")


def project_for(run_id: str, sector: int) -> Path:
    run_id_check(run_id)
    if sector not in SECTORS:
        raise ValueError("Sector not allowed in protected no-202 batch")
    if sector == 230:
        return previous.pilot_dir("next01", 230)
    return OUTPUT / f"vp05_non202_r8s5d3_{run_id}_sec{sector}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Expected non-linked JSON file: " + str(path))
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        raise RuntimeError("Invalid JSON payload: " + str(path))
    return obj


def classify(previous_status: dict) -> str:
    state = previous_status["state"]
    if state == "completed_local_retained":
        return state
    if state == "finished_needs_review":
        monitor = previous_status.get("monitor_result") or {}
        if (monitor.get("reason") in ("ram_stop", "swap_stop", "time_stop")
            and monitor.get("success") is False
            and monitor.get("kira_returncode") == -15):
            return "guard_stopped_" + monitor["reason"]
    return state


def verified_context() -> tuple[list[dict], dict]:
    """Reopen all original proof and isolated job inputs, never a label alone."""
    old_items, old_states = follow.verified_scope()
    old_map = {r["sector"]: r for r in old_states}
    for sec in (79, 109):
        if old_map[sec]["state"] != "completed_local_retained":
            raise RuntimeError("A prior retained local master set is no longer verified")
    for sec in BLOCKED:
        row = old_map[sec]
        monitored = row.get("monitor_result") or {}
        if (row["state"] != "finished_needs_review"
            or monitored.get("reason") != "ram_stop"
            or monitored.get("kira_returncode") != -15
            or monitored.get("success") is not False):
            raise RuntimeError(f"Protected sector{sec} RAM-stop provenance changed")
    if old_map[230]["state"] not in (
            "prepared", "completed_local_retained", "finished_needs_review",
            "interrupted_manual_review"):
        raise RuntimeError("Saved sector230 project not prepared/inspectable")

    existing = inventory.inspect()
    if (existing.get("status") != "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY"
        or existing.get("canonical_candidate_masters") != 63
        or existing.get("canonical_candidate_sectors") != 26
        or existing.get("step93_target_b_original_source_proof_verified") is not True):
        raise RuntimeError("Canonical Stage-2 or Step93 evidence has changed")
    rows = existing["boundary_inventory"][BOUNDARY]["sector_rows"]
    selected = []
    for sector, count in zip(SECTORS, EXPECTED_COUNTS):
        match = [x for x in rows if x["sector"] == sector]
        if len(match) != 1:
            raise RuntimeError(f"Missing canonical candidate sector{sector}")
        row = match[0]
        if (row["candidate_count"] != count
            or len(row["targets"]) != count
            or len(set(row["targets"])) != count
            or row.get("restricted_exact_sector_audit_match") is True
            or row.get("matching_local_master_inventory") is True
            or row.get("project_exists") is True):
            raise RuntimeError(f"Unexpected same-seed standard evidence in sector{sector}")
        if (sector & 202) == 202:
            raise RuntimeError(f"Unsafe selection: sector{sector} contains sector202")
        if min(8, sector.bit_count() + 3) != 8:
            raise RuntimeError(f"Unexpected dot-envelope for sector{sector}")
        selected.append({"sector": sector, "targets": row["targets"],
                         "effective_seed": "r8s5d3"})
    old_230 = next(x for x in old_items if x["sector"] == 230)
    if old_230["targets"] != selected[0]["targets"]:
        raise RuntimeError("Saved next01 sector230 mandatory list differs from canonical candidate")
    return selected, old_map


def status_one(run_id: str, item: dict) -> dict:
    sector = item["sector"]
    dest = project_for(run_id, sector)
    if sector == 230:
        row = previous.status_one("next01", item)
        return {**row, "state": classify(row), "project": str(dest),
                "reuses_prepared_next01": True}
    out = {"sector": sector, "project": str(dest),
           "target_count": len(item["targets"]), "effective_seed": "r8s5d3",
           "global_closure_proven": False}
    if dest.is_symlink():
        raise RuntimeError("Symlink pilot directory rejected")
    if not dest.exists():
        return {**out, "state": "not_prepared"}
    if not dest.is_dir():
        raise RuntimeError("Pilot path is not a directory")
    manifest = read_json(dest / MANIFEST)
    if (manifest.get("status") != "VP05_NON202_ISOLATED_PREPARED"
        or manifest.get("run_id") != run_id
        or manifest.get("sector") != sector
        or manifest.get("boundary_seed") != BOUNDARY
        or manifest.get("effective_seed") != "r8s5d3"
        or manifest.get("targets") != item["targets"]
        or set(manifest.get("input_sha256", {})) != set(FILES)):
        raise RuntimeError("Isolated project manifest mismatch")
    for filename, expected in manifest["input_sha256"].items():
        p = dest / filename
        if not p.is_file() or p.is_symlink() or sha256(p) != expected:
            raise RuntimeError("Project input hash mismatch: " + str(p))
    if (_read_integrals(dest / MANDATORY, FAMILY) != item["targets"]
        or _read_integrals(dest / PREFERRED, FAMILY) != item["targets"]):
        raise RuntimeError("Mandatory/preferred candidate list changed")
    result_file = dest / "monitored_exit.json"
    if result_file.is_file():
        result = read_json(result_file)
        success = (result.get("success") is True
                   and result.get("reason") == "kira_exit"
                   and result.get("kira_returncode") == 0)
        masters = []
        source = None
        if success:
            try:
                source, masters, _ = find_or_infer_masters(
                    dest, FAMILY, mandatory_targets=item["targets"])
            except (ValueError, RuntimeError, OSError):
                pass
        retained = success and set(masters) == set(item["targets"])
        state = classify({"state": "completed_local_retained" if retained
                          else "finished_needs_review",
                          "monitor_result": result})
        return {**out, "state": state, "candidate_retained": bool(retained),
                "monitor_result": result,
                "master_source": str(source) if source else None}
    runtime = any((dest / p).exists() for p in (
        "console_output.log", "monitored_kira.log", "monitored_metrics.jsonl",
        "results", "tmp", "sectormappings"))
    return {**out, "state": "interrupted_manual_review" if runtime else "prepared"}


def audit(run_id: str) -> dict:
    items, old = verified_context()
    rows = [status_one(run_id, item) for item in items]
    for row in rows:
        if row["state"] != "not_prepared":
            row["resources"] = previous.read_resource_peaks(Path(row["project"]))
    success = sum(row["state"] == "completed_local_retained" for row in rows)
    stopped = [row["sector"] for row in rows
               if row["state"].startswith("guard_stopped_")]
    return {
        "status": "VP05_NON202_SAVED_AUDIT_READ_ONLY",
        "run_id": run_id, "boundary": BOUNDARY,
        "verified_local_sectors": success, "selected_sectors": len(SECTORS),
        "selected_candidate_integrals": sum(len(x["targets"]) for x in items),
        "guard_stopped_sectors": stopped,
        "sector202_excluded_from_all_new_local_top_levels": True,
        "blocked_206_234": [
            {"sector": sec, "proven": False,
             "stop_reason": old[sec]["monitor_result"]["reason"],
             "last_sector": old[sec]["monitor_result"].get("last_sector")}
            for sec in BLOCKED
        ],
        "sector_rows": rows, "global_63_master_closure_proven": False,
        "promotion_ready_created": False, "original_projects_modified": False,
        "kira_executed": False, "files_modified": False
    }


def prepare(run_id: str) -> dict:
    items, _ = verified_context()
    new_items = [x for x in items if x["sector"] in NEW_SECTORS]
    if any(project_for(run_id, x["sector"]).exists() or
           project_for(run_id, x["sector"]).is_symlink() for x in new_items):
        raise FileExistsError("One or more new directories exist; refuse overwrite")
    if not OUTPUT.is_dir():
        raise RuntimeError("Output directory unavailable")
    source = ROOT / "scripts/vp05_stage2_monitored_kira.py"
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("Pinned RAM/swap monitor script missing")
    spec = build_family_spec(FAMILY)
    if spec.baseline_seed.tag != "r8s3d0":
        raise RuntimeError("Baseline VP05 family spec changed")
    prepared = []
    for item in new_items:
        dest = project_for(run_id, item["sector"])
        dest.mkdir(parents=False, exist_ok=False)
        export_kira_project(
            spec, dest, seed=Seed(8, 5, 3), solver="masters",
            mandatory_file=MANDATORY, preferred_masters_file=PREFERRED,
            reduce_sectors=[item["sector"]], top_level_sectors=[item["sector"]],
            clean=False)
        for name in (MANDATORY, PREFERRED):
            (dest / name).write_text("\n".join(item["targets"]) + "\n",
                                      encoding="utf-8", newline="\n")
        shutil.copyfile(source, dest / MONITOR)
        manifest = {
            "status": "VP05_NON202_ISOLATED_PREPARED", "run_id": run_id,
            "sector": item["sector"], "boundary_seed": BOUNDARY,
            "effective_seed": "r8s5d3", "targets": item["targets"],
            "input_sha256": {name: sha256(dest / name) for name in FILES},
            "standard_stage2_audit_updated": False
        }
        (dest / MANIFEST).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        prepared.append(str(dest))
    states = [status_one(run_id, x) for x in new_items]
    if any(x["state"] != "prepared" for x in states):
        raise RuntimeError("New pilot post-preparation input audit failed")
    return {"status": "VP05_NON202_PREPARE_PASS_NO_KIRA",
            "projects_created": prepared,
            "sector230_reuses_saved_project": str(project_for(run_id, 230)),
            "kira_executed": False, "standard_projects_modified": False}


def wsl_resource_preflight() -> dict:
    """Conservative, read-only fresh WSL pressure check before EACH job."""
    script = ("awk '/^(MemTotal|MemAvailable|SwapTotal|SwapFree):/"
              "{print $1,$2}' /proc/meminfo")
    cmd = ["wsl.exe", "--exec", "sh", "-lc", script]
    check = subprocess.run(cmd, capture_output=True, text=True)
    if check.returncode != 0:
        raise RuntimeError("Cannot inspect WSL RAM and swap; refusing to start Kira")
    mem = {}
    for line in check.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            try:
                mem[parts[0].rstrip(":")] = int(parts[1]) / 1024**2
            except ValueError:
                continue
    if not {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"} <= mem.keys():
        raise RuntimeError("WSL resource info incomplete; refusing Kira")
    used = mem["MemTotal"] - mem["MemAvailable"]
    swap_used = mem["SwapTotal"] - mem["SwapFree"]
    if (mem["MemTotal"] <= RAM_STOP + 1 or used >= RAM_WARN
        or mem["MemAvailable"] < 8 or swap_used >= SWAP_WARN):
        raise RuntimeError(
            f"WSL memory not recovered: used={used:.2f},"
            f" available={mem['MemAvailable']:.2f}, swap={swap_used:.2f} GiB")
    return {"ram_used_gib": round(used, 2),
            "ram_available_gib": round(mem["MemAvailable"], 2),
            "swap_used_gib": round(swap_used, 2)}


def run(run_id: str, acknowledge: str, max_total_seconds: int) -> dict:
    if acknowledge != ACK:
        raise ValueError("Explicit acknowledgement required")
    if os.name != "nt":
        raise RuntimeError("This controller launches Kira only from Windows")
    if not (30 <= max_total_seconds <= MAX_TOTAL_SECONDS):
        raise ValueError("Invalid wall time budget")
    items, _ = verified_context()
    initial = [status_one(run_id, x) for x in items]
    allowed = {"prepared", "completed_local_retained",
               "guard_stopped_ram_stop", "guard_stopped_swap_stop",
               "guard_stopped_time_stop"}
    if any(x["state"] not in allowed for x in initial):
        raise RuntimeError("Unprepared or unexpected interrupted project: fail closed")
    started = time.monotonic()
    records = []
    for item, before in zip(items, initial):
        sector, state = item["sector"], before["state"]
        if state == "completed_local_retained":
            records.append({"sector": sector, "action": "reused_saved_master_list"})
            continue
        if state.startswith("guard_stopped_"):
            records.append({"sector": sector, "action": "guard_stop_preserved_no_rerun",
                            "guard_reason": state})
            continue
        remaining = max_total_seconds - (time.monotonic() - started)
        if remaining < 30:
            records.append({"sector": sector, "action": "batch_budget_exhausted"})
            break
        try:
            previous._no_other_kira()
            safety = wsl_resource_preflight()
            project = project_for(run_id, sector)
            if shutil.disk_usage(project).free < 10 * 1024**3:
                raise RuntimeError("Less than 10 GiB free disk before Kira run")
        except (OSError, RuntimeError) as exc:
            # Do not even start the next Kira job if resources did not
            # recover or the previous process still exists. Keep a useful
            # execution report; read-only audit will remain possible.
            records.append({"sector": sector, "action": "preflight_blocked",
                            "detail": str(exc)[:300]})
            break
        log = project / "console_output.log"
        if log.exists() or log.is_symlink():
            raise RuntimeError("Refusing to overwrite saved Kira console log")
        cmd = ["wsl.exe", "--cd", str(project), "python3", MONITOR,
               "--max-seconds", str(min(MAX_SECTOR_SECONDS, int(remaining))),
               "--warn-gib", str(SWAP_WARN), "--stop-gib", str(SWAP_STOP),
               "--interval", str(INTERVAL_SECONDS),
               "--ram-warn-gib", str(RAM_WARN),
               "--ram-stop-gib", str(RAM_STOP)]
        print(f"START SECTOR {sector}: {project}", flush=True)
        with log.open("x", encoding="utf-8") as stream:
            job = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT)
        after = status_one(run_id, item)
        recorded = {
            "sector": sector, "action": "executed", "wsl_exit": job.returncode,
            "state": after["state"], "preflight_resources": safety,
            "resources": previous.read_resource_peaks(project),
            "monitor_result": after.get("monitor_result")
        }
        records.append(recorded)
        print("FINISHED " + json.dumps(recorded, ensure_ascii=False), flush=True)
        if (job.returncode == 0
            and after["state"] == "completed_local_retained"):
            continue
        if (job.returncode == 125 and
            after["state"] in ("guard_stopped_ram_stop", "guard_stopped_swap_stop")):
            # A new independent sector may be attempted only if the next
            # preflight confirms recovery. This is not scientific PASS.
            print(f"GUARD STOP sector {sector}: preserving; other sectors independent",
                  flush=True)
            continue
        # Non-resource failures and target-set changes require human review.
        print("UNEXPECTED FAILURE: stopping all later sectors", flush=True)
        break
    success = (len(records) == len(items) and all(
        x.get("action") == "reused_saved_master_list" or
        (x.get("action") == "executed" and x.get("wsl_exit") == 0 and
         x.get("state") == "completed_local_retained")
        for x in records))
    partial = (len(records) == len(items) and not success and all(
        x.get("action") in ("reused_saved_master_list",
                            "guard_stop_preserved_no_rerun") or
        (x.get("action") == "executed" and
         (x.get("state") == "completed_local_retained" or
          x.get("state") in ("guard_stopped_ram_stop", "guard_stopped_swap_stop")))
        for x in records))
    return {
        "status": ("VP05_NON202_ALL_LOCAL_RETAINED_206_234_OPEN" if success else
                   "VP05_NON202_PARTIAL_WITH_GUARD_STOPS" if partial else
                   "VP05_NON202_HALTED_REVIEW_REQUIRED"),
        "run_id": run_id, "records": records,
        "sector206_234_remain_unresolved": True,
        "global_stage2_closure_proven": False,
        "promotion_ready_created": False,
        "original_projects_overwritten": False
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "prepare", "audit", "run"))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--acknowledge", default="")
    parser.add_argument("--max-total-seconds", type=int, default=MAX_TOTAL_SECONDS)
    args = parser.parse_args()
    if args.mode in ("plan", "audit"):
        result = audit(args.run_id)
    elif args.mode == "prepare":
        result = prepare(args.run_id)
    else:
        result = run(args.run_id, args.acknowledge, args.max_total_seconds)
    print(TAG + json.dumps(result, ensure_ascii=False), flush=True)
    if args.mode == "run" and result["status"] != "VP05_NON202_ALL_LOCAL_RETAINED_206_234_OPEN":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
