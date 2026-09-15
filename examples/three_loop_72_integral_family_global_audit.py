"""Audit the 72-diagram topology inventory against canonical IBP-family evidence.

This first global pass is deliberately conservative.  It creates reproducible
structural candidate classes for all 72 diagrams and reports which diagrams
already have enough explicit evidence to be called confirmed canonical Kira
families.  Topology similarity is never silently promoted to an IBP-family
identity.
"""
from __future__ import annotations

import json
from pathlib import Path

from three_loop.integral_family_classification import (
    ROOT,
    build_global_classification,
    load_topologies,
    validate_global_audit,
)

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_72_integral_family_global_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_72_integral_family_global_audit.txt"


def main() -> None:
    rows = load_topologies()
    audit = build_global_classification(rows)
    errors = validate_global_audit(audit)
    audit["audit_errors"] = errors
    audit["audit_pass"] = not errors

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    status = audit["classification_status_counts"]
    lines = [
        "QEDCalc 72-diagram integral-family global classification audit",
        "",
        f"diagrams: {audit['diagram_count']}",
        f"physical family counts: {audit['physical_family_counts']}",
        f"structural candidate classes: {audit['structural_candidate_class_count']}",
        f"classification status counts: {status}",
        f"confirmed canonical mappings: {audit['confirmed_canonical_mapping_count']}",
        f"classification complete: {audit['classification_complete']}",
        f"internal audit errors: {len(errors)}",
        "",
        "Candidate classes (topology scheduling hints; NOT yet canonical IBP proofs):",
    ]
    for cid, ids in audit["structural_candidate_classes"].items():
        lines.append(f"  {cid}: {', '.join(ids)}")

    lines.extend(["", "Per-diagram canonical mapping status:"])
    for rec in audit["records"]:
        lines.append(
            "  {id}: topology={topology} candidate={candidate} status={status} "
            "canonical={canonical} master_basis={master}".format(
                id=rec["diagram_id"],
                topology=rec["physical_topology_family"],
                candidate=rec["structural_candidate_class"],
                status=rec["classification_status"],
                canonical=rec["canonical_integral_family_id"],
                master=rec["master_basis_id"],
            )
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "  audit_pass checks the 72-diagram inventory and candidate-class partition.",
            "  classification_complete is stricter: it becomes true only when every diagram",
            "  has an explicit canonical propagator basis and proven loop-momentum map.",
            "  A candidate topology class must not be treated as a proven Kira family.",
            "",
            f"audit JSON: {OUTPUT_JSON}",
            f"audit TXT: {OUTPUT_TXT}",
            "",
            "QEDCalc 72-diagram integral-family global classification audit "
            + ("PASS" if not errors else "FAIL"),
        ]
    )
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("QEDCalc 72-diagram integral-family global classification audit")
    print("diagrams:", audit["diagram_count"])
    print("physical family counts:", audit["physical_family_counts"])
    print("structural candidate classes:", audit["structural_candidate_class_count"])
    print("classification status counts:", status)
    print("confirmed canonical mappings:", audit["confirmed_canonical_mapping_count"])
    print("classification complete:", audit["classification_complete"])
    print("internal audit errors:", len(errors))
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc 72-diagram integral-family global classification audit FAIL")
    print("QEDCalc 72-diagram integral-family global classification audit PASS")


if __name__ == "__main__":
    main()
