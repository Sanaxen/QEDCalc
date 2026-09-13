"""Structural integral-family sharing analysis for the 72-diagram registry.

The reusable canonicalizer lives in ``qedcalc.operations.integral_family_sharing``.
This module is only the three-loop registry adapter.  Keeping that boundary lets
other diagram sets reuse the same machinery without Q01/Q## assumptions.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any

from qedcalc.operations.integral_family_sharing import (
    ChainEdge,
    OpenChainFamilyDescriptor,
    group_structural_families,
    multi_member_groups,
)
from three_loop.registry import ThreeLoopRegistry, ThreeLoopTopology


def _stable_metadata_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def topology_to_family_descriptor(
    topology: ThreeLoopTopology,
) -> tuple[OpenChainFamilyDescriptor | None, str | None]:
    """Translate one registry topology to the generic open-chain descriptor.

    Returns ``(None, reason)`` for topologies whose registry representation is
    not rich enough for this canonicalizer.  Such entries are kept as safe
    singletons by the report instead of being grouped speculatively.
    """
    if not isinstance(topology.external_vertex, int):
        return None, "non-integer external_vertex requires a specialized adapter"

    insert_on = topology.metadata.get("insert_on")
    edges: list[ChainEdge] = []
    for edge in topology.photon_edges:
        if edge.a is None or edge.b is None:
            return None, f"edge {edge.label!r} has no open-chain endpoint pair"
        role = "inserted" if insert_on == edge.label else "ordinary"
        edges.append(ChainEdge(edge.a, edge.b, role))

    # The registry family and loop count are physical structure, not arbitrary
    # routing labels.  Unknown metadata is retained conservatively, so it can
    # split groups but cannot accidentally merge unlike diagrams.  insert_on is
    # already represented by the edge role above and is therefore omitted.
    tags: list[tuple[str, str]] = [
        ("registry_family", topology.family),
        ("closed_fermion_loops", str(topology.closed_fermion_loops)),
    ]
    for key, value in sorted(topology.metadata.items()):
        if key == "insert_on":
            continue
        tags.append((f"metadata:{key}", _stable_metadata_value(value)))

    descriptor = OpenChainFamilyDescriptor(
        item_id=topology.diagram_id,
        open_vertices=topology.open_vertices,
        external_vertex=topology.external_vertex,
        edges=tuple(edges),
        tags=tuple(tags),
    )
    descriptor.validate()
    return descriptor, None


def analyze_three_loop_family_sharing(registry: ThreeLoopRegistry) -> dict[str, object]:
    """Analyze all 72 diagrams at the structural-topology level.

    Two grouping levels are emitted:

    * ``orientation_preserving``: conservative structural equivalence.
    * ``reflection_candidates``: additionally allows reversal of the open
      fermion chain.  These groups are promising Kira-family sharing candidates
      but need propagator/external-momentum mapping verification first.
    """
    descriptors: list[OpenChainFamilyDescriptor] = []
    unsupported: list[dict[str, str]] = []
    family_counts: Counter[str] = Counter()

    for topology in registry:
        family_counts[topology.family] += 1
        descriptor, reason = topology_to_family_descriptor(topology)
        if descriptor is None:
            unsupported.append({"diagram_id": topology.diagram_id, "reason": reason or "unsupported"})
        else:
            descriptors.append(descriptor)

    direct_groups = group_structural_families(descriptors, allow_chain_reflection=False)
    reflection_groups = group_structural_families(descriptors, allow_chain_reflection=True)

    # Unsupported entries are deliberately not merged.  This prevents a coarse
    # topology record from being mistaken for a proven reusable IBP family.
    direct_groups_all = list(direct_groups) + [(entry["diagram_id"],) for entry in unsupported]
    reflection_groups_all = list(reflection_groups) + [(entry["diagram_id"],) for entry in unsupported]

    def pack(groups: list[tuple[str, ...]] | tuple[tuple[str, ...], ...]) -> dict[str, object]:
        groups = sorted((tuple(group) for group in groups), key=lambda g: (g[0], len(g), g))
        shared = multi_member_groups(groups)
        return {
            "group_count": len(groups),
            "multi_member_group_count": len(shared),
            "largest_group_size": max((len(group) for group in groups), default=0),
            "groups": [list(group) for group in groups],
            "multi_member_groups": [list(group) for group in shared],
        }

    diagram_ids = [topology.diagram_id for topology in registry]
    q_ids = [diagram_id for diagram_id in diagram_ids if diagram_id.startswith("Q")]
    return {
        "schema_version": 1,
        "scope": "all three-loop registry diagrams",
        "diagram_count": len(diagram_ids),
        "q_diagram_count": len(q_ids),
        "registry_family_counts": dict(sorted(family_counts.items())),
        "supported_by_open_chain_adapter": len(descriptors),
        "unsupported_count": len(unsupported),
        "unsupported": unsupported,
        "orientation_preserving": pack(direct_groups_all),
        "reflection_candidates": pack(reflection_groups_all),
        "interpretation": {
            "orientation_preserving": (
                "structural-equivalence group with fixed open-chain orientation; "
                "propagator-level mapping is still required before Kira table reuse"
            ),
            "reflection_candidates": (
                "candidate group after open-chain reversal; verify p/p' exchange, "
                "denominator mapping, masses and ISP basis before Kira table reuse"
            ),
        },
        "next_stage": (
            "Construct and verify explicit propagator/loop-momentum maps for every "
            "multi-member candidate group; only then promote it to an exact Kira family."
        ),
    }
