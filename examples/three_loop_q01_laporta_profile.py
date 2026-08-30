"""Profile the mapped Q01 target integrals before IBP/Laporta seed expansion."""
from __future__ import annotations

import json
from pathlib import Path
import re

from qedcalc.operations.ibp import IntegralIndex
from three_loop import build_sector_demand_profiles


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_laporta_profile.json"
_INDEX_RE = re.compile(r"I\(([-0-9,]+)\)\s*$")


def _read_indices(path: Path) -> list[IntegralIndex]:
    indices = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        match = _INDEX_RE.search(stripped)
        if not match:
            raise ValueError(f"cannot parse integral index on line {line_no}")
        powers = tuple(int(value) for value in match.group(1).split(","))
        indices.append(IntegralIndex(powers))
    return indices


def main() -> int:
    print("QEDCalc Q01 Laporta demand profile")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_integral_map.bat first.")
        return 1

    indices = _read_indices(INPUT)
    profiles = build_sector_demand_profiles(indices)

    payload_profiles = []
    for profile in profiles:
        payload_profiles.append({
            "sector": list(profile.sector),
            "active_physical_lines": profile.active_physical_lines,
            "target_count": profile.target_count,
            "max_dot_degree": profile.max_dot_degree,
            "max_numerator_degree": profile.max_numerator_degree,
            "max_total_complexity": profile.max_total_complexity,
            "min_powers": list(profile.min_powers),
            "max_powers": list(profile.max_powers),
        })

    payload = {
        "diagram_id": "Q01",
        "source_integral_count": len(indices),
        "sector_count": len(profiles),
        "max_dot_degree": max((p.max_dot_degree for p in profiles), default=0),
        "max_numerator_degree": max((p.max_numerator_degree for p in profiles), default=0),
        "max_total_complexity": max((p.max_total_complexity for p in profiles), default=0),
        "max_active_physical_lines": max((p.active_physical_lines for p in profiles), default=0),
        "sectors": payload_profiles,
        "q_zero_taken": False,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"source integrals: {len(indices)}")
    print(f"physical sectors: {len(profiles)}")
    print(f"max dot degree: {payload['max_dot_degree']}")
    print(f"max numerator degree: {payload['max_numerator_degree']}")
    print(f"max total complexity: {payload['max_total_complexity']}")
    print(f"max active physical lines: {payload['max_active_physical_lines']}")
    print(f"generated: {OUTPUT}")
    print("Q01 Laporta demand profile PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
