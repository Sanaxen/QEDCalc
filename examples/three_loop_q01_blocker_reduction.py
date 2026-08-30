"""Audit local reducibility of the Q01 unresolved-target blocker layer."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

from qedcalc.operations.ibp import IntegralIndex
from three_loop.blocker_reduction import audit_blocker_reducibility
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_blocker_reduction_audit.json"
INDEX_RE = re.compile(r"I\(([-0-9,]+)\)")


def _read_indices(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if not match:
            continue
        out.append(IntegralIndex(tuple(int(x) for x in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> int:
    print("QEDCalc Q01 blocker-layer reducibility audit")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        return 1

    targets = _read_indices(INPUT)
    family = q01_integral_family()
    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    template_seconds = time.perf_counter() - t0
    t1 = time.perf_counter()
    profile = audit_blocker_reducibility(
        family, targets, templates=templates
    )
    audit_seconds = time.perf_counter() - t1

    payload = {
        "targets": len(targets),
        "unresolved_targets": profile.unresolved_target_count,
        "blockers": profile.blocker_count,
        "dot_one_blockers": profile.dot_one_blocker_count,
        "directly_pivotable_blockers": profile.directly_pivotable_blocker_count,
        "nonpivotable_blockers": profile.nonpivotable_blocker_count,
        "directly_pivotable_fraction": profile.directly_pivotable_fraction,
        "direct_pivot_equations": profile.direct_pivot_equation_count,
        "max_direct_pivot_equations_per_blocker": profile.max_direct_pivot_equations_per_blocker,
        "directly_pivotable_dot_one": profile.directly_pivotable_dot_one_count,
        "nonpivotable_dot_one": profile.nonpivotable_dot_one_count,
        "max_blocker_dot_degree": profile.max_blocker_dot_degree,
        "max_blocker_numerator_degree": profile.max_blocker_numerator_degree,
        "template_build_seconds": template_seconds,
        "audit_seconds": audit_seconds,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"targets: {len(targets)}")
    print(f"unresolved targets: {profile.unresolved_target_count}")
    print(f"blockers: {profile.blocker_count}")
    print(f"dot-one blockers: {profile.dot_one_blocker_count}")
    print(f"directly pivotable blockers: {profile.directly_pivotable_blocker_count}")
    print(f"nonpivotable blockers: {profile.nonpivotable_blocker_count}")
    print(f"direct pivot equations: {profile.direct_pivot_equation_count}")
    print(f"directly pivotable dot-one blockers: {profile.directly_pivotable_dot_one_count}")
    print(f"nonpivotable dot-one blockers: {profile.nonpivotable_dot_one_count}")
    print(f"template build: {template_seconds:.3f} s")
    print(f"blocker reducibility audit: {audit_seconds:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 blocker-layer reducibility audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
