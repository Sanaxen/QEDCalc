from __future__ import annotations

import json
from pathlib import Path
import time

from three_loop.kira_backend import KiraSeedLimits, export_q01_kira_project
from three_loop.kira_results import parse_kira_log
from three_loop.kira_wsl import kira_wsl_version, run_kira_wsl


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_triangular_r6s2d2"
OUTPUT = PROJECT / "qedcalc_kira_triangular_result.json"


def main() -> None:
    limits = KiraSeedLimits(r=6, s=2, d=2)
    project = export_q01_kira_project(
        PROJECT,
        limits=limits,
        back_substitution=False,
    )

    print("QEDCalc Q01 Kira triangular scaling benchmark")
    print(f"project: {project}")
    print(f"seed limits: r={limits.r}, s={limits.s}, d={limits.d}")
    print("mode: sectorwise triangular reduction; no back substitution")
    print("checking Kira in WSL ...", flush=True)
    print(kira_wsl_version(), flush=True)
    print("starting Kira triangular benchmark ...", flush=True)

    started = time.perf_counter()
    result = run_kira_wsl(project, log_name="kira_triangular.log")
    python_wall = time.perf_counter() - started

    print(f"Kira return code: {result.returncode}")
    print(f"wall time: {result.wall_seconds:.3f}s")
    print(f"log: {result.log_path}")
    if result.returncode != 0:
        raise SystemExit("Kira triangular benchmark failed; please send kira_triangular.log")

    parsed = parse_kira_log(result.log_path)
    payload = {
        "backend": "kira-wsl",
        "mode": "sectorwise_triangular_no_back_substitution",
        "seed_limits": {"r": limits.r, "s": limits.s, "d": limits.d},
        "kira_wall_seconds": result.wall_seconds,
        "total_python_wall_seconds": python_wall,
        "parsed": parsed,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")

    print(f"masters: {parsed['parsed_master_count']}")
    for master in parsed["masters"]:
        print(
            f"  {master['family']}[{','.join(str(v) for v in master['indices'])}] "
            f"# sector {master['sector']}"
        )
    if parsed.get("triangular_seconds") is not None:
        print(f"triangular time from Kira log: {parsed['triangular_seconds']:.3f}s")
    if parsed.get("total_seconds") is not None:
        print(f"total time from Kira log: {parsed['total_seconds']:.3f}s")
    print(f"generated: {OUTPUT}")

    if parsed["declared_master_count"] is None:
        raise SystemExit("Kira triangular benchmark did not report a master count")
    if not parsed["master_count_consistent"]:
        raise SystemExit("Kira triangular benchmark master count/parser mismatch")
    print("Q01 Kira triangular r6s2d2 PASS")


if __name__ == "__main__":
    main()
