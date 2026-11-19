"""Read-only VP05 sector202 target-A exact-source split feasibility review.

Stop the repeated 3-target Kira recursion. Existing archived Step93 proves
one B identity; the old modular original-row support for A is a *candidate*
to be checked over QQ(z,d), never an exact proof. C is the proposed reference
integral in the candidate A/B equations, not an independently proven master.
No Kira, coefficient reconstruction, source mutation or promotions.
"""
from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path

from examples import three_loop_vp05_stage2_sector202_stop_forensics as stop
from examples import three_loop_vp05_sector202_reuse_audit as reuse
from examples import three_loop_vp05_stage2_step93_gap_audit as gap
from examples import three_loop_vp05_sector202_target_exact_reduction as exact

TAG = "VP05_SECTOR202_SOURCE_SPLIT_AUDIT "
CERTIFICATE = exact.CERT
FORMAL_MANIFEST = gap.ARCHIVE / "formal_manifest.json"
B_PROOF = gap.ARCHIVE / "evidence" / "proof_step93.json"
EXPECTED_ORIGINAL_ROWS = 2678
EXPECTED_SELECTED_UNION = 389
EXPECTED_A_SUPPORT = 339
EXPECTED_B_EXACT_SUPPORT = 389
MAX_JSON_BYTES = 16 * 1024 * 1024


def read_pinned(path: Path, want_sha256: str) -> dict:
    """Bounded SHA-verified read; no symlinks or malformed input."""
    if len(want_sha256) != 64 or any(x not in "0123456789abcdef" for x in want_sha256):
        raise RuntimeError("Invalid pinned source SHA256")
    if not stat.S_ISREG(path.lstat().st_mode):
        raise RuntimeError("Missing/linked or nonregular original evidence: " + str(path))
    if path.stat().st_size > MAX_JSON_BYTES:
        raise RuntimeError("Evidence JSON too large for bounded analysis")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != want_sha256:
        raise RuntimeError("Pinned source SHA256 mismatch: " + str(path))
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON evidence object")
    return value


def ids_for(item: dict, index: int) -> set[int]:
    if (item.get("target_index") != index
        or tuple(item.get("target", ())) != gap.TARGETS[index]
        or item.get("modular_original_replay_verified") is not True):
        raise RuntimeError("Finite-field certificate target identity mismatch")
    values = item.get("support_original_ids")
    if (not isinstance(values, list)
        or not values
        or any(type(x) is not int or x < 0 or x >= EXPECTED_ORIGINAL_ROWS for x in values)
        or len(values) != len(set(values))
        or item.get("nonzero_original_support") != len(values)):
        raise RuntimeError("Invalid original-IBP modular certificate support")
    return set(values)


def reconcile(cert: dict, proof: dict, forensic: dict) -> dict:
    """Classify supported work units; do not turn modular replay into proof."""
    if (forensic.get("status") != "VP05_SECTOR202_RAM_STOP_FORENSICS_READ_ONLY"
        or forensic.get("run_id") != "sec202a"
        or forensic.get("conclusions", {}).get("ram_guard_stop_verified") is not True
        or forensic.get("conclusions", {}).get("no_automatic_retry") is not True):
        raise RuntimeError("Protected sec202a RAM-stop audit missing")
    target_results = cert.get("target_results")
    if (cert.get("status") != "MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF"
        or cert.get("total_original_rows") != EXPECTED_ORIGINAL_ROWS
        or cert.get("exact_target_reduction_proven") is not False
        or not isinstance(target_results, list) or len(target_results) != 2):
        raise RuntimeError("Saved modular provenance certificate scope changed")
    a, b = (ids_for(row, i) for i, row in enumerate(target_results))
    union, common = a | b, a & b
    if (len(a) != EXPECTED_A_SUPPORT or len(union) != EXPECTED_SELECTED_UNION
        or cert.get("union_nonzero_support") != len(union)
        or cert.get("shared_nonzero_support") != len(common)):
        raise RuntimeError("Original modular A/B support inventory changed")
    multipliers = proof.get("source_multipliers")
    if (proof.get("status") != "EXACT_SINGLE_TARGET_PROVEN"
        or proof.get("target") != "B"
        or proof.get("original_source_replay_verified") is not True
        or not isinstance(multipliers, list)
        or len(multipliers) != EXPECTED_B_EXACT_SUPPORT):
        raise RuntimeError("Step93 proof scope or original-source replay changed")
    exact_ids = []
    for pair in multipliers:
        if (not isinstance(pair, list) or len(pair) != 2 or
            type(pair[0]) is not int or pair[0] < 0 or
            pair[0] >= EXPECTED_ORIGINAL_ROWS or
            not isinstance(pair[1], str) or not pair[1]):
            raise RuntimeError("Malformed Step93 original-row multiplier")
        exact_ids.append(pair[0])
    if len(set(exact_ids)) != len(exact_ids):
        raise RuntimeError("Duplicate exact B multiplier")
    return {
        "status": "VP05_SECTOR202_A_EXACT_SOURCE_REVIEW_REQUIRED",
        "family": "VP05_full", "sector": 202,
        "latest_guard_stop": {"project": forensic["project"],
            "elapsed_s": forensic["saved_elapsed_s"],
            "max_ram_gib": forensic["resource_trace"]["max_ram_gib"],
            "last_kira_sector_progress": forensic["last_log_sector_progress"],
            "kira_master_final_available": forensic["saved_project"]["masters_final"]["exists"],
            "stop_at_recursive_equation_selection_suspected": True,
            "internal_solver_phase_exactly_proven": False},
        "original_restricted_kira_source_context": {
            "source_family": "VP05_full",
            "source_equation_rows": EXPECTED_ORIGINAL_ROWS,
            "source_codec": "saved original provisional sector203 ordering=5; do not reuse encoded weights in sec202a",
            "source_to_new_r7s5d3_scope_equivalence_proven": False},
        "original_modular_support": {
            "point": cert.get("point"),
            "target_a": {"row_count": len(a), "source_row_ids": sorted(a),
                         "modular_original_ibp_replay_verified": True,
                         "exact_QQ_z_d_proof": False},
            "target_b": {"row_count": len(b), "source_row_ids": sorted(b),
                         "modular_original_ibp_replay_verified": True},
            "intersection_count": len(common),
            "A_only_count": len(a - b), "B_only_count": len(b - a),
            "union_count": len(union),
            "a_and_b_source_row_subsets_are_modular_not_exact": True},
        "step93_exact_b": {
            "source_multipliers": len(exact_ids),
            "symbolic_QQ_z_d_original_ibp_replay_verified": True,
            "exact_B_support_equal_to_modular_B_support": set(exact_ids) == b,
            "exact_B_support_overlap_with_modular_A": len(set(exact_ids) & a),
            "substitutable_for_A_proof": False},
        "target_obligations": [
            {"target": "A", "exponents": list(gap.TARGETS[0]),
             "proven": False, "recommended_next_work":
             "Independent exact QQ(z,d) A identity reconstruction and original 2241-row export replay; fail closed and checkpoint, not full Kira"},
            {"target": "B", "exponents": list(gap.TARGETS[1]),
             "proven_within_archived_source": True,
             "recommended_next_work": "Reuse immutable Step93 proof as-is; do not recompute"},
            {"target": "C", "exponents": list(gap.TARGETS[2]),
             "proven_master_retained_at_new_boundary": False,
             "recommended_next_work":
             "Review C reference integral and cross-sector basis compatibility independently; no A/B target identity proves C is a master"}],
        "recommended_priority": "single-target A original-source exact audit before any new Kira",
        "requires_new_kira_for_this_read_only_audit": False,
        "sector202_all_three_masters_verified": False,
        "r8s5d3_global_boundary_closure_proven": False,
        "r8s6d2_global_boundary_closure_proven": False,
        "promotion_ready_created": False,
        "kira_executed": False, "files_modified": False,
    }


def inspect() -> dict:
    forensic = stop.inspect("sec202a")  # Reopens complete pinned prior evidence.
    manifest = json.loads(FORMAL_MANIFEST.read_text(encoding="utf-8-sig"))
    hashes = manifest.get("source_and_evidence_sha256")
    if (not isinstance(hashes, dict)
        or reuse.sha256_regular(FORMAL_MANIFEST) != gap.EXPECTED_MANIFEST_SHA256):
        raise RuntimeError("Formal archived Step93 manifest changed")
    cert = read_pinned(CERTIFICATE, hashes["original_source_provenance_certificate.json"])
    proof = read_pinned(B_PROOF, hashes["proof_step93.json"])
    return reconcile(cert, proof, forensic)


def main() -> None:
    print(TAG + json.dumps(inspect(), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
