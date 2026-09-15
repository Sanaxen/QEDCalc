"""Executable canonical-family registry overlay.

Quenched three-loop families are discovered and re-proven automatically from
exact algebraic witnesses.  This removes the former Q02/Q03/... hard-coded
promotion chain while preserving the dedicated stronger Q01 mapper checks.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from three_loop.integral_family_classification import Q01_CANONICAL_PROPAGATORS
from three_loop.quenched_family_autodiscovery import audit_quenched_family_autodiscovery

Q01_MASTER_BASIS = "Q01_final60"
Q01_CANONICAL_FAMILY = "Q01_full"


def _evidence(family_id: str, witness: dict[str, Any], mode: str) -> str:
    if family_id == Q01_CANONICAL_FAMILY:
        return (
            "Exact Q01-family mapper witness: "
            f"reflection={witness['reflection']}; "
            f"loops={witness['loop_momentum_transform']}; "
            f"external={witness['external_momentum_transform']}; "
            f"physical permutation={witness['physical_propagator_permutation']}; "
            "P1..P12 exact and native ISP bridge exact."
        )
    return (
        f"Exact autodiscovery witness ({mode}) for {family_id}: "
        f"reflection={witness['reflection']}; "
        f"loops={witness['loop_momentum_transform']}; "
        f"external={witness['external_momentum_transform']}; "
        f"physical->canonical={witness['physical_to_canonical_mapping']}; "
        "canonical P1..P12 exact."
    )


def apply_confirmed_family_registry(rows: list[dict[str, Any]], audit: dict[str, Any]) -> list[str]:
    """Overlay all automatically proven quenched canonical-family mappings."""
    errors: list[str] = []
    auto = audit_quenched_family_autodiscovery(rows)
    if not auto.get("audit_pass"):
        errors.extend(str(item) for item in auto.get("errors", []))
        if not auto.get("errors"):
            errors.append("quenched canonical-family autodiscovery failed")
        audit["canonical_registry"] = {}
        return errors

    records = audit.get("records", [])
    record_by_id = {str(rec.get("diagram_id")): rec for rec in records}
    registry = auto.get("canonical_registry", {})

    for auto_rec in auto.get("records", []):
        diagram_id = str(auto_rec.get("diagram_id"))
        family_id = str(auto_rec.get("canonical_integral_family_id"))
        representative = str(auto_rec.get("representative"))
        mode = str(auto_rec.get("promotion_mode"))
        witness = auto_rec.get("witness")
        rec = record_by_id.get(diagram_id)
        family = registry.get(family_id)

        if rec is None:
            errors.append(f"{diagram_id}: missing global classification record")
            continue
        if family is None:
            errors.append(f"{diagram_id}: missing autodiscovery registry family {family_id}")
            continue
        if witness is None:
            errors.append(f"{diagram_id}: missing autodiscovery witness")
            continue

        if family_id == Q01_CANONICAL_FAMILY:
            if not all(witness.get("propagator_exact_match", [])):
                errors.append(f"{diagram_id}: Q01 P1..P12 witness is not exact")
                continue
            if not all(witness.get("isp_bridge_exact_match", [])):
                errors.append(f"{diagram_id}: Q01 ISP bridge witness is not exact")
                continue
            canonical_basis = list(Q01_CANONICAL_PROPAGATORS)
            physical_mapping = None
            requires_new_aux = False
            master_basis = Q01_MASTER_BASIS
            sign_text = (
                "Exact denominator equality after the recorded reflection/momentum map; "
                "Q01 Kira physical sign convention and ISP bridge are inherited unchanged."
            )
        else:
            exact = witness.get("propagator_exact_match", [])
            if not exact or not all(exact):
                errors.append(f"{diagram_id}: {family_id} P1..P12 witness is not exact")
                continue
            canonical_basis = list(family.get("canonical_propagators", []))
            if len(canonical_basis) != 12:
                errors.append(
                    f"{diagram_id}: {family_id} canonical basis has {len(canonical_basis)} entries, expected 12"
                )
                continue
            physical_mapping = list(witness["physical_to_canonical_mapping"])
            requires_new_aux = True
            master_basis = None
            sign_text = (
                "Topology physical denominators map exactly to the canonical basis; "
                "duplicate physical powers are aggregated when the recorded mapping repeats an index."
            )

        update = {
            "classification_status": "confirmed",
            "canonical_integral_family_id": family_id,
            "canonical_propagator_basis": canonical_basis,
            "loop_momentum_transform": dict(witness["loop_momentum_transform"]),
            "external_momentum_transform": dict(witness["external_momentum_transform"]),
            "sign_normalization_transform": sign_text,
            "symmetry_representative": representative,
            "existing_kira_family_reusable": True,
            "requires_new_auxiliary_basis": requires_new_aux,
            "master_basis_id": master_basis,
            "canonical_equivalence_witness": witness,
            "evidence": _evidence(family_id, witness, mode),
        }
        if physical_mapping is not None:
            update["physical_to_canonical_mapping"] = physical_mapping
        rec.update(update)

    counts = Counter(str(rec.get("classification_status")) for rec in records)
    audit["classification_status_counts"] = dict(sorted(counts.items()))
    audit["confirmed_canonical_mapping_count"] = counts.get("confirmed", 0)
    audit["classification_complete"] = counts.get("confirmed", 0) == len(records)

    out_registry: dict[str, Any] = {}
    for family_id in auto.get("family_order", []):
        entry = dict(registry[family_id])
        entry.pop("canonical_propagators", None)
        out_registry[family_id] = entry
    audit["canonical_registry"] = out_registry
    audit["quenched_autodiscovery"] = {
        "audit_pass": bool(auto.get("audit_pass")),
        "transform_scope": auto.get("transform_scope"),
        "quenched_diagram_count": auto.get("quenched_diagram_count"),
        "confirmed_quenched_count": auto.get("confirmed_quenched_count"),
        "unresolved_quenched_count": auto.get("unresolved_quenched_count"),
        "canonical_family_count": auto.get("canonical_family_count"),
        "family_order": list(auto.get("family_order", [])),
    }
    return errors
