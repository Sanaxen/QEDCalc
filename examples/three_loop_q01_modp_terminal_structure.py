from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.modp_terminal_structure import (
    classify_modp_terminal_structure,
    terminal_structure_histograms,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_terminal_support.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_terminal_structure.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_sector = tuple(data["sector"])
    terminals = []
    for row in data["records"]:
        for powers in row["terminals"]:
            terminals.append(IntegralIndex(tuple(powers)))
    terminals = tuple(dict.fromkeys(terminals))

    family = q01_integral_family()
    profile = classify_modp_terminal_structure(
        family,
        terminals,
        source_sector=source_sector,
    )
    hist = terminal_structure_histograms(profile)

    out = {
        "source_sector": source_sector,
        "terminal_count": profile.terminal_count,
        "same_sector_count": profile.same_sector_count,
        "lower_sector_count": profile.lower_sector_count,
        "scalar_count": profile.scalar_count,
        "factorized_scalar_count": profile.factorized_scalar_count,
        "connected_scalar_count": profile.connected_scalar_count,
        "structurally_zero_count": profile.structurally_zero_count,
        "nonscalar_count": profile.nonscalar_count,
        **hist,
        "records": [record.__dict__ for record in profile.records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 mod-p terminal structure profile")
    print(f"source sector: {source_sector}")
    print(f"distinct non-pivot terminals: {profile.terminal_count}")
    print(f"same-sector terminals: {profile.same_sector_count}")
    print(f"lower-sector terminals: {profile.lower_sector_count}")
    print(f"scalar terminals: {profile.scalar_count}")
    print(f"factorized scalar terminals: {profile.factorized_scalar_count}")
    print(f"connected scalar terminals: {profile.connected_scalar_count}")
    print(f"structurally zero terminals: {profile.structurally_zero_count}")
    print(f"nonscalar terminals: {profile.nonscalar_count}")
    print(f"corrected-complexity histogram: {hist['corrected_complexity_histogram']}")
    print(f"active-line histogram: {hist['active_line_histogram']}")
    print(f"dot-degree histogram: {hist['dot_degree_histogram']}")
    print(f"full-numerator-degree histogram: {hist['full_numerator_degree_histogram']}")
    print(f"generated: {OUTPUT}")
    print("Q01 mod-p terminal structure profile PASS")


if __name__ == "__main__":
    main()
