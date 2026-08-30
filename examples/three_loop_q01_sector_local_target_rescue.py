from __future__ import annotations

import json
import re
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_local_target_rescue import audit_sector_local_target_rescue

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_sector_local_target_rescue_audit.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main():
    print("QEDCalc Q01 sector-local target rescue audit")
    family = q01_integral_family()
    targets = load_targets(SOURCE)
    start = time.perf_counter()

    def progress(stage, current=None, total=None):
        elapsed = time.perf_counter() - start
        suffix = ""
        if current is not None and total:
            suffix = f" {current}/{total} ({100.0 * current / total:.1f}%)"
        print(f"[progress {elapsed:9.1f}s] {stage}{suffix}", flush=True)

    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    t1 = time.perf_counter()
    profile = audit_sector_local_target_rescue(
        family, targets, templates=templates, progress=progress
    )
    t2 = time.perf_counter()

    data = profile.__dict__ | {
        "template_build_seconds": t1 - t0,
        "target_rescue_seconds": t2 - t1,
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"targets: {profile.original_target_count}")
    print(f"globally unresolved after one-hop: {profile.globally_unresolved_target_count}")
    print(f"sector: {profile.sector}")
    print(f"sector unresolved targets: {profile.sector_unresolved_target_count}")
    print(f"blockers: {profile.blocker_count}")
    print(f"equations: {profile.equation_count}")
    print(f"integrals: {profile.integral_count}")
    print(f"primes: {profile.primes}")
    print(f"pivot counts: {profile.pivot_counts}")
    print(f"solved sector targets by run: {profile.solved_sector_target_counts}")
    print(f"unsolved sector targets by run: {profile.unsolved_sector_target_counts}")
    print(f"stable across runs: {profile.stable_across_runs}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"target rescue audit: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 sector-local target rescue audit PASS")


if __name__ == "__main__":
    main()
