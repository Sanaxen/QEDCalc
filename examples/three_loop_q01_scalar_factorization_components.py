from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.scalar_subtopology_factorization import (
    classify_scalar_subtopologies,
    denominator_loop_support,
    loop_components_for_index,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_scalar_subtopology_factorization.json"
OUTPUT = ROOT / "output" / "3loop_q01_scalar_factorization_components.json"


def main() -> None:
    family = q01_integral_family()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    factorized = [
        IntegralIndex(tuple(record["index"]))
        for record in data["records"]
        if record["factorization"] == "factorized-2+1"
    ]

    rows = []
    for index in factorized:
        components = loop_components_for_index(family, index)
        component_rows = []
        for component in components:
            denominator_slots = []
            for i, power in enumerate(index.powers[:9]):
                if power <= 0:
                    continue
                support = set(denominator_loop_support(family, i))
                if support and support.issubset(set(component)):
                    denominator_slots.append(i + 1)
            component_rows.append({
                "loops": component,
                "denominators": tuple(denominator_slots),
            })
        rows.append({
            "index": index.powers,
            "components": component_rows,
        })

    OUTPUT.write_text(json.dumps({"factorized_count": len(rows), "records": rows}, indent=2), encoding="utf-8")
    print("QEDCalc Q01 explicit factorized component audit")
    print(f"factorized scalar subtopologies: {len(rows)}")
    for row in rows:
        print("  I(" + ", ".join(map(str, row["index"])) + ")")
        for component in row["components"]:
            print(f"    loops={tuple(component['loops'])} denominators={tuple(component['denominators'])}")
    print(f"generated: {OUTPUT}")
    print("Q01 explicit factorized component audit PASS")


if __name__ == "__main__":
    main()
