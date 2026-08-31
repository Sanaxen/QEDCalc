from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.laporta_plan import dot_degree, physical_sector
from three_loop.remaining_target_classification import full_numerator_degree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_all_higher_sector_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_all_higher_sector_rhs_structure.json"
PHYSICAL_COUNT = 9


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_sector = tuple(int(x) for x in data["sector"])
    source_lines = sum(source_sector)
    reductions = data["reductions"]
    if not reductions:
        raise RuntimeError("all-higher sector reduction JSON contains no reductions")

    supports = []
    for reduction in reductions:
        support = {
            tuple(int(x) for x in rhs_index)
            for rule in reduction["rules"]
            for rhs_index, coeff in rule["rhs"]
            if int(coeff) != 0
        }
        supports.append(support)
    if any(support != supports[0] for support in supports[1:]):
        raise RuntimeError("all-higher sector RHS support differs across primes")

    indices = tuple(IntegralIndex(powers) for powers in sorted(supports[0]))
    same: list[IntegralIndex] = []
    lower: list[IntegralIndex] = []
    higher: list[IntegralIndex] = []
    lower_counts = Counter()
    higher_counts = Counter()
    active_hist = Counter()
    dot_hist = Counter()
    numerator_hist = Counter()

    for index in indices:
        sector = physical_sector(index, PHYSICAL_COUNT)
        active = sum(sector)
        active_hist[active] += 1
        dot_hist[dot_degree(index, PHYSICAL_COUNT)] += 1
        numerator_hist[full_numerator_degree(index, PHYSICAL_COUNT)] += 1
        if sector == source_sector:
            same.append(index)
        elif active < source_lines:
            lower.append(index)
            lower_counts[sector] += 1
        else:
            higher.append(index)
            higher_counts[sector] += 1

    out = {
        "source_sector": source_sector,
        "rhs_integral_count": len(indices),
        "same_sector_count": len(same),
        "lower_sector_count": len(lower),
        "higher_or_other_count": len(higher),
        "distinct_lower_sector_count": len(lower_counts),
        "distinct_higher_sector_count": len(higher_counts),
        "largest_lower_sector_count": max(lower_counts.values(), default=0),
        "active_line_histogram": dict(sorted(active_hist.items())),
        "dot_degree_histogram": dict(sorted(dot_hist.items())),
        "full_numerator_histogram": dict(sorted(numerator_hist.items())),
        "same_sector_indices": [index.powers for index in sorted(same, key=lambda x: x.powers)],
        "lower_sector_rows": [
            {"sector": sector, "count": count}
            for sector, count in sorted(lower_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "higher_sector_rows": [
            {"sector": sector, "count": count}
            for sector, count in sorted(higher_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "higher_or_other_indices": [index.powers for index in sorted(higher, key=lambda x: x.powers)],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line all-higher sector RHS structure")
    print(f"source sector: {source_sector}")
    print(f"unique RHS integrals: {len(indices)}")
    print(f"same-sector RHS: {len(same)}")
    print(f"lower-sector RHS: {len(lower)}")
    print(f"higher/other RHS: {len(higher)}")
    print(f"distinct lower sectors: {len(lower_counts)}")
    print(f"distinct higher sectors: {len(higher_counts)}")
    print(f"largest lower-sector count: {max(lower_counts.values(), default=0)}")
    print(f"active-line histogram: {dict(sorted(active_hist.items()))}")
    print(f"dot-degree histogram: {dict(sorted(dot_hist.items()))}")
    print(f"full-numerator histogram: {dict(sorted(numerator_hist.items()))}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line all-higher sector RHS structure PASS")


if __name__ == "__main__":
    main()
