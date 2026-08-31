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

from examples.three_loop_q01_modp_4line_non_subsector_rank import is_subsector
from examples.three_loop_q01_modp_4line_sector_ordered_rank import constrained_target_rank

ROOT = Path(__file__).resolve().parents[1]
CLOSURE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step1.json"
FREE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free8_neighbor_rank.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def main() -> None:
    closure_data = json.loads(CLOSURE_SOURCE.read_text(encoding="utf-8"))
    free_data = json.loads(FREE_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    source_sector = tuple(int(x) for x in closure_data["sector"])
    block = tuple(IntegralIndex(tuple(p)) for p in closure_data["expanded_block_indices"])
    free_rows = free_data.get("rows", [])
    if not free_rows or not free_data.get("stable_free_basis_across_primes", False):
        raise RuntimeError("closure free-column basis is not stable across primes")
    free8 = tuple(IntegralIndex(tuple(p)) for p in free_rows[0]["free_indices"])

    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])

    if len(block) != 664 or len(free8) != 8:
        raise RuntimeError(f"expected 664-block and 8 free columns; got {len(block)} and {len(free8)}")

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)

    _, base_seed_layer = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(
        family, free5, templates=templates, physical_count=PHYSICAL_COUNT
    )
    base_seeds = set(base_seed_layer) | set(free5_neighbor) | set(free5)

    free8_neighbor = focused_neighbor_seeds(
        family, free8, templates=templates, physical_count=PHYSICAL_COUNT
    )
    all_seeds = tuple(
        sorted(base_seeds | set(free8_neighbor) | set(free8), key=lambda x: x.powers)
    )
    added_seeds = set(all_seeds) - base_seeds

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

    # Recompute the forbidden set after adding neighbor seeds.  New equations can
    # introduce new non-subsector columns, so reusing the old 5023-column list
    # would not guarantee triangularity.
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

    rows = []
    for prime in PRIMES:
        print(f"[progress] free-eight neighbor constrained rank prime {prime}", flush=True)
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
        "expanded_block_count": len(block),
        "free_candidate_count": len(free8),
        "free_candidate_indices": [index.powers for index in free8],
        "base_seed_count": len(base_seeds),
        "free8_neighbor_seed_count": len(free8_neighbor),
        "added_seed_count": len(added_seeds),
        "total_seed_count": len(all_seeds),
        "equation_count": len(equations),
        "forbidden_non_subsector_count": len(forbidden),
        "distinct_forbidden_sector_count": len(forbidden_sectors),
        "rows": rows,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line closure free-eight neighbor rank audit")
    print(f"sector: {source_sector}")
    print(f"expanded block: {len(block)}")
    print(f"free candidates: {len(free8)}")
    print(f"base seeds: {len(base_seeds)}")
    print(f"free-eight neighbor seeds: {len(free8_neighbor)}")
    print(f"newly added seeds: {len(added_seeds)}")
    print(f"total seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    print(f"forbidden non-subsector columns: {len(forbidden)}")
    print(f"distinct forbidden sectors: {len(forbidden_sectors)}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"sector-ordered target rank={row['sector_ordered_target_rank']}, "
            f"conditional free dimension={row['conditional_free_dimension']}"
        )
    print(f"stable across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line closure free-eight neighbor rank audit PASS")


if __name__ == "__main__":
    main()
