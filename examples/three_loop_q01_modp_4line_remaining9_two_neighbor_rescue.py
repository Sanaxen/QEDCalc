from __future__ import annotations

import json
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.modp_dot_two_neighbor_rescue import audit_dot_two_neighbor_rescue_mod_p
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
PRIMES = (1000003, 1000033)


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    targets = tuple(
        IntegralIndex(tuple(powers))
        for powers in data["stable_unresolved_indices"]
    )
    if not targets:
        raise RuntimeError("saved one-neighbor rescue has no stable unresolved targets")

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    point = default_q01_probe_points(family)[0]
    start = time.perf_counter()

    def progress(stage, current=None, total=None):
        elapsed = time.perf_counter() - start
        suffix = ""
        if current is not None and total:
            suffix = f" {current}/{total} ({100.0 * current / total:.1f}%)"
        print(f"[progress {elapsed:9.1f}s] {stage}{suffix}", flush=True)

    print("QEDCalc Q01 4-line remaining-nine dot-focused two-neighbor rescue")
    print(f"sector: {tuple(data['sector'])}")
    print(f"targets: {len(targets)}")

    profile = audit_dot_two_neighbor_rescue_mod_p(
        family,
        targets,
        probe_point=point,
        primes=PRIMES,
        templates=templates,
        complexity_margin=1,
        progress=progress,
    )

    out = {
        "sector": profile.sector,
        "target_count": profile.target_count,
        "layer1_seed_count": profile.layer1_seed_count,
        "layer2_added_seed_count": profile.layer2_added_seed_count,
        "total_seed_count": profile.total_seed_count,
        "same_sector_seed_count": profile.same_sector_seed_count,
        "adjacent_sector_seed_count": profile.adjacent_sector_seed_count,
        "complexity_ceiling": profile.complexity_ceiling,
        "equation_count": profile.equation_count,
        "integral_count": profile.integral_count,
        "primes": profile.primes,
        "pivot_counts": profile.pivot_counts,
        "solved_target_counts": profile.solved_target_counts,
        "unresolved_target_counts": profile.unresolved_target_counts,
        "stable_across_primes": profile.stable_across_primes,
        "stable_solved_indices": profile.stable_solved_indices,
        "stable_unresolved_indices": profile.stable_unresolved_indices,
        "elapsed_seconds": time.perf_counter() - start,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"layer-1 seeds: {profile.layer1_seed_count}")
    print(f"layer-2 added seeds: {profile.layer2_added_seed_count}")
    print(f"total seeds: {profile.total_seed_count}")
    print(f"same-sector seeds: {profile.same_sector_seed_count}")
    print(f"adjacent-sector seeds: {profile.adjacent_sector_seed_count}")
    print(f"complexity ceiling: {profile.complexity_ceiling}")
    print(f"equations: {profile.equation_count}")
    print(f"integrals: {profile.integral_count}")
    print(f"primes: {profile.primes}")
    print(f"pivot counts: {profile.pivot_counts}")
    print(f"solved residuals: {profile.solved_target_counts}")
    print(f"unresolved residuals: {profile.unresolved_target_counts}")
    print(f"stable across primes: {profile.stable_across_primes}")
    print(f"stable unresolved residuals: {len(profile.stable_unresolved_indices)}")
    for powers in profile.stable_unresolved_indices:
        print(f"  unresolved I{powers}")
    print(f"generated: {OUTPUT}")
    print("Q01 remaining-nine two-neighbor rescue PASS")


if __name__ == "__main__":
    main()
