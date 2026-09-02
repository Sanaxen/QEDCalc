from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex

ROOT = Path(__file__).resolve().parents[1]
STEP3_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure_step3.json"
SUPPORT_SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure5994_same_sector_support.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure5994_support_profile.json"
PHYSICAL_COUNT = 9


def complexity(index: IntegralIndex) -> dict[str, int]:
    powers = index.powers
    physical_dot = sum(max(powers[i] - 1, 0) for i in range(PHYSICAL_COUNT))
    physical_negative = sum(max(-powers[i], 0) for i in range(PHYSICAL_COUNT))
    auxiliary_negative = sum(max(-powers[i], 0) for i in range(PHYSICAL_COUNT, len(powers)))
    total_negative = physical_negative + auxiliary_negative
    return {
        "physical_dot_degree": physical_dot,
        "physical_negative_degree": physical_negative,
        "auxiliary_negative_degree": auxiliary_negative,
        "total_negative_degree": total_negative,
        "total_complexity": physical_dot + total_negative,
    }


def histogram(indices):
    total = Counter()
    dot = Counter()
    negative = Counter()
    pair = Counter()
    for index in indices:
        c = complexity(index)
        total[c["total_complexity"]] += 1
        dot[c["physical_dot_degree"]] += 1
        negative[c["total_negative_degree"]] += 1
        pair[(c["physical_dot_degree"], c["total_negative_degree"])] += 1
    return {
        "total_complexity": {str(k): total[k] for k in sorted(total)},
        "physical_dot_degree": {str(k): dot[k] for k in sorted(dot)},
        "total_negative_degree": {str(k): negative[k] for k in sorted(negative)},
        "dot_negative_pairs": [
            {"dot": a, "negative": b, "count": count}
            for (a, b), count in sorted(pair.items())
        ],
    }


def main() -> None:
    step3 = json.loads(STEP3_SOURCE.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT_SOURCE.read_text(encoding="utf-8"))

    if not support.get("stable_support_across_primes", False):
        raise RuntimeError("same-sector support is not stable across primes")
    rows = support.get("rows", [])
    if not rows:
        raise RuntimeError("same-sector support output has no rows")

    block = tuple(IntegralIndex(tuple(p)) for p in step3["expanded_block_indices"])
    same_support = tuple(IntegralIndex(tuple(p)) for p in rows[0]["same_sector_support_indices"])
    block_set = set(block)
    new_support = tuple(index for index in same_support if index not in block_set)

    if len(block) != 5994:
        raise RuntimeError(f"expected 5994 base block, got {len(block)}")
    if len(same_support) != 11454:
        raise RuntimeError(f"expected 11454 stable same-sector support integrals, got {len(same_support)}")

    base_hist = histogram(block)
    new_hist = histogram(new_support)

    complexity_layers = Counter(complexity(index)["total_complexity"] for index in new_support)
    cumulative = 0
    layer_plan = []
    for degree in sorted(complexity_layers, reverse=True):
        count = complexity_layers[degree]
        cumulative += count
        layer_plan.append(
            {
                "total_complexity": degree,
                "count": count,
                "cumulative_from_hardest": cumulative,
            }
        )

    out = {
        "sector": support["sector"],
        "base_block_count": len(block),
        "stable_same_sector_support_count": len(same_support),
        "new_same_sector_support_count": len(new_support),
        "full_union_count": len(block_set | set(new_support)),
        "base_histogram": base_hist,
        "new_support_histogram": new_hist,
        "descending_complexity_layers": layer_plan,
        "recommendation": (
            "Do not form the full base+support block at once. Process same-sector support "
            "in descending total-complexity layers and allow only lower-complexity same-sector "
            "columns plus proper subsectors on the RHS."
        ),
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 closure5994 same-sector support profile")
    print(f"sector: {tuple(out['sector'])}")
    print(f"base block: {out['base_block_count']}")
    print(f"stable same-sector support: {out['stable_same_sector_support_count']}")
    print(f"new same-sector support: {out['new_same_sector_support_count']}")
    print(f"full union if expanded at once: {out['full_union_count']}")
    print("descending total-complexity layers:")
    for layer in layer_plan:
        print(
            f"  complexity {layer['total_complexity']}: {layer['count']} "
            f"(cumulative {layer['cumulative_from_hardest']})"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 closure5994 same-sector support profile PASS")


if __name__ == "__main__":
    main()
