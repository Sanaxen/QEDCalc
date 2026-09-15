"""Cross-check an unresolved quenched structural class against confirmed families.

The current transform scope is deliberately conservative: open-line reflection
plus signed loop-momentum relabeling.  A negative result in this module does not
exclude a more general affine/GL(Z) loop-momentum equivalence.
"""
from __future__ import annotations

from typing import Any

from three_loop.canonical_family_bootstrap import (
    complete_with_quadratic_auxiliaries,
    deduplicate_exact_denominators,
    find_family_witness,
    q01_reuse_witness,
    topology_physical_denominators,
)

TRANSFORM_SCOPE = "open-line reflection + signed loop-momentum relabeling"


def _bootstrap_reference_basis(reference: dict[str, Any]):
    physical = topology_physical_denominators(reference)
    unique, _, _ = deduplicate_exact_denominators(physical)
    _, aux_vecs, aux_exprs = complete_with_quadratic_auxiliaries(unique)
    return unique, aux_vecs, aux_exprs


def audit_existing_family_reuse(
    rows: list[dict[str, Any]],
    candidate_ids: list[str],
    confirmed_family_representatives: list[str],
) -> dict[str, Any]:
    """Audit one candidate class against all already-confirmed representatives."""
    by_id = {str(row["id"]): row for row in rows}
    if not candidate_ids:
        raise ValueError("candidate_ids must not be empty")

    missing = [did for did in candidate_ids + confirmed_family_representatives if did not in by_id]
    if missing:
        raise ValueError(f"unknown diagram IDs: {missing}")

    reference_data: dict[str, tuple[list[Any], list[dict[str, Any]], list[Any]]] = {}
    for rep_id in confirmed_family_representatives:
        if rep_id == "Q01":
            continue
        reference_data[rep_id] = _bootstrap_reference_basis(by_id[rep_id])

    records: list[dict[str, Any]] = []
    for diagram_id in candidate_ids:
        candidate = by_id[diagram_id]
        reuse: dict[str, Any] = {}
        for rep_id in confirmed_family_representatives:
            family_id = f"{rep_id}_full"
            reference = by_id[rep_id]
            if rep_id == "Q01":
                witness = q01_reuse_witness(candidate, reference)
            else:
                unique, aux_vecs, aux_exprs = reference_data[rep_id]
                witness_obj = find_family_witness(
                    candidate,
                    reference,
                    unique,
                    aux_vecs,
                    aux_exprs,
                )
                witness = witness_obj.to_dict() if witness_obj is not None else None
            reuse[family_id] = witness
        records.append({"diagram_id": diagram_id, "reuse": reuse})

    representative = records[0]
    representative_hits = [family_id for family_id, witness in representative["reuse"].items() if witness is not None]
    errors: list[str] = []
    if representative_hits:
        errors.append(
            f"{candidate_ids[0]} reuses confirmed family/families under current scope: {representative_hits}"
        )

    return {
        "candidate_ids": list(candidate_ids),
        "confirmed_family_representatives": list(confirmed_family_representatives),
        "transform_scope": TRANSFORM_SCOPE,
        "records": records,
        "representative_reuse_hits": representative_hits,
        "new_family_required_under_current_scope": not representative_hits,
        "errors": errors,
        "audit_pass": not errors,
        "interpretation": (
            "A PASS means the candidate representative does not reuse any listed confirmed family "
            "within the explicit current transform scope. It does not exclude a more general "
            "affine/GL(Z) loop-momentum equivalence."
        ),
    }
