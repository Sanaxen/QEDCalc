"""Read-only reconciliation of VP05 sector202 Target B Step93 with standard Stage-2.

A verified single-target IBP identity does NOT certify the 63-master candidate
basis under the three required one-axis boundary seeds. This script reads
existing evidence only: it never launches Kira, updates checkpoints, writes a
promotion-ready file, or alters canonical_family_registry.py.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "output" / "three_loop_integral_family_audit"
PREFIX = "three_loop_vp05_full_masters_r8s3d0"
CANDIDATE_SEED = "r8s5d2"
SEEDS = ("r9s5d2", "r8s6d2", "r8s5d3")
ARCHIVE = AUDIT / "vp05_sector202_B_step93_formal_artifact"
EXPECTED_MANIFEST_SHA256 = "1021d9deb7d06811d2986e38e52f54db55a6770e2bb3faa6e86f0ab0e6e9c1a1"
TARGETS = (
    (0,1,0,1,-1,-1,1,1,0,0,0,0),  # sector202 A
    (0,1,0,1,-2,0,1,1,0,0,0,0),   # sector202 B (proven)
    (0,1,0,1,0,0,1,1,0,0,0,0),     # sector202 C
)
TAG = "VP05_STEP93_TO_STAGE2_GAP_AUDIT "


def read(path: Path) -> dict:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object: " + str(path))
    return value


def indices(value):
    if not isinstance(value, str) or not value.startswith("VP05_full[") or not value.endswith("]"):
        return None
    try:
        parts = value[len("VP05_full["):-1].split(",")
        if len(parts) != 12 or any(str(int(p)) != p.strip() for p in parts):
            return None
        return tuple(int(x) for x in parts)
    except ValueError:
        return None


def sector(row):
    return sum(1 << i for i, power in enumerate(row) if power > 0)


def target_coverage(items):
    entries = [indices(x) for x in items]
    return {name: target in entries for name, target in zip(("A", "B", "C"), TARGETS)}


def review(manifest, closure, local, promotion, proof):
    """Return a scope-limited diagnostic, not a promotion decision."""
    declared = manifest.get("candidate_masters")
    if manifest and (manifest.get("family") != "VP05_full"
                     or manifest.get("candidate_master_count") != 63
                     or not isinstance(declared, list) or len(declared) != 63
                     or any(indices(x) is None for x in declared)
                     or len({indices(x) for x in declared}) != 63):
        raise RuntimeError("Invalid or stale canonical 63-master manifest")
    candidates = declared or []
    closure_targets = manifest.get("closure_targets", [])
    if not isinstance(closure_targets, list):
        raise RuntimeError("Invalid standard closure target inventory")
    if closure and closure.get("family") not in (None, "VP05_full"):
        raise RuntimeError("Standard closure audit family mismatch")
    if closure and closure.get("candidate_master_count") not in (None, 63):
        raise RuntimeError("Standard closure candidate count mismatch")
    if (manifest and closure and closure.get("closure_target_count") is not None
        and closure.get("closure_target_count") != len(closure_targets)):
        raise RuntimeError("Standard closure target-count mismatch")
    standard = {}
    boundaries = closure.get("boundary_rows", [])
    if not isinstance(boundaries, list):
        raise RuntimeError("Invalid saved standard boundary rows")
    for seed in SEEDS:
        found = [row for row in boundaries if isinstance(row, dict) and row.get("seed") == seed]
        row = found[0] if len(found) == 1 else {}
        standard[seed] = {
            "audit_row_present": len(found) == 1,
            "stable": row.get("stable") is True and not row.get("error"),
            "error": row.get("error"),
            "master_count": row.get("master_count"),
        }
    complete = (bool(manifest) and bool(closure)
                and closure.get("audit_pass") is True
                and closure.get("stable_under_one_axis_extensions") is True
                and not closure.get("errors")
                and len(boundaries) == 3
                and all(item["stable"] for item in standard.values()))
    local_rows = {}
    for seed in SEEDS:
        data = local.get(seed, {})
        sector_rows = data.get("sector_rows", [])
        if not isinstance(sector_rows, list):
            raise RuntimeError("Invalid local sector rows for " + seed)
        bad_sectors = [row.get("sector") for row in sector_rows
                       if not isinstance(row, dict) or row.get("stable") is not True]
        matches = (data.get("family") == "VP05_full"
                   and data.get("test_seed") == seed
                   and data.get("candidate_master_count") == 63
                   and data.get("retained_candidate_count") == 63
                   and data.get("audit_pass") is True
                   and data.get("stable_under_sector_local_closure") is True
                   and data.get("missing_candidate_masters") == []
                   and data.get("errors") == []
                   and isinstance(data.get("sector_count"), int)
                   and len(sector_rows) == data["sector_count"]
                   and not bad_sectors)
        local_rows[seed] = {
            "audit_present": bool(data),
            "candidate63_sector_local_pass": bool(matches),
            "candidate_count": data.get("candidate_master_count"),
            "sector_count": data.get("sector_count"),
            "failed_or_missing_sectors": bad_sectors,
            "errors": data.get("errors"),
        }
    ready = (promotion.get("family") == "VP05_full"
             and promotion.get("audit_pass") is True)
    status = ("VP05_STEP93_PROOF_ARCHIVE_NOT_VERIFIED" if not proof
              else "VP05_STAGE2_BOUNDARY_GAPS_REMAIN" if not complete
              else "VP05_STAGE2_BOUNDARIES_REPORTED_PASS_REVIEW_REQUIRED")
    return {
        "status": status,
        "family": "VP05_full",
        "stage2_baseline": "r8s3d0",
        "candidate_envelope": CANDIDATE_SEED,
        "canonical_candidate_count": len(candidates),
        "canonical_candidate_sectors": sorted({sector(indices(x)) for x in candidates}),
        "canonical_sector202_candidate_count": sum(sector(indices(x)) == 202 for x in candidates),
        "missing_evidence": [name for name, present in (
            ("step93_formal_archive", proof),
            ("standard_candidate_manifest", bool(manifest)),
            ("standard_candidate_closure_audit", bool(closure)),
            ("standard_promotion_ready", bool(promotion))) if not present],
        "step93_target_b": {
            "formal_archive_verified": proof,
            "original_source_multipliers": 389 if proof else None,
            "exponents": list(TARGETS[1]),
            "sector": sector(TARGETS[1]),
            "in_63_candidate_masters": target_coverage(candidates)["B"],
            "in_standard_closure_targets": target_coverage(closure_targets)["B"],
            "other_sector202_targets_in_closure": {
                k: v for k, v in target_coverage(closure_targets).items() if k != "B"
            },
            "eligible_to_replace_any_full_boundary_closure": False,
            "can_be_reused_as_a_sha_pinned_single_target_identity": proof,
        },
        "standard_boundaries": standard,
        "sector_local_boundary_diagnostics": local_rows,
        "unresolved_standard_seed_closures": [seed for seed in SEEDS if not standard[seed]["stable"]],
        "standard_63_candidate_closure_saved_audit_pass": complete,
        "standard_promotion_ready_present": bool(promotion),
        "standard_promotion_ready_saved_audit_pass": ready,
        "promotion_ready_generated_by_this_script": False,
        "family_registry_changed": False,
        "safe_next_action": (
            "Review the saved standard Stage-2 closure and sector-local audits; "
            "identify the exact unverified seeds/sectors before any new Kira run. "
            "No automatic proof promotion."
        ),
        "kira_executed": False,
        "files_modified": False,
    }


def verified_archive():
    from examples.three_loop_vp05_sector202_target_b_step93_formal_promotion import post_audit
    manifest_path = ARCHIVE / "formal_manifest.json"
    if not manifest_path.exists():
        return False
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if digest != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("Step93 formal archive manifest differs from user's verified SHA256")
    verified = post_audit()
    if (verified.get("status") != "B_STEP93_FORMAL_ARTIFACT_POST_AUDIT_PASS"
        or verified.get("steps") != 93
        or verified.get("original_ibp_multipliers") != 389
        or verified.get("pivot_coefficient_keys_verified") != 393
        or verified.get("original_source_keys_verified") != 537
        or verified.get("target_b_proven_within_pinned_source") is not True):
        raise RuntimeError("Step93 independent saved-proof validation not PASS")
    return True


def inspect():
    manifest = read(AUDIT / f"{PREFIX}_candidate_{CANDIDATE_SEED}_closure_manifest.json")
    closure = read(AUDIT / f"{PREFIX}_candidate_{CANDIDATE_SEED}_closure_audit.json")
    local = {
        seed: read(AUDIT / f"{PREFIX}_candidate_sector_closure_{seed}_audit.json")
        for seed in SEEDS
    }
    promotion = read(AUDIT / "three_loop_vp05_full_promotion_ready.json")
    return review(manifest, closure, local, promotion, verified_archive())


def main():
    print(TAG + json.dumps(inspect(), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
