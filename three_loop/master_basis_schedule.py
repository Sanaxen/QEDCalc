"""Build a deterministic master-basis identification schedule for all 3-loop families.

The schedule is derived from the executable global canonical registry rather
than maintained by hand. Any family carrying a ``master_basis_id`` in that
registry is marked complete; currently Q01_full/Q01_final60,
Q02_full/Q02_final17, Q05_full/Q05_final13, Q07_full/Q07_final25,
Q08_full/Q08_final12, Q09_full/Q09_final17, and Q10_full/Q10_final13 are promoted reference families. Pending families are
ranked by practical payoff and expected pipeline reuse:

1. multi-diagram quenched families;
2. multi-diagram VP1 families;
3. singleton quenched families;
4. singleton VP1 families;
5. VP2/VP22 families;
6. external LBL families.

Within a tier, families with fewer unique physical denominators are placed first
as a conservative complexity heuristic. This is a scheduling heuristic only;
it is not a mathematical claim about actual Kira runtime.
"""
from __future__ import annotations

from typing import Any

from three_loop.canonical_family_registry import apply_confirmed_family_registry
from three_loop.integral_family_classification import build_global_classification, validate_global_audit


TOPOLOGY_ORDER = {
    "quenched": 0,
    "vp1_insert": 1,
    "vp2_insert": 2,
    "vp1_double": 3,
    "external_lbl": 4,
}


def _tier(topology: str, diagram_count: int) -> int:
    if topology == "quenched" and diagram_count >= 2:
        return 1
    if topology == "vp1_insert" and diagram_count >= 2:
        return 2
    if topology == "quenched":
        return 3
    if topology == "vp1_insert":
        return 4
    if topology in {"vp2_insert", "vp1_double"}:
        return 5
    if topology == "external_lbl":
        return 6
    return 99


def build_master_basis_schedule(rows: list[dict[str, Any]]) -> dict[str, Any]:
    audit = build_global_classification(rows)
    registry_errors = apply_confirmed_family_registry(rows, audit)
    errors = validate_global_audit(audit) + list(registry_errors)

    records = {str(rec["diagram_id"]): rec for rec in audit.get("records", [])}
    registry = audit.get("canonical_registry", {})
    entries: list[dict[str, Any]] = []

    for family_id, family in registry.items():
        representative = str(family["representative"])
        rep_record = records.get(representative)
        if rep_record is None:
            errors.append(f"{family_id}: representative {representative} missing from global records")
            continue

        diagrams = list(family.get("confirmed_diagrams", []))
        topology = str(rep_record.get("physical_topology_family"))
        aux_count = len(family.get("auxiliary_names", []))
        canonical_count = int(family.get("canonical_denominator_count", 12))
        unique_physical_count = canonical_count - aux_count
        master_basis_id = family.get("master_basis_id")
        completed = master_basis_id is not None

        entries.append({
            "canonical_family_id": family_id,
            "representative": representative,
            "physical_topology_family": topology,
            "confirmed_diagrams": diagrams,
            "diagram_count": len(diagrams),
            "unique_physical_denominator_count": unique_physical_count,
            "auxiliary_denominator_count": aux_count,
            "canonical_denominator_count": canonical_count,
            "master_basis_id": master_basis_id,
            "master_basis_status": "complete" if completed else "pending",
            "priority_tier": 0 if completed else _tier(topology, len(diagrams)),
        })

    completed = [item for item in entries if item["master_basis_status"] == "complete"]
    pending = [item for item in entries if item["master_basis_status"] == "pending"]
    pending.sort(key=lambda item: (
        item["priority_tier"],
        item["unique_physical_denominator_count"],
        TOPOLOGY_ORDER.get(item["physical_topology_family"], 99),
        item["representative"],
    ))
    for index, item in enumerate(pending, start=1):
        item["execution_order"] = index
    for item in completed:
        item["execution_order"] = 0

    covered_complete = sum(item["diagram_count"] for item in completed)
    covered_pending = sum(item["diagram_count"] for item in pending)
    if len(entries) != len(registry):
        errors.append(f"schedule entries={len(entries)} registry families={len(registry)}")
    if covered_complete + covered_pending != len(rows):
        errors.append(
            f"scheduled diagram coverage={covered_complete + covered_pending}, expected={len(rows)}"
        )

    return {
        "canonical_family_count": len(entries),
        "master_basis_complete_family_count": len(completed),
        "master_basis_pending_family_count": len(pending),
        "complete_diagram_coverage": covered_complete,
        "pending_diagram_coverage": covered_pending,
        "completed": completed,
        "schedule": pending,
        "priority_policy": [
            "multi-diagram quenched",
            "multi-diagram VP1",
            "singleton quenched",
            "singleton VP1",
            "VP2/VP22",
            "external LBL",
        ],
        "within_tier_heuristic": (
            "fewer unique physical denominators first; heuristic only, not a Kira runtime prediction"
        ),
        "errors": errors,
        "audit_pass": not errors,
    }
