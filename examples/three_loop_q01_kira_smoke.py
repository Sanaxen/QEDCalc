from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from three_loop.kira_backend import KiraSeedLimits, export_q01_kira_project, q01_kira_manifest
from three_loop.kira_wsl import kira_wsl_version, run_kira_wsl


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = ROOT / "output" / "kira_q01_4line_smoke"
SUMMARY = "qedcalc_kira_run_summary.json"


def _artifact_snapshot(project: Path) -> dict[str, object]:
    interesting = []
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(project).as_posix()
        if (
            rel.startswith("results/")
            or rel.startswith("sectormappings/")
            or rel.endswith("kira.db")
            or "master" in rel.lower()
        ):
            interesting.append({"path": rel, "size_bytes": path.stat().st_size})
    interesting.sort(key=lambda row: row["path"])
    return {
        "interesting_file_count": len(interesting),
        "interesting_files": interesting[:200],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export and optionally run the Q01 Kira four-line smoke benchmark")
    parser.add_argument("--r", type=int, default=4)
    parser.add_argument("--s", type=int, default=0)
    parser.add_argument("--d", type=int, default=0)
    parser.add_argument("--back-substitution", action="store_true")
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    args = parser.parse_args()

    limits = KiraSeedLimits(r=args.r, s=args.s, d=args.d)
    project = export_q01_kira_project(
        args.project,
        limits=limits,
        back_substitution=args.back_substitution,
    )
    manifest = q01_kira_manifest(limits)

    print("QEDCalc Q01 Kira four-line smoke benchmark")
    print(f"project: {project}")
    print(f"Kira top sector: {manifest['kira_top_sector']}")
    print(f"seed limits: r={limits.r}, s={limits.s}, d={limits.d}")
    print(
        "basis validation: "
        f"rank={manifest['basis_validation']['coefficient_matrix_rank']}/"
        f"{manifest['basis_validation']['scalar_product_count']}"
    )
    print("generated:")
    print(f"  {project / 'config' / 'integralfamilies.yaml'}")
    print(f"  {project / 'config' / 'kinematics.yaml'}")
    print(f"  {project / 'jobs.yaml'}")
    print(f"  {project / 'qedcalc_kira_manifest.json'}")

    if args.export_only:
        print("Q01 Kira export smoke PASS")
        return

    print("checking Kira in WSL ...", flush=True)
    version = kira_wsl_version()
    print(version, flush=True)
    print("starting Kira smoke reduction ...", flush=True)

    started = time.perf_counter()
    result = run_kira_wsl(project)
    total_wall = time.perf_counter() - started
    snapshot = _artifact_snapshot(project)
    summary = {
        "backend": "kira-wsl",
        "project": str(project),
        "seed_limits": {"r": limits.r, "s": limits.s, "d": limits.d},
        "back_substitution": bool(args.back_substitution),
        "returncode": result.returncode,
        "kira_wall_seconds": result.wall_seconds,
        "total_wall_seconds": total_wall,
        "linux_project_path": result.linux_project_path,
        "kira_version": result.version_text,
        "log_path": result.log_path,
        **snapshot,
    }
    (project / SUMMARY).write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")

    print(f"Kira return code: {result.returncode}")
    print(f"wall time: {result.wall_seconds:.3f}s")
    print(f"log: {result.log_path}")
    print(f"summary: {project / SUMMARY}")
    print(f"interesting Kira files: {snapshot['interesting_file_count']}")
    if result.returncode != 0:
        raise SystemExit(
            "Kira smoke run failed. Please send output/kira_q01_4line_smoke/kira_run.log."
        )
    print("Q01 Kira WSL smoke PASS")


if __name__ == "__main__":
    main()
