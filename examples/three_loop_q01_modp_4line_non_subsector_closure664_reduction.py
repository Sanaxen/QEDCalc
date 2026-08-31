from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_block_reduction import rule_support_signature
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_sector_ordered_reduction import reduce_block_sector_ordered_mod_p
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

from examples.three_loop_q01_modp_4line_non_subsector_rank import is_subsector

ROOT = Path(__file__).resolve().parents[1]
CLOSURE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step1.json"
FREE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure664_reduction.json"
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
    all_seeds = tuple(sorted(base_seeds | set(free8_neighbor) | set(free8), key=lambda x: x.powers))

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

    reductions = []
    for run_no, prime in enumerate(PRIMES, start=1):
        print(
            f"[progress] closure664 non-subsector reduction prime {prime} "
            f"({run_no}/{len(PRIMES)})",
            flush=True,
        )
        reductions.append(reduce_block_sector_ordered_mod_p(probed, block, forbidden, prime))

    signatures = [rule_support_signature(item.block_reduction) for item in reductions]
    support_stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True

    rows = []
    all_non_subsector_zero = True
    for item in reductions:
        reduction = item.block_reduction
        rhs_indices = {
            IntegralIndex(tuple(rhs_index))
            for rule in reduction.rules
            for rhs_index, coeff in rule.rhs
            if int(coeff) != 0
        }
        bad_rhs = tuple(
            sorted(
                (
                    index
                    for index in rhs_indices
                    if not is_subsector(physical_sector(index, PHYSICAL_COUNT), source_sector)
                ),
                key=lambda index: index.powers,
            )
        )
        if bad_rhs:
            all_non_subsector_zero = False
        counts = tuple(rule.rhs_term_count for rule in reduction.rules)
        rows.append(
            {
                "prime": item.prime,
                "forbidden_count": item.forbidden_count,
                "forbidden_rank": item.forbidden_rank,
                "residual_equation_count": item.residual_equation_count,
                "selected_row_count": reduction.selected_row_count,
                "outside_integral_count": reduction.outside_integral_count,
                "non_subsector_rhs_count": len(bad_rhs),
                "non_subsector_rhs_indices": [index.powers for index in bad_rhs],
                "rhs_term_count_min": min(counts, default=0),
                "rhs_term_count_max": max(counts, default=0),
                "rules": [
                    {
                        "target": rule.target,
                        "rhs_term_count": rule.rhs_term_count,
                        "rhs": rule.rhs,
                    }
                    for rule in reduction.rules
                ],
            }
        )

    out = {
        "sector": source_sector,
        "target_count": len(block),
        "forbidden_non_subsector_count": len(forbidden),
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "primes": list(PRIMES),
        "support_stable_across_primes": support_stable,
        "all_non_subsector_rhs_zero": all_non_subsector_zero,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line closure664 non-subsector mod-p reduction")
    print(f"sector: {source_sector}")
    print(f"target block: {len(block)}")
    print(f"forbidden non-subsector columns: {len(forbidden)}")
    print(f"seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    print(f"support stable across primes: {support_stable}")
    print(f"all non-subsector RHS zero: {all_non_subsector_zero}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"residual equations={row['residual_equation_count']}, "
            f"selected rows={row['selected_row_count']}, "
            f"outside integrals={row['outside_integral_count']}, "
            f"non-subsector RHS={row['non_subsector_rhs_count']}, "
            f"rhs term count min/max=({row['rhs_term_count_min']}, {row['rhs_term_count_max']})"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 four-line closure664 non-subsector mod-p reduction PASS")


if __name__ == "__main__":
    main()
