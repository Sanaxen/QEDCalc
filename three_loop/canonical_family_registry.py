"""Executable canonical-family registry overlay.

Quenched, VP1, VP2/VP22 and external LBL three-loop families are discovered and
re-proven automatically from exact algebraic witnesses. Q01 keeps its dedicated
stronger mapper checks.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from three_loop.integral_family_classification import Q01_CANONICAL_PROPAGATORS
from three_loop.lbl_family_autodiscovery import audit_lbl_family_autodiscovery
from three_loop.quenched_family_autodiscovery import audit_quenched_family_autodiscovery
from three_loop.vp1_family_autodiscovery import audit_vp1_family_autodiscovery
from three_loop.vp2_double_family_autodiscovery import audit_vp2_double_family_autodiscovery

Q01_MASTER_BASIS = "Q01_final60"
Q01_CANONICAL_FAMILY = "Q01_full"
Q02_MASTER_BASIS = "Q02_final17"
Q02_CANONICAL_FAMILY = "Q02_full"
Q08_MASTER_BASIS = "Q08_final12"
Q08_CANONICAL_FAMILY = "Q08_full"
Q10_MASTER_BASIS = "Q10_final13"
Q10_CANONICAL_FAMILY = "Q10_full"


def _master_basis_id(family_id: str) -> str | None:
    if family_id == Q01_CANONICAL_FAMILY:
        return Q01_MASTER_BASIS
    if family_id == Q02_CANONICAL_FAMILY:
        return Q02_MASTER_BASIS
    if family_id == Q08_CANONICAL_FAMILY:
        return Q08_MASTER_BASIS
    if family_id == Q10_CANONICAL_FAMILY:
        return Q10_MASTER_BASIS
    return None


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


def _apply_auto_records(
    *,
    auto: dict[str, Any],
    records: list[dict[str, Any]],
    errors: list[str],
    q01_special: bool,
) -> dict[str, Any]:
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

        if q01_special and family_id == Q01_CANONICAL_FAMILY:
            if not all(witness.get("propagator_exact_match", [])):
                errors.append(f"{diagram_id}: Q01 P1..P12 witness is not exact")
                continue
            if not all(witness.get("isp_bridge_exact_match", [])):
                errors.append(f"{diagram_id}: Q01 ISP bridge witness is not exact")
                continue
            canonical_basis = list(Q01_CANONICAL_PROPAGATORS)
            physical_mapping = None
            requires_new_aux = False
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
            sign_text = (
                "Topology physical denominators map exactly to the canonical basis; "
                "duplicate physical powers are aggregated when the recorded mapping repeats an index."
            )

        master_basis = _master_basis_id(family_id)
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

    return registry


def apply_confirmed_family_registry(rows: list[dict[str, Any]], audit: dict[str, Any]) -> list[str]:
    """Overlay every automatically proven three-loop canonical-family mapping."""
    errors: list[str] = []
    records = audit.get("records", [])

    quenched = audit_quenched_family_autodiscovery(rows)
    if not quenched.get("audit_pass"):
        errors.extend(str(item) for item in quenched.get("errors", []))
        if not quenched.get("errors"):
            errors.append("quenched canonical-family autodiscovery failed")
        audit["canonical_registry"] = {}
        return errors

    vp1 = audit_vp1_family_autodiscovery(rows)
    if not vp1.get("audit_pass"):
        errors.extend(str(item) for item in vp1.get("errors", []))
        if not vp1.get("errors"):
            errors.append("VP1 canonical-family autodiscovery failed")
        audit["canonical_registry"] = {}
        return errors

    vp2_double = audit_vp2_double_family_autodiscovery(rows)
    if not vp2_double.get("audit_pass"):
        errors.extend(str(item) for item in vp2_double.get("errors", []))
        if not vp2_double.get("errors"):
            errors.append("VP2/VP22 canonical-family autodiscovery failed")
        audit["canonical_registry"] = {}
        return errors

    lbl = audit_lbl_family_autodiscovery(rows)
    if not lbl.get("audit_pass"):
        errors.extend(str(item) for item in lbl.get("errors", []))
        if not lbl.get("errors"):
            errors.append("LBL canonical-family autodiscovery failed")
        audit["canonical_registry"] = {}
        return errors

    quenched_registry = _apply_auto_records(
        auto=quenched, records=records, errors=errors, q01_special=True
    )
    vp1_registry = _apply_auto_records(
        auto=vp1, records=records, errors=errors, q01_special=False
    )
    vp2_double_registry = _apply_auto_records(
        auto=vp2_double, records=records, errors=errors, q01_special=False
    )
    lbl_registry = _apply_auto_records(
        auto=lbl, records=records, errors=errors, q01_special=False
    )

    counts = Counter(str(rec.get("classification_status")) for rec in records)
    audit["classification_status_counts"] = dict(sorted(counts.items()))
    audit["confirmed_canonical_mapping_count"] = counts.get("confirmed", 0)
    audit["classification_complete"] = counts.get("confirmed", 0) == len(records)

    out_registry: dict[str, Any] = {}
    for family_id in quenched.get("family_order", []):
        entry = dict(quenched_registry[family_id])
        entry.pop("canonical_propagators", None)
        entry["master_basis_id"] = _master_basis_id(family_id)
        out_registry[family_id] = entry
    for raw_registry in (vp1_registry, vp2_double_registry, lbl_registry):
        for family_id, raw in raw_registry.items():
            entry = dict(raw)
            entry.pop("canonical_propagators", None)
            entry["master_basis_id"] = _master_basis_id(family_id)
            out_registry[family_id] = entry
    audit["canonical_registry"] = out_registry

    audit["quenched_autodiscovery"] = {
        "audit_pass": bool(quenched.get("audit_pass")),
        "transform_scope": quenched.get("transform_scope"),
        "quenched_diagram_count": quenched.get("quenched_diagram_count"),
        "confirmed_quenched_count": quenched.get("confirmed_quenched_count"),
        "unresolved_quenched_count": quenched.get("unresolved_quenched_count"),
        "canonical_family_count": quenched.get("canonical_family_count"),
        "family_order": list(quenched.get("family_order", [])),
    }
    audit["vp1_autodiscovery"] = {
        "audit_pass": bool(vp1.get("audit_pass")),
        "transform_scope": vp1.get("transform_scope"),
        "vp1_diagram_count": vp1.get("vp1_diagram_count"),
        "confirmed_vp1_count": vp1.get("confirmed_vp1_count"),
        "unresolved_vp1_count": vp1.get("unresolved_vp1_count"),
        "canonical_family_count": vp1.get("canonical_family_count"),
    }
    audit["vp2_double_autodiscovery"] = {
        "audit_pass": bool(vp2_double.get("audit_pass")),
        "transform_scope": vp2_double.get("transform_scope"),
        "diagram_count": vp2_double.get("diagram_count"),
        "confirmed_count": vp2_double.get("confirmed_count"),
        "unresolved_count": vp2_double.get("unresolved_count"),
        "canonical_family_count": vp2_double.get("canonical_family_count"),
        "formula_source": vp2_double.get("formula_source"),
    }
    audit["lbl_autodiscovery"] = {
        "audit_pass": bool(lbl.get("audit_pass")),
        "transform_scope": lbl.get("transform_scope"),
        "diagram_count": lbl.get("diagram_count"),
        "confirmed_count": lbl.get("confirmed_count"),
        "unresolved_count": lbl.get("unresolved_count"),
        "canonical_family_count": lbl.get("canonical_family_count"),
        "formula_source": lbl.get("formula_source"),
    }
    return errors
