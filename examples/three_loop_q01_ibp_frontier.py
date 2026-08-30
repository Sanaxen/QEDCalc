"""Profile the one-step IBP frontier of the saved Q01 target integral set."""
from __future__ import annotations

import json
from pathlib import Path
import re
import time

from qedcalc.operations.ibp import IntegralIndex
from three_loop import q01_integral_family
from three_loop.ibp_frontier import (
    build_ibp_derivative_templates,
    one_step_ibp_frontier,
    profile_ibp_frontier,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_ibp_frontier.txt"
SUMMARY = ROOT / "output" / "3loop_q01_ibp_frontier_summary.json"
INDEX_RE = re.compile(r"I\(([-0-9,]+)\)\s*$")


def _read_indices(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        match = INDEX_RE.search(line)
        if match is None:
            raise ValueError(f"cannot parse integral index at line {line_no}: {line[:120]}")
        powers = tuple(int(part) for part in match.group(1).split(","))
        out.append(IntegralIndex(powers))
    return tuple(out)


def main() -> int:
    print("QEDCalc Q01 one-step IBP frontier")
    if not INPUT.exists():
        print(f"missing input: {INPUT}")
        print("Run run_three_loop_q01_integral_map.bat first.")
        return 1

    seeds = _read_indices(INPUT)
    family = q01_integral_family()

    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    template_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    frontier = one_step_ibp_frontier(family, seeds, templates=templates)
    frontier_seconds = time.perf_counter() - t1
    profile = profile_ibp_frontier(seeds, frontier)

    OUTPUT.write_text(
        "\n".join(f"I({','.join(map(str, index.powers))})" for index in frontier) + "\n",
        encoding="utf-8",
    )
    payload = {
        "diagram_id": "Q01",
        "source_integral_count": profile.seed_count,
        "frontier_integral_count": profile.generated_index_count,
        "new_integral_count": profile.new_index_count,
        "physical_sector_count": profile.physical_sector_count,
        "max_dot_degree": profile.max_dot_degree,
        "max_numerator_degree": profile.max_numerator_degree,
        "max_active_physical_lines": profile.max_active_physical_lines,
        "derivative_template_count": len(templates),
        "elapsed_template_seconds": template_seconds,
        "elapsed_frontier_seconds": frontier_seconds,
        "q_zero_taken": False,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"source integrals: {profile.seed_count}")
    print(f"derivative templates: {len(templates)}")
    print(f"template build: {template_seconds:.3f} s")
    print(f"frontier build: {frontier_seconds:.3f} s")
    print(f"frontier integrals: {profile.generated_index_count}")
    print(f"new integrals: {profile.new_index_count}")
    print(f"physical sectors: {profile.physical_sector_count}")
    print(f"max dot degree: {profile.max_dot_degree}")
    print(f"max numerator degree: {profile.max_numerator_degree}")
    print(f"max active physical lines: {profile.max_active_physical_lines}")
    print(f"generated: {OUTPUT}")
    print(f"generated: {SUMMARY}")
    print("Q01 one-step IBP frontier PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
