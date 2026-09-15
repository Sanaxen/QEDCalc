"""Run the next unresolved quenched canonical-family bootstrap audit."""
from __future__ import annotations

import json
from pathlib import Path

from three_loop.canonical_family_bootstrap import audit_next_quenched_family
from three_loop.integral_family_classification import ROOT, load_topologies

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_next_quenched_family_bootstrap_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_next_quenched_family_bootstrap_audit.txt"


def main() -> None:
    rows = load_topologies()
    audit = audit_next_quenched_family(rows, {"Q01", "Q41"})
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc next quenched canonical-family bootstrap audit",
        f"representative: {audit['representative']}",
        f"canonical family: {audit['canonical_family_id']}",
        f"candidate IDs: {audit['candidate_ids']}",
        f"physical propagators: {audit['physical_propagator_count']}",
        f"physical SP rank: {audit['physical_scalar_product_rank']}",
        f"selected auxiliaries: {audit['auxiliary_names']}",
        f"canonical basis rank: {audit['canonical_basis_rank']}/12",
        "",
    ]
    for rec in audit["records"]:
        lines.append(f"{rec['diagram_id']} {rec['status']}")
        witness = rec.get("witness")
        if witness:
            lines.append(f"  reflection: {witness['reflection']}")
            lines.append(f"  loop transform: {witness['loop_momentum_transform']}")
            lines.append(f"  external transform: {witness['external_momentum_transform']}")
            lines.append(f"  physical permutation: {witness['physical_propagator_permutation']}")
            lines.append(f"  P1..P12 exact: {all(witness['propagator_exact_match'])}")
    lines.extend([
        "",
        f"internal audit errors: {len(audit['errors'])}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc next quenched canonical-family bootstrap audit " + ("PASS" if audit["audit_pass"] else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("QEDCalc next quenched canonical-family bootstrap audit")
    print("representative:", audit["representative"])
    print("canonical family:", audit["canonical_family_id"])
    print("candidate IDs:", audit["candidate_ids"])
    print("physical propagators:", audit["physical_propagator_count"])
    print("physical SP rank:", audit["physical_scalar_product_rank"])
    print("selected auxiliaries:", audit["auxiliary_names"])
    print("canonical basis rank:", f"{audit['canonical_basis_rank']}/12")
    for rec in audit["records"]:
        print(rec["diagram_id"], rec["status"])
        witness = rec.get("witness")
        if witness:
            print("  reflection:", witness["reflection"])
            print("  loop transform:", witness["loop_momentum_transform"])
            print("  external transform:", witness["external_momentum_transform"])
            print("  physical permutation:", witness["physical_propagator_permutation"])
            print("  P1..P12 exact:", all(witness["propagator_exact_match"]))
    print("internal audit errors:", len(audit["errors"]))
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if audit["errors"]:
        for error in audit["errors"]:
            print("ERROR:", error)
        raise SystemExit("QEDCalc next quenched canonical-family bootstrap audit FAIL")
    print("QEDCalc next quenched canonical-family bootstrap audit PASS")


if __name__ == "__main__":
    main()
