from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.modp_lower_sector_distribution import (
    profile_lower_sector_distribution,
    sector_size_histogram,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_terminal_structure.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_lower_sector_distribution.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_sector = tuple(data["source_sector"])
    terminals = tuple(
        IntegralIndex(tuple(row["index"]))
        for row in data["records"]
        if tuple(row["sector"]) != source_sector
    )
    profile = profile_lower_sector_distribution(terminals, source_sector=source_sector)
    hist = sector_size_histogram(profile)

    out = {
        "source_sector": source_sector,
        "lower_terminal_count": profile.lower_terminal_count,
        "lower_sector_count": profile.lower_sector_count,
        "largest_sector_terminal_count": profile.largest_sector_terminal_count,
        "sector_size_histogram": hist,
        "rows": [row.__dict__ for row in profile.rows],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 mod-p lower-sector terminal distribution")
    print(f"source sector: {source_sector}")
    print(f"lower-sector terminals: {profile.lower_terminal_count}")
    print(f"distinct lower sectors: {profile.lower_sector_count}")
    print(f"largest lower sector terminal count: {profile.largest_sector_terminal_count}")
    print(f"sector-size histogram: {hist}")
    print("largest lower sectors:")
    for row in profile.rows[:10]:
        print(f"  {row.sector}: terminals={row.terminal_count}, complexity={row.min_complexity}..{row.max_complexity}")
    print(f"generated: {OUTPUT}")
    print("Q01 mod-p lower-sector terminal distribution PASS")


if __name__ == "__main__":
    main()
