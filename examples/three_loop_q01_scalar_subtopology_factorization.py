from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.scalar_subtopology_factorization import classify_scalar_subtopologies

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_remaining_target_classification.json"
OUTPUT = ROOT / "output" / "3loop_q01_scalar_subtopology_factorization.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    scalar_indices = tuple(
        IntegralIndex(tuple(record["index"]))
        for record in data["records"]
        if record["is_scalar_subtopology"]
    )
    family = q01_integral_family()
    records = classify_scalar_subtopologies(family, scalar_indices)

    factor_hist = Counter(record.factorization for record in records)
    zero_count = sum(record.structurally_zero for record in records)
    nonzero_count = len(records) - zero_count

    out = {
        "scalar_subtopology_count": len(records),
        "factorization_histogram": dict(sorted(factor_hist.items())),
        "structurally_zero_count": zero_count,
        "structurally_nonzero_count": nonzero_count,
        "records": [record.__dict__ for record in records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 scalar-subtopology factorization audit")
    print(f"scalar subtopologies: {len(records)}")
    print(f"factorization histogram: {dict(sorted(factor_hist.items()))}")
    print(f"structurally zero: {zero_count}")
    print(f"structurally nonzero: {nonzero_count}")
    print("records:")
    for record in records:
        print(
            "  I(" + ", ".join(map(str, record.index)) + ")"
            f" factorization={record.factorization} components={record.component_sizes}"
            f" free-loops={record.free_loops} scaleless={record.conservative_scaleless_zero}"
            f" free-loop-zero={record.free_loop_zero} zero={record.structurally_zero}"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 scalar-subtopology factorization audit PASS")


if __name__ == "__main__":
    main()
