from __future__ import annotations

import json
from pathlib import Path
import time

from three_loop.kira_backend import KiraSeedLimits, export_q01_kira_project
from three_loop.kira_results import parse_kira_log
from three_loop.kira_wsl import kira_wsl_version, run_kira_wsl


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
OUTPUT = PROJECT / "qedcalc_kira_full_result.json"


def _result_files(project: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(project).as_posix()
        if rel.startswith("results/") or "master" in rel.lower():
            rows.append({"path": rel, "size_bytes": path.stat().st_size})
    rows.sort(key=lambda row: str(row["path"]))
    return rows


def main() -> None:
    limits = KiraSeedLimits(r=6, s=2, d=2)
    project = export_q01_kira_project(
        PROJECT,
        limits=limits,
        back_substitution=True,
    )

    print("QEDCalc Q01 Kira full r6s2d2 benchmark")
    print(f"project: {project}")
    print(f"seed limits: r={limits.r}, s={limits.s}, d={limits.d}")
    print("mode: sectorwise triangular reduction + back substitution")
    print("checking Kira in WSL ...", flush=True)
    print(kira_wsl_version(), flush=True)
    print("starting Kira full benchmark ...", flush=True)

    started = time.perf_counter()
    result = run_kira_wsl(project, log_name="kira_full.log")
    python_wall = time.perf_counter() - started

    print(f"Kira return code: {result.returncode}")
    print(f"wall time: {result.wall_seconds:.3f}s")
    print(f"log: {result.log_path}")
    if result.returncode != 0:
        raise SystemExit("Kira full benchmark failed; please send kira_full.log")

    parsed = parse_kira_log(result.log_path)
    files = _result_files(project)
    payload = {
        "backend": "kira-wsl",
        "mode": "sectorwise_triangular_with_back_substitution",
        "seed_limits": {"r": limits.r, "s": limits.s, "d": limits.d},
        "kira_wall_seconds": result.wall_seconds,
        "total_python_wall_seconds": python_wall,
        "parsed": parsed,
        "result_files": files,
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
    print(f"result files: {len(files)}")
    for row in files[:20]:
        print(f"  {row['path']} ({row['size_bytes']} bytes)")
    print(f"generated: {OUTPUT}")

    if parsed["declared_master_count"] is None:
        raise SystemExit("Kira full benchmark did not report a master count")
    if not parsed["master_count_consistent"]:
        raise SystemExit("Kira full benchmark master count/parser mismatch")
    if not files:
        raise SystemExit("Kira full benchmark produced no result files")
    print("Q01 Kira full r6s2d2 PASS")


if __name__ == "__main__":
    main()
