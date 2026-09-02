from __future__ import annotations

import json
import os
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex, prune_zero_sectors
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.local_block_elimination import local_same_seed_equations
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from three_loop.modp_sparse_sector_support import sparse_same_sector_support
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config
from three_loop.sector_local_probe import default_q01_probe_points

from examples.three_loop_q01_modp_4line_non_subsector_rank import is_subsector

ROOT = Path(__file__).resolve().parents[1]
STEP3_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3.json"
FREE57_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3_free_columns.json"
FREE41_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step2_free_columns.json"
FREE8_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure5994_same_sector_support.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def _load_inputs():
    step3 = json.loads(STEP3_SOURCE.read_text(encoding="utf-8"))
    free57_data = json.loads(FREE57_SOURCE.read_text(encoding="utf-8"))
    free41_data = json.loads(FREE41_SOURCE.read_text(encoding="utf-8"))
    free8_data = json.loads(FREE8_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))

    source_sector = tuple(int(x) for x in step3["sector"])
    block = tuple(IntegralIndex(tuple(p)) for p in step3["expanded_block_indices"])
    free57 = tuple(IntegralIndex(tuple(p)) for p in free57_data["rows"][0]["free_indices"])
    free41 = tuple(IntegralIndex(tuple(p)) for p in free41_data["rows"][0]["free_indices"])
    free8 = tuple(IntegralIndex(tuple(p)) for p in free8_data["rows"][0]["free_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])

    if len(block) != 5994 or len(free57) != 57:
        raise RuntimeError(f"expected 5994-block and 57 free columns; got {len(block)} and {len(free57)}")
    return source_sector, block, free57, free41, free8, free5, dotted


def _build_system(prime: int):
    source_sector, block, free57, free41, free8, free5, dotted = _load_inputs()
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)

    started = time.perf_counter()
    _, base_seed_layer = dot_focused_two_neighbor_seeds(
        family, dotted, templates=templates, complexity_margin=1
    )
    free5_neighbor = focused_neighbor_seeds(family, free5, templates=templates, physical_count=PHYSICAL_COUNT)
    free8_neighbor = focused_neighbor_seeds(family, free8, templates=templates, physical_count=PHYSICAL_COUNT)
    free41_neighbor = focused_neighbor_seeds(family, free41, templates=templates, physical_count=PHYSICAL_COUNT)
    base_seeds = (
        set(base_seed_layer)
        | set(free5_neighbor) | set(free5)
        | set(free8_neighbor) | set(free8)
        | set(free41_neighbor) | set(free41)
    )
    free57_neighbor = focused_neighbor_seeds(family, free57, templates=templates, physical_count=PHYSICAL_COUNT)
    all_seeds = tuple(sorted(base_seeds | set(free57_neighbor) | set(free57), key=lambda x: x.powers))
    seed_seconds = time.perf_counter() - started

    if len(base_seeds) != 3520 or len(all_seeds) != 7205:
        raise RuntimeError(f"unexpected seed counts: base={len(base_seeds)}, total={len(all_seeds)}")

    print(
        f"[worker pid={os.getpid()} prime={prime}] seeds ready: base={len(base_seeds)}, "
        f"free57-neighbors={len(free57_neighbor)}, total={len(all_seeds)}",
        flush=True,
    )

    started = time.perf_counter()
    equations = []
    total = len(all_seeds)
    for n, seed in enumerate(all_seeds, start=1):
        local = local_same_seed_equations(family, seed, templates=templates)
        local = prune_zero_sectors(family, local)
        equations.extend(local)
        if n == total or n % 500 == 0:
            print(f"[worker pid={os.getpid()} prime={prime}] build equations {n}/{total}", flush=True)
    equation_seconds = time.perf_counter() - started

    if len(equations) != 108075:
        raise RuntimeError(f"expected 108075 equations, got {len(equations)}")

    started = time.perf_counter()
    block_set = set(block)
    all_indices = {index for equation in equations for index in equation.terms}
    forbidden = tuple(sorted(
        (index for index in all_indices if not is_subsector(physical_sector(index, PHYSICAL_COUNT), source_sector)),
        key=lambda index: index.powers,
    ))
    same_sector_outside = tuple(sorted(
        (
            index for index in all_indices
            if index not in block_set
            and physical_sector(index, PHYSICAL_COUNT) == source_sector
        ),
        key=lambda index: index.powers,
    ))
    scan_seconds = time.perf_counter() - started

    print(
        f"[worker pid={os.getpid()} prime={prime}] columns scanned: forbidden={len(forbidden)}, "
        f"same-sector-outside={len(same_sector_outside)}",
        flush=True,
    )

    return (
        source_sector, block, forbidden, same_sector_outside, equations,
        {"seed_seconds": seed_seconds, "equation_build_seconds": equation_seconds, "column_scan_seconds": scan_seconds},
    )


def _prime_worker(prime: int):
    worker_started = time.perf_counter()
    source_sector, block, forbidden, outside, equations, setup = _build_system(prime)
    family = q01_integral_family()
    point = default_q01_probe_points(family)[0]

    print(f"[worker pid={os.getpid()} prime={prime}] sparse same-sector support start", flush=True)
    started = time.perf_counter()
    result = sparse_same_sector_support(
        equations,
        forbidden,
        block,
        outside,
        int(prime),
        probe_point=point,
    )
    support_seconds = time.perf_counter() - started
    print(
        f"[worker pid={os.getpid()} prime={prime}] sparse support done: "
        f"target_rank={result.target_rank}, free={result.conditional_free_dimension}, "
        f"same-sector-support={len(result.same_sector_support)}",
        flush=True,
    )

    return {
        "prime": int(prime),
        "pid": os.getpid(),
        "sector": source_sector,
        "block_count": len(block),
        "equation_count": len(equations),
        "forbidden_non_subsector_count": len(forbidden),
        "same_sector_outside_candidate_count": len(outside),
        "forbidden_rank": result.forbidden_rank,
        "target_rank": result.target_rank,
        "conditional_free_dimension": result.conditional_free_dimension,
        "selected_row_count": result.selected_row_count,
        "same_sector_support_count": len(result.same_sector_support),
        "same_sector_support_indices": [index.powers for index in result.same_sector_support],
        "sparse_projection": {
            "projected_nonzero_row_count": result.projected_nonzero_row_count,
            "projected_term_count": result.projected_term_count,
            "residual_row_count": result.residual_row_count,
        },
        "timings": {
            **setup,
            "same_sector_support_seconds": support_seconds,
            "worker_total_seconds": time.perf_counter() - worker_started,
        },
    }


def main() -> None:
    wall_started = time.perf_counter()
    config = load_runtime_config(root=ROOT, max_useful_processes=len(PRIMES))
    print("QEDCalc Q01 four-line closure5994 sparse same-sector support audit")
    print(format_runtime_config(config), flush=True)
    print("memory-saving mode: no 5994x5994 inverse is constructed", flush=True)

    jobs = run_process_jobs(_prime_worker, PRIMES, processes=config.effective_processes)
    rows = [dict(job.result) for job in jobs]
    support_signatures = [tuple(tuple(p) for p in row["same_sector_support_indices"]) for row in rows]
    stable = all(sig == support_signatures[0] for sig in support_signatures[1:]) if support_signatures else True
    wall_seconds = time.perf_counter() - wall_started

    first = rows[0]
    out = {
        "sector": first["sector"],
        "block_count": first["block_count"],
        "equation_count": first["equation_count"],
        "forbidden_non_subsector_count": first["forbidden_non_subsector_count"],
        "same_sector_outside_candidate_count": first["same_sector_outside_candidate_count"],
        "runtime": {
            "requested_processes": config.requested_processes,
            "effective_processes": config.effective_processes,
            "source": config.source,
            "wall_seconds": wall_seconds,
        },
        "rows": rows,
        "stable_support_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"sector: {tuple(first['sector'])}")
    print(f"target block: {first['block_count']}")
    print(f"equations: {first['equation_count']}")
    print(f"forbidden non-subsector columns: {first['forbidden_non_subsector_count']}")
    print(f"same-sector outside candidates: {first['same_sector_outside_candidate_count']}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"target rank={row['target_rank']}, free={row['conditional_free_dimension']}, "
            f"same-sector support={row['same_sector_support_count']}, "
            f"worker time={row['timings']['worker_total_seconds']:.3f}s"
        )
    print(f"stable support across primes: {stable}")
    print(f"wall time: {wall_seconds:.3f}s")
    print(f"generated: {OUTPUT}")
    if any(row["target_rank"] != first["block_count"] for row in rows):
        raise RuntimeError("5994 target block is not full rank in support audit")
    if not stable:
        raise RuntimeError("same-sector support differs across primes")
    print("Q01 four-line closure5994 sparse same-sector support audit PASS")


if __name__ == "__main__":
    main()
