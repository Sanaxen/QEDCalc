from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_local_master_rank import _keep_columns
from three_loop.modp_sector_ordered_reduction import eliminate_forbidden_columns_mod_p
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
CLOSURE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step2.json"
FREE8_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
FREE8_NEIGHBOR_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free8_neighbor_rank.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step2_free_columns.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def _free_columns_mod_p(equations, block, prime: int):
    block = tuple(block)
    restricted = _keep_columns(equations, set(block))
    p = int(prime)
    rows = []
    for equation in restricted:
        row = {index: int(coeff) % p for index, coeff in equation.terms.items() if int(coeff) % p}
        if row:
            rows.append(row)
    pivot_columns = []
    pivot_row = 0
    for column in block:
        pivot = next((r for r in range(pivot_row, len(rows)) if rows[r].get(column, 0) % p), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        lead = rows[pivot_row][column] % p
        inv = pow(lead, -1, p)
        rows[pivot_row] = {
            index: (value * inv) % p
            for index, value in rows[pivot_row].items()
            if (value * inv) % p
        }
        pivot_data = rows[pivot_row]
        for r in range(len(rows)):
            if r == pivot_row:
                continue
            coeff = rows[r].get(column, 0) % p
            if not coeff:
                continue
            work = dict(rows[r])
            for index, value in pivot_data.items():
                new_value = (work.get(index, 0) - coeff * value) % p
                if new_value:
                    work[index] = new_value
                else:
                    work.pop(index, None)
            rows[r] = work
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    pivot_set = set(pivot_columns)
    free = tuple(index for index in block if index not in pivot_set)
    return len(pivot_columns), free


def main() -> None:
    closure_data = json.loads(CLOSURE_SOURCE.read_text(encoding="utf-8"))
    free8_data = json.loads(FREE8_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))
    neighbor_data = json.loads(FREE8_NEIGHBOR_SOURCE.read_text(encoding="utf-8"))

    block = tuple(IntegralIndex(tuple(p)) for p in closure_data["expanded_block_indices"])
    free8 = tuple(IntegralIndex(tuple(p)) for p in free8_data["rows"][0]["free_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    forbidden = tuple(IntegralIndex(tuple(p)) for p in closure_data["forbidden_indices"])

    if len(block) != 1850:
        raise RuntimeError(f"expected 1850 block, got {len(block)}")

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

    expected_seeds = int(neighbor_data["total_seed_count"])
    if len(all_seeds) != expected_seeds:
        raise RuntimeError(f"seed reconstruction mismatch: {len(all_seeds)} != {expected_seeds}")

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
        print(f"[progress] closure step2 free-column audit prime {prime}", flush=True)
        residual, forbidden_rank = eliminate_forbidden_columns_mod_p(probed, forbidden, prime)
        target_rank, free = _free_columns_mod_p(residual, block, prime)
        rows.append({
            "prime": prime,
            "forbidden_rank": forbidden_rank,
            "target_rank": target_rank,
            "free_dimension": len(free),
            "free_indices": [index.powers for index in free],
        })

    stable = all(row["free_indices"] == rows[0]["free_indices"] for row in rows[1:]) if rows else True
    out = {
        "sector": closure_data["sector"],
        "expanded_block_count": len(block),
        "forbidden_non_subsector_count": len(forbidden),
        "seed_count": len(all_seeds),
        "equation_count": len(equations),
        "rows": rows,
        "stable_free_basis_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line closure step2 free-column audit")
    print(f"sector: {tuple(closure_data['sector'])}")
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
    print("Q01 four-line closure step2 free-column audit PASS")


if __name__ == "__main__":
    main()
