from __future__ import annotations

import json
from pathlib import Path
import time

from three_loop.kira_wsl import kira_wsl_version, run_kira_wsl


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
JOBS = PROJECT / "jobs_export_form.yaml"
OUTPUT = PROJECT / "qedcalc_kira_export_form_result.json"


def _render_jobs() -> str:
    return """jobs:\n  - kira2form:\n      target:\n        - {topologies: [Q01_4line], sectors: [15], r: 6, s: 2, d: 2}\n"""


def _snapshot(project: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(project).as_posix()
        if rel.startswith("results/") or "kira2form" in rel.lower() or rel.endswith(".inc"):
            rows.append({"path": rel, "size_bytes": path.stat().st_size})
    rows.sort(key=lambda row: str(row["path"]))
    return rows


def main() -> None:
    if not (PROJECT / "results" / "kira.db").is_file():
        raise SystemExit(
            "Existing full-reduction database not found. Run "
            "run_three_loop_q01_kira_full_r6s2d2.bat first."
        )

    JOBS.write_text(_render_jobs(), encoding="utf-8", newline="\n")

    print("QEDCalc Q01 Kira FORM export probe")
    print(f"project: {PROJECT}")
    print("mode: export-only from existing r6s2d2 reduction database")
    print(f"jobs: {JOBS}")
    print("checking Kira in WSL ...", flush=True)
    print(kira_wsl_version(), flush=True)
    print("starting kira2form export ...", flush=True)

    before = {p.relative_to(PROJECT).as_posix(): p.stat().st_size for p in PROJECT.rglob("*") if p.is_file()}
    started = time.perf_counter()
    result = run_kira_wsl(PROJECT, jobs_file=JOBS.name, log_name="kira_export_form.log")
    wall = time.perf_counter() - started

    print(f"Kira return code: {result.returncode}")
    print(f"wall time: {result.wall_seconds:.3f}s")
    print(f"log: {result.log_path}")
    if result.returncode != 0:
        raise SystemExit("Kira FORM export failed; please send kira_export_form.log")

    files = _snapshot(PROJECT)
    changed: list[dict[str, object]] = []
    for row in files:
        old = before.get(str(row["path"]))
        if old is None or old != row["size_bytes"]:
            changed.append(row)

    payload = {
        "backend": "kira-wsl",
        "mode": "kira2form_export_existing_r6s2d2_database",
        "kira_wall_seconds": result.wall_seconds,
        "total_python_wall_seconds": wall,
        "files": files,
        "new_or_changed_files": changed,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")

    print(f"result/export files: {len(files)}")
    for row in files:
        marker = " *" if row in changed else ""
        print(f"  {row['path']} ({row['size_bytes']} bytes){marker}")
    print(f"generated: {OUTPUT}")
    print("Q01 Kira FORM export probe PASS")


if __name__ == "__main__":
    main()
