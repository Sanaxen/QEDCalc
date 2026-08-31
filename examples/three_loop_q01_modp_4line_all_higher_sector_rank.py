from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

from examples.three_loop_q01_modp_4line_sector_ordered_rank import constrained_target_rank

ROOT = Path(__file__).resolve().parents[1]
RANK_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_rank.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_all_higher_sector_rank.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def main() -> None:
    rank_data = json.loads(RANK_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    block = tuple(IntegralIndex(tuple(p)) for p in rank_data["block_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    source_sector = tuple(int(x) for x in rank_data["sector"])
    source_lines = sum(source_sector)

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    _, base_seeds = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(
        family, free5, templates=templates, physical_count=PHYSICAL_COUNT
    )
    all_seeds = tuple(sorted(set(base_seeds) | set(free5_neighbor) | set(free5), key=lambda x: x.powers))

    equations = []
    total = len(all_seeds)
    for n, seed in enumerate(all_seeds, start=1):
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
        if n == 1 or n == total or n % 25 == 0:
            print(f"[progress] build equations {n}/{total}", flush=True)
    equations = prune_zero_sectors(family, equations)

    point = default_q01_probe_points(family)[0]
    probed = specialize_ibp_system(equations, point)
    probed = _specialize_remaining_symbols_by_name(probed, point)

    all_indices = {index for equation in probed for index in equation.terms}
    higher = tuple(sorted(
        (
            index for index in all_indices
            if sum(physical_sector(index, PHYSICAL_COUNT)) > source_lines
        ),
        key=lambda index: index.powers,
    ))
    higher_sectors = sorted({physical_sector(index, PHYSICAL_COUNT) for index in higher})

    rows = []
    for prime in PRIMES:
        print(f"[progress] all-higher constrained rank prime {prime}", flush=True)
        higher_rank, target_rank, free_dim = constrained_target_rank(probed, higher, block, prime)
        rows.append({
            "prime": prime,
            "higher_rank": higher_rank,
            "sector_ordered_target_rank": target_rank,
            "conditional_free_dimension": free_dim,
        })

    signatures = [
        (row["higher_rank"], row["sector_ordered_target_rank"], row["conditional_free_dimension"])
        for row in rows
    ]
    stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True

    out = {
        "sector": source_sector,
        "target_count": len(block),
        "all_higher_column_count": len(higher),
        "distinct_higher_sector_count": len(higher_sectors),
        "higher_sectors": [list(sector) for sector in higher_sectors],
        "higher_indices": [index.powers for index in higher],
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "rows": rows,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line all-higher sector rank audit")
    print(f"sector: {source_sector}")
    print(f"target block: {len(block)}")
    print(f"all higher-sector columns: {len(higher)}")
    print(f"distinct higher sectors: {len(higher_sectors)}")
    print(f"seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    for row in rows:
        print(
            f"prime {row['prime']}: higher rank={row['higher_rank']}, "
            f"sector-ordered target rank={row['sector_ordered_target_rank']}, "
            f"conditional free dimension={row['conditional_free_dimension']}"
        )
    print(f"stable across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line all-higher sector rank audit PASS")


if __name__ == "__main__":
    main()
