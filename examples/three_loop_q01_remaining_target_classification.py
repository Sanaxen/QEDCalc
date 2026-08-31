from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.remaining_target_classification import classify_remaining_targets

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_remaining_target_profile.json"
OUTPUT = ROOT / "output" / "3loop_q01_remaining_target_classification.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    indices = tuple(IntegralIndex(tuple(record["index"])) for record in data["records"])
    records = classify_remaining_targets(indices)

    full_num_hist = Counter(record.full_numerator_degree for record in records)
    pneg_hist = Counter(record.physical_negative_degree for record in records)
    scalar_count = sum(record.is_scalar_subtopology for record in records)
    non_scalar_count = len(records) - scalar_count
    sector_hist = Counter(record.sector for record in records)

    out = {
        "remaining_target_count": len(records),
        "scalar_subtopology_count": scalar_count,
        "non_scalar_count": non_scalar_count,
        "full_numerator_degree_histogram": dict(sorted(full_num_hist.items())),
        "physical_negative_degree_histogram": dict(sorted(pneg_hist.items())),
        "sector_count": len(sector_hist),
        "sector_histogram": [
            {"sector": sector, "count": count}
            for sector, count in sorted(sector_hist.items(), key=lambda item: (item[1], item[0]), reverse=True)
        ],
        "records": [record.__dict__ for record in records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 remaining-target corrected classification")
    print(f"remaining targets: {len(records)}")
    print(f"scalar subtopologies: {scalar_count}")
    print(f"non-scalar targets: {non_scalar_count}")
    print(f"full numerator-degree histogram: {dict(sorted(full_num_hist.items()))}")
    print(f"physical negative-degree histogram: {dict(sorted(pneg_hist.items()))}")
    print(f"remaining sectors: {len(sector_hist)}")
    print("classified records:")
    for record in records:
        print(
            "  I(" + ", ".join(map(str, record.index)) + ")"
            f" sector={record.sector} physical-neg={record.physical_negative_degree}"
            f" aux-num={record.auxiliary_numerator_degree} full-num={record.full_numerator_degree}"
            f" corrected-complexity={record.corrected_complexity} scalar={record.is_scalar_subtopology}"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 remaining-target corrected classification PASS")


if __name__ == "__main__":
    main()
