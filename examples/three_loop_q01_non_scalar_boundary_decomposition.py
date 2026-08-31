from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.non_scalar_boundary_decomposition import (
    decompose_non_scalar_boundary,
    decomposition_histograms,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_terminal_boundary_classification.json"
OUTPUT = ROOT / "output" / "3loop_q01_non_scalar_boundary_decomposition.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    indices = [
        IntegralIndex(tuple(row["index"]))
        for row in data["records"]
        if row["category"] == "nonscalar"
    ]
    profile = decompose_non_scalar_boundary(indices)
    hist = decomposition_histograms(profile)

    out = {
        "terminal_count": profile.terminal_count,
        "numerator_bearing_count": profile.numerator_bearing_count,
        "dot_only_count": profile.dot_only_count,
        "dot_and_numerator_count": profile.dot_and_numerator_count,
        **hist,
        "records": [record.__dict__ for record in profile.records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 non-scalar terminal boundary decomposition")
    print(f"non-scalar boundary terminals: {profile.terminal_count}")
    print(f"numerator-bearing terminals: {profile.numerator_bearing_count}")
    print(f"dot-only terminals: {profile.dot_only_count}")
    print(f"dot+numerator terminals: {profile.dot_and_numerator_count}")
    print(f"category histogram: {hist['category_histogram']}")
    print(f"dot-degree histogram: {hist['dot_degree_histogram']}")
    print(f"physical/aux degree histogram: {hist['physical_aux_degree_histogram']}")
    print(f"generated: {OUTPUT}")
    print("Q01 non-scalar terminal boundary decomposition PASS")


if __name__ == "__main__":
    main()
