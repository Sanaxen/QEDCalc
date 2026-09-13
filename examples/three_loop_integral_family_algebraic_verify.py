"""Algebraically verify Q reflection sharing and classify Kira readiness."""
from __future__ import annotations

import json
import sys
from collections import Counter
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

    direct_ready = [item for item in verified if item["direct_12_denominator_kira_ready"]]
    preprocess = [item for item in verified if item["requires_dependent_propagator_preprocessing"]]
    rank_hist = Counter(int(item["source_physical_rank"]) for item in verified)

    q_total = len([topology for topology in registry if topology.diagram_id.startswith("Q")])
    reflection_family_count = q_total - len(verified)
    direct_kira_family_count = q_total - len(direct_ready)
    q01 = next((item for item in verified if item["source_id"] == "Q01"), None)

    report = {
        "schema_version": 2,
        "q_diagram_count": q_total,
        "q_reflection_candidate_pair_count": len(q_groups),
        "q_algebraically_reflection_equivalent_pair_count": len(verified),
        "q_direct_12_denominator_kira_ready_pair_count": len(direct_ready),
        "q_dependent_propagator_preprocessing_pair_count": len(preprocess),
        "failed_pair_count": len(failed),
        "q_reflection_family_count": reflection_family_count,
        "q_direct_kira_family_count_without_preprocessing": direct_kira_family_count,
        "physical_rank_histogram": dict(sorted(rank_hist.items())),
        "verified_pairs": verified,
        "failed_pairs": failed,
        "interpretation": (
            "All algebraically verified pairs have exactly mapped physical propagators. "
            "Pairs with physical rank 9 are directly representable as nine physical "
            "denominators plus three ISPs. Lower-rank pairs remain reflection-equivalent "
            "but need dependent-propagator preprocessing before conventional Kira-family reuse."
        ),
        "next_stage": (
            "For lower-rank pairs, derive the linear dependence relations among physical "
            "propagators and build a safe partial-fraction/decomposition plan. In parallel, "
            "directly Kira-ready pairs can proceed to integral-index translation and demand union."
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Q reflection candidate pairs: {len(q_groups)}")
    print(f"algebraically reflection-equivalent pairs: {len(verified)}")
    print(f"direct 12-denominator Kira-ready pairs: {len(direct_ready)}")
    print(f"dependent-propagator preprocessing pairs: {len(preprocess)}")
    print(f"failed pairs: {len(failed)}")
    print(f"Q diagrams: {q_total}")
    print(f"reflection families after verified sharing: {reflection_family_count}")
    print(f"direct Kira families without preprocessing: {direct_kira_family_count}")
    print("physical-rank histogram:")
    for rank, count in sorted(rank_hist.items()):
        print(f"  rank {rank}: {count} pairs")

    if q01 is not None:
        print("\nQ01 <-> Q41 canonical-family proof:")
        print(f"  physical rank: {q01['source_physical_rank']}")
        print(f"  completed rank: {q01['source_completed_rank']}")
        print(f"  auxiliary count needed: {q01['auxiliary_count_needed']}")
        print(f"  legacy Q01 ISP basis preserved: {q01['q01_legacy_basis_preserved']}")
        print("  induced Q41 ISPs:")
        for expr in q01["induced_target_isps"]:
            print(f"    {expr}")

    if preprocess:
        print("\nPairs needing dependent-propagator preprocessing:")
        for item in preprocess:
            print(
                f"  {item['source_id']} <-> {item['target_id']}: "
                f"physical rank={item['source_physical_rank']}, "
                f"auxiliaries needed={item['auxiliary_count_needed']}"
            )
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
