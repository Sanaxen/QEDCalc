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
from three_loop.sector_local_modp import _rational_mod_p, _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
RANK_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_rank.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
REDUCTION_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_block_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_sector_ordered_rank.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def constrained_target_rank(equations, higher, targets, prime):
    """Rank of target columns using only row combinations whose higher columns vanish.

    Row-reduce the higher-column block first. Rows below rank(H) then have zero
    higher entries. Their target-column rank is exactly the rank available to
    solve the target block without leaving any higher-sector terms on the RHS.
    """
    p = int(prime)
    higher = tuple(higher)
    targets = tuple(targets)
    width_h = len(higher)
    rows = []
    for equation in equations:
        h = [int(_rational_mod_p(equation.terms.get(index, 0), p)) % p for index in higher]
        t = [int(_rational_mod_p(equation.terms.get(index, 0), p)) % p for index in targets]
        if any(h) or any(t):
            rows.append(h + t)

    pivot_row = 0
    for col in range(width_h):
        pivot = next((r for r in range(pivot_row, len(rows)) if rows[r][col] % p), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inv = pow(rows[pivot_row][col] % p, -1, p)
        rows[pivot_row] = [(value * inv) % p for value in rows[pivot_row]]
        for r in range(len(rows)):
            if r == pivot_row:
                continue
            coeff = rows[r][col] % p
            if coeff:
                rows[r] = [(a - coeff * b) % p for a, b in zip(rows[r], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    higher_rank = pivot_row

    residual = [row[width_h:] for row in rows[higher_rank:] if any(row[width_h:])]
    target_rank = 0
    for col in range(len(targets)):
        pivot = next((r for r in range(target_rank, len(residual)) if residual[r][col] % p), None)
        if pivot is None:
            continue
        residual[target_rank], residual[pivot] = residual[pivot], residual[target_rank]
        inv = pow(residual[target_rank][col] % p, -1, p)
        residual[target_rank] = [(value * inv) % p for value in residual[target_rank]]
        for r in range(len(residual)):
            if r == target_rank:
                continue
            coeff = residual[r][col] % p
            if coeff:
                residual[r] = [(a - coeff * b) % p for a, b in zip(residual[r], residual[target_rank])]
        target_rank += 1
        if target_rank == len(residual):
            break

    return higher_rank, target_rank, len(targets) - target_rank


def extract_higher_indices(reduction_data, source_sector):
    """Extract stable RHS integrals with more active physical lines than source."""
    source_lines = sum(source_sector)
    reductions = reduction_data.get("reductions", [])
    if not reductions:
        raise RuntimeError("expanded179 reduction JSON contains no reductions")

    supports = []
    for reduction in reductions:
        support = {
            tuple(int(x) for x in rhs_index)
            for rule in reduction["rules"]
            for rhs_index, coeff in rule["rhs"]
            if int(coeff) != 0
        }
        supports.append(support)
    if any(support != supports[0] for support in supports[1:]):
        raise RuntimeError("expanded179 RHS support differs across primes")

    higher = []
    for powers in sorted(supports[0]):
        index = IntegralIndex(powers)
        if sum(physical_sector(index, PHYSICAL_COUNT)) > source_lines:
            higher.append(index)
    return tuple(higher)


def main() -> None:
    rank_data = json.loads(RANK_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))
    reduction_data = json.loads(REDUCTION_SOURCE.read_text(encoding="utf-8"))

    source_sector = tuple(int(x) for x in rank_data["sector"])
    block = tuple(IntegralIndex(tuple(p)) for p in rank_data["block_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    higher = extract_higher_indices(reduction_data, source_sector)

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

    rows = []
    for prime in PRIMES:
        print(f"[progress] sector-ordered rank prime {prime}", flush=True)
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
        "higher_count": len(higher),
        "higher_indices": [index.powers for index in higher],
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "rows": rows,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line sector-ordered rank audit")
    print(f"sector: {source_sector}")
    print(f"target block: {len(block)}")
    print(f"forbidden higher-sector columns: {len(higher)}")
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
    print("Q01 four-line sector-ordered rank audit PASS")


if __name__ == "__main__":
    main()
