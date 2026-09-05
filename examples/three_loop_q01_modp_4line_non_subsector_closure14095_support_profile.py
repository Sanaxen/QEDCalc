from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex

from examples.three_loop_q01_modp_4line_non_subsector_closure5994_support_profile import (
    complexity,
    histogram,
)
from examples.three_loop_q01_modp_4line_non_subsector_closure_layer7_free15_neighbor_rank import (
    _load_inputs,
)

ROOT = Path(__file__).resolve().parents[1]
REFRESHED_SUPPORT_SOURCE = (
    ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure14095_same_sector_support.json"
)
OLD_SUPPORT_SOURCE = (
    ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure5994_same_sector_support.json"
)
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_non_subsector_closure14095_support_profile.json"


def _stable_support(path: Path, label: str) -> tuple[dict, tuple[IntegralIndex, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("stable_support_across_primes", False):
        raise RuntimeError(f"{label} support is not stable across primes")
    rows = data.get("rows", [])
    if not rows:
        raise RuntimeError(f"{label} support output has no rows")
    support = tuple(IntegralIndex(tuple(p)) for p in rows[0]["same_sector_support_indices"])
    return data, support


def _layer_plan(indices: tuple[IntegralIndex, ...]) -> list[dict[str, int]]:
    layers = Counter(complexity(index)["total_complexity"] for index in indices)
    cumulative = 0
    plan: list[dict[str, int]] = []
    for degree in sorted(layers, reverse=True):
        count = layers[degree]
        cumulative += count
        plan.append(
            {
                "total_complexity": degree,
                "count": count,
                "cumulative_from_hardest": cumulative,
            }
        )
    return plan


def main() -> None:
    refreshed_data, refreshed_support = _stable_support(
        REFRESHED_SUPPORT_SOURCE, "refreshed14095"
    )
    old_data, old_support = _stable_support(OLD_SUPPORT_SOURCE, "old5994")

    source_sector, target14095, *_ = _load_inputs()
    block = tuple(target14095)
    block_set = set(block)
    refreshed_set = set(refreshed_support)
    old_set = set(old_support)

    if tuple(refreshed_data["sector"]) != tuple(source_sector):
        raise RuntimeError("refreshed support sector differs from current source sector")
    if tuple(old_data["sector"]) != tuple(source_sector):
        raise RuntimeError("old support sector differs from current source sector")
    if len(block) != 14095:
        raise RuntimeError(f"expected 14095 current block integrals, got {len(block)}")
    if len(refreshed_support) != 29264:
        raise RuntimeError(
            f"expected 29264 refreshed same-sector support integrals, got {len(refreshed_support)}"
        )
    if len(old_support) != 11454:
        raise RuntimeError(f"expected 11454 old support integrals, got {len(old_support)}")

    outside_current = tuple(
        sorted((index for index in refreshed_support if index not in block_set), key=lambda x: x.powers)
    )
    outside_set = set(outside_current)
    retained_from_old = tuple(sorted(outside_set & old_set, key=lambda x: x.powers))
    newly_exposed = tuple(sorted(outside_set - old_set, key=lambda x: x.powers))
    old_now_absorbed = tuple(sorted(old_set & block_set, key=lambda x: x.powers))
    old_not_in_refreshed_outside = tuple(sorted((old_set - block_set) - outside_set, key=lambda x: x.powers))

    layer_plan = _layer_plan(outside_current)
    newly_exposed_plan = _layer_plan(newly_exposed)

    out = {
        "sector": list(source_sector),
        "current_block_count": len(block),
        "refreshed_same_sector_support_count": len(refreshed_support),
        "current_outside_support_count": len(outside_current),
        "current_union_count": len(block_set | refreshed_set),
        "old_same_sector_support_count": len(old_support),
        "retained_old_outside_support_count": len(retained_from_old),
        "newly_exposed_outside_support_count": len(newly_exposed),
        "old_support_absorbed_into_current_block_count": len(old_now_absorbed),
        "old_outside_not_in_refreshed_support_count": len(old_not_in_refreshed_outside),
        "current_block_histogram": histogram(block),
        "current_outside_support_histogram": histogram(outside_current),
        "newly_exposed_support_histogram": histogram(newly_exposed),
        "descending_complexity_layers": layer_plan,
        "newly_exposed_descending_complexity_layers": newly_exposed_plan,
        "newly_exposed_indices": [index.powers for index in newly_exposed],
        "recommendation": (
            "Use the refreshed 14095-block outside support, not the old 5994 frontier, "
            "to choose the next closure layer. Process the highest remaining complexity first; "
            "after another material block/seed expansion, refresh same-sector support again."
        ),
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 refreshed 14095 same-sector support profile")
    print(f"sector: {tuple(source_sector)}")
    print(f"current block: {len(block)}")
    print(f"refreshed same-sector support: {len(refreshed_support)}")
    print(f"outside current block: {len(outside_current)}")
    print(f"full current union: {len(block_set | refreshed_set)}")
    print(f"old support: {len(old_support)}")
    print(f"retained old outside support: {len(retained_from_old)}")
    print(f"newly exposed outside support: {len(newly_exposed)}")
    print(f"old support absorbed into current block: {len(old_now_absorbed)}")
    print(f"old outside no longer in refreshed support: {len(old_not_in_refreshed_outside)}")
    print("descending total-complexity layers for current outside support:")
    for layer in layer_plan:
        print(
            f"  complexity {layer['total_complexity']}: {layer['count']} "
            f"(cumulative {layer['cumulative_from_hardest']})"
        )
    print("newly exposed support by complexity:")
    for layer in newly_exposed_plan:
        print(
            f"  complexity {layer['total_complexity']}: {layer['count']} "
            f"(cumulative {layer['cumulative_from_hardest']})"
        )
    print(f"generated: {OUTPUT}")
    print("Q01 refreshed 14095 same-sector support profile PASS")


if __name__ == "__main__":
    main()
