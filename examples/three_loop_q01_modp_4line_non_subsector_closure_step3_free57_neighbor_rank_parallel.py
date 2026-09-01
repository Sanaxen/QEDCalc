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
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config
from three_loop.sector_local_modp import _specialize_remaining_symbols_by_name
from three_loop.sector_local_probe import default_q01_probe_points

from examples.three_loop_q01_modp_4line_non_subsector_rank import is_subsector
from examples.three_loop_q01_modp_4line_sector_ordered_rank import constrained_target_rank

ROOT = Path(__file__).resolve().parents[1]
STEP3_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3.json"
FREE57_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3_free_columns.json"
FREE41_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step2_free_columns.json"
FREE8_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3_free57_neighbor_rank.json"
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

    if not free57_data.get("stable_free_basis_across_primes", False):
        raise RuntimeError("step3 free-column basis is not stable across primes")
    free57_rows = free57_data.get("rows", [])
    if not free57_rows:
        raise RuntimeError("step3 free-column audit has no rows")

    free57 = tuple(IntegralIndex(tuple(p)) for p in free57_rows[0]["free_indices"])
    free41 = tuple(IntegralIndex(tuple(p)) for p in free41_data["rows"][0]["free_indices"])
    free8 = tuple(IntegralIndex(tuple(p)) for p in free8_data["rows"][0]["free_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])

    if len(block) != 5994 or len(free57) != 57:
        raise RuntimeError(
            f"expected 5994-block and 57 free columns; got {len(block)} and {len(free57)}"
        )
    return source_sector, block, free57, free41, free8, free5, dotted


def _build_augmented_system(prime: int):
    source_sector, block, free57, free41, free8, free5, dotted = _load_inputs()
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
    base_seeds = (
        set(base_seed_layer)
        | set(free5_neighbor)
        | set(free5)
        | set(free8_neighbor)
        | set(free8)
        | set(free41_neighbor)
        | set(free41)
    )
    if len(base_seeds) != 3520:
        raise RuntimeError(f"expected 3520 base seeds, got {len(base_seeds)}")

    free57_neighbor = focused_neighbor_seeds(
        family, free57, templates=templates, physical_count=PHYSICAL_COUNT
    )
    all_seeds = tuple(
        sorted(base_seeds | set(free57_neighbor) | set(free57), key=lambda index: index.powers)
    )
    added_seeds = set(all_seeds) - base_seeds
    seed_seconds = time.perf_counter() - started

    print(
        f"[worker pid={os.getpid()} prime={prime}] seeds ready: "
        f"base={len(base_seeds)}, free57-neighbors={len(free57_neighbor)}, "
        f"added={len(added_seeds)}, total={len(all_seeds)}",
        flush=True,
    )

    started = time.perf_counter()
    equations = []
    total = len(all_seeds)
    for n, seed in enumerate(all_seeds, start=1):
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
        if n == total or n % 500 == 0:
            print(
                f"[worker pid={os.getpid()} prime={prime}] build equations {n}/{total}",
                flush=True,
            )
    equations = prune_zero_sectors(family, equations)
    equation_seconds = time.perf_counter() - started
    print(
        f"[worker pid={os.getpid()} prime={prime}] equations built: {len(equations)}",
        flush=True,
    )

    started = time.perf_counter()
    point = default_q01_probe_points(family)[0]
    probed = specialize_ibp_system(equations, point)
    probed = _specialize_remaining_symbols_by_name(probed, point)
    specialize_seconds = time.perf_counter() - started
    print(
        f"[worker pid={os.getpid()} prime={prime}] specialized",
        flush=True,
    )

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
    forbidden_sectors = sorted(
        {physical_sector(index, PHYSICAL_COUNT) for index in forbidden}
    )
    forbidden_scan_seconds = time.perf_counter() - started

    timings = {
        "seed_seconds": seed_seconds,
        "equation_build_seconds": equation_seconds,
        "specialize_seconds": specialize_seconds,
        "forbidden_scan_seconds": forbidden_scan_seconds,
    }
    counts = {
        "base_seed_count": len(base_seeds),
        "free57_neighbor_seed_count": len(free57_neighbor),
        "added_seed_count": len(added_seeds),
        "total_seed_count": len(all_seeds),
        "equation_count": len(equations),
        "forbidden_non_subsector_count": len(forbidden),
        "distinct_forbidden_sector_count": len(forbidden_sectors),
    }
    return source_sector, block, forbidden, probed, timings, counts


def _prime_worker(prime: int):
    worker_started = time.perf_counter()
    source_sector, block, forbidden, probed, setup_timings, counts = _build_augmented_system(prime)

    print(
        f"[worker pid={os.getpid()} prime={prime}] constrained rank start: "
        f"forbidden={len(forbidden)}, target={len(block)}",
        flush=True,
    )
    started = time.perf_counter()
    forbidden_rank, target_rank, free_dim = constrained_target_rank(
        probed, forbidden, block, int(prime)
    )
    rank_seconds = time.perf_counter() - started
    print(
        f"[worker pid={os.getpid()} prime={prime}] constrained rank done: "
        f"forbidden_rank={forbidden_rank}, target_rank={target_rank}, free={free_dim}",
        flush=True,
    )

    return {
        "prime": int(prime),
        "pid": os.getpid(),
        "sector": source_sector,
        "block_count": len(block),
        **counts,
        "forbidden_rank": forbidden_rank,
        "sector_ordered_target_rank": target_rank,
        "conditional_free_dimension": free_dim,
        "timings": {
            **setup_timings,
            "constrained_rank_seconds": rank_seconds,
            "worker_total_seconds": time.perf_counter() - worker_started,
        },
    }


def main() -> None:
    wall_started = time.perf_counter()
    config = load_runtime_config(root=ROOT, max_useful_processes=len(PRIMES))

    print("QEDCalc Q01 four-line closure step3 free57 neighbor rank audit")
    print(format_runtime_config(config), flush=True)
    print(
        "note: each finite-field worker reconstructs the augmented seed system on Windows spawn",
        flush=True,
    )

    jobs = run_process_jobs(
        _prime_worker,
        PRIMES,
        processes=config.effective_processes,
    )
    rows = [dict(item.result) for item in jobs]

    signatures = [
        (
            row["forbidden_rank"],
            row["sector_ordered_target_rank"],
            row["conditional_free_dimension"],
        )
        for row in rows
    ]
    stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True
    wall_seconds = time.perf_counter() - wall_started

    first = rows[0]
    out = {
        "sector": first["sector"],
        "expanded_block_count": first["block_count"],
        "free_candidate_count": 57,
        "base_seed_count": first["base_seed_count"],
        "free57_neighbor_seed_count": first["free57_neighbor_seed_count"],
        "added_seed_count": first["added_seed_count"],
        "total_seed_count": first["total_seed_count"],
        "equation_count": first["equation_count"],
        "forbidden_non_subsector_count": first["forbidden_non_subsector_count"],
        "distinct_forbidden_sector_count": first["distinct_forbidden_sector_count"],
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
    print(f"expanded block: {first['block_count']}")
    print("free candidates: 57")
    print(f"base seeds: {first['base_seed_count']}")
    print(f"free57 neighbor seeds: {first['free57_neighbor_seed_count']}")
    print(f"newly added seeds: {first['added_seed_count']}")
    print(f"total seeds: {first['total_seed_count']}")
    print(f"equations: {first['equation_count']}")
    print(f"forbidden non-subsector columns: {first['forbidden_non_subsector_count']}")
    print(f"distinct forbidden sectors: {first['distinct_forbidden_sector_count']}")
    for row in rows:
        t = row["timings"]
        print(
            f"prime {row['prime']}: pid={row['pid']}, forbidden rank={row['forbidden_rank']}, "
            f"sector-ordered target rank={row['sector_ordered_target_rank']}, "
            f"conditional free dimension={row['conditional_free_dimension']}, "
            f"worker time={t['worker_total_seconds']:.3f}s"
        )
        print(
            "  timings: "
            f"seeds={t['seed_seconds']:.3f}s, equations={t['equation_build_seconds']:.3f}s, "
            f"specialize={t['specialize_seconds']:.3f}s, forbidden scan={t['forbidden_scan_seconds']:.3f}s, "
            f"constrained rank={t['constrained_rank_seconds']:.3f}s"
        )
    print(f"stable across primes: {stable}")
    print(f"wall time: {wall_seconds:.3f}s")
    print(f"generated: {OUTPUT}")
    if not stable:
        raise RuntimeError("free57 neighbor constrained-rank result differs across primes")
    print("Q01 four-line closure step3 free57 neighbor rank audit PASS")


if __name__ == "__main__":
    main()
