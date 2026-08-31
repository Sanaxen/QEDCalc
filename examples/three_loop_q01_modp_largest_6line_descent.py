from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.modp_sector_descent import audit_modp_sector_descent
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_terminal_structure.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_largest_6line_descent.json"
TARGET_SECTOR = (1, 0, 1, 0, 1, 1, 1, 1, 0)
PRIME = 1000003


def main() -> None:
    print("QEDCalc Q01 largest 6-line mod-p sector descent")
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    targets = tuple(
        IntegralIndex(tuple(row["index"]))
        for row in data["records"]
        if tuple(row["sector"]) == TARGET_SECTOR
    )
    targets = tuple(dict.fromkeys(targets))

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    point = default_q01_probe_points(family)[0]
    start = time.perf_counter()

    def progress(stage, current=None, total=None):
        elapsed = time.perf_counter() - start
        suffix = ""
        if current is not None and total:
            suffix = f" {current}/{total} ({100.0 * current / total:.1f}%)"
        print(f"[progress {elapsed:9.1f}s] {stage}{suffix}", flush=True)

    profile = audit_modp_sector_descent(
        family,
        targets,
        probe_point=point,
        prime=PRIME,
        templates=templates,
        progress=progress,
    )

    out = profile.__dict__ | {"elapsed_seconds": time.perf_counter() - start}
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"sector: {profile.sector}")
    print(f"targets: {profile.target_count}")
    print(f"equations: {profile.equation_count}")
    print(f"integrals: {profile.integral_count}")
    print(f"trace pivots: {profile.pivot_count}")
    print(f"solved targets: {profile.solved_target_count}")
    print(f"unsolved targets: {profile.unsolved_target_count}")
    print(f"distinct terminals: {profile.distinct_terminal_count}")
    print(f"same-sector terminals: {profile.same_sector_terminal_count}")
    print(f"lower-sector terminals: {profile.lower_sector_terminal_count}")
    print(f"higher/other-sector terminals: {profile.higher_or_other_sector_terminal_count}")
    print(f"distinct lower sectors: {profile.lower_sector_count}")
    print(f"largest lower-sector terminal count: {profile.largest_lower_sector_terminal_count}")
    print(f"generated: {OUTPUT}")
    print("Q01 largest 6-line mod-p sector descent PASS")


if __name__ == "__main__":
    main()
