from __future__ import annotations

import json
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.modp_local_master_rank import audit_local_master_rank_mod_p
from three_loop.sector_local_probe import default_q01_probe_points

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_remaining9_two_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_remaining9_master_rank.json"
PRIMES = (1000003, 1000033)
UNDOTTED = IntegralIndex((1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0))


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    targets = tuple(IntegralIndex(tuple(p)) for p in data["stable_unresolved_indices"])
    if len(targets) != 9:
        raise RuntimeError(f"expected 9 stable unresolved residuals, got {len(targets)}")
    block = tuple(dict.fromkeys(targets + (UNDOTTED,)))

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

    print("QEDCalc Q01 remaining-nine corrected local master-rank audit")
    print(f"dotted targets: {len(targets)}")
    print(f"candidate block size: {len(block)}")
    print(f"undotted base: I{UNDOTTED.powers}")

    profile = audit_local_master_rank_mod_p(
        family,
        targets,
        block,
        probe_point=point,
        primes=PRIMES,
        templates=templates,
        complexity_margin=1,
        progress=progress,
    )

    out = profile.__dict__ | {
        "target_indices": [t.powers for t in targets],
        "undotted_index": UNDOTTED.powers,
        "block_indices": [b.powers for b in block],
        "elapsed_seconds": time.perf_counter() - start,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"seeds: {profile.seed_count}")
    print(f"equations: {profile.equation_count}")
    print(f"integrals: {profile.integral_count}")
    print(f"primes: {profile.primes}")
    print(f"full ranks: {profile.full_ranks}")
    print(f"ranks without 9 dotted targets: {profile.without_target_ranks}")
    print(f"added column rank of 9 dotted targets: {profile.target_added_column_ranks}")
    print(f"restricted rank of 9 dotted targets: {profile.target_restricted_ranks}")
    print(f"conditional free dimensions of 9-target block: {profile.target_conditional_free_dimensions}")
    print(f"ranks without 10-integral block: {profile.without_block_ranks}")
    print(f"added column rank of 10-integral block: {profile.block_added_column_ranks}")
    print(f"restricted rank of 10-integral block: {profile.block_restricted_ranks}")
    print(f"conditional free dimensions of 10-integral block: {profile.block_conditional_free_dimensions}")
    print(f"stable across primes: {profile.stable_across_primes}")
    print(f"generated: {OUTPUT}")
    print("Q01 remaining-nine corrected local master-rank audit PASS")


if __name__ == "__main__":
    main()
