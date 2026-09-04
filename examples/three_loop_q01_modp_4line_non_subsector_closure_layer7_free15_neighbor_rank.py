from __future__ import annotations

import gc
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
from three_loop.modp_sparse_constrained_rank import sparse_constrained_target_rank_at_probe
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds
from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config
from three_loop.sector_local_probe import default_q01_probe_points

from examples.three_loop_q01_modp_4line_non_subsector_rank import is_subsector
from examples.three_loop_q01_modp_4line_non_subsector_closure_layer14_11_rank import _load_layer_indices
from examples.three_loop_q01_modp_4line_non_subsector_closure_layer10_rank import _load_complexity10_indices
from examples.three_loop_q01_modp_4line_non_subsector_closure_layer9_rank import _load_complexity9_indices
from examples.three_loop_q01_modp_4line_non_subsector_closure_layer8_rank import _load_complexity8_indices
from examples.three_loop_q01_modp_4line_non_subsector_closure_layer7_rank import _load_complexity7_indices

ROOT = Path(__file__).resolve().parents[1]
STEP3_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3.json"
FREE57_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3_free_columns.json"
FREE41_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step2_free_columns.json"
FREE8_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_free_columns.json"
FREE5_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded48_free_columns.json"
DOT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
FREE17_1411_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer14_11_free_columns.json"
FREE17_10_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer10_free_columns.json"
FREE12_9_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer9_free_columns.json"
FREE18_8_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer8_free_columns.json"
FREE15_7_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer7_free_columns.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_layer7_free15_neighbor_rank.json"
PRIMES = (1000003, 1000033)
PHYSICAL_COUNT = 9


def _load_inputs():
    step3 = json.loads(STEP3_SOURCE.read_text(encoding="utf-8"))
    free57_data = json.loads(FREE57_SOURCE.read_text(encoding="utf-8"))
    free41_data = json.loads(FREE41_SOURCE.read_text(encoding="utf-8"))
    free8_data = json.loads(FREE8_SOURCE.read_text(encoding="utf-8"))
    free5_data = json.loads(FREE5_SOURCE.read_text(encoding="utf-8"))
    dot_data = json.loads(DOT_SOURCE.read_text(encoding="utf-8"))
    free17_1411_data = json.loads(FREE17_1411_SOURCE.read_text(encoding="utf-8"))
    free17_10_data = json.loads(FREE17_10_SOURCE.read_text(encoding="utf-8"))
    free12_9_data = json.loads(FREE12_9_SOURCE.read_text(encoding="utf-8"))
    free18_8_data = json.loads(FREE18_8_SOURCE.read_text(encoding="utf-8"))
    free15_7_data = json.loads(FREE15_7_SOURCE.read_text(encoding="utf-8"))

    source_sector = tuple(int(x) for x in step3["sector"])
    base5994 = tuple(IntegralIndex(tuple(p)) for p in step3["expanded_block_indices"])

    layer1411 = _load_layer_indices(base5994)
    base5994_set = set(base5994)
    target6952 = tuple(base5994) + tuple(index for index in layer1411 if index not in base5994_set)

    layer10 = _load_complexity10_indices(target6952)
    target6952_set = set(target6952)
    target8300 = tuple(target6952) + tuple(index for index in layer10 if index not in target6952_set)

    layer9 = _load_complexity9_indices(target8300)
    target8300_set = set(target8300)
    target10283 = tuple(target8300) + tuple(index for index in layer9 if index not in target8300_set)

    layer8 = _load_complexity8_indices(target10283)
    target10283_set = set(target10283)
    target12212 = tuple(target10283) + tuple(index for index in layer8 if index not in target10283_set)

    layer7 = _load_complexity7_indices(target12212)
    target12212_set = set(target12212)
    target14095 = tuple(target12212) + tuple(index for index in layer7 if index not in target12212_set)

    for name, data in (
        ("free57", free57_data),
        ("free17_1411", free17_1411_data),
        ("free17_10", free17_10_data),
        ("free12_9", free12_9_data),
        ("free18_8", free18_8_data),
        ("free15_7", free15_7_data),
    ):
        if not data.get("stable_free_basis_across_primes", False):
            raise RuntimeError(f"{name} basis is not stable across primes")

    free57 = tuple(IntegralIndex(tuple(p)) for p in free57_data["rows"][0]["free_indices"])
    free41 = tuple(IntegralIndex(tuple(p)) for p in free41_data["rows"][0]["free_indices"])
    free8 = tuple(IntegralIndex(tuple(p)) for p in free8_data["rows"][0]["free_indices"])
    free5 = tuple(IntegralIndex(tuple(p)) for p in free5_data["rows"][0]["free_indices"])
    dotted = tuple(IntegralIndex(tuple(p)) for p in dot_data["stable_unresolved_indices"])
    free17_1411 = tuple(IntegralIndex(tuple(p)) for p in free17_1411_data["rows"][0]["free_indices"])
    free17_10 = tuple(IntegralIndex(tuple(p)) for p in free17_10_data["rows"][0]["free_indices"])
    free12_9 = tuple(IntegralIndex(tuple(p)) for p in free12_9_data["rows"][0]["free_indices"])
    free18_8 = tuple(IntegralIndex(tuple(p)) for p in free18_8_data["rows"][0]["free_indices"])
    free15_7 = tuple(IntegralIndex(tuple(p)) for p in free15_7_data["rows"][0]["free_indices"])

    if len(target14095) != 14095 or len(free15_7) != 15:
        raise RuntimeError(
            f"expected target14095/free15; got {len(target14095)}/{len(free15_7)}"
        )

    return (
        source_sector,
        target14095,
        free57,
        free41,
        free8,
        free5,
        dotted,
        free17_1411,
        free17_10,
        free12_9,
        free18_8,
        free15_7,
    )


def _build_augmented_system(prime: int):
    (
        source_sector,
        target,
        free57,
        free41,
        free8,
        free5,
        dotted,
        free17_1411,
        free17_10,
        free12_9,
        free18_8,
        free15_7,
    ) = _load_inputs()

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
    base3520 = (
        set(base_seed_layer)
        | set(free5_neighbor) | set(free5)
        | set(free8_neighbor) | set(free8)
        | set(free41_neighbor) | set(free41)
    )
    if len(base3520) != 3520:
        raise RuntimeError(f"expected 3520 pre-free57 seeds, got {len(base3520)}")

    free57_neighbor = focused_neighbor_seeds(
        family, free57, templates=templates, physical_count=PHYSICAL_COUNT
    )
    base7205 = base3520 | set(free57_neighbor) | set(free57)
    if len(base7205) != 7205:
        raise RuntimeError(f"expected 7205 pre-layer14-11-free17 seeds, got {len(base7205)}")

    free17_1411_neighbor = focused_neighbor_seeds(
        family, free17_1411, templates=templates, physical_count=PHYSICAL_COUNT
    )
    base8473 = base7205 | set(free17_1411_neighbor) | set(free17_1411)
    if len(base8473) != 8473:
        raise RuntimeError(f"expected 8473 pre-layer10-free17 seeds, got {len(base8473)}")

    free17_10_neighbor = focused_neighbor_seeds(
        family, free17_10, templates=templates, physical_count=PHYSICAL_COUNT
    )
    base9681 = base8473 | set(free17_10_neighbor) | set(free17_10)
    if len(base9681) != 9681:
        raise RuntimeError(f"expected 9681 pre-layer9-free12 seeds, got {len(base9681)}")

    free12_9_neighbor = focused_neighbor_seeds(
        family, free12_9, templates=templates, physical_count=PHYSICAL_COUNT
    )
    base10555 = base9681 | set(free12_9_neighbor) | set(free12_9)
    if len(base10555) != 10555:
        raise RuntimeError(f"expected 10555 pre-layer8-free18 seeds, got {len(base10555)}")

    free18_8_neighbor = focused_neighbor_seeds(
        family, free18_8, templates=templates, physical_count=PHYSICAL_COUNT
    )
    base11742 = base10555 | set(free18_8_neighbor) | set(free18_8)
    if len(base11742) != 11742:
        raise RuntimeError(f"expected 11742 pre-layer7-free15 seeds, got {len(base11742)}")

    free15_7_neighbor = focused_neighbor_seeds(
        family, free15_7, templates=templates, physical_count=PHYSICAL_COUNT
    )
    all_seeds = tuple(
        sorted(base11742 | set(free15_7_neighbor) | set(free15_7), key=lambda index: index.powers)
    )
    added = set(all_seeds) - base11742
    seed_seconds = time.perf_counter() - started

    print(
        f"[worker pid={os.getpid()} prime={prime}] seeds ready: "
        f"base11742={len(base11742)}, layer7-free15-neighbors={len(free15_7_neighbor)}, "
        f"added={len(added)}, total={len(all_seeds)}",
        flush=True,
    )

    started = time.perf_counter()
    equations = []
    total = len(all_seeds)
    for n, seed in enumerate(all_seeds, start=1):
        local = local_same_seed_equations(family, seed, templates=templates)
        equations.extend(prune_zero_sectors(family, local))
        if n == total or n % 500 == 0:
            print(
                f"[worker pid={os.getpid()} prime={prime}] build/prune equations {n}/{total}",
                flush=True,
            )
    equations = tuple(equations)
    equation_seconds = time.perf_counter() - started

    started = time.perf_counter()
    all_indices = {index for equation in equations for index in equation.terms}
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
    forbidden_sectors = {physical_sector(index, PHYSICAL_COUNT) for index in forbidden}
    forbidden_scan_seconds = time.perf_counter() - started
    del all_indices
    gc.collect()

    point = default_q01_probe_points(family)[0]
    timings = {
        "seed_seconds": seed_seconds,
        "equation_build_seconds": equation_seconds,
        "forbidden_scan_seconds": forbidden_scan_seconds,
    }
    counts = {
        "base_seed_count": len(base11742),
        "free15_neighbor_seed_count": len(free15_7_neighbor),
        "added_seed_count": len(added),
        "total_seed_count": len(all_seeds),
        "equation_count": len(equations),
        "forbidden_non_subsector_count": len(forbidden),
        "distinct_forbidden_sector_count": len(forbidden_sectors),
    }
    return source_sector, target, forbidden, equations, point, timings, counts


def _prime_worker(prime: int):
    worker_started = time.perf_counter()
    source_sector, target, forbidden, equations, point, setup_timings, counts = (
        _build_augmented_system(prime)
    )

    print(
        f"[worker pid={os.getpid()} prime={prime}] layer7 free15-neighbor sparse rank start: "
        f"target={len(target)}, forbidden={len(forbidden)}",
        flush=True,
    )
    started = time.perf_counter()
    result = sparse_constrained_target_rank_at_probe(
        equations, forbidden, target, point, int(prime)
    )
    rank_seconds = time.perf_counter() - started
    print(
        f"[worker pid={os.getpid()} prime={prime}] layer7 free15-neighbor sparse rank done: "
        f"forbidden_rank={result.forbidden_rank}, target_rank={result.target_rank}, "
        f"free={result.conditional_free_dimension}",
        flush=True,
    )

    return {
        "prime": int(prime),
        "pid": os.getpid(),
        "sector": source_sector,
        "target_count": len(target),
        **counts,
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
            "worker_total_seconds": time.perf_counter() - worker_started,
        },
    }


def main() -> None:
    wall_started = time.perf_counter()
    config = load_runtime_config(root=ROOT, max_useful_processes=len(PRIMES))

    print("QEDCalc Q01 closure complexity-7 free15 neighbor sparse-rank audit")
    print(format_runtime_config(config), flush=True)
    print(
        "memory mode: sparse rank; add neighbor seeds only for the stable complexity-7 free15; "
        "recompute non-subsector columns from the augmented system",
        flush=True,
    )
    if config.effective_processes > 1:
        print(
            "warning: Windows spawn duplicates the symbolic system; use QEDCALC_PROCESSES=1 for minimum memory",
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
        "target_count": first["target_count"],
        "free_candidate_count": 15,
        "base_seed_count": first["base_seed_count"],
        "free15_neighbor_seed_count": first["free15_neighbor_seed_count"],
        "added_seed_count": first["added_seed_count"],
        "total_seed_count": first["total_seed_count"],
        "equation_count": first["equation_count"],
        "forbidden_non_subsector_count": first["forbidden_non_subsector_count"],
        "distinct_forbidden_sector_count": first["distinct_forbidden_sector_count"],
        "algorithm": "sparse_forward_constrained_rank_layer7_free15_targeted_neighbor",
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
    print(f"target block: {first['target_count']}")
    print("free candidates targeted: 15")
    print(f"base seeds: {first['base_seed_count']}")
    print(f"free15 neighbor seeds: {first['free15_neighbor_seed_count']}")
    print(f"newly added seeds: {first['added_seed_count']}")
    print(f"total seeds: {first['total_seed_count']}")
    print(f"equations: {first['equation_count']}")
    print(f"forbidden non-subsector columns: {first['forbidden_non_subsector_count']}")
    for row in rows:
        print(
            f"prime {row['prime']}: forbidden rank={row['forbidden_rank']}, "
            f"target rank={row['target_rank']}, free dimension={row['conditional_free_dimension']}"
        )
    print(f"stable across primes: {stable}")
    print(f"wall time: {wall_seconds:.3f}s")
    print(f"generated: {OUTPUT}")
    if not stable:
        raise RuntimeError("complexity-7 free15 neighbor rank differs across primes")
    print("Q01 closure complexity-7 free15 neighbor sparse-rank audit PASS")


if __name__ == "__main__":
    main()
