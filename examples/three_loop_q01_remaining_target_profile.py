from __future__ import annotations

import json
import re
import threading
import time
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.remaining_target_profile import audit_remaining_expanded_targets

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
EXPANDED = ROOT / "output" / "3loop_q01_expanded_sector_target_rescue_audit.json"
OUTPUT = ROOT / "output" / "3loop_q01_remaining_target_profile.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def load_selected_sectors(path: Path) -> tuple[tuple[int, ...], ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    sectors = []
    for row in rows:
        unsolved = row.get("unsolved_target_counts", [])
        if unsolved and int(unsolved[0]) > 0:
            sectors.append(tuple(int(x) for x in row["sector"]))
    return tuple(dict.fromkeys(sectors))


def main() -> None:
    print("QEDCalc Q01 remaining-target structural profile", flush=True)
    if not EXPANDED.exists():
        raise FileNotFoundError(f"Missing prerequisite: {EXPANDED}")

    family = q01_integral_family()
    targets = load_targets(SOURCE)
    selected_sectors = load_selected_sectors(EXPANDED)
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
        profile = audit_remaining_expanded_targets(
            family,
            targets,
            selected_sectors=selected_sectors,
            templates=templates,
            progress=progress,
        )
    finally:
        stop.set()
        thread.join(timeout=1.0)
    t2 = time.perf_counter()

    dot_hist = Counter(record.dot_degree for record in profile.records)
    numerator_hist = Counter(record.numerator_degree for record in profile.records)
    complexity_hist = Counter(record.total_complexity for record in profile.records)
    sector_hist = Counter(record.sector for record in profile.records)

    data = {
        "original_target_count": profile.original_target_count,
        "unresolved_after_one_hop_count": profile.unresolved_after_one_hop_count,
        "selected_sector_count": profile.selected_sector_count,
        "recomputed_sector_target_count": profile.recomputed_sector_target_count,
        "remaining_target_count": profile.remaining_target_count,
        "prime": profile.prime,
        "dot_degree_histogram": dict(sorted(dot_hist.items())),
        "numerator_degree_histogram": dict(sorted(numerator_hist.items())),
        "complexity_histogram": dict(sorted(complexity_hist.items())),
        "remaining_sector_counts": [
            {"sector": sector, "count": count}
            for sector, count in sorted(sector_hist.items(), key=lambda item: (item[1], item[0]), reverse=True)
        ],
        "records": [record.__dict__ for record in profile.records],
        "template_build_seconds": t1 - t0,
        "profile_seconds": t2 - t1,
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"targets: {profile.original_target_count}")
    print(f"unresolved after one-hop: {profile.unresolved_after_one_hop_count}")
    print(f"selected sectors from expanded audit: {profile.selected_sector_count}")
    print(f"targets recomputed in selected sectors: {profile.recomputed_sector_target_count}")
    print(f"remaining targets: {profile.remaining_target_count}")
    print(f"dot-degree histogram: {dict(sorted(dot_hist.items()))}")
    print(f"numerator-degree histogram: {dict(sorted(numerator_hist.items()))}")
    print(f"complexity histogram: {dict(sorted(complexity_hist.items()))}")
    print(f"remaining sectors: {len(sector_hist)}")
    for sector, count in sorted(sector_hist.items(), key=lambda item: (item[1], item[0]), reverse=True):
        print(f"  sector {sector}: {count}")
    print("remaining IntegralIndex records:")
    for record in profile.records:
        print(
            f"  I{record.index} sector={record.sector} dot={record.dot_degree} "
            f"num={record.numerator_degree} complexity={record.total_complexity}"
        )
    print(f"template build: {t1 - t0:.3f} s")
    print(f"remaining-target profile: {t2 - t1:.3f} s")
    print(f"generated: {OUTPUT}")
    print("Q01 remaining-target structural profile PASS")


if __name__ == "__main__":
    main()
