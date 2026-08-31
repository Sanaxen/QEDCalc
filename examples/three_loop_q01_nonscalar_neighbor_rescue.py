from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.nonscalar_neighbor_rescue import audit_nonscalar_neighbor_rescue

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_remaining_target_classification.json"
OUTPUT = ROOT / "output" / "3loop_q01_nonscalar_neighbor_rescue_audit.json"


def load_nonscalar_targets(path: Path) -> tuple[IntegralIndex, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for record in data["records"]:
        if not record["is_scalar_subtopology"]:
            out.append(IntegralIndex(tuple(record["index"])))
    return tuple(out)


def main() -> None:
    print("QEDCalc Q01 focused nonscalar neighbor-sector rescue audit", flush=True)
    family = q01_integral_family()
    targets = load_nonscalar_targets(SOURCE)
    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    t1 = time.perf_counter()

    state = {"stage": "start", "current": None, "total": None, "changed": time.perf_counter()}
    stop = threading.Event()

    def progress(stage, current=None, total=None):
        state.update(stage=stage, current=current, total=total, changed=time.perf_counter())
        elapsed = time.perf_counter() - t1
        suffix = ""
        if current is not None and total:
            suffix = f" {current}/{total} ({100.0 * current / total:.1f}%)"
        print(f"[progress {elapsed:9.1f}s] {stage}{suffix}", flush=True)

    def heartbeat():
        while not stop.wait(30.0):
            elapsed = time.perf_counter() - t1
            unchanged = time.perf_counter() - state["changed"]
            suffix = ""
            if state["current"] is not None and state["total"]:
                suffix = f" {state['current']}/{state['total']} ({100.0 * state['current'] / state['total']:.1f}%)"
            print(
                f"[heartbeat {elapsed:9.1f}s] still running: {state['stage']}{suffix}; stage unchanged for {unchanged:.1f}s",
                flush=True,
            )

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    try:
        profile = audit_nonscalar_neighbor_rescue(
            family, targets, templates=templates, progress=progress
        )
    finally:
        stop.set()
        thread.join(timeout=1.0)
    t2 = time.perf_counter()

    data = {
        "target_count": profile.target_count,
        "seed_count": profile.seed_count,
        "same_sector_seed_count": profile.same_sector_seed_count,
        "neighbor_sector_seed_count": profile.neighbor_sector_seed_count,
        "equation_count": profile.equation_count,
        "integral_count": profile.integral_count,
        "primes": profile.primes,
        "pivot_counts": profile.pivot_counts,
        "solved_target_counts": profile.solved_target_counts,
        "unsolved_target_counts": profile.unsolved_target_counts,
        "stable_across_runs": profile.stable_across_runs,
        "template_build_seconds": t1 - t0,
        "audit_seconds": t2 - t1,
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"targets: {profile.target_count}")
    print(f"seeds: {profile.seed_count}")
    print(f"same-sector seeds: {profile.same_sector_seed_count}")
    print(f"neighbor-sector seeds: {profile.neighbor_sector_seed_count}")
    print(f"equations: {profile.equation_count}")
    print(f"integrals: {profile.integral_count}")
    print(f"primes: {profile.primes}")
    print(f"pivot counts: {profile.pivot_counts}")
    print(f"solved nonscalar targets by run: {profile.solved_target_counts}")
    print(f"remaining nonscalar targets by run: {profile.unsolved_target_counts}")
    print(f"stable across runs: {profile.stable_across_runs}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"focused rescue audit: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 focused nonscalar neighbor-sector rescue audit PASS")


if __name__ == "__main__":
    main()
