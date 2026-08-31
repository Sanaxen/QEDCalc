from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_local_master_rank import _keep_columns, _modp_rank
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
RANK_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_rank.json"
FREE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_free5_neighbor_rank.json"
PRIMES = (1000003, 1000033)


def main() -> None:
    rank_data = json.loads(RANK_SOURCE.read_text(encoding="utf-8"))
    free_data = json.loads(FREE_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    block = tuple(IntegralIndex(tuple(p)) for p in rank_data["block_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    rows = free_data["rows"]
    if not rows or not free_data["stable_free_basis_across_primes"]:
        raise RuntimeError("free-column basis is not stable across primes")
    free5 = tuple(IntegralIndex(tuple(p)) for p in rows[0]["free_indices"])

    if len(block) != 48 or len(dotted) != 9 or len(free5) != 5:
        raise RuntimeError(
            f"expected 48 block, 9 dotted seeds, 5 free candidates; got "
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
    all_seeds = tuple(sorted(set(base_seeds) | set(free5_neighbor) | set(free5), key=lambda x: x.powers))
    added_seeds = set(all_seeds) - set(base_seeds)

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
    restricted = _keep_columns(probed, set(block))

    full_ranks = tuple(_modp_rank(probed, prime) for prime in PRIMES)
    restricted_ranks = tuple(_modp_rank(restricted, prime) for prime in PRIMES)
    free_dimensions = tuple(len(block) - rank for rank in restricted_ranks)
    stable = len(set(zip(full_ranks, restricted_ranks, free_dimensions))) == 1

    out = {
        "sector": rank_data["sector"],
        "block_size": len(block),
        "free_candidate_indices": [idx.powers for idx in free5],
        "base_seed_count": len(base_seeds),
        "free5_neighbor_seed_count": len(free5_neighbor),
        "added_seed_count": len(added_seeds),
        "total_seed_count": len(all_seeds),
        "equation_count": len(equations),
        "integral_count": len({idx for eq in equations for idx in eq.terms}),
        "primes": list(PRIMES),
        "full_ranks": full_ranks,
        "restricted_ranks": restricted_ranks,
        "conditional_free_dimensions": free_dimensions,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line free-five neighbor rank audit")
    print(f"sector: {tuple(rank_data['sector'])}")
    print(f"expanded block size: {len(block)}")
    print(f"free candidates: {len(free5)}")
    print(f"base seeds: {len(base_seeds)}")
    print(f"free-five neighbor seeds: {len(free5_neighbor)}")
    print(f"newly added seeds: {len(added_seeds)}")
    print(f"total seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    print(f"full ranks: {full_ranks}")
    print(f"restricted 48-block ranks: {restricted_ranks}")
    print(f"conditional free dimensions: {free_dimensions}")
    print(f"stable across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line free-five neighbor rank audit PASS")


if __name__ == "__main__":
    main()
