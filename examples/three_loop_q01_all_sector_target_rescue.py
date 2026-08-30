from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.all_sector_target_rescue import audit_all_sector_target_rescue
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_all_sector_target_rescue_audit.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> None:
    print("QEDCalc Q01 all-sector finite-field target rescue audit", flush=True)
    family = q01_integral_family()
    targets = load_targets(SOURCE)
    t0 = time.perf_counter()
    templates = build_ibp_derivative_templates(family)
    t1 = time.perf_counter()
    state = {"stage": "starting", "changed": t1}
    lock = threading.Lock()
    stop = threading.Event()

    def progress(stage, current=None, total=None):
        now = time.perf_counter()
        with lock:
            state["stage"] = stage
            state["changed"] = now
        suffix = ""
        if current is not None and total is not None:
            pct = 100.0 * current / total if total else 100.0
            suffix = f" {current}/{total} ({pct:.1f}%)"
        print(f"[progress {now - t0:9.1f}s] {stage}{suffix}", flush=True)

    def heartbeat():
        while not stop.wait(30.0):
            now = time.perf_counter()
            with lock:
                stage = state["stage"]
                unchanged = now - state["changed"]
            print(
                f"[heartbeat {now - t0:9.1f}s] still running: {stage}; stage unchanged for {unchanged:.1f}s",
                flush=True,
            )

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    try:
        profile = audit_all_sector_target_rescue(
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
        "blocker_count": profile.blocker_count,
        "solved_target_counts": profile.solved_target_counts,
        "unsolved_target_counts": profile.unsolved_target_counts,
        "stable_across_runs": profile.stable_across_runs,
        "template_build_seconds": t1 - t0,
        "audit_seconds": t2 - t1,
        "rows": [
            {
                "sector": row.sector,
                "unresolved_target_count": row.unresolved_target_count,
                "blocker_count": row.blocker_count,
                "equation_count": row.equation_count,
                "integral_count": row.integral_count,
                "pivot_counts": row.pivot_counts,
                "solved_target_counts": row.solved_target_counts,
                "unsolved_target_counts": row.unsolved_target_counts,
                "stable_across_runs": row.stable_across_runs,
            }
            for row in profile.rows
        ],
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"targets: {profile.original_target_count}")
    print(f"unresolved after one-hop: {profile.unresolved_target_count}")
    print(f"target sectors processed: {profile.sector_count}")
    print(f"all blockers: {profile.blocker_count}")
    print(f"solved unresolved targets by run: {profile.solved_target_counts}")
    print(f"remaining unresolved targets by run: {profile.unsolved_target_counts}")
    print(f"stable across runs: {profile.stable_across_runs}")
    print(f"template build: {t1 - t0:.3f} s")
    print(f"all-sector audit: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 all-sector finite-field target rescue audit PASS")


if __name__ == "__main__":
    main()
