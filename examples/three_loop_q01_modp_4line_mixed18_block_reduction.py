from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_block_reduction import reduce_block_mod_p, rule_support_signature
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
NUM_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_numerator_residual_audit.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_mixed18_block_reduction.json"
PRIMES = (1000003, 1000033)


def main() -> None:
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))
    num_data = json.loads(NUM_SOURCE.read_text(encoding="utf-8"))

    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    numerator = tuple(IntegralIndex(tuple(p)) for p in num_data["unresolved_indices"])
    if len(dotted) != 9 or len(numerator) != 9:
        raise RuntimeError(
            f"expected 9 dotted + 9 numerator residuals, got {len(dotted)} + {len(numerator)}"
        )
    block = tuple(dict.fromkeys(dotted + numerator))
    if len(block) != 18:
        raise RuntimeError(f"mixed block should contain 18 unique integrals, got {len(block)}")

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    _, seeds = dot_focused_two_neighbor_seeds(
        family,
        dotted,
        templates=templates,
        complexity_margin=1,
    )

    equations = []
    for seed in seeds:
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
    equations = prune_zero_sectors(family, equations)

    point = default_q01_probe_points(family)[0]
    probed = specialize_ibp_system(equations, point)
    probed = _specialize_remaining_symbols_by_name(probed, point)

    reductions = [reduce_block_mod_p(probed, block, prime) for prime in PRIMES]
    signatures = [rule_support_signature(reduction) for reduction in reductions]
    support_stable = all(signature == signatures[0] for signature in signatures[1:])

    out = {
        "sector": num_data["sector"],
        "dotted_count": len(dotted),
        "numerator_count": len(numerator),
        "block_indices": [index.powers for index in block],
        "seed_count": len(seeds),
        "equation_count": len(equations),
        "primes": list(PRIMES),
        "support_stable_across_primes": support_stable,
        "reductions": [
            {
                "prime": reduction.prime,
                "selected_row_count": reduction.selected_row_count,
                "outside_integral_count": reduction.outside_integral_count,
                "rules": [
                    {
                        "target": rule.target,
                        "rhs_term_count": rule.rhs_term_count,
                        "rhs": rule.rhs,
                    }
                    for rule in reduction.rules
                ],
            }
            for reduction in reductions
        ],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line mixed 18-block mod-p reduction")
    print(f"sector: {tuple(num_data['sector'])}")
    print(f"block size: {len(block)}")
    print(f"seeds: {len(seeds)}")
    print(f"equations: {len(equations)}")
    print(f"primes: {PRIMES}")
    print(f"support stable across primes: {support_stable}")
    for reduction in reductions:
        counts = tuple(rule.rhs_term_count for rule in reduction.rules)
        print(
            f"prime {reduction.prime}: selected rows={reduction.selected_row_count}, "
            f"outside integrals={reduction.outside_integral_count}, rhs term counts={counts}"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 four-line mixed 18-block mod-p reduction PASS")


if __name__ == "__main__":
    main()
