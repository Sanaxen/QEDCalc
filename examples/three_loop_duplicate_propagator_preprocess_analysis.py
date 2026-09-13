"""Verify exact duplicate-propagator preprocessing for rank-deficient Q families."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.duplicate_propagator_preprocess import build_duplicate_propagator_plan
from three_loop.family_sharing import analyze_three_loop_family_sharing
from three_loop.family_sharing_algebraic import verify_q_reflection_family_algebraically
from three_loop.family_sharing_propagator import verify_reflection_physical_propagators
from three_loop.registry import ThreeLoopRegistry

REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_PATH = ROOT / "output" / "3loop_duplicate_propagator_preprocess.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    sharing = analyze_three_loop_family_sharing(registry)
    q_groups = [
        group
        for group in sharing["reflection_candidates"]["multi_member_groups"]
        if len(group) == 2 and group[0].startswith("Q") and group[1].startswith("Q")
    ]

    verified: list[dict[str, object]] = []
    failed: list[dict[str, str]] = []
    rank_hist = Counter()

    for source_id, target_id in q_groups:
        source = registry.get(source_id)
        target = registry.get(target_id)
        physical_map = verify_reflection_physical_propagators(source, target)
        algebraic = verify_q_reflection_family_algebraically(source, target, physical_map)
        if not algebraic.requires_dependent_propagator_preprocessing:
            continue
        try:
            source_plan = build_duplicate_propagator_plan(source)
            target_plan = build_duplicate_propagator_plan(target)
        except Exception as exc:
            failed.append({"group": f"{source_id},{target_id}", "reason": str(exc)})
            continue
        rank_hist[source_plan.physical_rank] += 1
        verified.append(
            {
                "source_id": source_id,
                "target_id": target_id,
                "source_plan": source_plan.as_dict(),
                "target_plan": target_plan.as_dict(),
                "pair_verified": True,
            }
        )

    report = {
        "schema_version": 1,
        "preprocessing_pair_count": len(verified) + len(failed),
        "exact_duplicate_merge_pair_count": len(verified),
        "failed_pair_count": len(failed),
        "physical_rank_histogram": {str(k): v for k, v in sorted(rank_hist.items())},
        "pairs": verified,
        "failed_pairs": failed,
        "interpretation": (
            "All verified dependencies are exact proportional duplicates. Their integral powers can be "
            "merged exactly before Kira; no partial-fraction expansion is required for these pairs."
        ),
        "next_stage": (
            "Build each representative Kira family from the independent physical denominators plus "
            "12-rank completion ISPs, then translate diagram integral indices into that layout."
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"dependent-propagator preprocessing pairs: {report['preprocessing_pair_count']}")
    print(f"exact duplicate exponent-merge pairs: {report['exact_duplicate_merge_pair_count']}")
    print(f"failed pairs: {report['failed_pair_count']}")
    print("physical-rank histogram:")
    for rank, count in sorted(rank_hist.items()):
        print(f"  rank {rank}: {count} pairs")
    print("\nExact exponent-merge plans:")
    for item in verified:
        source = item["source_plan"]
        target = item["target_plan"]
        print(f"  {item['source_id']} <-> {item['target_id']}:")
        src_rules = ", ".join(
            f"a{rule['keep_index']} += a{rule['dependent_index']}; a{rule['dependent_index']}=0"
            for rule in source["duplicate_rules"]
        )
        tgt_rules = ", ".join(
            f"a{rule['keep_index']} += a{rule['dependent_index']}; a{rule['dependent_index']}=0"
            for rule in target["duplicate_rules"]
        )
        print(f"    source: {src_rules}")
        print(f"    target: {tgt_rules}")
        print(f"    Kira layout after merge: {source['post_merge_physical_count']} physical + {source['extra_isp_slots_needed']} ISP = 12")

    if failed:
        print("\nFailures:")
        for item in failed:
            print(f"  {item['group']}: {item['reason']}")
    print(f"\nreport: {OUTPUT_PATH}")
    if failed:
        print("Three-loop duplicate-propagator preprocessing analysis FAIL")
        return 1
    print("Three-loop duplicate-propagator preprocessing analysis PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
