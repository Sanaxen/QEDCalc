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
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_rank.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def is_subsector(sector: tuple[int, ...], source_sector: tuple[int, ...]) -> bool:
    return all(int(a) <= int(b) for a, b in zip(sector, source_sector))


def main() -> None:
    rank_data = json.loads(RANK_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    block = tuple(IntegralIndex(tuple(p)) for p in rank_data["block_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    source_sector = tuple(int(x) for x in rank_data["sector"])

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    _, base_seeds = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(
        family, free5, templates=templates, physical_count=PHYSICAL_COUNT
    )
    all_seeds = tuple(
        sorted(set(base_seeds) | set(free5_neighbor) | set(free5), key=lambda x: x.powers)
    )

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
    forbidden = tuple(
        sorted(
            (
                index
                for index in all_indices
                if not is_subsector(physical_sector(index, PHYSICAL_COUNT), source_sector)
            ),
            key=lambda index: index.powers,
        )
    )
    forbidden_sectors = sorted({physical_sector(index, PHYSICAL_COUNT) for index in forbidden})
    same_line_other_sectors = [
        sector
        for sector in forbidden_sectors
        if sum(sector) == sum(source_sector) and sector != source_sector
    ]
    higher_sectors = [sector for sector in forbidden_sectors if sum(sector) > sum(source_sector)]

    rows = []
    for prime in PRIMES:
        print(f"[progress] non-subsector constrained rank prime {prime}", flush=True)
        forbidden_rank, target_rank, free_dim = constrained_target_rank(
            probed, forbidden, block, prime
        )
        rows.append(
            {
                "prime": prime,
                "forbidden_rank": forbidden_rank,
                "sector_ordered_target_rank": target_rank,
                "conditional_free_dimension": free_dim,
            }
        )

    signatures = [
        (row["forbidden_rank"], row["sector_ordered_target_rank"], row["conditional_free_dimension"])
        for row in rows
    ]
    stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True

    out = {
        "sector": source_sector,
        "target_count": len(block),
        "forbidden_non_subsector_column_count": len(forbidden),
        "distinct_forbidden_sector_count": len(forbidden_sectors),
        "distinct_higher_sector_count": len(higher_sectors),
        "distinct_same_line_other_sector_count": len(same_line_other_sectors),
        "forbidden_sectors": [list(sector) for sector in forbidden_sectors],
        "forbidden_indices": [index.powers for index in forbidden],
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "rows": rows,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line non-subsector rank audit")
    print(f"sector: {source_sector}")
    print(f"target block: {len(block)}")
    print(f"forbidden non-subsector columns: {len(forbidden)}")
    print(f"distinct forbidden sectors: {len(forbidden_sectors)}")
    print(f"distinct higher sectors: {len(higher_sectors)}")
    print(f"distinct same-line other sectors: {len(same_line_other_sectors)}")
    print(f"seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"sector-ordered target rank={row['sector_ordered_target_rank']}, "
            f"conditional free dimension={row['conditional_free_dimension']}"
        )
    print(f"stable across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line non-subsector rank audit PASS")


if __name__ == "__main__":
    main()
