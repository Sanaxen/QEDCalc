from __future__ import annotations

import gc
import json
import os
import time
from pathlib import Path

from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.modp_sparse_sector_support import sparse_same_sector_support
from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config
from three_loop.sector_local_probe import default_q01_probe_points

from examples.three_loop_q01_modp_4line_non_subsector_closure_layer7_free15_neighbor_rank import (
    _build_augmented_system,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure14095_same_sector_support.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def _prime_worker(prime: int):
    worker_started = time.perf_counter()
    source_sector, block, forbidden, equations, point, setup_timings, counts = (
        _build_augmented_system(prime)
    )
    if len(block) != 14095:
        raise RuntimeError(f"expected 14095 target integrals, got {len(block)}")
    if len(equations) != 191595:
        raise RuntimeError(f"expected 191595 equations, got {len(equations)}")

    scan_started = time.perf_counter()
    block_set = set(block)
    all_indices = {index for equation in equations for index in equation.terms}
    same_sector_outside = tuple(
        sorted(
            (
                index
                for index in all_indices
                if index not in block_set
                and physical_sector(index, PHYSICAL_COUNT) == source_sector
            ),
            key=lambda index: index.powers,
        )
    )
    scan_seconds = time.perf_counter() - scan_started
    del all_indices
    gc.collect()

    print(
        f"[worker pid={os.getpid()} prime={prime}] refreshed support columns ready: "
        f"block={len(block)}, forbidden={len(forbidden)}, "
        f"same-sector-outside={len(same_sector_outside)}",
        flush=True,
    )

    family = q01_integral_family()
    if point is None:
        point = default_q01_probe_points(family)[0]

    support_started = time.perf_counter()
    result = sparse_same_sector_support(
        equations,
        forbidden,
        block,
        same_sector_outside,
        int(prime),
        probe_point=point,
    )
    support_seconds = time.perf_counter() - support_started

    print(
        f"[worker pid={os.getpid()} prime={prime}] refreshed sparse support done: "
        f"target_rank={result.target_rank}, free={result.conditional_free_dimension}, "
        f"support={len(result.same_sector_support)}",
        flush=True,
    )

    if result.target_rank != 14095 or result.conditional_free_dimension != 0:
        raise RuntimeError(
            f"expected full-rank 14095 block; got rank={result.target_rank}, "
            f"free={result.conditional_free_dimension}"
        )

    return {
        "prime": int(prime),
        "pid": os.getpid(),
        "sector": source_sector,
        "block_count": len(block),
        **counts,
        "same_sector_outside_candidate_count": len(same_sector_outside),
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
            **setup_timings,
            "same_sector_column_scan_seconds": scan_seconds,
            "same_sector_support_seconds": support_seconds,
            "worker_total_seconds": time.perf_counter() - worker_started,
        },
    }


def main() -> None:
    wall_started = time.perf_counter()
    config = load_runtime_config(root=ROOT, max_useful_processes=len(PRIMES))

    print("QEDCalc Q01 four-line refreshed 14095-block same-sector support audit")
    print(format_runtime_config(config), flush=True)
    print(
        "memory mode: sparse same-sector support; no 14095x14095 inverse; "
        "use layer7-free15 augmented 12773-seed system",
        flush=True,
    )
    if config.effective_processes > 1:
        print(
            "warning: Windows spawn duplicates the symbolic system; "
            "use QEDCALC_PROCESSES=1 for minimum memory",
            flush=True,
        )

    jobs = run_process_jobs(_prime_worker, PRIMES, processes=config.effective_processes)
    rows = [dict(job.result) for job in jobs]
    support_signatures = [
        tuple(tuple(p) for p in row["same_sector_support_indices"])
        for row in rows
    ]
    stable = (
        all(sig == support_signatures[0] for sig in support_signatures[1:])
        if support_signatures
        else True
    )
    wall_seconds = time.perf_counter() - wall_started

    first = rows[0]
    out = {
        "sector": first["sector"],
        "block_count": first["block_count"],
        "base_seed_count": first["base_seed_count"],
        "free15_neighbor_seed_count": first["free15_neighbor_seed_count"],
        "added_seed_count": first["added_seed_count"],
        "total_seed_count": first["total_seed_count"],
        "equation_count": first["equation_count"],
        "forbidden_non_subsector_count": first["forbidden_non_subsector_count"],
        "distinct_forbidden_sector_count": first["distinct_forbidden_sector_count"],
        "same_sector_outside_candidate_count": first["same_sector_outside_candidate_count"],
        "algorithm": "sparse_refreshed_same_sector_support_after_layer7_free15",
        "runtime": {
            "requested_processes": config.requested_processes,
            "effective_processes": config.effective_processes,
            "source": config.source,
            "config_path": config.config_path,
            "wall_seconds": wall_seconds,
        },
        "rows": rows,
        "stable_support_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"sector: {tuple(first['sector'])}")
    print(f"target block: {first['block_count']}")
    print(f"total seeds: {first['total_seed_count']}")
    print(f"equations: {first['equation_count']}")
    print(f"forbidden non-subsector columns: {first['forbidden_non_subsector_count']}")
    print(f"same-sector outside candidates: {first['same_sector_outside_candidate_count']}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"target rank={row['target_rank']}, free={row['conditional_free_dimension']}, "
            f"same-sector support={row['same_sector_support_count']}"
        )
    print(f"stable support across primes: {stable}")
    print(f"wall time: {wall_seconds:.3f}s")
    print(f"generated: {OUTPUT}")
    if not stable:
        raise RuntimeError("refreshed same-sector support differs across primes")
    print("Q01 refreshed 14095-block same-sector support audit PASS")


if __name__ == "__main__":
    main()
