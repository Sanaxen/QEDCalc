"""Generate the FORM export job for the completed exact-944 Q01 reduction.

The reduction already lives under alt_dir=exact944.  This script only prepares
kira2form to export the same 944 mandatory QEDCalc-demand integrals from that
completed database; no triangular or back-substitution work is rerun.
"""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
TARGET_FILE = PROJECT / "q01_944_targets"
JOB_FILE = PROJECT / "jobs_exact944_export.yaml"
EXACT_RESULTS = PROJECT / "exact944" / "results" / "Q01_full"
MASTERS_FILE = EXACT_RESULTS / "masters.final"
FAMILY = "Q01_full"
EXPECTED_TARGETS = 944
ALT_DIR = "exact944"


def _count_targets() -> int:
    if not TARGET_FILE.exists():
        raise SystemExit(f"ERROR: exact target list not found: {TARGET_FILE}")
    lines = [line.strip() for line in TARGET_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != EXPECTED_TARGETS or len(set(lines)) != EXPECTED_TARGETS:
        raise SystemExit(
            f"ERROR: expected exactly {EXPECTED_TARGETS} unique target integrals; "
            f"got total={len(lines)} unique={len(set(lines))}"
        )
    return len(lines)


def _render_job() -> str:
    return f'''jobs:\n  - kira2form:\n      target:\n        - [{FAMILY},q01_944_targets]\n      reconstruct_mass: false\n      alt_dir: {ALT_DIR}\n'''


def main() -> None:
    print("QEDCalc Q01 exact-944 Kira FORM export generator")
    print("mode: export completed exact944 database only; reduction is NOT rerun")
    if not PROJECT.exists():
        raise SystemExit(f"ERROR: project not found: {PROJECT}")
    count = _count_targets()
    if not MASTERS_FILE.exists():
        raise SystemExit(
            "ERROR: exact944 completed masters.final was not found: " + str(MASTERS_FILE)
        )
    JOB_FILE.write_text(_render_job(), encoding="utf-8", newline="\n")
    text = JOB_FILE.read_text(encoding="utf-8")
    required = [
        "kira2form:",
        "[Q01_full,q01_944_targets]",
        "reconstruct_mass: false",
        "alt_dir: exact944",
    ]
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit(f"ERROR: generated exact export job audit failed: {missing}")
    print("exact targets:", count)
    print("exact masters:", MASTERS_FILE)
    print("alt_dir:", ALT_DIR)
    print("generated:", JOB_FILE)
    print("Q01 exact-944 Kira FORM export generation PASS")


if __name__ == "__main__":
    main()
