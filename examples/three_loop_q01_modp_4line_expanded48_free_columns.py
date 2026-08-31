from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_local_master_rank import _keep_columns
from three_loop.sector_local_modp import _rational_mod_p, _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_rank.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
PRIMES = (1000003, 1000033)


def pivot_and_free_columns(equations, block, prime):
    p = int(prime)
    rows = []
    for equation in equations:
        row = [int(_rational_mod_p(equation.terms.get(index, 0), p)) % p for index in block]
        if any(row):
            rows.append(row)

    pivot_columns = []
    pivot_row = 0
    width = len(block)
    for col in range(width):
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
        pivot_columns.append(col)
        pivot_row += 1
        if pivot_row == len(rows):
            break

    pivot_set = set(pivot_columns)
    free_columns = tuple(col for col in range(width) if col not in pivot_set)
    return tuple(pivot_columns), free_columns


def main() -> None:
    rank_data = json.loads(SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))
    block = tuple(IntegralIndex(tuple(p)) for p in rank_data["block_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    if len(block) != 48 or len(dotted) != 9:
        raise RuntimeError(f"expected 48 block indices and 9 dotted seeds, got {len(block)} and {len(dotted)}")

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

    rows = []
    for prime in PRIMES:
        pivots, free = pivot_and_free_columns(restricted, block, prime)
        rows.append({
            "prime": prime,
            "rank": len(pivots),
            "pivot_columns": list(pivots),
            "free_columns": list(free),
            "free_indices": [block[col].powers for col in free],
        })

    stable = all(row["free_indices"] == rows[0]["free_indices"] for row in rows[1:])
    out = {
        "sector": rank_data["sector"],
        "block_size": len(block),
        "primes": list(PRIMES),
        "stable_free_basis_across_primes": stable,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line expanded 48-block free-column audit")
    print(f"sector: {tuple(rank_data['sector'])}")
    print(f"block size: {len(block)}")
    for row in rows:
        print(f"prime {row['prime']}: rank={row['rank']}, free columns={len(row['free_columns'])}")
        for powers in row["free_indices"]:
            print(f"  free I{tuple(powers)}")
    print(f"stable free basis across primes: {stable}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line expanded 48-block free-column audit PASS")


if __name__ == "__main__":
    main()
