from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.modp_block_rhs_structure import classify_block_rhs_structure

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_block_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_block_rhs_structure.json"
SOURCE_SECTOR = (1, 0, 1, 0, 1, 1, 0, 0, 0)


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    reductions = data.get("reductions", [])
    if not reductions:
        raise RuntimeError("block reduction JSON contains no reductions")

    supports = []
    for reduction in reductions:
        rhs = {
            IntegralIndex(tuple(index))
            for rule in reduction["rules"]
            for index, _coefficient in rule["rhs"]
        }
        supports.append(rhs)
    stable = all(support == supports[0] for support in supports[1:])
    if not stable:
        raise RuntimeError("block RHS support is not stable across primes")

    profile = classify_block_rhs_structure(
        supports[0], source_sector=SOURCE_SECTOR
    )
    out = {
        "source_sector": profile.source_sector,
        "unique_rhs_count": profile.unique_rhs_count,
        "same_sector_count": profile.same_sector_count,
        "lower_sector_count": profile.lower_sector_count,
        "higher_or_other_count": profile.higher_or_other_count,
        "distinct_lower_sector_count": profile.distinct_lower_sector_count,
        "largest_lower_sector_count": profile.largest_lower_sector_count,
        "active_line_histogram": dict(profile.active_line_histogram),
        "dot_degree_histogram": dict(profile.dot_degree_histogram),
        "full_numerator_degree_histogram": dict(profile.full_numerator_degree_histogram),
        "scalar_count": profile.scalar_count,
        "lower_sector_rows": [row.__dict__ for row in profile.lower_sector_rows],
        "same_sector_indices": profile.same_sector_indices,
        "higher_or_other_indices": profile.higher_or_other_indices,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line block RHS structure")
    print(f"source sector: {profile.source_sector}")
    print(f"unique RHS integrals: {profile.unique_rhs_count}")
    print(f"same-sector RHS: {profile.same_sector_count}")
    print(f"lower-sector RHS: {profile.lower_sector_count}")
    print(f"higher/other RHS: {profile.higher_or_other_count}")
    print(f"distinct lower sectors: {profile.distinct_lower_sector_count}")
    print(f"largest lower-sector count: {profile.largest_lower_sector_count}")
    print(f"active-line histogram: {dict(profile.active_line_histogram)}")
    print(f"dot-degree histogram: {dict(profile.dot_degree_histogram)}")
    print(f"full-numerator histogram: {dict(profile.full_numerator_degree_histogram)}")
    print(f"scalar RHS integrals: {profile.scalar_count}")
    print("lower sectors:")
    for row in profile.lower_sector_rows:
        print(f"  {row.sector}: integrals={row.terminal_count}")
    if profile.same_sector_indices:
        print("same-sector RHS integrals:")
        for powers in profile.same_sector_indices:
            print(f"  I{powers}")
    if profile.higher_or_other_indices:
        print("higher/other RHS integrals:")
        for powers in profile.higher_or_other_indices:
            print(f"  I{powers}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line block RHS structure PASS")


if __name__ == "__main__":
    main()
