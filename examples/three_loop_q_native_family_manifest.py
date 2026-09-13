"""Generate the explicit native-family basis manifest for Q01--Q50."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.q_family_representatives import build_q_representative_families
from three_loop.q_native_family_manifest import build_q_native_family_manifest
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_PATH = ROOT / "output" / "3loop_q_native_family_manifest.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    families = build_q_representative_families(registry)
    manifests = build_q_native_family_manifest(registry, families)

    mode_hist = Counter(item.auxiliary_basis_mode for item in manifests)
    rank_hist = Counter(item.physical_rank for item in manifests)
    report = {
        "schema_version": 1,
        "diagram_count": len(manifests),
        "representative_family_count": len(families),
        "all_kira_layouts_are_12_slots": all(item.kira_slot_count == 12 for item in manifests),
        "auxiliary_basis_mode_histogram": dict(sorted(mode_hist.items())),
        "physical_rank_histogram": {str(k): v for k, v in sorted(rank_hist.items())},
        "members": [item.as_dict() for item in manifests],
        "contract": (
            "Future per-diagram native integral-index artifacts must use this exact physical packing and "
            "auxiliary-basis order and record the matching basis_fingerprint in a sidecar."
        ),
        "scope_note": (
            "Metadata-only stage. No projected trace, native integral mapping, or Kira reduction is run."
        ),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Q member manifests: {len(manifests)}")
    print(f"representative Q families: {len(families)}")
    print("auxiliary basis modes:")
    for key, value in sorted(mode_hist.items()):
        print(f"  {key}: {value}")
    print("member physical-rank histogram:")
    for rank, count in sorted(rank_hist.items()):
        print(f"  rank {rank}: {count}")

    print("\nBasis contract samples:")
    sample_ids = {"Q01", "Q02", "Q21", "Q41", "Q50"}
    for item in manifests:
        if item.diagram_id not in sample_ids:
            continue
        basis = ", ".join(item.auxiliary_basis)
        print(
            f"  {item.diagram_id} -> {item.representative_id}: "
            f"mode={item.auxiliary_basis_mode}, rank={item.physical_rank}, "
            f"basis=[{basis}], fingerprint={item.basis_fingerprint[:16]}..."
        )

    print(f"\nreport: {OUTPUT_PATH}")
    print("Three-loop Q native-family manifest PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
