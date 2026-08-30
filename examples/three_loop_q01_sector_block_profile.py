from __future__ import annotations

import json
import re
from pathlib import Path
from time import perf_counter

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_block_profile import build_sector_block_profiles

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_sector_block_profile.json"
INDEX_RE = re.compile(r"I\(([-0-9,]+)\)\s*$")


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    targets = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line.strip())
        if match:
            targets.append(IntegralIndex(tuple(int(x) for x in match.group(1).split(","))))
    return tuple(dict.fromkeys(targets))


def main():
    print("QEDCalc Q01 sector-wise blocker distribution profile")
    family = q01_integral_family()
    targets = load_targets(SOURCE)

    t0 = perf_counter()
    templates = build_ibp_derivative_templates(family)
    t1 = perf_counter()
    profiles = build_sector_block_profiles(family, targets, templates=templates)
    t2 = perf_counter()

    total_blockers = sum(profile.blocker_count for profile in profiles)
    total_dot_one = sum(profile.dot_one_count for profile in profiles)
    summary = {
        "diagram_id": "Q01",
        "target_count": len(targets),
        "sector_count": len(profiles),
        "blocker_count": total_blockers,
        "dot_one_blocker_count": total_dot_one,
        "max_blockers_in_sector": max((p.blocker_count for p in profiles), default=0),
        "template_build_seconds": t1 - t0,
        "profile_seconds": t2 - t1,
        "sectors": [
            {
                "sector": list(profile.sector),
                "blocker_count": profile.blocker_count,
                "dot_one_count": profile.dot_one_count,
                "max_dot_degree": profile.max_dot_degree,
                "max_numerator_degree": profile.max_numerator_degree,
                "active_physical_lines": profile.active_physical_lines,
            }
            for profile in profiles
        ],
        "q_zero_taken": False,
    }
    OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"targets: {len(targets)}")
    print(f"blocker sectors: {len(profiles)}")
    print(f"blockers: {total_blockers}")
    print(f"dot-one blockers: {total_dot_one}")
    print(f"max blockers in one sector: {summary['max_blockers_in_sector']}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"sector profile: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 sector-wise blocker distribution profile PASS")


if __name__ == "__main__":
    main()
