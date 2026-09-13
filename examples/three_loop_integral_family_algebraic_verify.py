"""Algebraically verify full 12-denominator sharing for Q reflection pairs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.family_sharing import analyze_three_loop_family_sharing
from three_loop.family_sharing_algebraic import verify_q_reflection_family_algebraically
from three_loop.family_sharing_propagator import verify_reflection_physical_propagators
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_PATH = ROOT / "output" / "3loop_integral_family_algebraic_maps.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    sharing = analyze_three_loop_family_sharing(registry)
    groups = sharing["reflection_candidates"]["multi_member_groups"]
    q_groups = [
        group for group in groups
        if len(group) == 2 and group[0].startswith("Q") and group[1].startswith("Q")
    ]

    verified: list[dict[str, object]] = []
    failed: list[dict[str, str]] = []
    for source_id, target_id in q_groups:
        source = registry.get(source_id)
        target = registry.get(target_id)
        try:
            physical_map = verify_reflection_physical_propagators(source, target)
            algebraic_map = verify_q_reflection_family_algebraically(
                source, target, physical_map
            )
        except Exception as exc:
            failed.append({"group": f"{source_id},{target_id}", "reason": str(exc)})
            continue
        verified.append(algebraic_map.as_dict())

    q_total = len([topology for topology in registry if topology.diagram_id.startswith("Q")])
    exact_family_count = q_total - len(verified)
    q01 = next((item for item in verified if item["source_id"] == "Q01"), None)

    report = {
        "schema_version": 1,
        "q_diagram_count": q_total,
        "q_reflection_candidate_pair_count": len(q_groups),
        "q_full_family_verified_pair_count": len(verified),
        "failed_pair_count": len(failed),
        "q_exact_family_count_after_verified_reflection_sharing": exact_family_count,
        "verified_pairs": verified,
        "failed_pairs": failed,
        "reuse_rule": (
            "Each verified pair shares one 12-dimensional IBP family after the "
            "recorded loop/external momentum reflection.  The target ISP basis is "
            "induced from the representative basis rather than chosen independently."
        ),
        "q01_note": (
            "Q01 keeps its existing (k.r, l.q, q.r) auxiliary basis so completed "
            "and in-progress Q01 Kira work remains the canonical representative for Q41."
        ),
        "next_stage": (
            "Build integral-index translation into each representative family and "
            "deduplicate/union the demanded integrals before generating Kira jobs."
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Q reflection candidate pairs: {len(q_groups)}")
    print(f"full 12-denominator family verified pairs: {len(verified)}")
    print(f"failed pairs: {len(failed)}")
    print(f"Q diagrams: {q_total}")
    print(f"exact Q families after verified sharing: {exact_family_count}")
    if q01 is not None:
        print("\nQ01 <-> Q41 canonical-family proof:")
        print(f"  source rank: {q01['source_family_rank']}")
        print(f"  target rank: {q01['target_family_rank']}")
        print(f"  legacy Q01 ISP basis preserved: {q01['q01_legacy_basis_preserved']}")
        print("  induced Q41 ISPs:")
        for expr in q01["induced_target_isps"]:
            print(f"    {expr}")
    if failed:
        print("\nFailures:")
        for item in failed:
            print(f"  {item['group']}: {item['reason']}")
    print(f"\nreport: {OUTPUT_PATH}")
    if failed:
        print("Three-loop Q integral-family algebraic verification FAIL")
        return 1
    print("Three-loop Q integral-family algebraic verification PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
