"""Audit why unresolved Q01 target integrals fail to become local pivots."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

from qedcalc.operations.ibp import IntegralIndex
from three_loop import q01_integral_family
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.pivot_blockers import audit_pivot_blockers


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_pivot_blockers.json"


def _load_indices(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    pattern = re.compile(r"I\(([-0-9,]+)\)\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.search(line.strip())
        if not match:
            continue
        out.append(IntegralIndex(tuple(int(x) for x in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> int:
    print("QEDCalc Q01 unresolved pivot-blocker audit")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_integral_map.bat first.")
        return 1

    targets = _load_indices(INPUT)
    family = q01_integral_family()

    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    template_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    profile = audit_pivot_blockers(family, targets, templates=templates)
    audit_seconds = time.perf_counter() - t1

    payload = {
        "target_count": profile.target_count,
        "unresolved_target_count": profile.unresolved_target_count,
        "blocked_equation_count": profile.blocked_equation_count,
        "blocker_index_count": profile.blocker_index_count,
        "blocker_same_sector_count": profile.blocker_same_sector_count,
        "blocker_higher_sector_count": profile.blocker_higher_sector_count,
        "blocker_higher_dot_count": profile.blocker_higher_dot_count,
        "blocker_higher_numerator_count": profile.blocker_higher_numerator_count,
        "max_blocker_dot_degree": profile.max_blocker_dot_degree,
        "max_blocker_numerator_degree": profile.max_blocker_numerator_degree,
        "template_build_seconds": template_seconds,
        "audit_seconds": audit_seconds,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"targets: {profile.target_count}")
    print(f"unresolved targets: {profile.unresolved_target_count}")
    print(f"blocked equations: {profile.blocked_equation_count}")
    print(f"unique blocker integrals: {profile.blocker_index_count}")
    print(f"blockers in same sector: {profile.blocker_same_sector_count}")
    print(f"blockers in higher/different sector: {profile.blocker_higher_sector_count}")
    print(f"blockers with higher dot degree: {profile.blocker_higher_dot_count}")
    print(f"blockers with higher numerator degree: {profile.blocker_higher_numerator_count}")
    print(f"max blocker dot degree: {profile.max_blocker_dot_degree}")
    print(f"max blocker numerator degree: {profile.max_blocker_numerator_degree}")
    print(f"template build: {template_seconds:.3f} s")
    print(f"blocker audit: {audit_seconds:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 unresolved pivot-blocker audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
