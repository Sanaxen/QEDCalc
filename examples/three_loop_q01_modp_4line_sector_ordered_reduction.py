from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_block_reduction import rule_support_signature
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_sector_ordered_reduction import reduce_block_sector_ordered_mod_p
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
RANK_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_rank.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
BLOCK_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_block_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_sector_ordered_reduction.json"
PRIMES = (1000003, 1000033)


def extract_higher_indices(block_data, source_lines: int):
    supports = []
    for reduction in block_data["reductions"]:
        support = {
            tuple(int(x) for x in rhs_index)
            for rule in reduction["rules"]
            for rhs_index, coeff in rule["rhs"]
            if int(coeff) != 0 and sum(1 for x in rhs_index[:9] if int(x) > 0) > source_lines
        }
        supports.append(support)
    if not supports:
        raise RuntimeError("179-block reduction contains no finite-field reductions")
    if any(support != supports[0] for support in supports[1:]):
        raise RuntimeError("higher-sector RHS support differs across primes")
    return tuple(IntegralIndex(powers) for powers in sorted(supports[0]))


def main() -> None:
    rank_data = json.loads(RANK_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))
    block_data = json.loads(BLOCK_SOURCE.read_text(encoding="utf-8"))

    block = tuple(IntegralIndex(tuple(p)) for p in rank_data["block_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    source_sector = tuple(int(x) for x in rank_data["sector"])
    higher = extract_higher_indices(block_data, sum(source_sector))

    if len(block) != 179 or len(dotted) != 9 or len(free5) != 5 or len(higher) != 6:
        raise RuntimeError(
            f"expected 179 targets, 9 dotted seeds, 5 free seeds, 6 higher integrals; got "
            f"{len(block)}, {len(dotted)}, {len(free5)}, {len(higher)}"
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

    ordered = []
    for run_no, prime in enumerate(PRIMES, start=1):
        print(
            f"[progress] sector-ordered 179-block reduction prime {prime} ({run_no}/{len(PRIMES)})",
            flush=True,
        )
        ordered.append(reduce_block_sector_ordered_mod_p(probed, block, higher, prime))

    signatures = [rule_support_signature(item.block_reduction) for item in ordered]
    support_stable = all(signature == signatures[0] for signature in signatures[1:])
    higher_powers = {index.powers for index in higher}
    higher_rhs_counts = []
    for item in ordered:
        count = sum(
            1
            for rule in item.block_reduction.rules
            for rhs_index, coeff in rule.rhs
            if coeff and rhs_index in higher_powers
        )
        higher_rhs_counts.append(count)

    out = {
        "sector": source_sector,
        "block_size": len(block),
        "higher_indices": [index.powers for index in higher],
        "higher_count": len(higher),
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "primes": list(PRIMES),
        "support_stable_across_primes": support_stable,
        "reductions": [
            {
                "prime": item.prime,
                "forbidden_rank": item.forbidden_rank,
                "residual_equation_count": item.residual_equation_count,
                "selected_row_count": item.block_reduction.selected_row_count,
                "outside_integral_count": item.block_reduction.outside_integral_count,
                "higher_rhs_term_count": higher_rhs_count,
                "rules": [
                    {
                        "target": rule.target,
                        "rhs_term_count": rule.rhs_term_count,
                        "rhs": rule.rhs,
                    }
                    for rule in item.block_reduction.rules
                ],
            }
            for item, higher_rhs_count in zip(ordered, higher_rhs_counts)
        ],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line sector-ordered 179-block mod-p reduction")
    print(f"sector: {source_sector}")
    print(f"target block: {len(block)}")
    print(f"forbidden higher-sector columns: {len(higher)}")
    print(f"seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    print(f"support stable across primes: {support_stable}")
    for item, higher_rhs_count in zip(ordered, higher_rhs_counts):
        counts = tuple(rule.rhs_term_count for rule in item.block_reduction.rules)
        print(
            f"prime {item.prime}: forbidden rank={item.forbidden_rank}, "
            f"residual equations={item.residual_equation_count}, "
            f"selected rows={item.block_reduction.selected_row_count}, "
            f"outside integrals={item.block_reduction.outside_integral_count}, "
            f"higher RHS terms={higher_rhs_count}, "
            f"rhs term count min/max=({min(counts, default=0)}, {max(counts, default=0)})"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 four-line sector-ordered 179-block mod-p reduction PASS")


if __name__ == "__main__":
    main()
