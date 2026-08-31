from __future__ import annotations

import json
import re
import time
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.blocker_reduction import collect_unresolved_blockers
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_pivot_trace import forward_eliminate_mod_p_with_trace
from three_loop.modp_terminal_support import profile_terminal_support_mod_p
from three_loop.sector_local_laporta import largest_blocker_sector
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points
from three_loop.sector_local_target_rescue import unresolved_targets_after_one_hop

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_modp_terminal_support.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")
PRIME = 1000003


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> None:
    print("QEDCalc Q01 mod-p target terminal-support profile")
    family = q01_integral_family()
    targets = load_targets(SOURCE)
    start = time.perf_counter()

    def progress(stage, current=None, total=None):
        elapsed = time.perf_counter() - start
        suffix = ""
        if current is not None and total:
            suffix = f" {current}/{total} ({100.0 * current / total:.1f}%)"
        print(f"[progress {elapsed:9.1f}s] {stage}{suffix}", flush=True)

    templates = build_ibp_derivative_templates(family)
    unresolved = unresolved_targets_after_one_hop(
        family, targets, templates=templates, progress=progress
    )
    blockers = collect_unresolved_blockers(family, targets, templates=templates)
    sector = largest_blocker_sector(family, targets, templates=templates)
    sector_targets = tuple(t for t in unresolved if physical_sector(t) == sector)
    sector_blockers = tuple(b for b in blockers if physical_sector(b) == sector)

    equations = []
    for n, blocker in enumerate(sector_blockers, start=1):
        equations.extend(local_same_seed_equations(family, blocker, templates=templates))
        if n == 1 or n == len(sector_blockers) or n % 10 == 0:
            progress("build blocker IBP equations", n, len(sector_blockers))
    equations = prune_zero_sectors(family, equations)

    point = default_q01_probe_points(family)[0]
    progress("specialize probe coefficients", 1, 1)
    probed = specialize_ibp_system(equations, point)
    probed = _specialize_remaining_symbols_by_name(probed, point)
    trace = forward_eliminate_mod_p_with_trace(probed, PRIME, progress=progress)
    profile = profile_terminal_support_mod_p(trace, sector_targets)
    hist = Counter(record.terminal_count for record in profile.records)

    out = {
        "sector": sector,
        "prime": PRIME,
        "sector_target_count": len(sector_targets),
        "sector_blocker_count": len(sector_blockers),
        "equation_count": len(equations),
        "trace_pivot_count": trace.pivot_count,
        "requested_target_count": profile.requested_target_count,
        "solved_target_count": profile.solved_target_count,
        "unsolved_target_count": profile.unsolved_target_count,
        "distinct_terminal_count": profile.distinct_terminal_count,
        "common_terminal_count": profile.common_terminal_count,
        "min_terminal_count": profile.min_terminal_count,
        "max_terminal_count": profile.max_terminal_count,
        "terminal_count_histogram": dict(sorted(hist.items())),
        "records": [record.__dict__ for record in profile.records],
        "elapsed_seconds": time.perf_counter() - start,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"sector: {sector}")
    print(f"sector targets: {len(sector_targets)}")
    print(f"sector blockers: {len(sector_blockers)}")
    print(f"equations: {len(equations)}")
    print(f"trace pivots: {trace.pivot_count}")
    print(f"solved sector targets: {profile.solved_target_count}")
    print(f"unsolved sector targets: {profile.unsolved_target_count}")
    print(f"distinct non-pivot terminals across solved targets: {profile.distinct_terminal_count}")
    print(f"terminals common to all solved targets: {profile.common_terminal_count}")
    print(f"min terminals per solved target: {profile.min_terminal_count}")
    print(f"max terminals per solved target: {profile.max_terminal_count}")
    print(f"terminal-count histogram: {dict(sorted(hist.items()))}")
    print(f"generated: {OUTPUT}")
    print("Q01 mod-p target terminal-support profile PASS")


if __name__ == "__main__":
    main()
