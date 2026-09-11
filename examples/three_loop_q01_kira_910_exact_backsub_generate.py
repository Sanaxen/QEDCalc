"""Generate the exact-944 Q01 Kira back-substitution job.

This reuses the completed exact944 triangular system and runs only back
substitution.  The exact 944-integral mandatory list and alt_dir=exact944 are
kept unchanged so the previous triangular work is reused rather than rerun.
"""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
TARGET_FILE = PROJECT / "q01_944_targets"
JOB_FILE = PROJECT / "jobs_exact944_backsub.yaml"
VERCONFIG = PROJECT / "exact944" / "tmp" / "Q01_full" / "VERconfig"
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
    return f'''jobs:\n  - reduce_sectors:\n      reduce:\n        - {{topologies: [{FAMILY}], sectors: [511], r: 9, s: 3, d: 0}}\n      select_integrals:\n        select_mandatory_list:\n          - [{FAMILY},q01_944_targets]\n      run_symmetries: false\n      run_initiate: false\n      run_triangular: false\n      run_back_substitution: true\n      conditional: true\n      alt_dir: {ALT_DIR}\n'''


def main() -> None:
    print("QEDCalc Q01 exact-944 Kira back-substitution generator")
    print("mode: reuse exact944 triangular system; back substitution only")
    if not PROJECT.exists():
        raise SystemExit(f"ERROR: project not found: {PROJECT}")
    if not VERCONFIG.exists():
        raise SystemExit(
            "ERROR: exact944 triangular system was not found: " + str(VERCONFIG)
        )
    count = _count_targets()
    JOB_FILE.write_text(_render_job(), encoding="utf-8", newline="\n")
    text = JOB_FILE.read_text(encoding="utf-8")
    required = [
        "select_mandatory_list:",
        "[Q01_full,q01_944_targets]",
        "run_symmetries: false",
        "run_initiate: false",
        "run_triangular: false",
        "run_back_substitution: true",
        "conditional: true",
        "alt_dir: exact944",
    ]
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit(f"ERROR: generated exact back-substitution job audit failed: {missing}")
    print("exact targets:", count)
    print("triangular system:", VERCONFIG)
    print("alt_dir:", ALT_DIR)
    print("generated:", JOB_FILE)
    print("Q01 exact-944 Kira back-substitution generation PASS")


if __name__ == "__main__":
    main()
