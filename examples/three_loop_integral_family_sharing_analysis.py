"""Analyze structural integral-family sharing across all 72 three-loop diagrams."""
from __future__ import annotations

import json
from pathlib import Path

from three_loop.family_sharing import analyze_three_loop_family_sharing
from three_loop.registry import ThreeLoopRegistry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_PATH = ROOT / "output" / "3loop_integral_family_sharing.json"


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    report = analyze_three_loop_family_sharing(registry)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    direct = report["orientation_preserving"]
    reflected = report["reflection_candidates"]
    print(f"three-loop diagrams: {report['diagram_count']}")
    print(f"Q diagrams: {report['q_diagram_count']}")
    print(f"open-chain adapter supported: {report['supported_by_open_chain_adapter']}")
    print(f"specialized adapter required: {report['unsupported_count']}")
    print(
        "orientation-preserving structural groups: "
        f"{direct['group_count']} "
        f"(shared={direct['multi_member_group_count']}, "
        f"largest={direct['largest_group_size']})"
    )
    print(
        "reflection candidate groups: "
        f"{reflected['group_count']} "
        f"(shared={reflected['multi_member_group_count']}, "
        f"largest={reflected['largest_group_size']})"
    )
    print("\nMulti-member reflection candidates:")
    for group in reflected["multi_member_groups"]:
        print("  " + ", ".join(group))
    if report["unsupported"]:
        print("\nEntries requiring a specialized adapter:")
        for entry in report["unsupported"]:
            print(f"  {entry['diagram_id']}: {entry['reason']}")
    print(f"\nreport: {OUTPUT_PATH}")
    print("Three-loop integral-family sharing structural analysis PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
