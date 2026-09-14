"""Run the Q01 symmetry supplement without iterative FireFly splitting.

This wrapper exists because the small 146-target supplemental system triggers a
FireFly validation failure when Kira splits it with
``iterative_reduction: sectorwise``.  The original exact944 FireFly workflow is
left unchanged.  This supplemental retry uses a fresh alt_dir and a single
non-iterative FireFly reduction, then reuses the validated audit logic from the
base helper.
"""
from __future__ import annotations

import argparse

from examples import three_loop_q01_kira_symmetry_supplement_firefly as base

ALT_DIR_NAME = "symmetry_supplement_firefly_v3_noniterative"


def _configure_base() -> None:
    base.ALT_DIR_NAME = ALT_DIR_NAME
    base.ALT_ROOT = base.PROJECT / ALT_DIR_NAME


def generate() -> None:
    _configure_base()
    targets = base._load_source_unresolved()

    maxima = [0, 0, 0]
    for target in targets:
        r, s, d = base._bounds(target)
        maxima[0] = max(maxima[0], r)
        maxima[1] = max(maxima[1], s)
        maxima[2] = max(maxima[2], d)
    target_rmax, smax, dmax = maxima

    sector_min_r = base.TOP_SECTOR.bit_count()
    rmax = max(target_rmax, sector_min_r)

    base.TARGET_FILE.write_text(
        "\n".join(base._integral_text(v) for v in targets) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    # Intentionally omit iterative_reduction.  Kira therefore hands one
    # selected system to FireFly instead of creating the 14 consecutive
    # reductions seen in the failing sectorwise supplemental run.
    text = f'''jobs:\n  - reduce_sectors:\n      reduce:\n        - {{topologies: [{base.FAMILY}], sectors: [{base.TOP_SECTOR}], r: {rmax}, s: {smax}, d: {dmax}}}\n      select_integrals:\n        select_mandatory_list:\n          - [{base.FAMILY},{base.TARGET_FILE.name}]\n      run_symmetries: true\n      run_initiate: true\n      run_triangular: false\n      run_back_substitution: false\n      run_firefly: true\n      alt_dir: {ALT_DIR_NAME}\n  - kira2form:\n      target:\n        - [{base.FAMILY},{base.TARGET_FILE.name}]\n      alt_dir: {ALT_DIR_NAME}\n'''
    base.JOB_FILE.write_text(text, encoding="utf-8", newline="\n")

    print("QEDCalc Q01 symmetry supplemental FireFly generator")
    print("mode: isolated non-iterative supplemental reduction")
    print("supplement targets:", len(targets))
    print("target-derived r max:", target_rmax)
    print(f"top sector: {base.TOP_SECTOR}; active lines / minimum r: {sector_min_r}")
    print(f"effective seed bounds: r={rmax} s={smax} d={dmax}")
    print("iterative_reduction: disabled")
    print("alt_dir:", ALT_DIR_NAME)
    print("generated target list:", base.TARGET_FILE)
    print("generated job:", base.JOB_FILE)
    print("Q01 symmetry supplemental non-iterative FireFly generation PASS")


def audit() -> None:
    _configure_base()
    base.audit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "audit"))
    args = parser.parse_args()
    if args.mode == "generate":
        generate()
    else:
        audit()


if __name__ == "__main__":
    main()
