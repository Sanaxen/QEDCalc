"""Inventory existing Q projected-scalar and native-demand artifacts."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.q_family_representatives import build_q_representative_families
from three_loop.q_native_demand_source_inventory import inventory_q_native_demand_sources
from three_loop.q_native_family_manifest import build_q_native_family_manifest
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_DIR = ROOT / "output"
REPORT_PATH = OUTPUT_DIR / "3loop_q_native_demand_source_inventory.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    families = build_q_representative_families(registry)
    manifests = build_q_native_family_manifest(registry, families)
    statuses = inventory_q_native_demand_sources(manifests, OUTPUT_DIR)

    projected = [x for x in statuses if x.projected_scalar_exists]
    indices = [x for x in statuses if x.integral_indices_exists]
    fingerprinted = [x for x in statuses if x.sidecar_fingerprint_matches]
    proven = [x for x in statuses if x.integral_indices_exists and x.basis_proven]
    candidates = [x for x in statuses if x.new_mapping_candidate]

    family_members = defaultdict(list)
    for item in statuses:
        family_members[item.representative_id].append(item)
    source_complete_families = [
        rep for rep, members in family_members.items()
        if all(m.projected_scalar_exists for m in members)
    ]
    demand_complete_families = [
        rep for rep, members in family_members.items()
        if all(m.integral_indices_exists and m.basis_proven for m in members)
    ]

    report = {
        "schema_version": 1,
        "diagram_count": len(statuses),
        "representative_family_count": len(families),
        "projected_scalar_artifact_count": len(projected),
        "integral_indices_artifact_count": len(indices),
        "matching_fingerprint_sidecar_count": len(fingerprinted),
        "basis_proven_integral_indices_count": len(proven),
        "new_mapping_candidate_count": len(candidates),
        "source_complete_family_count": len(source_complete_families),
        "demand_complete_family_count": len(demand_complete_families),
        "source_complete_families": sorted(source_complete_families),
        "demand_complete_families": sorted(demand_complete_families),
        "members": [item.as_dict() for item in statuses],
        "scope_note": (
            "Read-only file inventory. Projected scalar contents are not parsed and no native mapping, "
            "trace, FORM, Kira, Fermat, or FireFly job is run."
        ),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Q diagrams inventoried: {len(statuses)}")
    print(f"representative Q families: {len(families)}")
    print(f"projected scalar artifacts: {len(projected)}")
    print(f"integral-index artifacts: {len(indices)}")
    print(f"matching basis sidecars: {len(fingerprinted)}")
    print(f"basis-proven integral-index artifacts: {len(proven)}")
    print(f"new mapping candidates with existing projected scalar: {len(candidates)}")
    print(f"families with projected sources for all members: {len(source_complete_families)}")
    print(f"families with basis-proven demands for all members: {len(demand_complete_families)}")

    print("\nExisting projected scalar sources:")
    if projected:
        for item in projected:
            size = item.projected_scalar_size_bytes or 0
            print(f"  {item.diagram_id}: {size:,} bytes")
    else:
        print("  none")

    print("\nExisting integral-index artifacts:")
    if indices:
        for item in indices:
            print(
                f"  {item.diagram_id}: basis_proven={item.basis_proven}, "
                f"proof={item.basis_proof}"
            )
    else:
        print("  none")

    print("\nNew mapping candidates:")
    if candidates:
        for item in candidates:
            print(f"  {item.diagram_id} -> representative {item.representative_id}")
    else:
        print("  none")

    print(f"\nreport: {REPORT_PATH}")
    print("Three-loop Q native-demand source inventory PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
