from __future__ import annotations

import json
from pathlib import Path
import time

from three_loop.kira_backend import KiraSeedLimits
from three_loop.kira_probe import export_q01_kira_initiate_probe
from three_loop.kira_results import parse_kira_log
from three_loop.kira_wsl import kira_wsl_version, run_kira_wsl


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_probe_r6s2d2"
OUTPUT = PROJECT / "qedcalc_kira_probe_result.json"


def main() -> None:
    limits = KiraSeedLimits(r=6, s=2, d=2)
    project = export_q01_kira_initiate_probe(PROJECT, limits=limits)

    print("QEDCalc Q01 Kira initiate-only scaling probe")
    print(f"project: {project}")
    print(f"seed limits: r={limits.r}, s={limits.s}, d={limits.d}")
    print("mode: run_initiate only; no triangular reduction/back substitution")
    print("checking Kira in WSL ...", flush=True)
    print(kira_wsl_version(), flush=True)
    print("starting Kira initiate-only probe ...", flush=True)

    started = time.perf_counter()
    result = run_kira_wsl(project, log_name="kira_probe.log")
    wall = time.perf_counter() - started
    print(f"Kira return code: {result.returncode}")
    print(f"wall time: {result.wall_seconds:.3f}s")
    print(f"log: {result.log_path}")
    if result.returncode != 0:
        raise SystemExit("Kira initiate-only probe failed; please send kira_probe.log")

    parsed = parse_kira_log(result.log_path)
    payload = {
        "backend": "kira-wsl",
        "mode": "initiate_only_scaling_probe",
        "seed_limits": {"r": limits.r, "s": limits.s, "d": limits.d},
        "kira_wall_seconds": result.wall_seconds,
        "total_python_wall_seconds": wall,
        "parsed": parsed,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")

    print(f"masters: {parsed['parsed_master_count']}")
    for master in parsed["masters"]:
        print(
            f"  {master['family']}[{','.join(str(v) for v in master['indices'])}] "
            f"# sector {master['sector']}"
        )
    print(f"generated: {OUTPUT}")
    if parsed["declared_master_count"] is None:
        raise SystemExit("Kira initiate-only probe did not report a master count")
    if not parsed["master_count_consistent"]:
        raise SystemExit("Kira initiate-only probe master count/parser mismatch")
    print("Q01 Kira initiate-only scaling probe PASS")


if __name__ == "__main__":
    main()
