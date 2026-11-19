"""Read-only VP05 Stage-2 per-sector evidence inventory for the two blocked seeds.

Classify *existing* restricted-equivalent audits and sector-local Kira master
inventories without executing Kira or manufacturing a generic closure PASS.
Passing a sector-level diagnostic never replaces the independent 63-candidate
one-axis closure and never changes the canonical family registry.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from examples import three_loop_vp05_stage2_step93_gap_audit as gap
from examples.three_loop_master_basis_candidate_sector_closure import (
    _groups, _project, _restricted_equivalent_audit, _reusable_project,
    MANDATORY_NAME, PREFERRED_NAME,
)
from three_loop.master_basis_api import Seed, find_or_infer_masters

TAG = "VP05_STAGE2_SECTOR_EVIDENCE_INVENTORY "
FAMILY = "VP05_full"
BASELINE = Seed(8, 3, 0)
SEEDS = (Seed(8, 6, 2), Seed(8, 5, 3))


def category(restricted: bool, inventory_valid: bool, project_exists: bool,
             invalid_or_missing: bool) -> str:
    if restricted:
        return "restricted_equivalent_audit_candidate_for_review"
    if inventory_valid:
        return "matching_local_master_inventory_needs_closure_audit"
    if project_exists:
        return "existing_project_requires_forensics"
    if invalid_or_missing:
        return "no_matching_verified_sector_evidence"
    return "no_matching_verified_sector_evidence"


def analyze_sector(seed: Seed, sector: int, targets: list[str]) -> dict:
    project = _project(FAMILY, BASELINE, seed, sector)
    restricted, restricted_note = _restricted_equivalent_audit(
        FAMILY, BASELINE, seed, sector, targets)
    project_exists = project.is_dir()
    matching_master_inventory = False
    master_count = None
    master_source = None
    missing_masters = None
    project_note = "project not present"
    input_copies = {
        "mandatory_exists": (project / MANDATORY_NAME).is_file(),
        "preferred_exists": (project / PREFERRED_NAME).is_file(),
    }
    if project_exists:
        # Read the exact mandatory/preferred input lists before trusting a
        # masters file. The existing helper does NOT itself certify retention.
        reusable, project_note = _reusable_project(project, FAMILY, targets)
        if reusable:
            try:
                master_path, masters, source_mode = find_or_infer_masters(
                    project, FAMILY, mandatory_targets=targets)
                missing_masters = sorted(set(targets) - set(masters))
                master_count = len(masters)
                master_source = str(master_path)
                matching_master_inventory = len(missing_masters) == 0
                project_note = (
                    f"matched candidate input lists; master source mode={source_mode}; "
                    f"missing targets={len(missing_masters)}; "
                    "no new Kira or exact coefficient verification"
                )
            except (OSError, ValueError, RuntimeError) as exc:
                project_note = "could not safely read Kira candidate master inventory: " + str(exc)[:350]
    return {
        "sector": sector,
        "candidate_count": len(targets),
        "targets": targets,
        "test_seed": seed.tag,
        "project": str(project),
        "project_exists": project_exists,
        "input_copies": input_copies,
        "restricted_exact_sector_audit_match": bool(restricted),
        "restricted_audit_note": restricted_note,
        "matching_local_master_inventory": matching_master_inventory,
        "local_master_count": master_count,
        "local_masters_path": master_source,
        "local_missing_candidates": missing_masters,
        "local_project_note": project_note,
        "classification": category(
            bool(restricted), matching_master_inventory, project_exists, True),
        "whole_family_closure_proven_by_this_entry": False,
        "safe_to_auto_promote": False,
    }


def inspect():
    stage = gap.inspect()
    if stage["status"] != "VP05_STAGE2_BOUNDARY_GAPS_REMAIN":
        raise RuntimeError("Expected incomplete VP05 Stage-2; re-review changed Stage-2 status")
    if stage["step93_target_b"]["formal_archive_verified"] is not True:
        raise RuntimeError("Protected Step93 original-source proof archive failed audit")
    if stage["canonical_candidate_count"] != 63:
        raise RuntimeError("Expected exactly 63 master candidates")
    if stage["unresolved_standard_seed_closures"] != [s.tag for s in SEEDS]:
        raise RuntimeError("Unexpected remaining boundary seeds; re-review standard closure")
    manifest_path = gap.AUDIT / f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    manifest = gap.read(manifest_path)
    candidates = manifest["candidate_masters"]
    if len(candidates) != 63 or len(set(candidates)) != 63:
        raise RuntimeError("Duplicate or incorrect candidate inventory")
    groups = _groups(candidates)
    if (len(groups) != 26
        or sorted(groups) != stage["canonical_candidate_sectors"]
        or len(groups.get(202, [])) != 3
        or sum(map(len, groups.values())) != 63):
        raise RuntimeError("Standard candidate sector inventory unexpectedly changed")
    results = {}
    for seed in SEEDS:
        rows = [analyze_sector(seed, sector, targets)
                for sector, targets in groups.items()]
        counts = Counter(row["classification"] for row in rows)
        results[seed.tag] = {
            "sector_count": len(rows),
            "candidate_count": sum(row["candidate_count"] for row in rows),
            "classification_counts": dict(sorted(counts.items())),
            "restricted_review_sector_ids": [r["sector"] for r in rows
                if r["restricted_exact_sector_audit_match"]],
            "local_master_inventory_sector_ids": [r["sector"] for r in rows
                if r["matching_local_master_inventory"]],
            "requiring_further_evidence_sector_ids": [r["sector"] for r in rows
                if not r["restricted_exact_sector_audit_match"]
                and not r["matching_local_master_inventory"]],
            "sector_rows": rows,
            "formal_standard_seed_closure_pass": False,
        }
    return {
        "status": "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY",
        "family": FAMILY,
        "canonical_candidate_masters": 63,
        "canonical_candidate_sectors": len(groups),
        "baseline_seed": BASELINE.tag,
        "candidate_envelope": gap.CANDIDATE_SEED,
        "unverified_standard_boundaries": [s.tag for s in SEEDS],
        "step93_target_b_original_source_proof_verified": True,
        "boundary_inventory": results,
        "operational_notes": [
            "Restricted-equivalent audits match exact-sector candidate targets, not global 63-master closure",
            "A Kira master-list inventory is not an independent exact closure certificate",
            "Inspect any incomplete saved projects and exact restricted evidence before planning new sector runs",
            "No full Stage-2 run/resume, Step93 re-promotion, or registry edit authorized",
        ],
        "promote_or_update_registry_allowed": False,
        "kira_executed": False,
        "files_modified": False,
    }


def main():
    print(TAG + json.dumps(inspect(), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
