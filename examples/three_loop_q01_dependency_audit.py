"""Audit whether Q01 targets can be solved from same-seed IBP equations."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

from qedcalc.operations.ibp import IntegralIndex
from three_loop import q01_integral_family
from three_loop.dependency_audit import audit_target_direct_pivots
from three_loop.ibp_frontier import build_ibp_derivative_templates


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
SUMMARY = ROOT / "output" / "3loop_q01_dependency_audit.json"

INDEX_RE = re.compile(r"I\(([-0-9,]+)\)\s*$")


def load_indices(path: Path) -> tuple[IntegralIndex, ...]:
    indices = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line.strip())
        if not match:
            continue
        powers = tuple(int(x) for x in match.group(1).split(","))
        indices.append(IntegralIndex(powers))
    return tuple(dict.fromkeys(indices))


def main() -> int:
    print("QEDCalc Q01 dependency-driven IBP pivot audit")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_integral_map.bat first.")
        return 1

    targets = load_indices(INPUT)
    family = q01_integral_family()

    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    template_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    audit = audit_target_direct_pivots(family, targets, templates=templates)
    audit_seconds = time.perf_counter() - t1

    payload = {
        "target_count": audit.target_count,
        "same_seed_equation_count": audit.equation_count,
        "directly_pivotable_target_count": audit.directly_pivotable_target_count,
        "nonpivotable_target_count": audit.nonpivotable_target_count,
        "directly_pivotable_fraction": audit.directly_pivotable_fraction,
        "direct_pivot_equation_count": audit.direct_pivot_equation_count,
        "max_direct_pivot_equations_per_target": audit.max_direct_pivot_equations_per_target,
        "derivative_template_count": len(templates),
        "template_build_seconds": template_seconds,
        "audit_seconds": audit_seconds,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"targets: {audit.target_count}")
    print(f"same-seed IBP equations audited: {audit.equation_count}")
    print(f"directly pivotable targets: {audit.directly_pivotable_target_count}")
    print(f"nonpivotable targets: {audit.nonpivotable_target_count}")
    print(f"direct pivot equations: {audit.direct_pivot_equation_count}")
    print(f"max direct pivot equations per target: {audit.max_direct_pivot_equations_per_target}")
    print(f"template build: {template_seconds:.3f} s")
    print(f"dependency audit: {audit_seconds:.3f} s")
    print(f"generated: {SUMMARY}")
    print("Q01 dependency-driven IBP pivot audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
