"""Verify physical-propagator maps for all reflection family candidates."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.family_sharing import analyze_three_loop_family_sharing
from three_loop.family_sharing_propagator import verify_reflection_physical_propagators
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_PATH = ROOT / "output" / "3loop_integral_family_propagator_maps.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    sharing = analyze_three_loop_family_sharing(registry)
    groups = sharing["reflection_candidates"]["multi_member_groups"]

    verified: list[dict[str, object]] = []
    failed: list[dict[str, str]] = []
    for group in groups:
        if len(group) != 2:
            failed.append({"group": ",".join(group), "reason": "only pair groups supported in this stage"})
            continue
        source_id, target_id = group
        try:
            mapping = verify_reflection_physical_propagators(
                registry.get(source_id), registry.get(target_id)
            )
        except Exception as exc:
            failed.append({"group": f"{source_id},{target_id}", "reason": str(exc)})
            continue
        verified.append(mapping.as_dict())

    q_verified = [
        item for item in verified
        if str(item["source_id"]).startswith("Q") and str(item["target_id"]).startswith("Q")
    ]
    vp_verified = [
        item for item in verified
        if str(item["source_id"]).startswith("VP") and str(item["target_id"]).startswith("VP")
    ]

    report = {
        "schema_version": 1,
        "candidate_pair_count": len(groups),
        "physical_propagator_verified_pair_count": len(verified),
        "q_verified_pair_count": len(q_verified),
        "vp_verified_pair_count": len(vp_verified),
        "failed_pair_count": len(failed),
        "verified_pairs": verified,
        "failed_pairs": failed,
        "scope_note": (
            "This stage proves open-electron-chain segment and internal-photon "
            "propagator equivalence under reflection. ISP-basis mapping is not yet "
            "proved; do not reuse Kira reduction tables until the ISP stage passes."
        ),
        "next_stage": (
            "Construct the induced loop/external-momentum transformation and verify "
            "the full denominator plus ISP basis algebraically, starting with Q01<->Q41."
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"reflection candidate pairs: {len(groups)}")
    print(f"physical propagator verified pairs: {len(verified)}")
    print(f"Q verified pairs: {len(q_verified)}")
    print(f"VP verified pairs: {len(vp_verified)}")
    print(f"failed pairs: {len(failed)}")
    print("\nVerified Q pairs and loop-label maps:")
    for item in q_verified:
        mapping = ", ".join(f"{k}->{v}" for k, v in item["loop_label_map"].items())
        print(f"  {item['source_id']} <-> {item['target_id']}: {mapping}")
    if failed:
        print("\nFailures:")
        for item in failed:
            print(f"  {item['group']}: {item['reason']}")
    print(f"\nreport: {OUTPUT_PATH}")
    if failed:
        print("Three-loop integral-family physical-propagator verification FAIL")
        return 1
    print("Three-loop integral-family physical-propagator verification PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
