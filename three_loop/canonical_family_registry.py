"""Executable registry overlay for proven three-loop canonical integral families.

The structural classifier remains conservative.  A diagram is promoted only
from an executable algebraic witness.  Q01/Q41 are re-proven through the Q01
family mapper; Q02/Q45 are re-proven through the deduplicating family bootstrap
that detects D4 == D6, builds eight unique physical denominators plus four
quadratic auxiliaries, and requires a full-rank 12-denominator basis.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from three_loop.canonical_family_bootstrap import audit_next_quenched_family
from three_loop.integral_family_classification import Q01_CANONICAL_PROPAGATORS
from three_loop.q01_family_equivalence import audit_q01_family_equivalence

Q01_MASTER_BASIS = "Q01_final60"
Q01_CANONICAL_FAMILY = "Q01_full"
Q02_CANONICAL_FAMILY = "Q02_full"


def _q01_witness_text(witness: dict[str, Any]) -> str:
    return (
        "Exact Q01-family mapper witness: "
        f"reflection={witness['reflection']}; "
        f"loops={witness['loop_momentum_transform']}; "
        f"external={witness['external_momentum_transform']}; "
        f"physical permutation={witness['physical_propagator_permutation']}; "
        "P1..P12 exact and native ISP bridge exact."
    )


def _q02_witness_text(witness: dict[str, Any]) -> str:
    return (
        "Exact Q02-family deduplicated witness: "
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


def _promote_q02(rows: list[dict[str, Any]], record_by_id: dict[str, dict[str, Any]], errors: list[str]) -> dict[str, Any] | None:
    boot = audit_next_quenched_family(rows, {"Q01", "Q41"})
    if not boot.get("audit_pass"):
        errors.extend(str(item) for item in boot.get("errors", []))
        if not boot.get("errors"):
            errors.append("Q02-family bootstrap audit did not pass")
        return None
    if boot.get("representative") != "Q02" or boot.get("family_candidate_id") != Q02_CANONICAL_FAMILY:
        errors.append(f"unexpected next canonical family bootstrap: {boot.get('representative')} / {boot.get('family_candidate_id')}")
        return None
    if not boot.get("kira_ready"):
        errors.append("Q02_full bootstrap is not Kira-ready")
        return None
    if boot.get("requires_partial_fraction_or_family_split"):
        errors.append("Q02_full unexpectedly requires partial fraction/family split")
        return None
    if boot.get("canonical_denominator_count") != 12 or boot.get("canonical_scalar_product_rank") != 12:
        errors.append(
            "Q02_full canonical basis is not 12-entry full rank: "
            f"count={boot.get('canonical_denominator_count')} rank={boot.get('canonical_scalar_product_rank')}"
        )
        return None
    if boot.get("duplicate_physical_groups") != [[4, 6]]:
        errors.append(f"Q02 duplicate physical structure changed: {boot.get('duplicate_physical_groups')}")
        return None

    for item in boot.get("records", []):
        if item.get("status") != "confirmed_algebraic_equivalence":
            continue
        diagram_id = str(item["diagram_id"])
        witness = item.get("witness")
        rec = record_by_id.get(diagram_id)
        if witness is None or rec is None:
            errors.append(f"{diagram_id}: missing Q02 registry witness or global record")
            continue
        if not all(witness.get("propagator_exact_match", [])):
            errors.append(f"{diagram_id}: Q02 P1..P12 witness is not exact")
            continue
        rec.update({
            "classification_status": "confirmed",
            "canonical_integral_family_id": Q02_CANONICAL_FAMILY,
            "canonical_propagator_basis": list(boot["canonical_propagators"]),
            "loop_momentum_transform": dict(witness["loop_momentum_transform"]),
            "external_momentum_transform": dict(witness["external_momentum_transform"]),
            "physical_to_canonical_mapping": list(witness["physical_to_canonical_mapping"]),
            "sign_normalization_transform": (
                "Topology physical denominators are mapped exactly to the deduplicated Q02 basis; "
                "duplicate physical D4 and D6 share one canonical denominator and their powers add."
            ),
            "symmetry_representative": "Q02",
            "existing_kira_family_reusable": True,
            "requires_new_auxiliary_basis": True,
            "master_basis_id": None,
            "canonical_equivalence_witness": witness,
            "evidence": _q02_witness_text(witness),
        })
    return boot


def apply_confirmed_family_registry(rows: list[dict[str, Any]], audit: dict[str, Any]) -> list[str]:
    """Promote executable, algebraically proven canonical-family mappings."""
    errors: list[str] = []
    records = audit.get("records", [])
    record_by_id = {str(rec.get("diagram_id")): rec for rec in records}

    q01 = _promote_q01(rows, record_by_id, errors)
    q02 = _promote_q02(rows, record_by_id, errors)

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
    if q02 is not None:
        confirmed_q02 = [
            str(rec["diagram_id"])
            for rec in q02.get("records", [])
            if rec.get("status") == "confirmed_algebraic_equivalence"
        ]
        registry[Q02_CANONICAL_FAMILY] = {
            "representative": "Q02",
            "confirmed_diagrams": confirmed_q02,
            "candidate_diagrams": list(q02.get("candidate_ids", [])),
            "master_basis_id": None,
            "kira_reusable": True,
            "kira_ready": bool(q02.get("kira_ready")),
            "duplicate_physical_groups": q02.get("duplicate_physical_groups"),
            "raw_physical_to_unique_mapping": q02.get("raw_physical_to_unique_mapping"),
            "auxiliary_names": q02.get("auxiliary_names"),
            "canonical_denominator_count": q02.get("canonical_denominator_count"),
            "canonical_scalar_product_rank": q02.get("canonical_scalar_product_rank"),
            "equivalence_audit_pass": bool(q02.get("audit_pass")),
        }
    audit["canonical_registry"] = registry
    return errors
