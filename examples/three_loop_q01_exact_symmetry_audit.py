from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.q01_exact_symmetry import (
    canonicalize_scalar_under_exact_symmetry,
    discover_q01_exact_signed_loop_symmetries,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_scalar_subtopology_factorization.json"
OUTPUT = ROOT / "output" / "3loop_q01_exact_symmetry_audit.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    connected = [
        IntegralIndex(tuple(record["index"]))
        for record in data["records"]
        if record["factorization"] == "connected-3loop"
    ]
    symmetries = discover_q01_exact_signed_loop_symmetries()

    groups = defaultdict(list)
    for index in connected:
        canonical = canonicalize_scalar_under_exact_symmetry(index, symmetries)
        groups[canonical.powers].append(index.powers)

    rows = [
        {"canonical": canonical, "members": tuple(sorted(members))}
        for canonical, members in sorted(groups.items())
    ]
    out = {
        "connected_scalar_count": len(connected),
        "exact_symmetry_count": len(symmetries),
        "independent_orbit_count": len(rows),
        "symmetries": [sym.__dict__ for sym in symmetries],
        "orbits": rows,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 exact signed-loop symmetry audit")
    print(f"connected scalar targets: {len(connected)}")
    print(f"exact signed-loop symmetries: {len(symmetries)}")
    print(f"independent symmetry orbits: {len(rows)}")
    print("accepted symmetries:")
    for sym in symmetries:
        print(
            f"  images={sym.loop_images} signs={sym.loop_signs}"
            f" physical-permutation={sym.physical_permutation}"
        )
    print("connected-scalar orbits:")
    for row in rows:
        print(f"  canonical=I{row['canonical']} members={len(row['members'])}")
        for member in row["members"]:
            print(f"    I{member}")
    print(f"generated: {OUTPUT}")
    print("Q01 exact signed-loop symmetry audit PASS")


if __name__ == "__main__":
    main()
