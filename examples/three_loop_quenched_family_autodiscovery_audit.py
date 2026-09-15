"""Run automatic canonical-family discovery for all 50 quenched diagrams."""
from __future__ import annotations

import json

from three_loop.integral_family_classification import ROOT, load_topologies
from three_loop.quenched_family_autodiscovery import audit_quenched_family_autodiscovery

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_quenched_family_autodiscovery_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_quenched_family_autodiscovery_audit.txt"


def main() -> None:
    rows = load_topologies()
    audit = audit_quenched_family_autodiscovery(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc quenched canonical-family autodiscovery audit",
        f"transform scope: {audit['transform_scope']}",
        f"quenched diagrams: {audit['quenched_diagram_count']}",
        f"confirmed quenched: {audit['confirmed_quenched_count']}",
        f"unresolved quenched: {audit['unresolved_quenched_count']}",
        f"canonical families: {audit['canonical_family_count']}",
        "",
        "Discovery steps:",
    ]
    for step in audit["steps"]:
        lines.append(
            "  step {step}: rep={rep} candidates={candidates} status={status} "
            "family={family} reuse_hits={hits} confirmed={confirmed} families={families}".format(
                step=step["step"],
                rep=step["representative"],
                candidates=step["candidate_ids"],
                status=step["status"],
                family=step.get("canonical_family_id"),
                hits=step.get("reuse_hits", []),
                confirmed=step.get("confirmed_after_step", "-"),
                families=step.get("family_count_after_step", "-"),
            )
        )

    lines.extend(["", "Canonical registry:"])
    for family_id in audit["family_order"]:
        entry = audit["canonical_registry"][family_id]
        lines.append(
            f"  {family_id}: representative={entry['representative']} "
            f"confirmed={entry['confirmed_diagrams']} master_basis={entry['master_basis_id']} "
            f"mode={entry['discovery_mode']}"
        )

    lines.extend([
        "",
        f"internal audit errors: {len(audit['errors'])}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc quenched canonical-family autodiscovery audit "
        + ("PASS" if audit["audit_pass"] else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for line in lines:
        print(line)
    if audit["errors"]:
        for error in audit["errors"]:
            print("ERROR:", error)
        raise SystemExit("QEDCalc quenched canonical-family autodiscovery audit FAIL")


if __name__ == "__main__":
    main()
