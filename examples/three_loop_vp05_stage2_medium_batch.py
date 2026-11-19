"""Protected, resumable six-sector VP05 r8s5d3 medium pilot batch.

Default planning and auditing are read-only. Preparation exclusively creates
new run-id-scoped Kira project folders; execution requires explicit user
acknowledgement and uses a separate RAM/swap-guarded WSL monitor sequentially.

This is a same-seed exact-sector diagnostic, NOT a global 63-master closure
certificate, no promotion-ready, and no canonical registry mutation.
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

from examples import three_loop_vp05_stage2_sector_inventory as inventory
from examples import three_loop_vp05_stage2_small_pilot as first_pilot
from examples import three_loop_vp05_stage2_light_batch as previous_batch
from examples.three_loop_master_basis_candidate_closure import _read_integrals
from three_loop.master_basis_api import Seed, build_family_spec, export_kira_project, find_or_infer_masters

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FAMILY = "VP05_full"
SEED = "r8s5d3"
SECTORS = (201, 228, 117, 118, 199, 204)
ACK = "EXECUTE_VP05_ISOLATED_MEDIUM_BATCH"
MANDATORY = "mandatory_candidate_sector_closure_targets.txt"
PREFERRED = "preferred_candidate_sector_masters.txt"
MONITOR = "vp05_stage2_monitored_kira.py"
FILES = ("jobs.yaml", "config/integralfamilies.yaml", "config/kinematics.yaml",
         "qedcalc_master_basis_manifest.json", MANDATORY, PREFERRED, MONITOR)
MAX_SECTOR_SECONDS = 5400
SWAP_WARN = 4
SWAP_STOP = 8
RAM_WARN = 18
RAM_STOP = 22
INTERVAL = 5
TAG = "VP05_STAGE2_MEDIUM_BATCH "


def pilot_dir(run_id: str, sector: int) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", run_id):
        raise ValueError("Invalid run ID")
    if sector not in SECTORS:
        raise ValueError("Sector not in approved medium pilot list")
    return OUTPUT / f"vp05_stage2_r8s5d3_medium_{run_id}_sec{sector}"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required regular file absent: " + str(path))
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise RuntimeError("Invalid JSON root object")
    return result


def sector_input_scope() -> list[dict]:
    """Gate the batch on current canonical evidence and the successful first pilot."""
    stage = inventory.inspect()
    if (stage.get("status") != "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY"
        or stage.get("canonical_candidate_masters") != 63
        or stage.get("canonical_candidate_sectors") != 26
        or stage.get("step93_target_b_original_source_proof_verified") is not True
        or stage.get("unverified_standard_boundaries") != ["r8s6d2", "r8s5d3"]):
        raise RuntimeError("VP05 canonical Stage-2/Step93 scope has changed")
    first = first_pilot.audit("first01")
    if first.get("status") != "VP05_PILOT_SECTOR73_MASTER_RETAINED_PENDING_CROSS_SECTOR_REVIEW":
        raise RuntimeError("Original isolated sector73 pilot not verified")
    previous = previous_batch.report_all("light01")
    old_rows = previous["sector_rows"]
    if (len(old_rows) != 3
        or [x["sector"] for x in old_rows] != [78, 101, 116]
        or any(x["state"] != "completed_local_retained" or
               x.get("candidate_retained") is not True for x in old_rows)):
        raise RuntimeError("Protected light01 prior three-sector PASS not verified")
    rows = stage["boundary_inventory"][SEED]["sector_rows"]
    selected = []
    for sector in SECTORS:
        hits = [r for r in rows if r["sector"] == sector]
        if len(hits) != 1:
            raise RuntimeError("Candidate sector absent: " + str(sector))
        row = hits[0]
        if row["project_exists"] or row["restricted_exact_sector_audit_match"] or row["matching_local_master_inventory"]:
            raise RuntimeError("Standard sector evidence already exists; do not rerun: " + str(sector))
        if len(row["targets"]) != row["candidate_count"] or len(set(row["targets"])) != row["candidate_count"]:
            raise RuntimeError("Invalid candidate integral list for sector " + str(sector))
        r = min(8, sector.bit_count() + 3)
        if sector.bit_count() not in (4, 5) or r not in (7, 8):
            raise RuntimeError("Unexpected effective r for sector " + str(sector))
        selected.append({"sector": sector, "targets": row["targets"],
                         "effective_seed": f"r{r}s5d3"})
    if [r["candidate_count"] for r in [next(x for x in rows if x["sector"] == s) for s in SECTORS]] != [1, 2, 1, 1, 1, 1]:
        raise RuntimeError("Unexpected Stage-2 target counts")
    return selected


def status_one(run_id: str, item: dict) -> dict:
    sector = item["sector"]
    directory = pilot_dir(run_id, sector)
    report = {"sector": sector, "project": str(directory),
              "effective_seed": item["effective_seed"],
              "target_count": len(item["targets"])}
    if directory.is_symlink():
        raise RuntimeError("Linked isolated pilot project")
    if not directory.exists():
        return {**report, "state": "not_prepared",
                "candidate_retained": False, "global_closure_proven": False}
    data = read(directory / "medium_pilot_manifest.json")
    if (data.get("status") != "VP05_MEDIUM_PILOT_PREPARED"
        or data.get("run_id") != run_id or data.get("sector") != sector
        or data.get("requested_seed") != SEED
        or data.get("effective_seed") != item["effective_seed"]
        or data.get("targets") != item["targets"]
        or set(data.get("input_sha256", {})) != set(FILES)):
        raise RuntimeError("Isolated pilot manifest does not match verified scope")
    for rel, want in data["input_sha256"].items():
        path = directory / rel
        if not path.is_file() or path.is_symlink() or digest(path) != want:
            raise RuntimeError("Pilot input hash mismatch: " + str(path))
    if (_read_integrals(directory / MANDATORY, FAMILY) != item["targets"]
        or _read_integrals(directory / PREFERRED, FAMILY) != item["targets"]):
        raise RuntimeError("Pilot mandatory/preferred target list has changed")
    end = directory / "monitored_exit.json"
    if end.exists():
        result = read(end)
        succeeded = (result.get("success") is True and
                     result.get("reason") == "kira_exit" and
                     result.get("kira_returncode") == 0)
        masters = []
        source = None
        if succeeded:
            try:
                source, masters, mode = find_or_infer_masters(
                    directory, FAMILY, mandatory_targets=item["targets"])
            except (OSError, ValueError, RuntimeError):
                pass
        retained = (succeeded and set(masters) == set(item["targets"]))
        return {**report,
                "state": "completed_local_retained" if retained else "finished_needs_review",
                "candidate_retained": bool(retained),
                "master_source": str(source) if source else None,
                "monitor_result": result, "global_closure_proven": False}
    runtime = any((directory / s).exists()
                  for s in ("monitored_kira.log", "monitored_metrics.jsonl",
                            "console_output.log", "tmp", "results", "sectormappings"))
    return {**report, "state": "interrupted_manual_review" if runtime else "prepared",
            "candidate_retained": False, "global_closure_proven": False}


def read_resource_peaks(project: Path) -> dict:
    path = project / "monitored_metrics.jsonl"
    if not path.is_file() or path.is_symlink():
        return {"metrics_available": False}
    ram = swap = None
    samples = 0
    # At 5s samples, even a 30-minute run has ~360 lines; bounded file size
    # prevents accidentally scanning an enormous corrupted log.
    if path.stat().st_size > 5 * 1024 * 1024:
        return {"metrics_available": False, "reason": "metrics file above review cap"}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            sample = json.loads(line)
            if not isinstance(sample, dict):
                continue
            a, b = sample.get("ram_used_gib"), sample.get("swap_used_gib")
            if isinstance(a, (float, int)):
                ram = max(float(a), ram or 0)
            if isinstance(b, (float, int)):
                swap = max(float(b), swap or 0)
            samples += 1
        except ValueError:
            continue
    return {"metrics_available": samples > 0, "samples": samples,
            "peak_ram_used_gib": ram, "peak_swap_used_gib": swap}


def report_all(run_id: str) -> dict:
    selection = sector_input_scope()
    rows = [status_one(run_id, x) for x in selection]
    for row in rows:
        if row["state"] != "not_prepared":
            row["resources"] = read_resource_peaks(Path(row["project"]))
    previous = read_resource_peaks(OUTPUT / "vp05_stage2_pilot_r8s5d3_sec73_first01")
    light01 = previous_batch.report_all("light01")
    old_peaks = [
        {"sector": x["sector"], "state": x["state"],
         "resources": x.get("resources")} for x in light01["sector_rows"]
    ]
    return {"status": "VP05_MEDIUM_BATCH_REVIEW_ONLY", "run_id": run_id,
            "previous_sector73_metrics": previous,
            "prior_light01_sector_results": old_peaks,
            "sector_rows": rows,
            "candidate_count": sum(len(x["targets"]) for x in selection),
            "max_sector_seconds": MAX_SECTOR_SECONDS,
            "swap_warn_gib": SWAP_WARN, "swap_stop_gib": SWAP_STOP,
            "ram_warn_gib": RAM_WARN, "ram_stop_gib": RAM_STOP,
            "concurrent_processes": 1,
            "new_global_closure_proven": False,
            "files_modified": False, "kira_executed": False}


def prepare(run_id: str) -> dict:
    selection = sector_input_scope()
    if any(pilot_dir(run_id, x["sector"]).exists() or
           pilot_dir(run_id, x["sector"]).is_symlink() for x in selection):
        raise FileExistsError("At least one run-id directory already exists; refuse partial overwrite")
    source_monitor = ROOT / "scripts/vp05_stage2_monitored_kira.py"
    if not source_monitor.is_file() or source_monitor.is_symlink():
        raise RuntimeError("Monitor source missing")
    if not OUTPUT.is_dir():
        raise RuntimeError("Expected output directory absent")
    spec = build_family_spec(FAMILY)
    if spec.baseline_seed.tag != "r8s3d0":
        raise RuntimeError("Unexpected VP05 baseline")
    paths = []
    for item in selection:
        dest = pilot_dir(run_id, item["sector"])
        dest.mkdir(exist_ok=False)
        export_kira_project(spec, dest, seed=Seed(min(8, item["sector"].bit_count() + 3), 5, 3), solver="masters",
                            mandatory_file=MANDATORY, preferred_masters_file=PREFERRED,
                            reduce_sectors=[item["sector"]],
                            top_level_sectors=[item["sector"]], clean=False)
        for name in (MANDATORY, PREFERRED):
            (dest / name).write_text("\n".join(item["targets"]) + "\n",
                                     encoding="utf-8", newline="\n")
        shutil.copyfile(source_monitor, dest / MONITOR)
        manifest = {
            "status": "VP05_MEDIUM_PILOT_PREPARED", "run_id": run_id,
            "family": FAMILY, "sector": item["sector"],
            "requested_seed": SEED, "effective_seed": item["effective_seed"],
            "targets": item["targets"], "input_sha256": {
                name: digest(dest / name) for name in FILES},
            "original_projects_unchanged": True,
            "family_closure_proven": False,
        }
        (dest / "medium_pilot_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths.append(str(dest))
    results = [status_one(run_id, item) for item in selection]
    if any(r["state"] != "prepared" for r in results):
        raise RuntimeError("Prepared new projects failed post-preparation audit")
    return {"status": "VP05_MEDIUM_BATCH_PREPARE_PASS_NO_KIRA",
            "run_id": run_id, "projects": paths, "kira_executed": False,
            "protected_inputs_unchanged": True, "global_closure_proven": False}


def _no_other_kira() -> None:
    check = subprocess.run(
        ["wsl.exe", "--exec", "sh", "-lc",
         "command -v pgrep >/dev/null 2>&1 || exit 126; pgrep -x kira >/dev/null && exit 99; exit 0"],
        capture_output=True, text=True)
    if check.returncode != 0:
        raise RuntimeError("WSL Kira process or monitor preflight issue; refusing parallel run: "
                           + str(check.returncode))


def execute(run_id: str, acknowledge: str, max_total_seconds: int) -> dict:
    if acknowledge != ACK:
        raise ValueError("Explicit execution acknowledgement missing")
    if os.name != "nt":
        raise RuntimeError("Kira execution must be initiated on Windows/WSL")
    if not (30 <= max_total_seconds <= 43200):
        raise ValueError("max-total-seconds must be between 30 and 43200")
    selection = sector_input_scope()
    statuses = [status_one(run_id, x) for x in selection]
    if any(r["state"] not in ("prepared", "completed_local_retained")
           for r in statuses):
        raise RuntimeError("Pilot requires manual review or missing preparation; refusing execution")
    done = []
    started = time.monotonic()
    for item, state in zip(selection, statuses):
        if state["state"] == "completed_local_retained":
            done.append({"sector": item["sector"], "action": "reused_existing_pass"})
            continue
        remain = max_total_seconds - (time.monotonic() - started)
        if remain < 30:
            done.append({"sector": item["sector"], "action": "time_budget_exhausted"})
            break
        _no_other_kira()
        project = pilot_dir(run_id, item["sector"])
        seconds = min(MAX_SECTOR_SECONDS, int(remain))
        cmd = ["wsl.exe", "--cd", str(project), "python3", MONITOR,
               "--max-seconds", str(seconds), "--warn-gib", str(SWAP_WARN),
               "--stop-gib", str(SWAP_STOP), "--interval", str(INTERVAL),
               "--ram-warn-gib", str(RAM_WARN), "--ram-stop-gib", str(RAM_STOP)]
        log = project / "console_output.log"
        if log.exists() or log.is_symlink():
            raise RuntimeError("Refusing to overwrite pilot console log: " + str(log))
        with log.open("x", encoding="utf-8") as out:
            result = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT)
        after = status_one(run_id, item)
        done.append({"sector": item["sector"], "action": "executed",
                     "wsl_returncode": result.returncode, "state": after["state"],
                     "resources": read_resource_peaks(project)})
        # Fail closed on resource stop, unexpected master selection, or signal.
        if result.returncode != 0 or after["state"] != "completed_local_retained":
            break
    completed = len(done) == len(selection) and all(
        x.get("action") == "reused_existing_pass" or
        (x.get("action") == "executed" and
         x.get("wsl_returncode") == 0 and
         x.get("state") == "completed_local_retained") for x in done)
    return {"status": ("VP05_MEDIUM_BATCH_ALL_LOCAL_PILOTS_RETAINED"
                        if completed else "VP05_MEDIUM_BATCH_HALTED_REVIEW_REQUIRED"),
            "run_id": run_id,
            "sectors": done, "global_closure_proven": False,
            "promotion_ready_created": False, "original_projects_modified": False}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("plan", "prepare", "audit", "execute"))
    p.add_argument("--run-id", required=True)
    p.add_argument("--acknowledge", default="")
    p.add_argument("--max-total-seconds", type=int, default=43200)
    args = p.parse_args()
    if args.mode in ("plan", "audit"):
        data = report_all(args.run_id)
    elif args.mode == "prepare":
        data = prepare(args.run_id)
    else:
        data = execute(args.run_id, args.acknowledge, args.max_total_seconds)
    print(TAG + json.dumps(data, ensure_ascii=False), flush=True)
    if args.mode == "execute" and data["status"] != "VP05_MEDIUM_BATCH_ALL_LOCAL_PILOTS_RETAINED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
