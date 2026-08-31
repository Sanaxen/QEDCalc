from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.remaining_target_self_seed_rescue import audit_remaining_target_self_seed_rescue

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
REMAINING_SOURCE = ROOT / "output" / "3loop_q01_remaining_target_profile.json"
OUTPUT = ROOT / "output" / "3loop_q01_remaining_target_self_seed_rescue_audit.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_original_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def load_remaining_targets(path: Path) -> tuple[IntegralIndex, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(IntegralIndex(tuple(record["index"])) for record in data["records"])


def main() -> None:
    print("QEDCalc Q01 remaining-target self-seed finite-field rescue", flush=True)
    family = q01_integral_family()
    original_targets = load_original_targets(ORIGINAL_SOURCE)
    remaining_targets = load_remaining_targets(REMAINING_SOURCE)

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
        profile = audit_remaining_target_self_seed_rescue(
            family,
            original_targets,
            remaining_targets,
            templates=templates,
            progress=progress,
        )
    finally:
        stop.set()
        thread.join(timeout=1.0)
    t2 = time.perf_counter()

    data = {
        "original_target_count": profile.original_target_count,
        "remaining_target_count": profile.remaining_target_count,
        "sector_count": profile.sector_count,
        "blocker_seed_count": profile.blocker_seed_count,
        "target_seed_count": profile.target_seed_count,
        "total_seed_count": profile.total_seed_count,
        "solved_target_counts": profile.solved_target_counts,
        "unsolved_target_counts": profile.unsolved_target_counts,
        "stable_across_runs": profile.stable_across_runs,
        "rows": [row.__dict__ for row in profile.rows],
        "template_build_seconds": t1 - t0,
        "audit_seconds": t2 - t1,
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"original targets: {profile.original_target_count}")
    print(f"remaining targets supplied: {profile.remaining_target_count}")
    print(f"target sectors processed: {profile.sector_count}")
    print(f"blocker seeds in selected sectors: {profile.blocker_seed_count}")
    print(f"target self-seeds: {profile.target_seed_count}")
    print(f"total unique seeds: {profile.total_seed_count}")
    print(f"solved remaining targets by run: {profile.solved_target_counts}")
    print(f"still unresolved by run: {profile.unsolved_target_counts}")
    print(f"stable across runs: {profile.stable_across_runs}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"self-seed rescue audit: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 remaining-target self-seed rescue audit PASS")


if __name__ == "__main__":
    main()
