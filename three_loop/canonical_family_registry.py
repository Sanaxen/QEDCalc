"""Executable registry overlay for proven three-loop canonical integral families.

The structural classifier intentionally remains conservative.  This module
promotes diagrams only from executable algebraic witnesses.  In particular,
Q41 is promoted to Q01_full only when the Q01-family equivalence mapper again
proves the complete P1..P12 and native-ISP bridge identities at audit time.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from three_loop.integral_family_classification import Q01_CANONICAL_PROPAGATORS
from three_loop.q01_family_equivalence import audit_q01_family_equivalence


Q01_MASTER_BASIS = "Q01_final60"
Q01_CANONICAL_FAMILY = "Q01_full"


def _witness_text(witness: dict[str, Any]) -> str:
    return (
        "Exact Q01-family mapper witness: "
        f"reflection={witness['reflection']}; "
        f"loops={witness['loop_momentum_transform']}; "
        f"external={witness['external_momentum_transform']}; "
        f"physical permutation={witness['physical_propagator_permutation']}; "
        "P1..P12 exact and native ISP bridge exact."
    )


def apply_confirmed_family_registry(
    rows: list[dict[str, Any]],
    audit: dict[str, Any],
) -> list[str]:
    """Promote executable, algebraically proven canonical-family mappings.

    Returns registry-specific errors.  The caller should append these to the
    ordinary global-classification validation errors.
    """
    errors: list[str] = []
    eq = audit_q01_family_equivalence(rows)
    if not eq.get("audit_pass"):
        errors.extend(str(item) for item in eq.get("errors", []))
        if not errors:
            errors.append("Q01-family equivalence mapper did not pass")
        return errors

    witness_by_id = {
        str(rec["diagram_id"]): rec.get("witness")
        for rec in eq.get("records", [])
        if rec.get("status") == "confirmed" and rec.get("witness") is not None
    }

    records = audit.get("records", [])
    record_by_id = {str(rec.get("diagram_id")): rec for rec in records}
    for diagram_id in eq.get("confirmed_ids", []):
        diagram_id = str(diagram_id)
        witness = witness_by_id.get(diagram_id)
        rec = record_by_id.get(diagram_id)
        if witness is None or rec is None:
            errors.append(f"{diagram_id}: missing registry witness or global record")
            continue
        if not all(witness.get("propagator_exact_match", [])):
            errors.append(f"{diagram_id}: P1..P12 witness is not exact")
            continue
        if not all(witness.get("isp_bridge_exact_match", [])):
            errors.append(f"{diagram_id}: ISP bridge witness is not exact")
            continue

        rec.update(
            {
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
                "evidence": _witness_text(witness),
            }
        )

    counts = Counter(str(rec.get("classification_status")) for rec in records)
    audit["classification_status_counts"] = dict(sorted(counts.items()))
    audit["confirmed_canonical_mapping_count"] = counts.get("confirmed", 0)
    audit["classification_complete"] = counts.get("confirmed", 0) == len(records)
    audit["canonical_registry"] = {
        "Q01_full": {
            "representative": "Q01",
            "confirmed_diagrams": list(eq.get("confirmed_ids", [])),
            "candidate_diagrams": list(eq.get("candidate_ids", [])),
            "master_basis_id": Q01_MASTER_BASIS,
            "kira_reusable": True,
            "equivalence_audit_pass": True,
        }
    }
    return errors
