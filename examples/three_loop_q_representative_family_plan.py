"""Build and validate the canonical Q01--Q50 representative-family plan."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.q_family_representatives import (
    build_q_representative_families,
    translate_q_physical_powers_to_representative,
)
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_PATH = ROOT / "output" / "3loop_q_representative_family_plan.json"


def _validate_translation(family) -> None:
    representative_member = next(
        member for member in family.member_maps
        if member.diagram_id == family.representative_id
    )
    source_raw = tuple(range(1, 10))
    auxiliary = tuple(-(i + 1) for i in range(family.auxiliary_slot_count))
    expected = translate_q_physical_powers_to_representative(
        family, representative_member, source_raw, auxiliary
    )

    for member in family.member_maps:
        if not member.reflected:
            continue
        partner_raw = [0] * 9
        # member.physical_to_representative is target(member) -> source(rep).
        for member_index, representative_index in member.physical_to_representative:
            partner_raw[member_index - 1] = source_raw[representative_index - 1]
        translated = translate_q_physical_powers_to_representative(
            family, member, partner_raw, auxiliary
        )
        if translated != expected:
            raise ValueError(
                f"{member.diagram_id}->{family.representative_id}: index translation mismatch: "
                f"{translated} != {expected}"
            )


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    families = build_q_representative_families(registry)
    for family in families:
        _validate_translation(family)

    q_count = len([t for t in registry if t.diagram_id.startswith("Q")])
    paired = [family for family in families if len(family.members) == 2]
    singleton = [family for family in families if len(family.members) == 1]
    preprocessed = [family for family in families if family.requires_duplicate_preprocessing]
    rank_hist = Counter(family.physical_rank for family in families)

    report = {
        "schema_version": 1,
        "q_diagram_count": q_count,
        "representative_family_count": len(families),
        "shared_pair_family_count": len(paired),
        "singleton_family_count": len(singleton),
        "duplicate_preprocessing_family_count": len(preprocessed),
        "physical_rank_histogram": {str(rank): count for rank, count in sorted(rank_hist.items())},
        "families": [family.as_dict() for family in families],
        "translation_contract": {
            "input_physical_slots": 9,
            "output_kira_slots": 12,
            "rule": (
                "merge exact duplicate physical propagators, reflect partner physical slots "
                "to the representative, merge representative duplicates, pack independent "
                "physical slots, then append induced auxiliary powers"
            ),
        },
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Q diagrams: {q_count}")
    print(f"canonical representative families: {len(families)}")
    print(f"shared two-diagram families: {len(paired)}")
    print(f"singleton families: {len(singleton)}")
    print(f"families needing duplicate preprocessing: {len(preprocessed)}")
    print("representative physical-rank histogram:")
    for rank, count in sorted(rank_hist.items()):
        print(f"  rank {rank}: {count} families")

    print("\nCanonical Q representative families:")
    for family in families:
        members = ", ".join(family.members)
        mode = "merge" if family.requires_duplicate_preprocessing else "direct"
        print(
            f"  {family.representative_id}: [{members}] "
            f"rank={family.physical_rank} layout={family.physical_slot_count}+{family.auxiliary_slot_count}=12 "
            f"mode={mode}"
        )

    print(f"\nreport: {OUTPUT_PATH}")
    print("Three-loop Q representative-family plan PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
