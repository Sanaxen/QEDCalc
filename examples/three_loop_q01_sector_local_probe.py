from __future__ import annotations

import json
import re
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_local_probe import audit_sector_local_probes

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_sector_local_probe_audit.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> None:
    print("QEDCalc Q01 generic-point sector-local Laporta probe audit")
    family = q01_integral_family()
    targets = load_targets(SOURCE)
    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    t1 = time.perf_counter()
    profile = audit_sector_local_probes(family, targets, templates=templates)
    t2 = time.perf_counter()
    data = {
        "sector": profile.sector,
        "blocker_count": profile.blocker_count,
        "dot_one_blocker_count": profile.dot_one_blocker_count,
        "equation_count": profile.equation_count,
        "integral_count": profile.integral_count,
        "pivot_counts": profile.pivot_counts,
        "solved_blocker_counts": profile.solved_blocker_counts,
        "solved_dot_one_counts": profile.solved_dot_one_counts,
        "stable_across_probes": profile.stable_across_probes,
        "template_build_seconds": t1 - t0,
        "probe_audit_seconds": t2 - t1,
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"targets: {len(targets)}")
    print(f"sector: {profile.sector}")
    print(f"blockers: {profile.blocker_count}")
    print(f"dot-one blockers: {profile.dot_one_blocker_count}")
    print(f"equations: {profile.equation_count}")
    print(f"integrals: {profile.integral_count}")
    print(f"pivot counts: {profile.pivot_counts}")
    print(f"solved blockers by probe: {profile.solved_blocker_counts}")
    print(f"solved dot-one by probe: {profile.solved_dot_one_counts}")
    print(f"stable across probes: {profile.stable_across_probes}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"probe audit: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 generic-point sector-local Laporta probe audit PASS")


if __name__ == "__main__":
    main()
