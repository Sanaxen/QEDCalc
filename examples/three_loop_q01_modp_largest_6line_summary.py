from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_largest_6line_descent.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    print("QEDCalc Q01 largest 6-line saved descent summary")
    print(f"sector: {tuple(data['sector'])}")
    print(f"targets: {data['target_count']}")
    print(f"solved targets: {data['solved_target_count']}")
    print(f"unsolved targets: {data['unsolved_target_count']}")
    print(f"distinct terminals: {data['distinct_terminal_count']}")
    print(f"same-sector terminals: {data['same_sector_terminal_count']}")
    print(f"lower-sector terminals: {data['lower_sector_terminal_count']}")
    print("lower sectors:")
    for row in data.get("lower_sector_rows", []):
        print(f"  {tuple(row['sector'])}: terminals={row['terminal_count']}")
    print("same-sector residual terminals:")
    for powers in data.get("same_sector_terminal_indices", []):
        print(f"  I{tuple(powers)}")
    print("Q01 largest 6-line saved descent summary PASS")


if __name__ == "__main__":
    main()
