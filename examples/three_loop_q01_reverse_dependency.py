"""Audit one-hop rescue seeds for Q01 nonpivotable targets."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.reverse_dependency import audit_reverse_dependencies

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_reverse_dependency_audit.json"


def _read_indices(path: Path) -> tuple[IntegralIndex, ...]:
    indices = []
    pattern = re.compile(r"I\(([-0-9,]+)\)\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.search(line.strip())
        if match:
            indices.append(IntegralIndex(tuple(int(x) for x in match.group(1).split(","))))
    return tuple(dict.fromkeys(indices))


def main() -> int:
    print("QEDCalc Q01 reverse one-hop dependency audit")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        return 1
    targets = _read_indices(INPUT)
    family = q01_integral_family()
    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    template_seconds = time.perf_counter() - t0
    t1 = time.perf_counter()
    profile = audit_reverse_dependencies(family, targets, templates=templates)
    audit_seconds = time.perf_counter() - t1
    payload = {
        "target_count": profile.target_count,
        "nonpivotable_target_count": profile.nonpivotable_target_count,
        "rescued_target_count": profile.rescued_target_count,
        "unresolved_target_count": profile.unresolved_target_count,
        "unique_rescue_seed_count": profile.unique_rescue_seed_count,
        "candidate_seed_count": profile.candidate_seed_count,
        "rescue_equation_count": profile.rescue_equation_count,
        "max_rescue_equations_per_target": profile.max_rescue_equations_per_target,
        "template_build_seconds": template_seconds,
        "audit_seconds": audit_seconds,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"targets: {profile.target_count}")
    print(f"nonpivotable targets: {profile.nonpivotable_target_count}")
    print(f"rescued targets: {profile.rescued_target_count}")
    print(f"unresolved targets: {profile.unresolved_target_count}")
    print(f"candidate predecessor seeds: {profile.candidate_seed_count}")
    print(f"unique rescue seeds: {profile.unique_rescue_seed_count}")
    print(f"rescue equations: {profile.rescue_equation_count}")
    print(f"max rescue equations per target: {profile.max_rescue_equations_per_target}")
    print(f"template build: {template_seconds:.3f} s")
    print(f"reverse audit: {audit_seconds:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 reverse one-hop dependency audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
