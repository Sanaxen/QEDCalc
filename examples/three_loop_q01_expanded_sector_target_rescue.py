from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.expanded_sector_target_rescue import audit_expanded_sector_target_rescue
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_expanded_sector_target_rescue_audit.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> None:
    print("QEDCalc Q01 expanded same-sector predecessor target rescue audit", flush=True)
    family = q01_integral_family()
    targets = load_targets(SOURCE)
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
        profile = audit_expanded_sector_target_rescue(
            family, targets, templates=templates, progress=progress
        )
    finally:
        stop.set()
        thread.join(timeout=1.0)
    t2 = time.perf_counter()

    data = {
        "original_target_count": profile.original_target_count,
        "unresolved_target_count": profile.unresolved_target_count,
        "sector_count": profile.sector_count,
        "blocker_seed_count": profile.blocker_seed_count,
        "predecessor_seed_count": profile.predecessor_seed_count,
        "total_seed_count": profile.total_seed_count,
        "solved_target_counts": profile.solved_target_counts,
        "unsolved_target_counts": profile.unsolved_target_counts,
        "stable_across_runs": profile.stable_across_runs,
        "rows": [row.__dict__ for row in profile.rows],
        "template_build_seconds": t1 - t0,
        "audit_seconds": t2 - t1,
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"targets: {profile.original_target_count}")
    print(f"unresolved after one-hop: {profile.unresolved_target_count}")
    print(f"target sectors processed: {profile.sector_count}")
    print(f"blocker seeds: {profile.blocker_seed_count}")
    print(f"additional same-sector predecessor seeds: {profile.predecessor_seed_count}")
    print(f"total seeds: {profile.total_seed_count}")
    print(f"solved unresolved targets by run: {profile.solved_target_counts}")
    print(f"remaining unresolved targets by run: {profile.unsolved_target_counts}")
    print(f"stable across runs: {profile.stable_across_runs}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"expanded-sector audit: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 expanded same-sector predecessor target rescue audit PASS")


if __name__ == "__main__":
    main()
