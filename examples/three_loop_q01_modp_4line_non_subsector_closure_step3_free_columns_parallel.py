from __future__ import annotations

import json
import os
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors, specialize_ibp_system
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_local_master_rank import _keep_columns
from three_loop.modp_sector_ordered_reduction import eliminate_forbidden_columns_mod_p
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

from examples.three_loop_q01_modp_4line_non_subsector_rank import is_subsector

ROOT = Path(__file__).resolve().parents[1]
STEP3_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3.json"
FREE41_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step2_free_columns.json"
FREE8_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3_free_columns.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def _free_columns_mod_p(equations, block, prime: int):
    block = tuple(block)
    restricted = _keep_columns(equations, set(block))
    p = int(prime)
    rows = []
    for equation in restricted:
        row = {
            index: int(coeff) % p
            for index, coeff in equation.terms.items()
            if int(coeff) % p
        }
        if row:
            rows.append(row)

    pivot_columns = []
    pivot_row = 0
    for column in block:
        pivot = next(
            (r for r in range(pivot_row, len(rows)) if rows[r].get(column, 0) % p),
            None,
        )
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


def _load_inputs():
    step3 = json.loads(STEP3_SOURCE.read_text(encoding="utf-8"))
    free41_data = json.loads(FREE41_SOURCE.read_text(encoding="utf-8"))
    free8_data = json.loads(FREE8_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    source_sector = tuple(int(x) for x in step3["sector"])
    block = tuple(IntegralIndex(tuple(p)) for p in step3["expanded_block_indices"])
    free41 = tuple(IntegralIndex(tuple(p)) for p in free41_data["rows"][0]["free_indices"])
    free8 = tuple(IntegralIndex(tuple(p)) for p in free8_data["rows"][0]["free_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])

    if len(block) != 5994:
        raise RuntimeError(f"expected 5994 block, got {len(block)}")
    if len(free41) != 41 or len(free8) != 8 or len(free5) != 5 or len(dotted) != 9:
        raise RuntimeError(
            "seed-layer reconstruction inputs have unexpected sizes: "
            f"free41={len(free41)}, free8={len(free8)}, free5={len(free5)}, dotted={len(dotted)}"
        )
    return source_sector, block, free41, free8, free5, dotted


def _build_probed_system():
    source_sector, block, free41, free8, free5, dotted = _load_inputs()
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)

    started = time.perf_counter()
    _, base_seed_layer = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(
        family, free5, templates=templates, physical_count=PHYSICAL_COUNT
    )
    free8_neighbor = focused_neighbor_seeds(
        family, free8, templates=templates, physical_count=PHYSICAL_COUNT
    )
    free41_neighbor = focused_neighbor_seeds(
        family, free41, templates=templates, physical_count=PHYSICAL_COUNT
    )
    all_seeds = tuple(
        sorted(
            set(base_seed_layer)
            | set(free5_neighbor)
            | set(free5)
            | set(free8_neighbor)
            | set(free8)
            | set(free41_neighbor)
            | set(free41),
            key=lambda x: x.powers,
        )
    )
    seed_seconds = time.perf_counter() - started

    if len(all_seeds) != 3520:
        raise RuntimeError(f"expected 3520 seeds, got {len(all_seeds)}")

    started = time.perf_counter()
    equations = []
    for seed in all_seeds:
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
    equations = prune_zero_sectors(family, equations)
    equation_seconds = time.perf_counter() - started

    if len(equations) != 52800:
        raise RuntimeError(f"expected 52800 equations, got {len(equations)}")

    started = time.perf_counter()
    point = default_q01_probe_points(family)[0]
    probed = specialize_ibp_system(equations, point)
    probed = _specialize_remaining_symbols_by_name(probed, point)
    specialize_seconds = time.perf_counter() - started

    started = time.perf_counter()
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
    forbidden_seconds = time.perf_counter() - started

    if len(forbidden) != 38658:
        raise RuntimeError(f"expected 38658 forbidden columns, got {len(forbidden)}")

    timings = {
        "seed_seconds": seed_seconds,
        "equation_build_seconds": equation_seconds,
        "specialize_seconds": specialize_seconds,
        "forbidden_scan_seconds": forbidden_seconds,
    }
    return source_sector, block, forbidden, probed, timings


def _prime_worker(prime: int):
    worker_started = time.perf_counter()
    source_sector, block, forbidden, probed, setup_timings = _build_probed_system()

    started = time.perf_counter()
    residual, forbidden_rank = eliminate_forbidden_columns_mod_p(probed, forbidden, int(prime))
    eliminate_seconds = time.perf_counter() - started

    started = time.perf_counter()
    target_rank, free = _free_columns_mod_p(residual, block, int(prime))
    free_column_seconds = time.perf_counter() - started

    return {
        "prime": int(prime),
        "pid": os.getpid(),
        "sector": source_sector,
        "block_count": len(block),
        "forbidden_count": len(forbidden),
        "equation_count": len(probed),
        "forbidden_rank": forbidden_rank,
        "target_rank": target_rank,
        "free_dimension": len(free),
        "free_indices": [index.powers for index in free],
        "timings": {
            **setup_timings,
            "forbidden_elimination_seconds": eliminate_seconds,
            "free_column_seconds": free_column_seconds,
            "worker_total_seconds": time.perf_counter() - worker_started,
        },
    }


def main() -> None:
    wall_started = time.perf_counter()
    config = load_runtime_config(root=ROOT, max_useful_processes=len(PRIMES))
    print("QEDCalc Q01 four-line closure step3 free-column audit")
    print(format_runtime_config(config), flush=True)
    print("note: each finite-field worker reconstructs its own 3520-seed system on Windows spawn", flush=True)

    jobs = run_process_jobs(
        _prime_worker,
        PRIMES,
        processes=config.effective_processes,
    )
    rows = [dict(item.result) for item in jobs]

    stable = (
        all(row["free_indices"] == rows[0]["free_indices"] for row in rows[1:])
        if rows
        else True
    )
    wall_seconds = time.perf_counter() - wall_started

    out = {
        "sector": rows[0]["sector"] if rows else None,
        "expanded_block_count": rows[0]["block_count"] if rows else 0,
        "forbidden_non_subsector_count": rows[0]["forbidden_count"] if rows else 0,
        "equation_count": rows[0]["equation_count"] if rows else 0,
        "runtime": {
            "requested_processes": config.requested_processes,
            "effective_processes": config.effective_processes,
            "source": config.source,
            "config_path": config.config_path,
            "wall_seconds": wall_seconds,
        },
        "rows": rows,
        "stable_free_basis_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"sector: {tuple(rows[0]['sector'])}")
    print(f"expanded block: {rows[0]['block_count']}")
    print(f"forbidden non-subsector columns: {rows[0]['forbidden_count']}")
    print(f"equations: {rows[0]['equation_count']}")
    for row in rows:
        t = row["timings"]
        print(
            f"prime {row['prime']}: pid={row['pid']}, forbidden rank={row['forbidden_rank']}, "
            f"target rank={row['target_rank']}, free dimension={row['free_dimension']}, "
            f"worker time={t['worker_total_seconds']:.3f}s"
        )
        print(
            "  timings: "
            f"seeds={t['seed_seconds']:.3f}s, equations={t['equation_build_seconds']:.3f}s, "
            f"specialize={t['specialize_seconds']:.3f}s, forbidden scan={t['forbidden_scan_seconds']:.3f}s, "
            f"forbidden elimination={t['forbidden_elimination_seconds']:.3f}s, "
            f"free columns={t['free_column_seconds']:.3f}s"
        )
        for powers in row["free_indices"]:
            print(f"  I{tuple(powers)}")
    print(f"stable free basis across primes: {stable}")
    print(f"wall time: {wall_seconds:.3f}s")
    print(f"generated: {OUTPUT}")
    if not stable:
        raise RuntimeError("step3 free-column basis differs across primes")
    print("Q01 four-line closure step3 free-column audit PASS")


if __name__ == "__main__":
    main()
