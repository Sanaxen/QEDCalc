"""Run canonical-family autodiscovery for the six external LBL diagrams."""
from __future__ import annotations

import json

from three_loop.integral_family_classification import ROOT, load_topologies
from three_loop.lbl_family_autodiscovery import audit_lbl_family_autodiscovery

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_lbl_family_autodiscovery_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_lbl_family_autodiscovery_audit.txt"


def main() -> None:
    rows = load_topologies()
    audit = audit_lbl_family_autodiscovery(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc LBL canonical-family autodiscovery audit",
        f"transform scope: {audit['transform_scope']}",
        f"diagrams: {audit['diagram_count']}",
        f"confirmed: {audit['confirmed_count']}",
        f"unresolved: {audit['unresolved_count']}",
        f"canonical families: {audit['canonical_family_count']}",
        "",
        "Discovery steps:",
    ]
    for i, step in enumerate(audit["steps"], start=1):
        lines.append(
            "  step {i}: rep={rep} status={status} family={family} confirmed={confirmed} families={families}".format(
                i=i,
                rep=step["representative"],
                status=step["status"],
                family=step["canonical_family_id"],
                confirmed=step["confirmed_after_step"],
                families=step["family_count_after_step"],
            )
        )

    lines.extend(["", "Canonical registry:"])
    for family_id, entry in audit["canonical_registry"].items():
        lines.append(
            f"  {family_id}: representative={entry['representative']} "
            f"confirmed={entry['confirmed_diagrams']} "
            f"duplicates={entry['duplicate_physical_groups']} "
            f"aux={entry['auxiliary_names']} rank={entry['canonical_scalar_product_rank']}/12"
        )

    lines.extend([
        "",
        f"internal audit errors: {len(audit['errors'])}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc LBL canonical-family autodiscovery audit " + ("PASS" if audit["audit_pass"] else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for line in lines:
        print(line)
    if audit["errors"]:
        for error in audit["errors"]:
            print("ERROR:", error)
        raise SystemExit("QEDCalc LBL canonical-family autodiscovery audit FAIL")


if __name__ == "__main__":
    main()
