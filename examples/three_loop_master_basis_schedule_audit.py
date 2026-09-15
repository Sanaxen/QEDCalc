"""Audit and print the master-basis identification schedule."""
from __future__ import annotations

import json

from three_loop.integral_family_classification import ROOT, load_topologies
from three_loop.master_basis_schedule import build_master_basis_schedule

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_master_basis_schedule_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_master_basis_schedule_audit.txt"


def main() -> None:
    rows = load_topologies()
    audit = build_master_basis_schedule(rows)

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

    lines.extend(["", "Pending execution order:"])
    for item in audit["schedule"]:
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
        f"internal audit errors: {len(audit['errors'])}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc three-loop master-basis schedule audit " + ("PASS" if audit["audit_pass"] else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for line in lines:
        print(line)
    if audit["errors"]:
        for error in audit["errors"]:
            print("ERROR:", error)
        raise SystemExit("QEDCalc three-loop master-basis schedule audit FAIL")


if __name__ == "__main__":
    main()
