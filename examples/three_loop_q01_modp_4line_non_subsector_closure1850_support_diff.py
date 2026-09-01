from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.laporta_plan import physical_sector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure1850_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure1850_support_diff.json"
PHYSICAL_COUNT = 9


def _support(row: dict) -> set[tuple[int, ...]]:
    return {
        tuple(int(x) for x in rhs_index)
        for rule in row.get("rules", [])
        for rhs_index, coeff in rule.get("rhs", [])
        if int(coeff) != 0
    }


def _is_subsector(sector: tuple[int, ...], source_sector: tuple[int, ...]) -> bool:
    return all(int(a) <= int(b) for a, b in zip(sector, source_sector))


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    if len(rows) != 2:
        raise RuntimeError(f"expected two prime rows, got {len(rows)}")

    source_sector = tuple(int(x) for x in data["sector"])
    s0 = _support(rows[0])
    s1 = _support(rows[1])
    only0 = sorted(s0 - s1)
    only1 = sorted(s1 - s0)
    common = s0 & s1
    union = s0 | s1

    def classify(items):
        same = []
        proper = []
        nonsub = []
        for powers in items:
            idx = IntegralIndex(powers)
            sector = physical_sector(idx, PHYSICAL_COUNT)
            if sector == source_sector:
                same.append(powers)
            elif _is_subsector(sector, source_sector):
                proper.append(powers)
            else:
                nonsub.append(powers)
        return same, proper, nonsub

    only0_same, only0_proper, only0_nonsub = classify(only0)
    only1_same, only1_proper, only1_nonsub = classify(only1)

    out = {
        "sector": source_sector,
        "prime0": int(rows[0]["prime"]),
        "prime1": int(rows[1]["prime"]),
        "support0_count": len(s0),
        "support1_count": len(s1),
        "common_count": len(common),
        "union_count": len(union),
        "only_prime0_count": len(only0),
        "only_prime1_count": len(only1),
        "symmetric_difference_count": len(only0) + len(only1),
        "only_prime0_same_sector_count": len(only0_same),
        "only_prime0_proper_subsector_count": len(only0_proper),
        "only_prime0_non_subsector_count": len(only0_nonsub),
        "only_prime1_same_sector_count": len(only1_same),
        "only_prime1_proper_subsector_count": len(only1_proper),
        "only_prime1_non_subsector_count": len(only1_nonsub),
        "only_prime0_indices": only0,
        "only_prime1_indices": only1,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line closure1850 support-difference audit")
    print(f"sector: {source_sector}")
    print(f"prime {out['prime0']} support: {len(s0)}")
    print(f"prime {out['prime1']} support: {len(s1)}")
    print(f"common support: {len(common)}")
    print(f"union support: {len(union)}")
    print(f"only prime {out['prime0']}: {len(only0)}")
    print(f"  same-sector: {len(only0_same)}")
    print(f"  proper subsector: {len(only0_proper)}")
    print(f"  non-subsector: {len(only0_nonsub)}")
    print(f"only prime {out['prime1']}: {len(only1)}")
    print(f"  same-sector: {len(only1_same)}")
    print(f"  proper subsector: {len(only1_proper)}")
    print(f"  non-subsector: {len(only1_nonsub)}")
    print(f"symmetric difference: {len(only0) + len(only1)}")
    if only0:
        print(f"first only-{out['prime0']}: I{only0[0]}")
    if only1:
        print(f"first only-{out['prime1']}: I{only1[0]}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line closure1850 support-difference audit PASS")


if __name__ == "__main__":
    main()
