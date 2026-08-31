from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_local_master_rank import _keep_columns, _modp_rank
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
NUM_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_numerator_residual_audit.json"
RHS_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_mixed18_rhs_structure.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_expanded48_rank.json"
PRIMES = (1000003, 1000033)


def main() -> None:
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))
    num_data = json.loads(NUM_SOURCE.read_text(encoding="utf-8"))
    rhs_data = json.loads(RHS_SOURCE.read_text(encoding="utf-8"))

    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    numerator = tuple(IntegralIndex(tuple(p)) for p in num_data["unresolved_indices"])
    same_rhs = tuple(IntegralIndex(tuple(p)) for p in rhs_data["same_sector_indices"])

    if len(dotted) != 9 or len(numerator) != 9 or len(same_rhs) != 30:
        raise RuntimeError(
            f"expected 9 dotted + 9 numerator + 30 same-sector RHS, got "
            f"{len(dotted)} + {len(numerator)} + {len(same_rhs)}"
        )

    block = tuple(dict.fromkeys(dotted + numerator + same_rhs))
    if len(block) != 48:
        raise RuntimeError(f"expanded block expected 48 distinct integrals, got {len(block)}")

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    _, seeds = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    equations = []
    for seed in seeds:
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
    equations = prune_zero_sectors(family, equations)

    point = default_q01_probe_points(family)[0]
    probed = specialize_ibp_system(equations, point)
    probed = _specialize_remaining_symbols_by_name(probed, point)
    restricted = _keep_columns(probed, set(block))

    full_ranks = tuple(_modp_rank(probed, prime) for prime in PRIMES)
    restricted_ranks = tuple(_modp_rank(restricted, prime) for prime in PRIMES)
    free_dimensions = tuple(len(block) - rank for rank in restricted_ranks)
    stable = len(set(zip(full_ranks, restricted_ranks, free_dimensions))) == 1

    out = {
        "sector": rhs_data["source_sector"],
        "dotted_count": len(dotted),
        "numerator_count": len(numerator),
        "same_rhs_count": len(same_rhs),
        "block_indices": [idx.powers for idx in block],
        "block_size": len(block),
        "seed_count": len(seeds),
        "equation_count": len(equations),
        "integral_count": len({idx for eq in equations for idx in eq.terms}),
        "primes": list(PRIMES),
        "full_ranks": full_ranks,
        "restricted_ranks": restricted_ranks,
        "conditional_free_dimensions": free_dimensions,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line expanded 48-block rank audit")
    print(f"sector: {tuple(rhs_data['source_sector'])}")
    print(f"dotted residuals: {len(dotted)}")
    print(f"numerator residuals: {len(numerator)}")
    print(f"same-sector RHS additions: {len(same_rhs)}")
    print(f"expanded block size: {len(block)}")
    print(f"seeds: {len(seeds)}")
    print(f"equations: {len(equations)}")
    print(f"full ranks: {full_ranks}")
    print(f"restricted expanded-block ranks: {restricted_ranks}")
    print(f"conditional free dimensions: {free_dimensions}")
    print(f"stable across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line expanded 48-block rank audit PASS")


if __name__ == "__main__":
    main()
