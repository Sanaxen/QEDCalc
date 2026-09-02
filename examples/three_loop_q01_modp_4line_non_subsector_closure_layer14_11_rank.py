from __future__ import annotations

import json
import os
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.modp_sparse_constrained_rank import sparse_constrained_target_rank_at_probe
from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config

from examples.three_loop_q01_modp_4line_non_subsector_closure5994_support_profile import complexity
from examples.three_loop_q01_modp_4line_non_subsector_closure_step3_free57_neighbor_rank_parallel import (
    _build_augmented_symbolic_system,
)

ROOT = Path(__file__).resolve().parents[1]
SUPPORT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure5994_same_sector_support.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer14_11_rank.json"
PRIMES = (1000003, 1000033)
MIN_COMPLEXITY = 11


def _load_layer_indices(base_block):
    support = json.loads(SUPPORT_SOURCE.read_text(encoding="utf-8"))
    if not support.get("stable_support_across_primes", False):
        raise RuntimeError("same-sector support is not stable across primes")
    rows = support.get("rows", [])
    if not rows:
        raise RuntimeError("same-sector support output has no rows")

    base_set = set(base_block)
    same_support = tuple(IntegralIndex(tuple(p)) for p in rows[0]["same_sector_support_indices"])
    layer = tuple(
        sorted(
            (
                index
                for index in same_support
                if index not in base_set and complexity(index)["total_complexity"] >= MIN_COMPLEXITY
            ),
            key=lambda index: (-complexity(index)["total_complexity"], index.powers),
        )
    )
    if len(layer) != 958:
        raise RuntimeError(f"expected 958 complexity>=11 support integrals, got {len(layer)}")
    return layer


def _prime_worker(prime: int):
    started = time.perf_counter()
    source_sector, base_block, forbidden, equations, point, setup_timings, counts = (
        _build_augmented_symbolic_system(prime)
    )
    layer = _load_layer_indices(base_block)
    target = tuple(base_block) + tuple(index for index in layer if index not in set(base_block))
    if len(target) != 6952:
        raise RuntimeError(f"expected 6952 expanded target block, got {len(target)}")

    print(
        f"[worker pid={os.getpid()} prime={prime}] layer14-11 sparse rank start: "
        f"base={len(base_block)}, added={len(layer)}, target={len(target)}, forbidden={len(forbidden)}",
        flush=True,
    )
    rank_started = time.perf_counter()
    result = sparse_constrained_target_rank_at_probe(
        equations,
        forbidden,
        target,
        point,
        int(prime),
    )
    rank_seconds = time.perf_counter() - rank_started
    print(
        f"[worker pid={os.getpid()} prime={prime}] layer14-11 sparse rank done: "
        f"forbidden_rank={result.forbidden_rank}, target_rank={result.target_rank}, "
        f"free={result.conditional_free_dimension}",
        flush=True,
    )

    layer_hist = {}
    for index in layer:
        degree = str(complexity(index)["total_complexity"])
        layer_hist[degree] = layer_hist.get(degree, 0) + 1

    return {
        "prime": int(prime),
        "pid": os.getpid(),
        "sector": source_sector,
        "base_block_count": len(base_block),
        "added_layer_count": len(layer),
        "expanded_block_count": len(target),
        "layer_histogram": layer_hist,
        "forbidden_non_subsector_count": len(forbidden),
        "forbidden_rank": result.forbidden_rank,
        "target_rank": result.target_rank,
        "conditional_free_dimension": result.conditional_free_dimension,
        "sparse_projection": {
            "input_equation_count": result.input_equation_count,
            "projected_nonzero_row_count": result.projected_nonzero_row_count,
            "projected_term_count": result.projected_term_count,
            "residual_row_count": result.residual_row_count,
            "residual_term_count": result.residual_term_count,
        },
        "timings": {
            **setup_timings,
            "sparse_constrained_rank_seconds": rank_seconds,
            "worker_total_seconds": time.perf_counter() - started,
        },
        "added_layer_indices": [index.powers for index in layer],
    }


def main() -> None:
    wall_started = time.perf_counter()
    config = load_runtime_config(root=ROOT, max_useful_processes=len(PRIMES))

    print("QEDCalc Q01 four-line closure complexity 14-11 sparse-rank audit")
    print(format_runtime_config(config), flush=True)
    print("memory mode: sparse rank; add only complexity 14-11 support (958 integrals)", flush=True)
    if config.effective_processes > 1:
        print(
            "warning: Windows spawn duplicates the symbolic equation system; "
            "QEDCALC_PROCESSES=1 is recommended for minimum memory",
            flush=True,
        )

    jobs = run_process_jobs(_prime_worker, PRIMES, processes=config.effective_processes)
    rows = [dict(job.result) for job in jobs]
    signatures = [
        (row["forbidden_rank"], row["target_rank"], row["conditional_free_dimension"])
        for row in rows
    ]
    stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True
    wall_seconds = time.perf_counter() - wall_started

    first = rows[0]
    out = {
        "sector": first["sector"],
        "minimum_added_complexity": MIN_COMPLEXITY,
        "base_block_count": first["base_block_count"],
        "added_layer_count": first["added_layer_count"],
        "expanded_block_count": first["expanded_block_count"],
        "layer_histogram": first["layer_histogram"],
        "forbidden_non_subsector_count": first["forbidden_non_subsector_count"],
        "algorithm": "sparse_forward_constrained_rank_layered_closure",
        "runtime": {
            "requested_processes": config.requested_processes,
            "effective_processes": config.effective_processes,
            "source": config.source,
            "config_path": config.config_path,
            "wall_seconds": wall_seconds,
        },
        "rows": rows,
        "stable_across_primes": stable,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"sector: {tuple(first['sector'])}")
    print(f"base block: {first['base_block_count']}")
    print(f"added complexity 14-11: {first['added_layer_count']}")
    print(f"expanded block: {first['expanded_block_count']}")
    print(f"layer histogram: {first['layer_histogram']}")
    print(f"forbidden non-subsector columns: {first['forbidden_non_subsector_count']}")
    for row in rows:
        t = row["timings"]
        s = row["sparse_projection"]
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"target rank={row['target_rank']}, free dimension={row['conditional_free_dimension']}, "
            f"worker time={t['worker_total_seconds']:.3f}s"
        )
        print(
            f"  sparse rows={s['projected_nonzero_row_count']}, terms={s['projected_term_count']}, "
            f"residual rows={s['residual_row_count']}, residual terms={s['residual_term_count']}"
        )
    print(f"stable across primes: {stable}")
    print(f"wall time: {wall_seconds:.3f}s")
    print(f"generated: {OUTPUT}")
    if not stable:
        raise RuntimeError("layer14-11 constrained-rank result differs across primes")
    print("Q01 four-line closure complexity 14-11 sparse-rank audit PASS")


if __name__ == "__main__":
    main()
