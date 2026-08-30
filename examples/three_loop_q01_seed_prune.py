"""Prune the Q01 one-step IBP frontier to a bounded Laporta seed set."""
from __future__ import annotations

import json
from pathlib import Path
import re

from qedcalc.operations.ibp import IntegralIndex
from three_loop import (
    SeedPruningPolicy,
    descendant_sector_closure,
    physical_sector,
    profile_seed_pruning,
    prune_seed_indices,
)


ROOT = Path(__file__).resolve().parents[1]
TARGET_INPUT = ROOT / "output" / "3loop_q01_integral_indices.txt"
FRONTIER_INPUT = ROOT / "output" / "3loop_q01_ibp_frontier.txt"
OUTPUT = ROOT / "output" / "3loop_q01_pruned_seeds.txt"
SUMMARY = ROOT / "output" / "3loop_q01_pruned_seeds_summary.json"

INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def _read_indices(path: Path) -> tuple[IntegralIndex, ...]:
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if not match:
            continue
        powers = tuple(int(piece.strip()) for piece in match.group(1).split(","))
        out.add(IntegralIndex(powers))
    return tuple(sorted(out, key=lambda index: index.powers, reverse=True))


def main() -> int:
    print("QEDCalc Q01 bounded Laporta seed pruning")
    if not TARGET_INPUT.exists():
        print(f"missing input: {TARGET_INPUT}")
        return 1
    if not FRONTIER_INPUT.exists():
        print(f"missing input: {FRONTIER_INPUT}")
        return 1

    targets = _read_indices(TARGET_INPUT)
    frontier = _read_indices(FRONTIER_INPUT)
    target_sectors = {physical_sector(index) for index in targets}
    allowed_sectors = descendant_sector_closure(target_sectors)

    policy = SeedPruningPolicy(
        max_dot_degree=1,
        max_numerator_degree=4,
        allowed_physical_sectors=allowed_sectors,
    )
    accepted = prune_seed_indices(frontier, policy)
    profile = profile_seed_pruning(frontier, policy)

    OUTPUT.write_text(
        "\n".join(f"I({','.join(map(str, index.powers))})" for index in accepted)
        + ("\n" if accepted else ""),
        encoding="utf-8",
    )

    payload = {
        "diagram_id": "Q01",
        "target_integral_count": len(targets),
        "target_sector_count": len(target_sectors),
        "allowed_descendant_sector_count": len(allowed_sectors),
        "frontier_integral_count": len(frontier),
        "policy": {
            "max_dot_degree": 1,
            "max_numerator_degree": 4,
            "sector_rule": "downward closure of target physical sectors",
        },
        "accepted_seed_count": profile.accepted_count,
        "rejected_seed_count": profile.rejected_count,
        "accepted_sector_count": profile.accepted_sector_count,
        "rejected_for_dot_count": profile.rejected_for_dot_count,
        "rejected_for_numerator_count": profile.rejected_for_numerator_count,
        "rejected_for_sector_count": profile.rejected_for_sector_count,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"target integrals: {len(targets)}")
    print(f"target sectors: {len(target_sectors)}")
    print(f"allowed descendant sectors: {len(allowed_sectors)}")
    print(f"frontier integrals: {len(frontier)}")
    print(f"accepted seeds: {profile.accepted_count}")
    print(f"rejected seeds: {profile.rejected_count}")
    print(f"accepted sectors: {profile.accepted_sector_count}")
    print(f"rejected by dot bound: {profile.rejected_for_dot_count}")
    print(f"rejected by numerator bound: {profile.rejected_for_numerator_count}")
    print(f"rejected by sector bound: {profile.rejected_for_sector_count}")
    print(f"generated: {OUTPUT}")
    print(f"generated: {SUMMARY}")
    print("Q01 bounded Laporta seed pruning PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
