"""Generate the closure-wave-1 Q01 Kira triangular job.

This reuses the validated closure-wave-1 mandatory list produced from the
original 944 targets plus unresolved exact944 RHS leaves.  Results stay
isolated under alt_dir=exact944closure1.  Back substitution remains disabled.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
TARGET_FILE = PROJECT / "q01_exact944_closure1_targets"
JOB_FILE = PROJECT / "jobs_exact944_closure1_triangular.yaml"
FAMILY = "Q01_full"
ALT_DIR = "exact944closure1"


def _parse_target(line: str) -> tuple[int, ...]:
    text = line.strip()
    prefix = FAMILY + "["
    if not text.startswith(prefix) or not text.endswith("]"):
        raise ValueError(f"unexpected target syntax: {text!r}")
    values = tuple(int(v.strip()) for v in text[len(prefix):-1].split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices: {text!r}")
    return values


def _bounds(indices: tuple[int, ...]) -> tuple[int, int, int]:
    r = sum(v for v in indices if v > 0)
    s = sum(-v for v in indices if v < 0)
    d = sum(max(v - 1, 0) for v in indices if v > 0)
    return r, s, d


def main() -> None:
    print("QEDCalc Q01 exact944 closure-wave-1 triangular generator")
    print("mode: closure-wave-1 mandatory list; triangular only")
    if not TARGET_FILE.exists():
        raise SystemExit(f"ERROR: closure-wave-1 target list not found: {TARGET_FILE}")

    lines = [line.strip() for line in TARGET_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines or len(lines) != len(set(lines)):
        raise SystemExit(
            f"ERROR: closure-wave-1 target list must be non-empty and unique; "
            f"got total={len(lines)} unique={len(set(lines))}"
        )

    targets = tuple(_parse_target(line) for line in lines)
    maxima = [0, 0, 0]
    for target in targets:
        r, s, d = _bounds(target)
        maxima[0] = max(maxima[0], r)
        maxima[1] = max(maxima[1], s)
        maxima[2] = max(maxima[2], d)
    rmax, smax, dmax = maxima

    text = f'''jobs:\n  - reduce_sectors:\n      reduce:\n        - {{topologies: [{FAMILY}], sectors: [511], r: {rmax}, s: {smax}, d: {dmax}}}\n      select_integrals:\n        select_mandatory_list:\n          - [{FAMILY},{TARGET_FILE.name}]\n      run_symmetries: true\n      run_initiate: true\n      run_triangular: sectorwise\n      run_back_substitution: false\n      alt_dir: {ALT_DIR}\n'''
    JOB_FILE.write_text(text, encoding="utf-8", newline="\n")

    required = [
        "select_mandatory_list:",
        f"[{FAMILY},{TARGET_FILE.name}]",
        "run_triangular: sectorwise",
        "run_back_substitution: false",
        f"alt_dir: {ALT_DIR}",
    ]
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit(f"ERROR: generated closure1 triangular job audit failed: {missing}")

    print("closure-wave-1 targets:", len(targets))
    print(f"seed bounds: r={rmax} s={smax} d={dmax}")
    print("alt_dir:", ALT_DIR)
    print("generated:", JOB_FILE)
    print("Q01 exact944 closure-wave-1 triangular generation PASS")


if __name__ == "__main__":
    main()
