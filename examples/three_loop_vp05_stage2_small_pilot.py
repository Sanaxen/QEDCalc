"""VP05 Stage-2: isolated, guarded single-sector pilot for r8s5d3 / sector 73.

Default mode is a read-only plan. --prepare creates ONLY a new exclusive
pilot directory; original standard/sector-local Kira projects and proof
archives are never cleaned or overwritten. --check and --audit are read-only.
The separate BAT requires explicit acknowledgement to launch the existing
WSL monitor with a 30-minute and 8-GiB swap ceiling.
This pilot is NOT a full 63-master family-closure certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from examples import three_loop_vp05_stage2_sector_inventory as inventory
from examples.three_loop_master_basis_candidate_sector_closure import _groups
from examples.three_loop_master_basis_candidate_closure import _read_integrals
from three_loop.master_basis_api import Seed, build_family_spec, export_kira_project, find_or_infer_masters

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
SEED = Seed(8, 5, 3)
SECTOR = 73
MANDATORY = "mandatory_candidate_sector_closure_targets.txt"
PREFERRED = "preferred_candidate_sector_masters.txt"
MONITOR = "scripts/sector203_monitored_kira.py"
PLAN_TAG = "VP05_STAGE2_PILOT "
ACK = "EXECUTE_ISOLATED_R8S5D3_SECTOR73"
FILES = ("jobs.yaml", "config/integralfamilies.yaml",
         "config/kinematics.yaml", MANDATORY, PREFERRED,
         "sector203_monitored_kira.py", "qedcalc_master_basis_manifest.json")


def pilot_dir(run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", run_id):
        raise ValueError("run-id must use 1..32 ASCII letters, digits, underscore or dash")
    return OUTPUT / ("vp05_stage2_pilot_r8s5d3_sec73_" + run_id)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parameters() -> dict:
    """Validate pinned current Stage-2 gap and return the single exact target."""
    stage = inventory.inspect()
    if (stage["status"] != "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY"
        or stage["canonical_candidate_masters"] != 63
        or stage["canonical_candidate_sectors"] != 26
        or not stage["step93_target_b_original_source_proof_verified"]
        or stage["unverified_standard_boundaries"] != ["r8s6d2", "r8s5d3"]):
        raise RuntimeError("Canonical Stage-2/Step93 prerequisites changed")
    matching = [x for x in stage["boundary_inventory"][SEED.tag]["sector_rows"]
                if x["sector"] == SECTOR]
    if len(matching) != 1 or matching[0]["candidate_count"] != 1:
        raise RuntimeError("Unexpected sector73 candidate list")
    row = matching[0]
    if row["project_exists"] or row["restricted_exact_sector_audit_match"] or row["matching_local_master_inventory"]:
        raise RuntimeError("A matching standard sector73 result already exists; pilot unnecessary")
    if row["targets"] != ["VP05_full[1,0,0,1,0,0,1,0,0,0,0,0]"]:
        raise RuntimeError("Sector73 target differs from pinned 63-candidate Stage-2 inventory")
    # Exact-sector dot limit: r <= number of positive lines + d.
    npositive = SECTOR.bit_count()
    effective = Seed(min(SEED.r, npositive + SEED.d), SEED.s, SEED.d)
    if npositive != 3 or effective.tag != "r6s5d3":
        raise RuntimeError("Unexpected exact-sector effective envelope")
    return {"target": row["targets"][0], "effective_seed": effective,
            "requested_seed": SEED.tag, "sector": SECTOR,
            "positive_lines": npositive}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def stable_manifest(project: Path, data: dict) -> dict:
    """Refuse altered generated inputs and unexpected runtime directories."""
    if not project.is_dir() or project.is_symlink():
        raise RuntimeError("Pilot directory absent or linked")
    if (data.get("status") != "VP05_ISOLATED_PILOT_PREPARED"
        or data.get("run_id") != project.name.removeprefix("vp05_stage2_pilot_r8s5d3_sec73_")
        or data.get("family") != "VP05_full" or data.get("sector") != SECTOR
        or data.get("requested_seed") != SEED.tag
        or data.get("effective_seed") != "r6s5d3"
        or set(data.get("input_sha256", {})) != set(FILES)):
        raise RuntimeError("Pilot manifest scope mismatch")
    for filename, expected in data["input_sha256"].items():
        path = project / filename
        if not path.is_file() or path.is_symlink() or sha(path) != expected:
            raise RuntimeError("Pilot input changed: " + filename)
    required = [data["target"]]
    if _read_integrals(project / MANDATORY, "VP05_full") != required:
        raise RuntimeError("Mandatory candidate list changed")
    if _read_integrals(project / PREFERRED, "VP05_full") != required:
        raise RuntimeError("Preferred master list changed")
    return {"input_hashes_verified": True, "target": data["target"],
            "requested_seed": SEED.tag, "effective_seed": "r6s5d3",
            "scientific_closure_proven": False}


def plan(run_id: str) -> dict:
    data = parameters()
    project = pilot_dir(run_id)
    return {
        "status": "VP05_PILOT_PLAN_ONLY_NO_KIRA",
        "run_id": run_id, "project": str(project),
        "destination_absent": not project.exists() and not project.is_symlink(),
        "family": "VP05_full", "candidate_sector": SECTOR,
        "target": data["target"], "effective_seed": data["effective_seed"].tag,
        "requested_boundary_seed": data["requested_seed"],
        "why": "single candidate in first physical sector; non-destructive s/d-boundary pilot",
        "monitor_policy": {"max_seconds": 1800, "swap_warn_gib": 4,
                           "swap_stop_gib": 8, "interval_seconds": 5,
                           "concurrent_kira_processes": 1},
        "full_stage2_closure_proven": False,
        "kira_executed": False, "files_modified": False,
    }


def prepare(run_id: str) -> dict:
    info = plan(run_id)
    if not info["destination_absent"]:
        raise FileExistsError("Refusing to overwrite existing pilot: " + info["project"])
    project = pilot_dir(run_id)
    spec = build_family_spec("VP05_full")
    if spec.baseline_seed.tag != "r8s3d0":
        raise RuntimeError("Canonical VP05 baseline changed")
    source_monitor = ROOT / MONITOR
    if not source_monitor.is_file() or source_monitor.is_symlink():
        raise FileNotFoundError("Verified repo monitor script missing")
    # mkdir(exist_ok=False) ensures the destination is owned by this run.
    project.mkdir(parents=False, exist_ok=False)
    export_kira_project(spec, project, seed=Seed(6, 5, 3), solver="masters",
                        mandatory_file=MANDATORY, preferred_masters_file=PREFERRED,
                        reduce_sectors=[SECTOR], top_level_sectors=[SECTOR],
                        clean=False)
    target = info["target"]
    for filename in (MANDATORY, PREFERRED):
        (project / filename).write_text(target + "\n", encoding="utf-8", newline="\n")
    shutil.copyfile(source_monitor, project / "sector203_monitored_kira.py")
    data = {
        "status": "VP05_ISOLATED_PILOT_PREPARED",
        "run_id": run_id, "family": "VP05_full",
        "requested_seed": SEED.tag, "effective_seed": "r6s5d3",
        "sector": SECTOR, "target": target,
        "input_sha256": {name: sha(project / name) for name in FILES},
        "no_existing_project_modified": True,
        "does_not_establish_63_master_closure": True,
    }
    (project / "isolated_pilot_manifest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    stable_manifest(project, data)
    return {"status": "VP05_PILOT_PREPARE_PASS_NO_KIRA",
            "project": str(project), "run_id": run_id,
            "effective_seed": "r6s5d3", "target": target,
            "kira_executed": False, "standard_output_modified": False}


def check(run_id: str) -> dict:
    project = pilot_dir(run_id)
    data = read(project / "isolated_pilot_manifest.json")
    report = stable_manifest(project, data)
    for name in ("monitored_kira.log", "monitored_metrics.jsonl", "monitored_exit.json"):
        if (project / name).exists():
            raise RuntimeError("Pilot already started; run --audit, never restart in-place")
    for subdir in ("tmp", "results", "sectormappings"):
        if (project / subdir).exists():
            raise RuntimeError("Pilot has unexpected runtime files: " + subdir)
    return {"status": "VP05_PILOT_EXECUTION_PREFLIGHT_PASS_NO_KIRA",
            "project": str(project), **report}


def audit(run_id: str) -> dict:
    project = pilot_dir(run_id)
    data = read(project / "isolated_pilot_manifest.json")
    stable_manifest(project, data)
    exit_path = project / "monitored_exit.json"
    if not exit_path.is_file() or exit_path.is_symlink():
        return {"status": "VP05_PILOT_NOT_COMPLETED", "project": str(project),
                "full_stage2_closure_proven": False}
    result = read(exit_path)
    success = result.get("success") is True and result.get("reason") == "kira_exit" and result.get("kira_returncode") == 0
    present = []
    source = None
    if success:
        try:
            source, present, _ = find_or_infer_masters(
                project, "VP05_full", mandatory_targets=[data["target"]])
        except (OSError, ValueError, RuntimeError):
            pass
    target_retained = success and data["target"] in set(present)
    return {
        "status": ("VP05_PILOT_SECTOR73_MASTER_RETAINED_PENDING_CROSS_SECTOR_REVIEW"
                   if target_retained else "VP05_PILOT_INCOMPLETE_OR_TARGET_NOT_RETAINED"),
        "project": str(project), "monitor_result": result,
        "candidate_retained_in_local_master_list": target_retained,
        "master_count": len(present), "master_source": str(source) if source else None,
        "full_stage2_closure_proven": False, "promotion_ready_generated": False,
        "files_modified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", choices=("plan", "prepare", "check", "audit"), default="plan")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    fn = {"plan": plan, "prepare": prepare, "check": check, "audit": audit}[args.mode]
    print(PLAN_TAG + json.dumps(fn(args.run_id), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
