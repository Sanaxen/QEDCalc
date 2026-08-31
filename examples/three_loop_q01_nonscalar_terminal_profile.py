from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.nonscalar_terminal_profile import classify_nonscalar_terminals, profile_histograms

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_terminal_boundary_classification.json"
OUTPUT = ROOT / "output" / "3loop_q01_nonscalar_terminal_profile.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    indices = []
    for row in data["records"]:
        if row["category"] == "nonscalar":
            indices.append(IntegralIndex(tuple(row["index"])))
    profile = classify_nonscalar_terminals(indices)
    hist = profile_histograms(profile)

    out = {
        "terminal_count": profile.terminal_count,
        "physical_only_count": profile.physical_only_count,
        "auxiliary_only_count": profile.auxiliary_only_count,
        "mixed_count": profile.mixed_count,
        **hist,
        "records": [record.__dict__ for record in profile.records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 nonscalar symbolic terminal profile")
    print(f"nonscalar terminals: {profile.terminal_count}")
    print(f"physical-numerator only: {profile.physical_only_count}")
    print(f"auxiliary-numerator only: {profile.auxiliary_only_count}")
    print(f"mixed physical+auxiliary numerator: {profile.mixed_count}")
    print(f"negative-slot histogram: {hist['negative_slot_histogram']}")
    print(f"physical/aux degree histogram: {hist['physical_aux_degree_histogram']}")
    print(f"corrected-complexity histogram: {hist['corrected_complexity_histogram']}")
    print(f"active-line histogram: {hist['active_line_histogram']}")
    print(f"generated: {OUTPUT}")
    print("Q01 nonscalar symbolic terminal profile PASS")


if __name__ == "__main__":
    main()
