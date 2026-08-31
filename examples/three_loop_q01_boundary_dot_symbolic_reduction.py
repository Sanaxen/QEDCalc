from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.boundary_dot_symbolic_reduction import build_boundary_dot_symbolic_profile
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_non_scalar_boundary_decomposition.json"
OUTPUT = ROOT / "output" / "3loop_q01_boundary_dot_symbolic_reduction.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    indices = tuple(
        IntegralIndex(tuple(row["index"]))
        for row in data["records"]
        if row["category"] == "dot-only"
    )
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    profile = build_boundary_dot_symbolic_profile(
        family,
        indices,
        templates=templates,
    )
    rhs_hist = Counter(rule.rhs_term_count for rule in profile.rules)
    out = {
        "target_count": profile.target_count,
        "exact_symbolic_rule_count": profile.directly_reduced_count,
        "unresolved_count": profile.unresolved_count,
        "rhs_term_count_histogram": dict(sorted(rhs_hist.items())),
        "rules": [
            {
                "target": rule.target,
                "source_label": rule.source_label,
                "target_coefficient": str(rule.target_coefficient),
                "rhs": [
                    {"index": powers, "coefficient": str(coeff)}
                    for powers, coeff in rule.rhs
                ],
            }
            for rule in profile.rules
        ],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("QEDCalc Q01 exact dot-only boundary symbolic reduction")
    print(f"dot-only targets: {profile.target_count}")
    print(f"exact dot-only symbolic rules: {profile.directly_reduced_count}")
    print(f"remaining dot-only targets: {profile.unresolved_count}")
    print(f"rhs term-count histogram: {dict(sorted(rhs_hist.items()))}")
    print(f"generated: {OUTPUT}")
    print("Q01 exact dot-only boundary symbolic reduction PASS")


if __name__ == "__main__":
    main()
