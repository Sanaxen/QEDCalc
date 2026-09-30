"""Read-only audit of interrupted Kira/FireFly runtime state.

This command never prepares, cleans, or launches a Kira project.  It only
reports whether known FireFly/Kira runtime-state directories survived an
interruption and shows the latest progress lines from existing logs.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

from three_loop.integral_family_classification import ROOT

STATE_NAMES = (
    "firefly_saves",
    "ff_save",
    "firefly_saves_alt",
    "sectormappings",
    "tmp",
    "results",
    "pyred",
)
PROGRESS_RE = re.compile(
    r"FireFly info:\s*Probe:\s*\d+\s*\|\s*Done:.*\|\s*Requires new prime field:.*"
)


def _tree_stats(path: Path) -> tuple[int, int]:
    files = 0
    total = 0
    if not path.exists():
        return files, total
    if path.is_file():
        try:
            return 1, path.stat().st_size
        except OSError:
            return 1, 0
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        files += 1
        try:
            total += item.stat().st_size
        except OSError:
            pass
    return files, total


def _latest_progress(log: Path) -> str | None:
    try:
        text = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    matches = PROGRESS_RE.findall(text)
    return matches[-1] if matches else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    args = parser.parse_args()

    prefix = f"kira_{args.family.lower()}"
    output = ROOT / "output"
    projects = sorted(
        (p for p in output.glob(prefix + "*") if p.is_dir()),
        key=lambda p: str(p),
    )

    print("QEDCalc FireFly resume-state audit")
    print(f"family: {args.family}")
    print(f"project candidates: {len(projects)}")

    any_state = False
    for project in projects:
        print()
        print(f"project: {project}")
        project_state = False
        for name in STATE_NAMES:
            path = project / name
            if not path.exists():
                continue
            files, total = _tree_stats(path)
            print(f"  state {name}: files={files} bytes={total}")
            if files or total or path.is_dir():
                project_state = True
                any_state = True

        logs = sorted(
            [*project.glob("*.log"), *project.glob("*.log.gz")],
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
        )
        if logs:
            latest = logs[-1]
            print(f"  latest log: {latest.name}")
            if latest.suffix != ".gz":
                progress = _latest_progress(latest)
                if progress:
                    print(f"  latest FireFly progress: {progress}")
        print(f"  resumable-state candidate: {project_state}")

    print()
    if any_state:
        print("RESULT: runtime state is present. Do not use fresh mode before testing resume.")
    else:
        print("RESULT: no known runtime-state directory was found for this family.")
    print("This audit is read-only and does not prove that Kira/FireFly will accept the saved state.")


if __name__ == "__main__":
    main()
