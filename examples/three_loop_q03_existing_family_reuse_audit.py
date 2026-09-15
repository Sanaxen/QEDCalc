"""Audit Q03/Q43 against already confirmed quenched canonical families.

The transform scope is deliberately the same explicit scope used by the current
family bootstrap: open-line reflection plus signed loop-momentum relabeling.
This does not claim to exhaust arbitrary affine/GL(Z) loop-momentum changes.
"""
from __future__ import annotations

import json

from three_loop.canonical_family_bootstrap import (
    complete_with_quadratic_auxiliaries,
    deduplicate_exact_denominators,
    find_family_witness,
    q01_reuse_witness,
    topology_physical_denominators,
)
from three_loop.integral_family_classification import ROOT, load_topologies

OUTPUT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUTPUT_JSON = OUTPUT_DIR / "three_loop_q03_existing_family_reuse_audit.json"
OUTPUT_TXT = OUTPUT_DIR / "three_loop_q03_existing_family_reuse_audit.txt"


def main() -> None:
    rows = load_topologies()
    by_id = {str(row["id"]): row for row in rows}

    q01 = by_id["Q01"]
    q02 = by_id["Q02"]
    q02_physical = topology_physical_denominators(q02)
    q02_unique, _, _ = deduplicate_exact_denominators(q02_physical)
    _, q02_aux_vecs, q02_aux_exprs = complete_with_quadratic_auxiliaries(q02_unique)

    records = []
    errors = []
    for diagram_id in ("Q03", "Q43"):
        candidate = by_id[diagram_id]
        q01_witness = q01_reuse_witness(candidate, q01)
        q02_witness_obj = find_family_witness(
            candidate,
            q02,
            q02_unique,
            q02_aux_vecs,
            q02_aux_exprs,
        )
        q02_witness = q02_witness_obj.to_dict() if q02_witness_obj is not None else None
        records.append(
            {
                "diagram_id": diagram_id,
                "q01_full_reuse_under_current_scope": q01_witness,
                "q02_full_reuse_under_current_scope": q02_witness,
            }
        )

    representative = next(rec for rec in records if rec["diagram_id"] == "Q03")
    new_family_required = (
        representative["q01_full_reuse_under_current_scope"] is None
        and representative["q02_full_reuse_under_current_scope"] is None
    )
    if not new_family_required:
        errors.append("Q03 reuses an existing confirmed family under the current transform scope")

    audit = {
        "candidate_ids": ["Q03", "Q43"],
        "transform_scope": "open-line reflection + signed loop-momentum relabeling",
        "records": records,
        "new_family_required_under_current_scope": new_family_required,
        "errors": errors,
        "audit_pass": not errors,
        "interpretation": (
            "A PASS means Q03 does not reuse Q01_full or Q02_full within the explicit current transform scope. "
            "It does not exclude a more general affine/GL(Z) loop-momentum equivalence."
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q03 existing-family reuse audit",
        f"transform scope: {audit['transform_scope']}",
        f"candidate IDs: {audit['candidate_ids']}",
    ]
    for rec in records:
        lines.append(
            f"{rec['diagram_id']}: Q01_full reuse={rec['q01_full_reuse_under_current_scope'] is not None}; "
            f"Q02_full reuse={rec['q02_full_reuse_under_current_scope'] is not None}"
        )
    lines.extend(
        [
            f"new family required under current scope: {new_family_required}",
            f"internal audit errors: {len(errors)}",
            f"audit JSON: {OUTPUT_JSON}",
            f"audit TXT: {OUTPUT_TXT}",
            "QEDCalc Q03 existing-family reuse audit " + ("PASS" if not errors else "FAIL"),
        ]
    )
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q03 existing-family reuse audit FAIL")


if __name__ == "__main__":
    main()
