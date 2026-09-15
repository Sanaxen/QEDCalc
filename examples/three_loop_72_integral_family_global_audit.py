"""Audit the 72-diagram topology inventory against canonical IBP-family evidence.

Structural candidate classes are only scheduling hints.  Confirmed canonical
families are overlaid from executable algebraic witnesses, so topology
similarity is never silently promoted to an IBP/Kira-family identity.
"""
from __future__ import annotations

import json

from three_loop.canonical_family_registry import apply_confirmed_family_registry
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

    registry_errors = apply_confirmed_family_registry(rows, audit)
    errors = validate_global_audit(audit)
    errors.extend(registry_errors)
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
        "Confirmed canonical registries:",
    ]
    for family_id, entry in audit.get("canonical_registry", {}).items():
        lines.append(
            f"  {family_id}: representative={entry['representative']} "
            f"confirmed={entry['confirmed_diagrams']} master_basis={entry['master_basis_id']}"
        )

    lines.extend(["", "Candidate classes (topology scheduling hints; NOT canonical proofs by themselves):"])
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
        witness = rec.get("canonical_equivalence_witness")
        if witness is not None:
            lines.append(
                "    witness: reflection={reflection} loops={loops} external={external} "
                "physical_perm={perm}".format(
                    reflection=witness["reflection"],
                    loops=witness["loop_momentum_transform"],
                    external=witness["external_momentum_transform"],
                    perm=witness["physical_propagator_permutation"],
                )
            )

    lines.extend(
        [
            "",
            "Interpretation:",
            "  audit_pass checks the 72-diagram inventory, candidate partition,",
            "  and every executable canonical-family witness used for promotion.",
            "  classification_complete is stricter: it becomes true only when every diagram",
            "  has an explicit canonical propagator basis and proven momentum map.",
            "  Q01-family members are promoted only after exact P1..P12 and ISP-bridge checks.",
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
    print("canonical registry:", audit.get("canonical_registry", {}))
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
