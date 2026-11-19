"""Non-destructive VP05 Stage-2 residual project forensics.

Stage-2 formal obligations belong to the full candidate closure, not this
read-only filesystem inventory. Never infer a reduction from a log, a Kira DB,
a partial SYSTEM file, or a sector-local initiate-only master list.

The original sector projects and Stage-2 checkpoints are never touched.
Only a bounded tail of each Kira log is read, and SYSTEM .gz files are only
listed/stat'ed, not decompressed or modified.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FAMILY = "VP05_full"
SEEDS = ("r8s6d2", "r8s5d3")
LOG_TAIL_BYTES = 262144
MAX_LOGS = 16
MAX_SYSTEM_NAMES = 16
MAX_SMALL_INPUT_BYTES = 1024 * 1024
TAG = "VP05_STAGE2_RESIDUAL_FORENSICS "
PROGRESS = re.compile(
    r"Generate equations for topology\s+VP05_full,\s*sector\s+(\d+)\s*"
    r"\((\d+)\s+of\s+(\d+)\)", re.I,
)
RESOURCE_TERMS = (
    "out of memory", "oom-kill", "oom killer", "bad_alloc",
    "cannot allocate memory", "killed", "swap", "no space left",
    "memory exhausted", "memoryerror", "timeout", "timed out",
)
ERROR_TERMS = (
    "error:", "failed:", "fatal", "traceback", "segmentation fault",
    "terminate called", "abort", "exited with code",
)


def regular_file(path: Path) -> bool:
    """Refuse symlink evidence and avoid following redirected paths."""
    try:
        mode = path.lstat().st_mode
    except OSError:
        return False
    return stat.S_ISREG(mode)


def safe_dir(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except OSError:
        return False
    return stat.S_ISDIR(mode)


def stat_file(path: Path, *, hash_small: bool = False) -> dict:
    if not regular_file(path):
        return {"exists": False, "size_bytes": None}
    size = path.stat().st_size
    result = {"exists": True, "size_bytes": size}
    if hash_small and size <= MAX_SMALL_INPUT_BYTES:
        result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def bounded_log_tail(path: Path) -> dict:
    """Read at most LOG_TAIL_BYTES, without scanning massive Kira logs."""
    info = stat_file(path)
    if not info["exists"]:
        return {**info, "last_sector_progress": None, "completed_marker_in_tail": False}
    size = info["size_bytes"]
    with path.open("rb") as stream:
        stream.seek(max(0, size - LOG_TAIL_BYTES))
        tail = stream.read(LOG_TAIL_BYTES).decode("utf-8", errors="replace")
    lines = tail.splitlines()
    matches = []
    for line in lines:
        match = PROGRESS.search(line)
        if match:
            matches.append({"sector": int(match[1]), "index": int(match[2]),
                            "of": int(match[3]), "line": line.strip()[:280]})
    low = tail.lower()
    hints = [line.strip()[:280] for line in lines if any(k in line.lower()
                                                            for k in (*RESOURCE_TERMS, *ERROR_TERMS))]
    return {**info, "tail_bytes_read": min(size, LOG_TAIL_BYTES),
            "last_sector_progress": matches[-1] if matches else None,
            "completed_marker_in_tail": "total time:" in low,
            "issue_hints_in_tail": hints[-8:],
            "last_lines": [line.strip()[:280] for line in lines[-5:]],
            "warning": "Text hints are not a verified OOM/exit diagnosis"}


def _logs(project: Path) -> list[Path]:
    found = []
    for parent in (project, project / "logs", project / "results"):
        if not safe_dir(parent):
            continue
        for path in parent.iterdir():
            if (regular_file(path) and
                (path.suffix.lower() in (".log", ".out", ".err") or
                 path.name.lower() in ("kira.log", "run.log"))):
                found.append(path)
    # Deterministic order; never follow symlinks or recurse into unknown trees.
    return sorted(found, key=lambda p: str(p).lower())


def _systems(project: Path) -> dict:
    directory = project / "tmp" / FAMILY
    if not safe_dir(directory):
        return {"count": 0, "total_size_bytes": 0, "examples": []}
    files = sorted((p for p in directory.glob("SYSTEM_VP05_full_*.gz")
                    if regular_file(p)), key=lambda p: p.name)
    return {"count": len(files),
            "total_size_bytes": sum(p.stat().st_size for p in files),
            "examples": [{"file": p.name, "bytes": p.stat().st_size}
                         for p in files[:MAX_SYSTEM_NAMES]],
            "name_list_truncated": len(files) > MAX_SYSTEM_NAMES}


def _integrals(path: Path) -> list[str] | None:
    """Parse small mandatory input only; do not read huge/linked files."""
    if not regular_file(path) or path.stat().st_size > MAX_SMALL_INPUT_BYTES:
        return None
    raw = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"VP05_full\s*\[\s*(-?\d+(?:\s*,\s*-?\d+){11})\s*\]")
    return ["VP05_full[" + ",".join(map(str.strip, m.split(","))) + "]"
            for m in pattern.findall(raw)]


def project_profile(project: Path, *, expected_targets: list[str] | None,
                    mandatory_name: str, preferred_name: str | None = None) -> dict:
    if project.is_symlink():
        raise RuntimeError("Refusing linked project path: " + str(project))
    present = safe_dir(project)
    mandatory = project / mandatory_name
    preferred = project / preferred_name if preferred_name else None
    observed = _integrals(mandatory) if present else None
    preferred_observed = _integrals(preferred) if preferred is not None and present else None
    # The 63-item global manifest may order targets differently from the
    # per-sector grouping. Use multiplicity-sensitive set-equivalence here,
    # and report ordering separately; neither test is a closure certificate.
    mandatory_match = (sorted(observed) == sorted(expected_targets)
                       if observed is not None and expected_targets is not None else None)
    preferred_match = (sorted(preferred_observed) == sorted(expected_targets)
                       if preferred_observed is not None and expected_targets is not None else None)
    log_paths = _logs(project) if present else []
    logs = [{"file": str(p.relative_to(project)), **bounded_log_tail(p)}
            for p in log_paths[:MAX_LOGS]]
    systems = _systems(project) if present else {"count": 0, "total_size_bytes": 0, "examples": []}
    master = project / "results" / FAMILY / "masters"
    master_final = project / "results" / FAMILY / "masters.final"
    meta = {
        "kira_db": stat_file(project / "results" / "kira.db"),
        "masters": stat_file(master), "masters_final": stat_file(master_final),
        "system_equations": systems,
        "results_dir_present": safe_dir(project / "results"),
        "tmp_dir_present": safe_dir(project / "tmp"),
        "sectormappings_dir_present": safe_dir(project / "sectormappings"),
        "jobs_yaml": stat_file(project / "jobs.yaml", hash_small=True),
        "mandatory_input": stat_file(mandatory, hash_small=True),
        "preferred_input": (stat_file(preferred, hash_small=True) if preferred is not None else None),
    }
    final_marker = any(x["completed_marker_in_tail"] for x in logs)
    # Report evidence only; do not imply the result is valid or reusable.
    if not present:
        finding = "project_missing"
    elif systems["count"]:
        finding = "partial_system_gz_present_requires_exact_source_audit"
    elif meta["masters"]["exists"] or meta["masters_final"]["exists"]:
        finding = "saved_master_file_present_requires_candidate_audit"
    elif logs or meta["kira_db"]["exists"] or meta["tmp_dir_present"]:
        finding = "intermediate_state_present_no_proven_master_list"
    else:
        finding = "prepared_inputs_only_or_no_execution_evidence"
    return {
        "path": str(project), "project_exists": present,
        "mandatory_input_set_matches_expected": mandatory_match,
        "mandatory_input_order_matches_expected": (observed == expected_targets
            if observed is not None and expected_targets is not None else None),
        "preferred_input_set_matches_expected": preferred_match,
        "mandatory_items_parsed": len(observed) if observed is not None else None,
        "preferred_items_parsed": len(preferred_observed) if preferred_observed is not None else None,
        "metadata": meta,
        "log_files": logs, "log_files_truncated": len(log_paths) > MAX_LOGS,
        "any_completion_text_in_log_tail": final_marker,
        "finding": finding,
        "scientific_reduction_proven": False,
    }


def inspect() -> dict:
    # Delay importing the stage inspector so offline filesystem tests need no
    # live Kira work or exact proof archive. In the real app, its full Step93
    # immutable formal archive check must pass first.
    from examples import three_loop_vp05_stage2_sector_inventory as inventory

    stage = inventory.inspect()
    if (stage.get("status") != "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY"
        or stage.get("canonical_candidate_masters") != 63
        or stage.get("canonical_candidate_sectors") != 26
        or stage.get("step93_target_b_original_source_proof_verified") is not True
        or stage.get("unverified_standard_boundaries") != list(SEEDS)):
        raise RuntimeError("VP05 Stage-2 / Step93 saved evidence scope changed; review before triage")

    out = {}
    for seed in SEEDS:
        saved = stage["boundary_inventory"][seed]
        rows = saved["sector_rows"]
        if len(rows) != 26 or sum(r["candidate_count"] for r in rows) != 63:
            raise RuntimeError("Unexpected saved sector candidate inventory for " + seed)
        needs = [r for r in rows if (not r["restricted_exact_sector_audit_match"] and
                not r["matching_local_master_inventory"])]
        profiles = []
        for row in needs:
            sector = row["sector"]
            project = OUTPUT / (
                f"kira_vp05_full_masters_candidate_sector_closure_r8s3d0_{seed}_sec{sector}")
            if Path(row["project"]).resolve() != project.resolve():
                raise RuntimeError("Saved sector project path differs for sector " + str(sector))
            profile = project_profile(
                project, expected_targets=row["targets"],
                mandatory_name="mandatory_candidate_sector_closure_targets.txt",
                preferred_name="preferred_candidate_sector_masters.txt")
            profiles.append({"sector": sector, "candidate_count": row["candidate_count"],
                             "prior_classification": row["classification"], **profile})
        full = OUTPUT / f"kira_vp05_full_masters_candidate_closure_r8s3d0_{seed}"
        # The original monolithic project is separate from all 26 sector-local
        # projects; verify mandatory target copies but NEVER overwrite either.
        expected_full = [target for r in rows for target in r["targets"]]
        original = project_profile(
            full, expected_targets=expected_full,
            mandatory_name="mandatory_candidate_closure_targets.txt")
        out[seed] = {
            "total_candidate_sectors": 26,
            "sector_profiles_examined": len(profiles),
            "profiles": profiles,
            "original_monolithic_closure_project": original,
            "other_sectors_with_preexisting_evidence": 26 - len(profiles),
            "newly_certified_sector_closure": False,
        }
    return {"status": "VP05_STAGE2_RESIDUAL_PROJECT_FORENSICS_READ_ONLY",
            "family": FAMILY, "baseline_seed": "r8s3d0",
            "candidate_envelope": "r8s5d2", "candidate_masters": 63,
            "target_b_step93_exact_archive_verified": True,
            "boundaries": out, "whole_family_closure_proven": False,
            "safe_next_action": "Review partial project logs, available SYSTEM equations and input match before defining isolated resource-guarded completion; preserve all originals",
            "kira_executed": False, "files_modified": False,
            "promotion_ready_created": False, "canonical_registry_changed": False}


def main() -> None:
    print(TAG + json.dumps(inspect(), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
