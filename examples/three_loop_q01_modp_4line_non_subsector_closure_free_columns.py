from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_sector_ordered_reduction import eliminate_forbidden_columns_mod_p
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.sector_local_modp import _rational_mod_p, _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
CLOSURE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step1.json"
NON_SUBSECTOR_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_rank.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def target_pivots_mod_p(equations, targets, prime):
    p = int(prime)
    targets = tuple(targets)
    rows = []
    for equation in equations:
        row = [int(_rational_mod_p(equation.terms.get(index, 0), p)) % p for index in targets]
        if any(row):
            rows.append(row)

    pivot_row = 0
    pivot_cols = []
    for col in range(len(targets)):
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
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    free_cols = tuple(i for i in range(len(targets)) if i not in set(pivot_cols))
    return tuple(pivot_cols), free_cols


def main() -> None:
    closure = json.loads(CLOSURE_SOURCE.read_text(encoding="utf-8"))
    non_sub = json.loads(NON_SUBSECTOR_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    block = tuple(IntegralIndex(tuple(p)) for p in closure["expanded_block_indices"])
    forbidden = tuple(IntegralIndex(tuple(p)) for p in non_sub["forbidden_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    _, base_seeds = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(
        family, free5, templates=templates, physical_count=PHYSICAL_COUNT
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
        print(f"[progress] closure free-column audit prime {prime}", flush=True)
        residual, forbidden_rank = eliminate_forbidden_columns_mod_p(probed, forbidden, prime)
        pivot_cols, free_cols = target_pivots_mod_p(residual, block, prime)
        rows.append({
            "prime": prime,
            "forbidden_rank": forbidden_rank,
            "target_rank": len(pivot_cols),
            "free_dimension": len(free_cols),
            "free_column_positions": list(free_cols),
            "free_indices": [block[i].powers for i in free_cols],
        })

    signatures = [tuple(row["free_indices"]) for row in rows]
    stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True

    out = {
        "sector": closure["sector"],
        "block_count": len(block),
        "forbidden_non_subsector_count": len(forbidden),
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "rows": rows,
        "stable_free_basis_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line non-subsector closure free-column audit")
    print(f"sector: {tuple(closure['sector'])}")
    print(f"expanded block: {len(block)}")
    print(f"forbidden non-subsector columns: {len(forbidden)}")
    print(f"seeds: {len(all_seeds)}")
    print(f"equations: {len(equations)}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"target rank={row['target_rank']}, free dimension={row['free_dimension']}"
        )
        for powers in row["free_indices"]:
            print(f"  I{tuple(powers)}")
    print(f"stable free basis across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line non-subsector closure free-column audit PASS")


if __name__ == "__main__":
    main()
