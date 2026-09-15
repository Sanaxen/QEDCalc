"""Run the next unresolved quenched family bootstrap audit."""
from __future__ import annotations

import json

from three_loop.canonical_family_bootstrap import audit_next_quenched_family
from three_loop.integral_family_classification import ROOT, load_topologies

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_next_quenched_family_bootstrap_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_next_quenched_family_bootstrap_audit.txt"


def _relation_lines(audit: dict) -> list[str]:
    lines: list[str] = []
    for i, rel in enumerate(audit["physical_denominator_relations"], start=1):
        lines.append(f"physical relation {i}: {rel['relation']}")
        lines.append(f"  affine residual: {rel['affine_residual']}")
        lines.append(f"  exact zero relation: {rel['exact_zero_relation']}")
    return lines


def main() -> None:
    rows = load_topologies()
    audit = audit_next_quenched_family(rows, {"Q01", "Q41"})
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc next quenched family bootstrap audit",
        f"representative: {audit['representative']}",
        f"family candidate: {audit['family_candidate_id']}",
        f"candidate IDs: {audit['candidate_ids']}",
        f"Q01 reuse under current scope: {audit['q01_reuse_under_current_scope'] is not None}",
        f"new family required under current scope: {audit['new_family_required_under_current_scope']}",
        f"physical propagators: {audit['physical_propagator_count']}",
        f"physical SP rank: {audit['physical_scalar_product_rank']}",
        f"physical rank deficiency: {audit['physical_rank_deficiency']}",
        f"selected auxiliary count: {audit['selected_auxiliary_count']}",
        f"selected auxiliaries: {audit['auxiliary_names']}",
        f"generated denominator count: {audit['generated_denominator_count']}",
        f"generated SP rank: {audit['generated_scalar_product_rank']}/12",
        f"overcomplete generated set: {audit['overcomplete_generated_set']}",
        f"Kira ready: {audit['kira_ready']}",
        f"requires partial fraction / family split: {audit['requires_partial_fraction_or_family_split']}",
        "",
    ]
    lines.extend(_relation_lines(audit))
    if audit["physical_denominator_relations"]:
        lines.append("")

    for rec in audit["records"]:
        lines.append(f"{rec['diagram_id']} {rec['status']}")
        witness = rec.get("witness")
        if witness:
            lines.append(f"  reflection: {witness['reflection']}")
            lines.append(f"  loop transform: {witness['loop_momentum_transform']}")
            lines.append(f"  external transform: {witness['external_momentum_transform']}")
            lines.append(f"  physical permutation: {witness['physical_propagator_permutation']}")
            lines.append(f"  all generated denominators exact: {all(witness['propagator_exact_match'])}")
    lines.extend([
        "",
        f"internal audit errors: {len(audit['errors'])}",
        f"audit JSON: {OUTPUT_JSON}",
        f"audit TXT: {OUTPUT_TXT}",
        "QEDCalc next quenched family bootstrap audit " + ("PASS" if audit["audit_pass"] else "FAIL"),
    ])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("QEDCalc next quenched family bootstrap audit")
    print("representative:", audit["representative"])
    print("family candidate:", audit["family_candidate_id"])
    print("candidate IDs:", audit["candidate_ids"])
    print("Q01 reuse under current scope:", audit["q01_reuse_under_current_scope"] is not None)
    print("new family required under current scope:", audit["new_family_required_under_current_scope"])
    print("physical propagators:", audit["physical_propagator_count"])
    print("physical SP rank:", audit["physical_scalar_product_rank"])
    print("physical rank deficiency:", audit["physical_rank_deficiency"])
    print("selected auxiliary count:", audit["selected_auxiliary_count"])
    print("selected auxiliaries:", audit["auxiliary_names"])
    print("generated denominator count:", audit["generated_denominator_count"])
    print("generated SP rank:", f"{audit['generated_scalar_product_rank']}/12")
    print("overcomplete generated set:", audit["overcomplete_generated_set"])
    print("Kira ready:", audit["kira_ready"])
    print("requires partial fraction / family split:", audit["requires_partial_fraction_or_family_split"])
    for line in _relation_lines(audit):
        print(line)
    for rec in audit["records"]:
        print(rec["diagram_id"], rec["status"])
        witness = rec.get("witness")
        if witness:
            print("  reflection:", witness["reflection"])
            print("  loop transform:", witness["loop_momentum_transform"])
            print("  external transform:", witness["external_momentum_transform"])
            print("  physical permutation:", witness["physical_propagator_permutation"])
            print("  all generated denominators exact:", all(witness["propagator_exact_match"]))
    print("internal audit errors:", len(audit["errors"]))
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if audit["errors"]:
        for error in audit["errors"]:
            print("ERROR:", error)
        raise SystemExit("QEDCalc next quenched family bootstrap audit FAIL")
    print("QEDCalc next quenched family bootstrap audit PASS")


if __name__ == "__main__":
    main()
