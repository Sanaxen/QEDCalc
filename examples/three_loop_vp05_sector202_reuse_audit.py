"""Read-only VP05 sector202 evidence reuse and seven-sector frontier audit.

No Kira execution, project preparation, checkpoint mutation or promotion.
Step93 proves one pinned Target B identity only, not A/C or any Stage-2
one-axis closure. Original guard-stopped 206/234 projects are immutable.
"""
from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path

from examples import three_loop_vp05_stage2_step93_gap_audit as gap
from examples import three_loop_vp05_stage2_non202_batch as no202
from examples import three_loop_vp05_stage2_continuation_batch as continuation
from examples import three_loop_vp05_stage2_residual_forensics as forensic
from examples import three_loop_vp05_sector202_target_exact_reduction as exact

TAG = "VP05_SECTOR202_REUSE_READ_ONLY_AUDIT "
EXPECTED_FRONTIER = {202: 3, 203: 4, 206: 1, 207: 4, 234: 2, 238: 5, 239: 4}
EXPECTED_NON202 = 19
EXPECTED_NON202_CANDIDATES = 40
BLOCKED = (206, 234)


def sha256_regular(path: Path) -> str:
    """Hash original bytes with bounded memory; refuse symlink or non-file."""
    if not stat.S_ISREG(path.lstat().st_mode):
        raise RuntimeError("Missing, linked or non-regular protected file: " + str(path))
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_audit(archive: dict) -> dict:
    """Match exact-source evidence to the *already post-audited* Step93 archive."""
    expected = archive.get("source_and_evidence_sha256")
    if not isinstance(expected, dict):
        raise RuntimeError("Step93 archive source hash map missing")
    saved = {
        "original_source_rows.json.gz": exact.SOURCE,
        "original_exact_support_checkpoint.json": exact.CHECKPOINT,
        "original_source_provenance_certificate.json": exact.CERT,
    }
    result = {}
    for name, path in saved.items():
        match = expected.get(name)
        if not isinstance(match, str) or len(match) != 64:
            raise RuntimeError("Missing Step93 protected hash for " + name)
        observed = sha256_regular(path)
        if observed != match:
            raise RuntimeError("Original Step93 exact-source bytes changed: " + name)
        result[name] = {"path": str(path), "sha256": observed,
                        "matches_formal_archive": True}
    return {
        "sha256_pinned_original_inputs": result,
        "original_ibp_rows_in_step93_source_dataset": 2241,
        "step93_original_ibp_multipliers": 389,
        "proof_scope": "single Target B original-source QQ(z,d) identity",
        "equivalence_to_new_r7s5d3_local_Kira_system": "not_established",
        "source_input_immutable": True,
    }


def inspect_blocked(sector: int, target_set: list[str]) -> dict:
    """Reuse SHA-checked next01 input and guard records, inspect bounded logs."""
    if sector not in BLOCKED:
        raise ValueError("Only protected guard-stopped parent sectors allowed")
    item = {"sector": sector, "targets": target_set,
            "effective_seed": "r8s5d3"}
    saved = continuation.status_one("next01", item)
    monitor = saved.get("monitor_result") or {}
    if (saved.get("state") != "finished_needs_review"
        or monitor.get("reason") != "ram_stop"
        or monitor.get("kira_returncode") != -15
        or monitor.get("success") is not False):
        raise RuntimeError("Protected sector guard-stop evidence changed: " + str(sector))
    directory = continuation.pilot_dir("next01", sector)
    profile = forensic.project_profile(
        directory, expected_targets=target_set,
        mandatory_name=continuation.MANDATORY,
        preferred_name=continuation.PREFERRED)
    if (profile["mandatory_input_set_matches_expected"] is not True
        or profile["preferred_input_set_matches_expected"] is not True):
        raise RuntimeError("Protected parent-sector input no longer matches: " + str(sector))
    progress = [log["last_sector_progress"] for log in profile["log_files"]
                if log.get("last_sector_progress")]
    metric = continuation.read_resource_peaks(directory)
    return {
        "sector": sector,
        "candidate_count": len(target_set),
        "project": str(directory),
        "state": "ram_guard_stopped_not_master_proof",
        "returncode": monitor["kira_returncode"],
        "reason": monitor["reason"],
        "last_logged_recursive_sector": progress[-1] if progress else None,
        "saved_system_file_count": profile["metadata"]["system_equations"]["count"],
        "saved_master_file_present": (
            profile["metadata"]["masters"]["exists"]
            or profile["metadata"]["masters_final"]["exists"]),
        "resources": metric,
        "candidate_master_retention_verified": False,
        "project_preserved_without_restarting": True,
    }


def reconcile(manifest: dict, archived: dict, no202_report: dict,
              source: dict, blocked: list[dict], seed202: dict) -> dict:
    """Pure, conservative evidence classification; never creates closure."""
    values = manifest.get("candidate_masters")
    if (manifest.get("family") != "VP05_full"
        or manifest.get("candidate_master_count") != 63
        or not isinstance(values, list) or len(values) != 63
        or len(set(values)) != 63):
        raise RuntimeError("Canonical VP05 candidate manifest changed")
    groups: dict[int, list[str]] = {}
    for value in values:
        index = gap.indices(value)
        if index is None:
            raise RuntimeError("Invalid VP05 candidate integral: " + str(value))
        groups.setdefault(gap.sector(index), []).append(value)
    frontier = {s: len(v) for s, v in groups.items() if (s & 202) == 202}
    if (frontier != EXPECTED_FRONTIER or len(groups) != 26
        or len(values) - sum(frontier.values()) != EXPECTED_NON202_CANDIDATES
        or len(groups) - len(frontier) != EXPECTED_NON202):
        raise RuntimeError("Canonical 202 inclusion partition changed")
    sector202_targets = {gap.indices(v) for v in groups[202]}
    if sector202_targets != set(gap.TARGETS):
        raise RuntimeError("Canonical three sector202 targets A/B/C changed")
    if (archived.get("status") !=
            "FORMAL_STEP93_SECTOR202_TARGET_B_INDEPENDENT_EXACT_PROOF"
        or archived.get("target_b_proven_within_pinned_source") is not True
        or archived.get("entire_vp05_family_proven") is not False):
        raise RuntimeError("Archived Step93 scope changed")
    if (no202_report.get("status") != "VP05_NON202_SAVED_AUDIT_READ_ONLY"
        or no202_report.get("run_id") != "no202a"
        or no202_report.get("verified_local_sectors") != 6
        or no202_report.get("selected_candidate_integrals") != 23
        or no202_report.get("guard_stopped_sectors") != []
        or len(no202_report.get("sector_rows", [])) != 6
        or any(r.get("state") != "completed_local_retained"
               or r.get("candidate_retained") is not True
               for r in no202_report["sector_rows"])):
        raise RuntimeError("Six saved no202a passes no longer independently verified")
    if (len(blocked) != 2
        or {r.get("sector") for r in blocked} != set(BLOCKED)
        or any(r.get("state") != "ram_guard_stopped_not_master_proof"
               or r.get("candidate_master_retention_verified") is not False
               for r in blocked)):
        raise RuntimeError("Stopped parent project status no longer preserved")
    if (not isinstance(source.get("sha256_pinned_original_inputs"), dict)
        or len(source["sha256_pinned_original_inputs"]) != 3
        or any(r.get("matches_formal_archive") is not True
               for r in source["sha256_pinned_original_inputs"].values())):
        raise RuntimeError("Source integrity review incomplete")
    if (seed202.get("candidate_count") != 3 or
        set(seed202.get("targets", [])) != set(groups[202])
        or seed202.get("sector") != 202):
        raise RuntimeError("r8s6d2 source inventory has changed")
    labels = []
    for name, target in zip(("A", "B", "C"), gap.TARGETS):
        labels.append({
            "target": name,
            "exponents": list(target),
            "canonical_candidate": True,
            "step93_pinned_source_exact_identity_proven": name == "B",
            "r8s5d3_local_master_retained": False,
            "needs_new_same_seed_evidence": True,
            "note": ("Exact Step93 identity only; not a full sector or seed proof"
                     if name == "B" else
                     "No Step93 exact identity for this target; seek separate evidence"),
        })
    return {
        "status": "VP05_SECTOR202_EVIDENCE_REUSED_FRONTIER_OPEN",
        "family": "VP05_full", "stage2_baseline": "r8s3d0",
        "current_one_axis_seed": "r8s5d3",
        "canonical_candidate_masters": len(values),
        "local_master_retention_previously_verified": {
            "sector_groups": EXPECTED_NON202,
            "candidate_masters": EXPECTED_NON202_CANDIDATES,
            "kind": "local initiate-only saved master inventories, not IBP closure"},
        "remaining_sector_groups": [
            {"sector": sec, "candidate_count": len(groups[sec]),
             "targets": groups[sec], "includes_sector202": True,
             "blocked_guard_stop": sec in BLOCKED}
            for sec in sorted(frontier)],
        "sector202_exact_target_obligations": labels,
        "sector202_local_requested_boundary": "r8s5d3",
        "sector202_local_effective_boundary": "r7s5d3",
        "sector202_effective_boundary_reason": "four positive propagators; r=min(8,4+3)",
        "sector202_standard_r8s6d2_existing_inventory": {
            "project_exists": seed202.get("project_exists"),
            "matching_local_master_inventory": seed202.get("matching_local_master_inventory"),
            "restricted_audit_match": seed202.get("restricted_exact_sector_audit_match"),
            "classification": seed202.get("classification")},
        "source": source, "guard_stopped_parents": blocked,
        "sector202_all_three_targets_proven": False,
        "parent_sector206_234_closure_proven": False,
        "r8s5d3_standard_seed_closure_proven": False,
        "r8s6d2_standard_seed_closure_proven": False,
        "global_63_master_basis_proven": False,
        "promotion_ready_created": False,
        "proposed_next_action": (
            "Review exact source-to-r7s5d3 envelope/codec compatibility for A/B/C; "
            "only then consider one isolated guarded sector202 r7s5d3 diagnostic, "
            "90min, WSL RAM 22GiB and swap 8GiB sampled stops. "
            "Never restart preserved 206/234."),
        "kira_executed": False, "files_modified": False,
    }


def inspect() -> dict:
    # no202.audit re-reads saved Step93 post-audit and all predecessor pinned
    # inputs and stops; it never prepares or executes a Kira project.
    finished = no202.audit("no202a")
    candidate = gap.read(gap.AUDIT / (
        f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"))
    archive_path = gap.ARCHIVE / "formal_manifest.json"
    if sha256_regular(archive_path) != gap.EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("Step93 manifest digest differs from accepted archive")
    archive = gap.read(archive_path)
    source = source_audit(archive)
    groups: dict[int, list[str]] = {}
    for value in candidate.get("candidate_masters", []):
        index = gap.indices(value)
        if index is None:
            raise RuntimeError("Malformed standard candidate")
        groups.setdefault(gap.sector(index), []).append(value)
    parents = [inspect_blocked(sec, groups.get(sec, [])) for sec in BLOCKED]
    # This is the *other*, still unverified, independent standard seed.
    from examples import three_loop_vp05_stage2_sector_inventory as inventory
    standard = inventory.analyze_sector(inventory.SEEDS[0], 202, groups.get(202, []))
    return reconcile(candidate, archive, finished, source, parents, standard)


def main() -> None:
    print(TAG + json.dumps(inspect(), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
