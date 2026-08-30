"""Run local 15-equation Laporta elimination for Q01 blocker integrals."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

from qedcalc.operations.ibp import IntegralIndex
from three_loop.blocker_reduction import audit_blocker_reducibility
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import audit_local_block_elimination


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_local_block_elimination_audit.json"
INDEX_RE = re.compile(r"I\(([-0-9,]+)\)")


def read_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if not match:
            continue
        out.append(IntegralIndex(tuple(int(x) for x in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> int:
    print("QEDCalc Q01 local 15-equation blocker elimination audit")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        return 1

    targets = read_targets(INPUT)
    family = q01_integral_family()
    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    template_seconds = time.perf_counter() - t0

    baseline = audit_blocker_reducibility(
        family, targets, templates=templates
    )
    t1 = time.perf_counter()
    profile = audit_local_block_elimination(
        family, targets, templates=templates
    )
    audit_seconds = time.perf_counter() - t1

    payload = {
        "targets": len(targets),
        "unresolved_targets": baseline.unresolved_target_count,
        "blockers": profile.blocker_count,
        "dot_one_blockers": profile.dot_one_blocker_count,
        "single_equation_directly_pivotable_blockers": baseline.directly_pivotable_blocker_count,
        "locally_solved_blockers": profile.locally_solved_blocker_count,
        "locally_unsolved_blockers": profile.locally_unsolved_blocker_count,
        "locally_solved_dot_one_blockers": profile.locally_solved_dot_one_count,
        "locally_unsolved_dot_one_blockers": profile.locally_unsolved_dot_one_count,
        "total_local_equations": profile.total_local_equations,
        "total_local_rules": profile.total_local_rules,
        "max_rules_per_blocker": profile.max_rules_per_blocker,
        "template_build_seconds": template_seconds,
        "audit_seconds": audit_seconds,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"targets: {len(targets)}")
    print(f"unresolved targets: {baseline.unresolved_target_count}")
    print(f"blockers: {profile.blocker_count}")
    print(f"dot-one blockers: {profile.dot_one_blocker_count}")
    print(f"single-equation directly pivotable blockers: {baseline.directly_pivotable_blocker_count}")
    print(f"locally solved blockers: {profile.locally_solved_blocker_count}")
    print(f"locally unsolved blockers: {profile.locally_unsolved_blocker_count}")
    print(f"locally solved dot-one blockers: {profile.locally_solved_dot_one_count}")
    print(f"locally unsolved dot-one blockers: {profile.locally_unsolved_dot_one_count}")
    print(f"total local equations: {profile.total_local_equations}")
    print(f"total local rules: {profile.total_local_rules}")
    print(f"max rules per blocker: {profile.max_rules_per_blocker}")
    print(f"template build: {template_seconds:.3f} s")
    print(f"local elimination audit: {audit_seconds:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 local blocker elimination audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
