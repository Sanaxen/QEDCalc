from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.boundary_layer_pivot_audit import audit_boundary_layer_direct_pivots
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_non_scalar_boundary_decomposition.json"
OUTPUT = ROOT / "output" / "3loop_q01_boundary_layer_pivot_audit.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    categories = {"dot-only": [], "numerator-only": []}
    for row in data["records"]:
        category = row["category"]
        if category in categories:
            categories[category].append(IntegralIndex(tuple(row["index"])))

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    profile = audit_boundary_layer_direct_pivots(
        family,
        categories,
        templates=templates,
    )

    out = {
        "target_count": profile.target_count,
        "directly_pivotable_count": profile.directly_pivotable_count,
        "nonpivotable_count": profile.nonpivotable_count,
        "rows": [row.__dict__ for row in profile.rows],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 boundary-layer direct-pivot audit")
    for row in profile.rows:
        print(f"{row.category} targets: {row.target_count}")
        print(f"{row.category} directly pivotable: {row.directly_pivotable_count}")
        print(f"{row.category} nonpivotable: {row.nonpivotable_count}")
        print(f"{row.category} direct pivot equations: {row.direct_pivot_equation_count}")
        print(f"{row.category} max direct equations per target: {row.max_direct_pivot_equations_per_target}")
    print(f"combined targets: {profile.target_count}")
    print(f"combined directly pivotable: {profile.directly_pivotable_count}")
    print(f"combined nonpivotable: {profile.nonpivotable_count}")
    print(f"generated: {OUTPUT}")
    print("Q01 boundary-layer direct-pivot audit PASS")


if __name__ == "__main__":
    main()
