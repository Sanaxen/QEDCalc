from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.remaining_target_classification import classify_remaining_targets
from three_loop.scalar_subtopology_factorization import classify_scalar_subtopologies

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_neighbor_rescue.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_remaining9_profile.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    indices = tuple(IntegralIndex(tuple(p)) for p in data["stable_unresolved_indices"])
    family = q01_integral_family()
    classes = classify_remaining_targets(indices)

    scalar_indices = tuple(
        IntegralIndex(record.index) for record in classes if record.is_scalar_subtopology
    )
    scalar_factors = {
        record.index: record
        for record in classify_scalar_subtopologies(family, scalar_indices)
    }

    rows = []
    for record in classes:
        factor = scalar_factors.get(record.index)
        rows.append({
            "index": record.index,
            "sector": record.sector,
            "active_physical_lines": record.active_physical_lines,
            "dot_degree": record.dot_degree,
            "auxiliary_numerator_degree": record.auxiliary_numerator_degree,
            "physical_negative_degree": record.physical_negative_degree,
            "full_numerator_degree": record.full_numerator_degree,
            "corrected_complexity": record.corrected_complexity,
            "is_scalar_subtopology": record.is_scalar_subtopology,
            "factorization": factor.factorization if factor is not None else None,
            "structurally_zero": factor.structurally_zero if factor is not None else False,
        })

    dot_hist = Counter(row["dot_degree"] for row in rows)
    num_hist = Counter(row["full_numerator_degree"] for row in rows)
    complexity_hist = Counter(row["corrected_complexity"] for row in rows)
    scalar_count = sum(row["is_scalar_subtopology"] for row in rows)
    factorized_count = sum(
        bool(row["factorization"] and row["factorization"].startswith("factorized-"))
        for row in rows
    )
    zero_count = sum(row["structurally_zero"] for row in rows)

    out = {
        "sector": data["sector"],
        "remaining_count": len(rows),
        "scalar_count": scalar_count,
        "factorized_scalar_count": factorized_count,
        "structurally_zero_count": zero_count,
        "dot_degree_histogram": dict(sorted(dot_hist.items())),
        "full_numerator_degree_histogram": dict(sorted(num_hist.items())),
        "corrected_complexity_histogram": dict(sorted(complexity_hist.items())),
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 4-line remaining-nine structural profile")
    print(f"sector: {tuple(data['sector'])}")
    print(f"remaining residuals: {len(rows)}")
    print(f"scalar residuals: {scalar_count}")
    print(f"factorized scalar residuals: {factorized_count}")
    print(f"structurally zero residuals: {zero_count}")
    print(f"dot-degree histogram: {dict(sorted(dot_hist.items()))}")
    print(f"full-numerator-degree histogram: {dict(sorted(num_hist.items()))}")
    print(f"corrected-complexity histogram: {dict(sorted(complexity_hist.items()))}")
    print("remaining indices:")
    for row in rows:
        print(
            f"  I{tuple(row['index'])} "
            f"dot={row['dot_degree']} num={row['full_numerator_degree']} "
            f"complexity={row['corrected_complexity']} "
            f"scalar={row['is_scalar_subtopology']}"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 4-line remaining-nine structural profile PASS")


if __name__ == "__main__":
    main()
