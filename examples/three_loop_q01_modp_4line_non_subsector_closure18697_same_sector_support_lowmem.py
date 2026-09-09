from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from examples.three_loop_q01_modp_4line_non_subsector_closure18697_same_sector_support import (
    _prime_worker,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
OUTPUT = OUTPUT_DIR / "3loop_q01_modp_4line_non_subsector_closure18697_same_sector_support_lowmem.json"
PRIMES = (1000003, 1000033)


def checkpoint_path(prime: int) -> Path:
    return OUTPUT_DIR / (
        "3loop_q01_modp_4line_non_subsector_closure18697_same_sector_support_"
        f"prime{prime}.json"
    )


def checkpoint_is_valid(path: Path, prime: int) -> bool:
    if not path.exists():
        return False
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return (
        int(row.get("prime", -1)) == int(prime)
        and int(row.get("block_count", -1)) == 18697
        and int(row.get("target_rank", -1)) == 18697
        and int(row.get("conditional_free_dimension", -1)) == 0
        and int(row.get("equation_count", -1)) == 271965
    )


def run_worker(prime: int) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = checkpoint_path(prime)
    started = time.perf_counter()
    print(
        f"QEDCalc Q01 low-memory support worker start: prime={prime}, pid={os.getpid()}",
        flush=True,
    )
    row = dict(_prime_worker(int(prime)))
    row["checkpoint_wall_seconds"] = time.perf_counter() - started
    path.write_text(json.dumps(row, indent=2), encoding="utf-8")
    print(f"checkpoint generated: {path}", flush=True)
    print(
        f"prime {prime} worker PASS; process will now exit so Windows can reclaim all memory",
        flush=True,
    )


def launch_prime(prime: int) -> None:
    path = checkpoint_path(prime)
    if checkpoint_is_valid(path, prime):
        print(f"prime {prime}: valid checkpoint found; skipping recomputation: {path}", flush=True)
        return

    if path.exists():
        print(f"prime {prime}: stale/incomplete checkpoint ignored: {path}", flush=True)

    env = os.environ.copy()
    env["QEDCALC_PROCESSES"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    print(
        f"prime {prime}: launching isolated child process with QEDCALC_PROCESSES=1",
        flush=True,
    )
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker-prime", str(prime)],
        cwd=str(ROOT),
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"prime {prime} child process failed with exit code {completed.returncode}; "
            "completed checkpoints remain reusable"
        )
    if not checkpoint_is_valid(path, prime):
        raise RuntimeError(f"prime {prime} child exited successfully but checkpoint is invalid")
    print(
        f"prime {prime}: child exited successfully; memory reclaimed before next prime",
        flush=True,
    )


def combine_checkpoints(wall_seconds: float) -> None:
    rows = [json.loads(checkpoint_path(prime).read_text(encoding="utf-8")) for prime in PRIMES]
    support_signatures = [
        tuple(tuple(p) for p in row["same_sector_support_indices"])
        for row in rows
    ]
    stable = all(sig == support_signatures[0] for sig in support_signatures[1:])
    first = rows[0]
    out = {
        "sector": first["sector"],
        "block_count": first["block_count"],
        "base_seed_count": first["base_seed_count"],
        "free40_neighbor_seed_count": first["free40_neighbor_seed_count"],
        "added_seed_count": first["added_seed_count"],
        "total_seed_count": first["total_seed_count"],
        "equation_count": first["equation_count"],
        "forbidden_non_subsector_count": first["forbidden_non_subsector_count"],
        "distinct_forbidden_sector_count": first["distinct_forbidden_sector_count"],
        "same_sector_outside_candidate_count": first["same_sector_outside_candidate_count"],
        "algorithm": "isolated_sequential_prime_sparse_same_sector_support_after_layer12_free40",
        "runtime": {
            "mode": "isolated_sequential_prime_processes",
            "effective_heavy_workers_at_once": 1,
            "wall_seconds": wall_seconds,
        },
        "checkpoint_files": [str(checkpoint_path(prime)) for prime in PRIMES],
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
        raise RuntimeError("low-memory 18697 same-sector support differs across primes")
    print("Q01 low-memory refreshed 18697-block same-sector support audit PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-prime", type=int, default=None)
    args = parser.parse_args()

    if args.worker_prime is not None:
        if args.worker_prime not in PRIMES:
            raise RuntimeError(f"unsupported prime {args.worker_prime}")
        run_worker(args.worker_prime)
        return

    wall_started = time.perf_counter()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("QEDCalc Q01 low-memory refreshed 18697-block same-sector support audit")
    print(
        "memory mode: one heavy prime per isolated Python process; checkpoint after each prime; "
        "completed prime checkpoints are reused on restart",
        flush=True,
    )
    print(
        "IMPORTANT: this launcher intentionally ignores QEDCALC_PROCESSES>1 for heavy support work",
        flush=True,
    )

    for prime in PRIMES:
        launch_prime(prime)

    combine_checkpoints(time.perf_counter() - wall_started)


if __name__ == "__main__":
    main()
