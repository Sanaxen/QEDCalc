"""Audit and print the master-basis identification schedule."""
from __future__ import annotations

import json

from three_loop.integral_family_classification import ROOT, load_topologies
from three_loop.master_basis_schedule import build_master_basis_schedule

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_master_basis_schedule_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_master_basis_schedule_audit.txt"
EXPECTED_FAMILY_COUNT = 45
EXPECTED_COMPLETE = {
    "Q01_full": "Q01_final60",
    "Q02_full": "Q02_final17",
    "Q05_full": "Q05_final13",
    "Q07_full": "Q07_final25",
    "Q08_full": "Q08_final12",
    "Q10_full": "Q10_final13",
}


def main() -> None:
    rows = load_topologies()
    audit = build_master_basis_schedule(rows)
    errors = list(audit.get("errors", []))

    if audit.get("canonical_family_count") != EXPECTED_FAMILY_COUNT:
        errors.append(
            f"canonical family count={audit.get('canonical_family_count')}, expected={EXPECTED_FAMILY_COUNT}"
        )
    if audit.get("master_basis_complete_family_count") != len(EXPECTED_COMPLETE):
        errors.append(
            "complete family count="
            f"{audit.get('master_basis_complete_family_count')}, expected={len(EXPECTED_COMPLETE)}"
        )
    expected_pending = EXPECTED_FAMILY_COUNT - len(EXPECTED_COMPLETE)
    if audit.get("master_basis_pending_family_count") != expected_pending:
        errors.append(
            "pending family count="
            f"{audit.get('master_basis_pending_family_count')}, expected={expected_pending}"
        )

    completed = {
        str(item.get("canonical_family_id")): item
        for item in audit.get("completed", [])
    }
    for family_id, master_basis_id in EXPECTED_COMPLETE.items():
        item = completed.get(family_id)
        if item is None:
            errors.append(f"missing completed family {family_id}")
            continue
        if item.get("master_basis_id") != master_basis_id:
            errors.append(
                f"{family_id}: master_basis_id={item.get('master_basis_id')}, expected={master_basis_id}"
            )

    expected_diagrams = {
        "Q02_full": ["Q02", "Q45"],
        "Q05_full": ["Q05", "Q42"],
        "Q07_full": ["Q07", "Q47"],
        "Q08_full": ["Q08", "Q48"],
        "Q10_full": ["Q10", "Q50"],
    }
    for family_id, diagrams in expected_diagrams.items():
        item = completed.get(family_id)
        if item is not None and item.get("confirmed_diagrams") != diagrams:
            errors.append(
                f"{family_id} diagrams={item.get('confirmed_diagrams')}, expected={diagrams}"
            )

    schedule = list(audit.get("schedule", []))
    next_pending = schedule[0] if schedule else None
    if expected_pending and next_pending is None:
        errors.append("master-basis schedule is unexpectedly empty")
    audit["errors"] = errors
    audit["audit_pass"] = not errors
    audit["next_pending_family"] = next_pending

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc three-loop master-basis schedule audit",
        f"canonical families: {audit['canonical_family_count']}",
        f"master-basis complete families: {audit['master_basis_complete_family_count']}",
        f"master-basis pending families: {audit['master_basis_pending_family_count']}",
        f"complete diagram coverage: {audit['complete_diagram_coverage']}",
        f"pending diagram coverage: {audit['pending_diagram_coverage']}",
        "",
        "Completed:",
    ]
    for item in audit["completed"]:
        lines.append(
            f"  {item['canonical_family_id']}: diagrams={item['confirmed_diagrams']} "
            f"master={item['master_basis_id']}"
        )

    if next_pending is not None:
        lines.extend([
            "",
            "Next pending family:",
            f"  {next_pending['canonical_family_id']}: representative={next_pending['representative']} "
            f"diagrams={next_pending['confirmed_diagrams']} "
            f"unique_physical={next_pending['unique_physical_denominator_count']} "
            f"aux={next_pending['auxiliary_denominator_count']} "
            f"tier={next_pending['priority_tier']}",
        ])

    lines.extend(["", "Pending execution order:"])
    for item in schedule:
        lines.append(
            "  {order:02d}. {family}: topology={topology} diagrams={diagrams} "
            "unique_physical={unique} aux={aux} tier={tier}".format(
                order=item["execution_order"],
                family=item["canonical_family_id"],
                topology=item["physical_topology_family"],
                diagrams=item["confirmed_diagrams"],
                unique=item["unique_physical_denominator_count"],
                aux=item["auxiliary_denominator_count"],
                tier=item["priority_tier"],
            )
        )

    lines.extend([
        "",
        "Priority policy:",
        "  " + " -> ".join(audit["priority_policy"]),
        f"Within-tier heuristic: {audit['within_tier_heuristic']}",
        "",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc three-loop master-basis schedule audit " + ("PASS" if not errors else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc three-loop master-basis schedule audit FAIL")


if __name__ == "__main__":
    main()
