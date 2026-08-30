from __future__ import annotations

import json
import re
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_local_laporta import audit_sector_local_laporta

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_sector_local_laporta_audit.json"
PATTERN = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PATTERN.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(x.strip()) for x in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main():
    print("QEDCalc Q01 largest-sector local Laporta audit")
    family = q01_integral_family()
    targets = load_targets(INPUT)
    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    t1 = time.perf_counter()
    profile = audit_sector_local_laporta(family, targets, templates=templates)
    t2 = time.perf_counter()

    payload = {
        "targets": len(targets),
        "sector": list(profile.sector),
        "blockers": profile.blocker_count,
        "dot_one_blockers": profile.dot_one_blocker_count,
        "equations": profile.equation_count,
        "rules": profile.rule_count,
        "solved_blockers": profile.solved_blocker_count,
        "unsolved_blockers": profile.unsolved_blocker_count,
        "solved_dot_one": profile.solved_dot_one_count,
        "unsolved_dot_one": profile.unsolved_dot_one_count,
        "template_build_seconds": t1 - t0,
        "sector_laporta_seconds": t2 - t1,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"targets: {len(targets)}")
    print(f"sector: {profile.sector}")
    print(f"blockers: {profile.blocker_count}")
    print(f"dot-one blockers: {profile.dot_one_blocker_count}")
    print(f"equations: {profile.equation_count}")
    print(f"rules: {profile.rule_count}")
    print(f"solved blockers: {profile.solved_blocker_count}")
    print(f"unsolved blockers: {profile.unsolved_blocker_count}")
    print(f"solved dot-one blockers: {profile.solved_dot_one_count}")
    print(f"unsolved dot-one blockers: {profile.unsolved_dot_one_count}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"sector Laporta: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 largest-sector local Laporta audit PASS")


if __name__ == "__main__":
    main()
