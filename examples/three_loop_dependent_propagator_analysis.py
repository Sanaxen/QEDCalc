"""Analyze redundant physical propagators in Q reflection families."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.dependent_propagator_analysis import analyze_dependent_physical_propagators
from three_loop.family_sharing import analyze_three_loop_family_sharing
from three_loop.family_sharing_algebraic import verify_q_reflection_family_algebraically
from three_loop.family_sharing_propagator import verify_reflection_physical_propagators
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_PATH = ROOT / "output" / "3loop_dependent_propagator_relations.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    sharing = analyze_three_loop_family_sharing(registry)
    groups = sharing["reflection_candidates"]["multi_member_groups"]
    q_groups = [
        group for group in groups
        if len(group) == 2 and group[0].startswith("Q") and group[1].startswith("Q")
    ]

    analyses: list[dict[str, object]] = []
    failed: list[dict[str, str]] = []
    rank_histogram: Counter[int] = Counter()

    for source_id, target_id in q_groups:
        source = registry.get(source_id)
        target = registry.get(target_id)
        try:
            physical_map = verify_reflection_physical_propagators(source, target)
            family_map = verify_q_reflection_family_algebraically(source, target, physical_map)
            if not family_map.requires_dependent_propagator_preprocessing:
                continue
            source_analysis = analyze_dependent_physical_propagators(source)
            target_analysis = analyze_dependent_physical_propagators(target)
            if source_analysis.physical_rank != target_analysis.physical_rank:
                raise ValueError("source/target dependent-propagator ranks differ")
            rank_histogram[source_analysis.physical_rank] += 1
            analyses.append({
                "source_id": source_id,
                "target_id": target_id,
                "physical_index_map": [list(pair) for pair in family_map.physical_index_map],
                "source": source_analysis.as_dict(),
                "target": target_analysis.as_dict(),
            })
        except Exception as exc:
            failed.append({"group": f"{source_id},{target_id}", "reason": str(exc)})

    report = {
        "schema_version": 1,
        "preprocessing_pair_count": len(analyses),
        "failed_pair_count": len(failed),
        "physical_rank_histogram": dict(sorted(rank_histogram.items())),
        "pairs": analyses,
        "failed_pairs": failed,
        "interpretation": (
            "Each listed dependent physical denominator is exactly expressible as a "
            "linear combination of a deterministic independent subset plus a loop-free "
            "invariant shift.  These identities are candidates for partial-fraction or "
            "denominator-elimination preprocessing before Kira; no integral has yet been rewritten."
        ),
        "next_stage": (
            "Implement and validate an integral-level partial-fraction/elimination transform, "
            "then re-canonicalize the resulting terms into reflection-shared Kira families."
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"dependent-propagator preprocessing pairs: {len(analyses)}")
    print(f"failed pairs: {len(failed)}")
    print("physical-rank histogram:")
    for rank, count in sorted(rank_histogram.items()):
        print(f"  rank {rank}: {count} pairs")

    print("\nExact source-family dependent-propagator identities:")
    for item in analyses:
        source = item["source"]
        print(
            f"  {item['source_id']} <-> {item['target_id']}: "
            f"independent={source['independent_indices']} dependent={source['dependent_indices']}"
        )
        for relation in source["relations"]:
            kind = "homogeneous" if relation["homogeneous"] else "affine"
            print(f"    [{kind}] {relation['identity']}")

    if failed:
        print("\nFailures:")
        for item in failed:
            print(f"  {item['group']}: {item['reason']}")

    print(f"\nreport: {OUTPUT_PATH}")
    if failed:
        print("Three-loop dependent-propagator analysis FAIL")
        return 1
    print("Three-loop dependent-propagator analysis PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
