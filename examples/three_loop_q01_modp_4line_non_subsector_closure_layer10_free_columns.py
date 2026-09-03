from __future__ import annotations

import os
import time
from pathlib import Path

from three_loop.modp_sparse_free_columns import sparse_constrained_free_columns_at_probe
from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config

from examples.three_loop_q01_modp_4line_non_subsector_closure_layer10_rank import (
    _load_complexity10_indices,
)
from examples.three_loop_q01_modp_4line_non_subsector_closure_layer14_11_free17_neighbor_rank import (
    _build_augmented_system,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer10_free_columns.json"
PRIMES = (1000003, 1000033)


def _prime_worker(prime: int):
    started = time.perf_counter()
    source_sector, base6952, forbidden, equations, point, setup_timings, counts = (
        _build_augmented_system(prime)
    )
    layer10 = _load_complexity10_indices(base6952)
    base_set = set(base6952)
    target = tuple(base6952) + tuple(index for index in layer10 if index not in base_set)
    if len(target) != 8300:
        raise RuntimeError(f"expected 8300 target integrals, got {len(target)}")

    print(
        f"[worker pid={os.getpid()} prime={prime}] complexity-10 sparse free-column audit start: "
        f"target={len(target)}, forbidden={len(forbidden)}",
        flush=True,
    )
    audit_started = time.perf_counter()
    result = sparse_constrained_free_columns_at_probe(
        equations,
        forbidden,
        target,
        point,
        int(prime),
    )
    audit_seconds = time.perf_counter() - audit_started
    print(
        f"[worker pid={os.getpid()} prime={prime}] complexity-10 sparse free-column audit done: "
        f"target_rank={result.target_rank}, free={result.conditional_free_dimension}",
        flush=True,
    )

    if result.target_rank != 8283 or result.conditional_free_dimension != 17:
        raise RuntimeError(
            f"expected target rank 8283 and free dimension 17; got "
            f"{result.target_rank} and {result.conditional_free_dimension}"
        )

    return {
        "prime": int(prime),
        "pid": os.getpid(),
        "sector": source_sector,
        "expanded_block_count": len(target),
        "forbidden_non_subsector_count": len(forbidden),
        "forbidden_rank": result.forbidden_rank,
        "target_rank": result.target_rank,
        "conditional_free_dimension": result.conditional_free_dimension,
        "free_indices": [index.powers for index in result.free_columns],
        "sparse_projection": {
            "input_equation_count": result.input_equation_count,
            "projected_nonzero_row_count": result.projected_nonzero_row_count,
            "projected_term_count": result.projected_term_count,
            "residual_row_count": result.residual_row_count,
            "residual_term_count": result.residual_term_count,
        },
        "timings": {
            **setup_timings,
            "sparse_free_column_seconds": audit_seconds,
            "worker_total_seconds": time.perf_counter() - started,
        },
    }


def main() -> None:
    wall_started = time.perf_counter()
    config = load_runtime_config(root=ROOT, max_useful_processes=len(PRIMES))

    print("QEDCalc Q01 four-line closure complexity-10 sparse free-column audit")
    print(format_runtime_config(config), flush=True)
    print(
        "memory mode: sparse forward elimination; record target pivots only; no dense RREF",
        flush=True,
    )
    if config.effective_processes > 1:
        print(
            "warning: QEDCALC_PROCESSES=1 is recommended for minimum memory on Windows",
            flush=True,
        )

    jobs = run_process_jobs(_prime_worker, PRIMES, processes=config.effective_processes)
    rows = [dict(job.result) for job in jobs]
    stable = (
        all(row["free_indices"] == rows[0]["free_indices"] for row in rows[1:])
        if rows
        else True
    )
    wall_seconds = time.perf_counter() - wall_started

    first = rows[0]
    out = {
        "sector": first["sector"],
        "expanded_block_count": first["expanded_block_count"],
        "forbidden_non_subsector_count": first["forbidden_non_subsector_count"],
        "free_dimension": first["conditional_free_dimension"],
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
    OUTPUT.write_text(__import__("json").dumps(out, indent=2), encoding="utf-8")

    print(f"sector: {tuple(first['sector'])}")
    print(f"expanded block: {first['expanded_block_count']}")
    print(f"forbidden non-subsector columns: {first['forbidden_non_subsector_count']}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"target rank={row['target_rank']}, free dimension={row['conditional_free_dimension']}"
        )
        for powers in row["free_indices"]:
            print(f"  I{tuple(powers)}")
    print(f"stable free basis across primes: {stable}")
    print(f"wall time: {wall_seconds:.3f}s")
    print(f"generated: {OUTPUT}")
    if not stable:
        raise RuntimeError("complexity-10 free-column basis differs across primes")
    print("Q01 four-line closure complexity-10 sparse free-column audit PASS")


if __name__ == "__main__":
    main()
