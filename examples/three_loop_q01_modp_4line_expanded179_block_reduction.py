from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_block_reduction import reduce_block_mod_p, rule_support_signature
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
RANK_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_rank.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_expanded179_block_reduction.json"
PRIMES = (1000003, 1000033)


def main() -> None:
    rank_data = json.loads(RANK_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    block = tuple(IntegralIndex(tuple(p)) for p in rank_data["block_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    rows = free5_data["rows"]
    if not rows or not free5_data["stable_free_basis_across_primes"]:
        raise RuntimeError("free-five basis is not stable across primes")
    free5 = tuple(IntegralIndex(tuple(p)) for p in rows[0]["free_indices"])
    if len(block) != 179 or len(dotted) != 9 or len(free5) != 5:
        raise RuntimeError(
            f"expected 179 block, 9 dotted seeds, 5 free candidates; got "
            f"{len(block)}, {len(dotted)}, {len(free5)}"
        )

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    _, base_seeds = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(
        family, free5, templates=templates, physical_count=9
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

    reductions = []
    for run_no, prime in enumerate(PRIMES, start=1):
        print(f"[progress] reduce 179-block prime {prime} ({run_no}/{len(PRIMES)})", flush=True)
        reductions.append(reduce_block_mod_p(probed, block, prime))

    signatures = [rule_support_signature(reduction) for reduction in reductions]
    support_stable = all(signature == signatures[0] for signature in signatures[1:])

    out = {
        "sector": rank_data["sector"],
        "block_indices": [idx.powers for idx in block],
        "block_size": len(block),
        "total_seed_count": len(all_seeds),
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

    print("QEDCalc Q01 four-line expanded 179-block mod-p reduction")
    print(f"sector: {tuple(rank_data['sector'])}")
    print(f"block size: {len(block)}")
    print(f"total seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    print(f"primes: {PRIMES}")
    print(f"support stable across primes: {support_stable}")
    for reduction in reductions:
        counts = tuple(rule.rhs_term_count for rule in reduction.rules)
        print(
            f"prime {reduction.prime}: selected rows={reduction.selected_row_count}, "
            f"outside integrals={reduction.outside_integral_count}, "
            f"rhs term count min/max=({min(counts, default=0)}, {max(counts, default=0)})"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 four-line expanded 179-block mod-p reduction PASS")


if __name__ == "__main__":
    main()
