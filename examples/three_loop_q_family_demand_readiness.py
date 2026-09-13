"""Report existing native-demand artifacts against the 28 Q representative families."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.q_family_demand_readiness import audit_q_family_demand_readiness
from three_loop.q_family_representatives import build_q_representative_families
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_DIR = ROOT / "output"
REPORT_PATH = OUTPUT_DIR / "3loop_q_family_demand_readiness.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    families = build_q_representative_families(registry)
    readiness = audit_q_family_demand_readiness(families, OUTPUT_DIR)

    member_status = [item for family in readiness for item in family.member_status]
    existing = [item for item in member_status if item.exists]
    parseable = [item for item in member_status if item.twelve_slot_parse_ok]
    translatable = [item for item in member_status if item.full_translation_ready]
    union_ready = [family for family in readiness if family.union_ready]

    report = {
        "schema_version": 1,
        "representative_family_count": len(families),
        "diagram_count": len(member_status),
        "existing_native_demand_artifact_count": len(existing),
        "parseable_12slot_artifact_count": len(parseable),
        "full_translation_ready_diagram_count": len(translatable),
        "union_ready_family_count": len(union_ready),
        "families": [family.as_dict() for family in readiness],
        "scope_note": (
            "Read-only readiness audit. No projected trace or native integral mapping is regenerated. "
            "Reflection equivalence alone is not treated as proof that a diagram's native ISP convention "
            "matches the representative basis."
        ),
        "next_stage": (
            "Add a generic Q native-family generator that emits explicit auxiliary-basis metadata, then "
            "translate and union already-existing or deliberately generated demand artifacts family by family."
        ),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"representative Q families: {len(families)}")
    print(f"Q diagrams covered: {len(member_status)}")
    print(f"existing native demand artifacts: {len(existing)}")
    print(f"parseable 12-slot artifacts: {len(parseable)}")
    print(f"full translation-ready diagrams: {len(translatable)}")
    print(f"union-ready families: {len(union_ready)}")
    print("\nExisting artifacts:")
    if existing:
        for item in existing:
            count = item.integral_count if item.integral_count is not None else "?"
            print(
                f"  {item.diagram_id}: integrals={count}, "
                f"basis={item.auxiliary_basis_status}, ready={item.full_translation_ready}"
            )
    else:
        print("  none")
    print("\nFamilies not yet union-ready:")
    pending = [family for family in readiness if not family.union_ready]
    for family in pending:
        states = ", ".join(
            f"{item.diagram_id}={'ready' if item.full_translation_ready else 'pending'}"
            for item in family.member_status
        )
        print(f"  {family.representative_id}: {states}")
    print(f"\nreport: {REPORT_PATH}")
    print("Three-loop Q family demand readiness audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
