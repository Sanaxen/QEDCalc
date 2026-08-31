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
CLOSURE1_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step1.json"
REDUCTION_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure664_reduction.json"
FREE8_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step2.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def main() -> None:
    closure1 = json.loads(CLOSURE1_SOURCE.read_text(encoding="utf-8"))
    reduction = json.loads(REDUCTION_SOURCE.read_text(encoding="utf-8"))
    free8_data = json.loads(FREE8_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    source_sector = tuple(int(x) for x in closure1["sector"])
    base_block = tuple(IntegralIndex(tuple(p)) for p in closure1["expanded_block_indices"])

    rows = reduction.get("rows", [])
    if not rows:
        raise RuntimeError("closure664 reduction JSON contains no rows")
    supports = []
    for row in rows:
        support = {
            tuple(int(x) for x in rhs_index)
            for rule in row["rules"]
            for rhs_index, coeff in rule["rhs"]
            if int(coeff) != 0
        }
        supports.append(support)
    if any(support != supports[0] for support in supports[1:]):
        raise RuntimeError("closure664 reduction RHS support differs across primes")

    same_rhs = tuple(
        sorted(
            (
                IntegralIndex(powers)
                for powers in supports[0]
                if physical_sector(IntegralIndex(powers), PHYSICAL_COUNT) == source_sector
            ),
            key=lambda index: index.powers,
        )
    )
    base_set = set(base_block)
    new_same = tuple(index for index in same_rhs if index not in base_set)
    expanded_block = tuple(dict.fromkeys(base_block + same_rhs))

    free8_rows = free8_data.get("rows", [])
    if not free8_rows or not free8_data.get("stable_free_basis_across_primes", False):
        raise RuntimeError("closure free-column basis is not stable across primes")
    free8 = tuple(IntegralIndex(tuple(p)) for p in free8_rows[0]["free_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    _, base_seed_layer = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(
        family, free5, templates=templates, physical_count=PHYSICAL_COUNT
    )
    free8_neighbor = focused_neighbor_seeds(
        family, free8, templates=templates, physical_count=PHYSICAL_COUNT
    )
    all_seeds = tuple(
        sorted(
            set(base_seed_layer)
            | set(free5_neighbor)
            | set(free5)
            | set(free8_neighbor)
            | set(free8),
            key=lambda x: x.powers,
        )
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

    result_rows = []
    for prime in PRIMES:
        print(f"[progress] closure step 2 constrained rank prime {prime}", flush=True)
        forbidden_rank, target_rank, free_dim = constrained_target_rank(
            probed, forbidden, expanded_block, prime
        )
        result_rows.append(
            {
                "prime": prime,
                "forbidden_rank": forbidden_rank,
                "sector_ordered_target_rank": target_rank,
                "conditional_free_dimension": free_dim,
            }
        )

    signatures = [
        (row["forbidden_rank"], row["sector_ordered_target_rank"], row["conditional_free_dimension"])
        for row in result_rows
    ]
    stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True

    out = {
        "sector": source_sector,
        "base_block_count": len(base_block),
        "same_sector_rhs_count": len(same_rhs),
        "new_same_sector_count": len(new_same),
        "expanded_block_count": len(expanded_block),
        "expanded_block_indices": [index.powers for index in expanded_block],
        "forbidden_non_subsector_count": len(forbidden),
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "rows": result_rows,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line non-subsector closure step 2")
    print(f"sector: {source_sector}")
    print(f"base block: {len(base_block)}")
    print(f"same-sector RHS support: {len(same_rhs)}")
    print(f"new same-sector integrals: {len(new_same)}")
    print(f"expanded block: {len(expanded_block)}")
    print(f"forbidden non-subsector columns: {len(forbidden)}")
    print(f"seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    for row in result_rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"sector-ordered target rank={row['sector_ordered_target_rank']}, "
            f"conditional free dimension={row['conditional_free_dimension']}"
        )
    print(f"stable across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line non-subsector closure step 2 PASS")


if __name__ == "__main__":
    main()
