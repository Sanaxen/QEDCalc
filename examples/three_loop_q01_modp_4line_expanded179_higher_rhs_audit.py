from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.laporta_plan import dot_degree, physical_sector
from three_loop.remaining_target_classification import full_numerator_degree

ROOT = Path(__file__).resolve().parents[1]
REDUCTION_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_block_reduction.json"
STRUCTURE_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_expanded179_rhs_structure.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_expanded179_higher_rhs_audit.json"
PHYSICAL_COUNT = 9


def main() -> None:
    reduction_data = json.loads(REDUCTION_SOURCE.read_text(encoding="utf-8"))
    structure_data = json.loads(STRUCTURE_SOURCE.read_text(encoding="utf-8"))

    source_sector = tuple(int(x) for x in structure_data["source_sector"])
    higher = tuple(
        IntegralIndex(tuple(int(x) for x in powers))
        for powers in structure_data["higher_or_other_indices"]
    )
    if len(higher) != 6:
        raise RuntimeError(f"expected 6 higher/other RHS integrals, got {len(higher)}")

    higher_set = set(higher)
    reductions = reduction_data["reductions"]
    if len(reductions) < 2:
        raise RuntimeError("expected at least two prime reductions")

    prime_rows = []
    occurrence_signatures = []
    for reduction in reductions:
        prime = int(reduction["prime"])
        occurrence_count = Counter()
        target_map = defaultdict(list)
        for rule_no, rule in enumerate(reduction["rules"]):
            target = tuple(int(x) for x in rule["target"])
            for rhs_index, coeff in rule["rhs"]:
                index = IntegralIndex(tuple(int(x) for x in rhs_index))
                if index in higher_set and int(coeff) != 0:
                    occurrence_count[index] += 1
                    target_map[index].append((rule_no, target))

        signature = tuple(
            (index.powers, occurrence_count[index], tuple(target for _, target in target_map[index]))
            for index in sorted(higher, key=lambda x: x.powers)
        )
        occurrence_signatures.append(signature)
        prime_rows.append(
            {
                "prime": prime,
                "rows": [
                    {
                        "index": index.powers,
                        "sector": physical_sector(index, PHYSICAL_COUNT),
                        "active_lines": sum(physical_sector(index, PHYSICAL_COUNT)),
                        "dot_degree": dot_degree(index, PHYSICAL_COUNT),
                        "full_numerator_degree": full_numerator_degree(index, PHYSICAL_COUNT),
                        "rule_occurrence_count": occurrence_count[index],
                        "target_indices": [target for _, target in target_map[index]],
                    }
                    for index in sorted(higher, key=lambda x: x.powers)
                ],
            }
        )

    stable = all(sig == occurrence_signatures[0] for sig in occurrence_signatures[1:])
    sector_counts = Counter(physical_sector(index, PHYSICAL_COUNT) for index in higher)

    out = {
        "source_sector": source_sector,
        "higher_integral_count": len(higher),
        "distinct_higher_sector_count": len(sector_counts),
        "higher_sector_rows": [
            {"sector": sector, "count": count}
            for sector, count in sorted(sector_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "occurrence_pattern_stable_across_primes": stable,
        "prime_rows": prime_rows,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line expanded 179-block higher-RHS audit")
    print(f"source sector: {source_sector}")
    print(f"higher/other RHS integrals: {len(higher)}")
    print(f"distinct higher sectors: {len(sector_counts)}")
    for sector, count in sorted(sector_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"  sector {sector}: {count}")
    print(f"occurrence pattern stable across primes: {stable}")
    first = prime_rows[0]
    print(f"prime {first['prime']} higher integrals:")
    for row in first["rows"]:
        print(
            f"  I{tuple(row['index'])} sector={tuple(row['sector'])} "
            f"dot={row['dot_degree']} num={row['full_numerator_degree']} "
            f"appears_in_rules={row['rule_occurrence_count']}"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 four-line expanded 179-block higher-RHS audit PASS")


if __name__ == "__main__":
    main()
