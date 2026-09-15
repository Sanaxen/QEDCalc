"""Executable registry overlay for proven three-loop canonical integral families.

The structural classifier remains conservative. A diagram is promoted only
from executable algebraic witnesses. Q01/Q41 are re-proven through the Q01
family mapper. Later quenched families are re-proven from the generic bootstrap
and, where required, an explicit existing-family reuse audit.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from examples.three_loop_q03_existing_family_reuse_audit import audit_q03_existing_family_reuse
from three_loop.canonical_family_bootstrap import audit_next_quenched_family
from three_loop.existing_family_reuse import audit_existing_family_reuse
from three_loop.integral_family_classification import Q01_CANONICAL_PROPAGATORS
from three_loop.q01_family_equivalence import audit_q01_family_equivalence

Q01_MASTER_BASIS = "Q01_final60"
Q01_CANONICAL_FAMILY = "Q01_full"
Q02_CANONICAL_FAMILY = "Q02_full"
Q03_CANONICAL_FAMILY = "Q03_full"
Q04_CANONICAL_FAMILY = "Q04_full"
Q05_CANONICAL_FAMILY = "Q05_full"
Q06_CANONICAL_FAMILY = "Q06_full"


def _q01_witness_text(witness: dict[str, Any]) -> str:
    return (
        "Exact Q01-family mapper witness: "
        f"reflection={witness['reflection']}; "
        f"loops={witness['loop_momentum_transform']}; "
        f"external={witness['external_momentum_transform']}; "
        f"physical permutation={witness['physical_propagator_permutation']}; "
        "P1..P12 exact and native ISP bridge exact."
    )


def _generic_witness_text(family_id: str, witness: dict[str, Any]) -> str:
    return (
        f"Exact {family_id} witness: "
        f"reflection={witness['reflection']}; "
        f"loops={witness['loop_momentum_transform']}; "
        f"external={witness['external_momentum_transform']}; "
        f"physical->canonical={witness['physical_to_canonical_mapping']}; "
        "all canonical P1..P12 exact."
    )


def _promote_q01(rows: list[dict[str, Any]], record_by_id: dict[str, dict[str, Any]], errors: list[str]) -> dict[str, Any] | None:
    eq = audit_q01_family_equivalence(rows)
    if not eq.get("audit_pass"):
        errors.extend(str(item) for item in eq.get("errors", []))
        if not eq.get("errors"):
            errors.append("Q01-family equivalence mapper did not pass")
        return None

    witness_by_id = {
        str(rec["diagram_id"]): rec.get("witness")
        for rec in eq.get("records", [])
        if rec.get("status") == "confirmed" and rec.get("witness") is not None
    }
    for diagram_id in eq.get("confirmed_ids", []):
        diagram_id = str(diagram_id)
        witness = witness_by_id.get(diagram_id)
        rec = record_by_id.get(diagram_id)
        if witness is None or rec is None:
            errors.append(f"{diagram_id}: missing Q01 registry witness or global record")
            continue
        if not all(witness.get("propagator_exact_match", [])):
            errors.append(f"{diagram_id}: Q01 P1..P12 witness is not exact")
            continue
        if not all(witness.get("isp_bridge_exact_match", [])):
            errors.append(f"{diagram_id}: Q01 ISP bridge witness is not exact")
            continue
        rec.update({
            "classification_status": "confirmed",
            "canonical_integral_family_id": Q01_CANONICAL_FAMILY,
            "canonical_propagator_basis": list(Q01_CANONICAL_PROPAGATORS),
            "loop_momentum_transform": dict(witness["loop_momentum_transform"]),
            "external_momentum_transform": dict(witness["external_momentum_transform"]),
            "sign_normalization_transform": (
                "Exact denominator equality after the recorded reflection/momentum map; "
                "Q01 Kira physical sign convention and ISP bridge are inherited unchanged."
            ),
            "symmetry_representative": "Q01",
            "existing_kira_family_reusable": True,
            "requires_new_auxiliary_basis": False,
            "master_basis_id": Q01_MASTER_BASIS,
            "canonical_equivalence_witness": witness,
            "evidence": _q01_witness_text(witness),
        })
    return eq


def _promote_bootstrap_family(
    rows: list[dict[str, Any]],
    record_by_id: dict[str, dict[str, Any]],
    errors: list[str],
    confirmed_ids: set[str],
    expected_representative: str,
    family_id: str,
    expected_duplicates: list[list[int]],
    reuse_representatives: list[str] | None = None,
    q03_legacy_reuse_audit: bool = False,
) -> dict[str, Any] | None:
    boot = audit_next_quenched_family(rows, confirmed_ids)
    if not boot.get("audit_pass"):
        errors.extend(str(item) for item in boot.get("errors", []))
        if not boot.get("errors"):
            errors.append(f"{family_id} bootstrap audit did not pass")
        return None
    if boot.get("representative") != expected_representative or boot.get("family_candidate_id") != family_id:
        errors.append(
            f"unexpected canonical family bootstrap for {family_id}: "
            f"{boot.get('representative')} / {boot.get('family_candidate_id')}"
        )
        return None
    if not boot.get("kira_ready"):
        errors.append(f"{family_id} bootstrap is not Kira-ready")
        return None
    if boot.get("requires_partial_fraction_or_family_split"):
        errors.append(f"{family_id} unexpectedly requires partial fraction/family split")
        return None
    if boot.get("canonical_denominator_count") != 12 or boot.get("canonical_scalar_product_rank") != 12:
        errors.append(
            f"{family_id} canonical basis is not 12-entry full rank: "
            f"count={boot.get('canonical_denominator_count')} rank={boot.get('canonical_scalar_product_rank')}"
        )
        return None
    if boot.get("duplicate_physical_groups") != expected_duplicates:
        errors.append(
            f"{family_id} duplicate physical structure changed: "
            f"{boot.get('duplicate_physical_groups')}"
        )
        return None

    if q03_legacy_reuse_audit:
        reuse = audit_q03_existing_family_reuse(rows)
        if not reuse.get("audit_pass") or not reuse.get("new_family_required_under_current_scope"):
            errors.extend(str(item) for item in reuse.get("errors", []))
            if not reuse.get("errors"):
                errors.append(f"{family_id} existing-family reuse audit did not prove a new family")
            return None
    elif reuse_representatives:
        reuse = audit_existing_family_reuse(
            rows,
            list(boot.get("candidate_ids", [])),
            reuse_representatives,
        )
        if not reuse.get("audit_pass") or not reuse.get("new_family_required_under_current_scope"):
            errors.extend(str(item) for item in reuse.get("errors", []))
            if not reuse.get("errors"):
                errors.append(f"{family_id} existing-family reuse audit did not prove a new family")
            return None

    for item in boot.get("records", []):
        if item.get("status") != "confirmed_algebraic_equivalence":
            continue
        diagram_id = str(item["diagram_id"])
        witness = item.get("witness")
        rec = record_by_id.get(diagram_id)
        if witness is None or rec is None:
            errors.append(f"{diagram_id}: missing {family_id} registry witness or global record")
            continue
        if not all(witness.get("propagator_exact_match", [])):
            errors.append(f"{diagram_id}: {family_id} P1..P12 witness is not exact")
            continue
        rec.update({
            "classification_status": "confirmed",
            "canonical_integral_family_id": family_id,
            "canonical_propagator_basis": list(boot["canonical_propagators"]),
            "loop_momentum_transform": dict(witness["loop_momentum_transform"]),
            "external_momentum_transform": dict(witness["external_momentum_transform"]),
            "physical_to_canonical_mapping": list(witness["physical_to_canonical_mapping"]),
            "sign_normalization_transform": (
                "Topology physical denominators map exactly to the canonical basis; "
                "duplicate physical powers are aggregated only when the recorded mapping repeats an index."
            ),
            "symmetry_representative": expected_representative,
            "existing_kira_family_reusable": True,
            "requires_new_auxiliary_basis": True,
            "master_basis_id": None,
            "canonical_equivalence_witness": witness,
            "evidence": _generic_witness_text(family_id, witness),
        })
    return boot


def apply_confirmed_family_registry(rows: list[dict[str, Any]], audit: dict[str, Any]) -> list[str]:
    """Promote executable, algebraically proven canonical-family mappings."""
    errors: list[str] = []
    records = audit.get("records", [])
    record_by_id = {str(rec.get("diagram_id")): rec for rec in records}

    q01 = _promote_q01(rows, record_by_id, errors)
    q02 = _promote_bootstrap_family(
        rows, record_by_id, errors,
        {"Q01", "Q41"}, "Q02", Q02_CANONICAL_FAMILY, [[4, 6]],
    )
    q03 = _promote_bootstrap_family(
        rows, record_by_id, errors,
        {"Q01", "Q02", "Q41", "Q45"}, "Q03", Q03_CANONICAL_FAMILY, [],
        q03_legacy_reuse_audit=True,
    )
    q04 = _promote_bootstrap_family(
        rows, record_by_id, errors,
        {"Q01", "Q02", "Q03", "Q41", "Q43", "Q45"},
        "Q04", Q04_CANONICAL_FAMILY, [],
        reuse_representatives=["Q01", "Q02", "Q03"],
    )
    q05 = _promote_bootstrap_family(
        rows, record_by_id, errors,
        {"Q01", "Q02", "Q03", "Q04", "Q41", "Q43", "Q45", "Q46"},
        "Q05", Q05_CANONICAL_FAMILY, [[2, 4]],
        reuse_representatives=["Q01", "Q02", "Q03", "Q04"],
    )
    q06 = _promote_bootstrap_family(
        rows, record_by_id, errors,
        {"Q01", "Q02", "Q03", "Q04", "Q05", "Q41", "Q42", "Q43", "Q45", "Q46"},
        "Q06", Q06_CANONICAL_FAMILY, [],
        reuse_representatives=["Q01", "Q02", "Q03", "Q04", "Q05"],
    )

    counts = Counter(str(rec.get("classification_status")) for rec in records)
    audit["classification_status_counts"] = dict(sorted(counts.items()))
    audit["confirmed_canonical_mapping_count"] = counts.get("confirmed", 0)
    audit["classification_complete"] = counts.get("confirmed", 0) == len(records)

    registry: dict[str, Any] = {}
    if q01 is not None:
        registry[Q01_CANONICAL_FAMILY] = {
            "representative": "Q01",
            "confirmed_diagrams": list(q01.get("confirmed_ids", [])),
            "candidate_diagrams": list(q01.get("candidate_ids", [])),
            "master_basis_id": Q01_MASTER_BASIS,
            "kira_reusable": True,
            "equivalence_audit_pass": True,
        }
    for family_id, boot in (
        (Q02_CANONICAL_FAMILY, q02),
        (Q03_CANONICAL_FAMILY, q03),
        (Q04_CANONICAL_FAMILY, q04),
        (Q05_CANONICAL_FAMILY, q05),
        (Q06_CANONICAL_FAMILY, q06),
    ):
        if boot is None:
            continue
        confirmed = [
            str(rec["diagram_id"])
            for rec in boot.get("records", [])
            if rec.get("status") == "confirmed_algebraic_equivalence"
        ]
        registry[family_id] = {
            "representative": str(boot.get("representative")),
            "confirmed_diagrams": confirmed,
            "candidate_diagrams": list(boot.get("candidate_ids", [])),
            "master_basis_id": None,
            "kira_reusable": True,
            "kira_ready": bool(boot.get("kira_ready")),
            "duplicate_physical_groups": boot.get("duplicate_physical_groups"),
            "raw_physical_to_unique_mapping": boot.get("raw_physical_to_unique_mapping"),
            "auxiliary_names": boot.get("auxiliary_names"),
            "canonical_denominator_count": boot.get("canonical_denominator_count"),
            "canonical_scalar_product_rank": boot.get("canonical_scalar_product_rank"),
            "equivalence_audit_pass": bool(boot.get("audit_pass")),
        }
    audit["canonical_registry"] = registry
    return errors
