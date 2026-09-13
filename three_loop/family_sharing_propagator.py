"""Propagator-level verification for structural family-sharing candidates.

This module takes the open-chain reflection candidates found by
``three_loop.family_sharing`` and derives an explicit physical-propagator map.
It verifies the six open-electron-chain segments and the internal photon edges.
The resulting proof is stronger than topology grouping, but ISP-basis mapping
is intentionally left for the next stage before Kira tables are reused.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from three_loop.registry import ThreeLoopTopology


@dataclass(frozen=True)
class ReflectionPropagatorMap:
    source_id: str
    target_id: str
    loop_label_map: tuple[tuple[str, str], ...]
    electron_segment_map: tuple[tuple[int, int], ...]
    external_vertex_map: tuple[int, int]
    photon_edge_map: tuple[tuple[str, str], ...]
    physical_propagators_verified: bool
    isp_mapping_status: str = "pending"

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "loop_label_map": dict(self.loop_label_map),
            "electron_segment_map": [list(pair) for pair in self.electron_segment_map],
            "external_vertex_map": list(self.external_vertex_map),
            "photon_edge_map": [list(pair) for pair in self.photon_edge_map],
            "physical_propagators_verified": self.physical_propagators_verified,
            "isp_mapping_status": self.isp_mapping_status,
        }


def _reflected_interval(a: int, b: int, n: int) -> tuple[int, int]:
    ra = n + 1 - a
    rb = n + 1 - b
    return min(ra, rb), max(ra, rb)


def verify_reflection_physical_propagators(
    source: ThreeLoopTopology,
    target: ThreeLoopTopology,
) -> ReflectionPropagatorMap:
    """Verify an open-chain reflection at the physical-propagator level.

    For an n-vertex open fermion chain, electron propagator segment i lies
    between vertices i and i+1.  Reflection maps segment i -> n-i.  Internal
    photon propagators are matched by reflected endpoint pairs and edge role.
    The external vertex must map as v -> n+1-v.
    """
    if source.family != target.family:
        raise ValueError("registry family differs")
    if source.open_vertices != target.open_vertices:
        raise ValueError("open vertex counts differ")
    if source.closed_fermion_loops != target.closed_fermion_loops:
        raise ValueError("closed fermion loop counts differ")
    if not isinstance(source.external_vertex, int) or not isinstance(target.external_vertex, int):
        raise ValueError("integer external vertices are required")

    n = source.open_vertices
    expected_external = n + 1 - source.external_vertex
    if target.external_vertex != expected_external:
        raise ValueError(
            f"external vertex does not reflect: {source.external_vertex} -> "
            f"{expected_external}, got {target.external_vertex}"
        )

    source_insert = source.metadata.get("insert_on")
    target_insert = target.metadata.get("insert_on")

    target_by_key: dict[tuple[int, int, str], str] = {}
    for edge in target.photon_edges:
        if edge.a is None or edge.b is None:
            raise ValueError(f"{target.diagram_id}: edge {edge.label} lacks endpoints")
        role = "inserted" if target_insert == edge.label else "ordinary"
        key = (min(edge.a, edge.b), max(edge.a, edge.b), role)
        if key in target_by_key:
            raise ValueError(f"{target.diagram_id}: duplicate reflected edge key {key}")
        target_by_key[key] = edge.label

    label_map: list[tuple[str, str]] = []
    edge_map: list[tuple[str, str]] = []
    for edge in source.photon_edges:
        if edge.a is None or edge.b is None:
            raise ValueError(f"{source.diagram_id}: edge {edge.label} lacks endpoints")
        role = "inserted" if source_insert == edge.label else "ordinary"
        a, b = _reflected_interval(edge.a, edge.b, n)
        key = (a, b, role)
        target_label = target_by_key.get(key)
        if target_label is None:
            raise ValueError(
                f"{source.diagram_id}->{target.diagram_id}: no target edge for "
                f"reflected {edge.label} at {(a, b)} role={role}"
            )
        label_map.append((edge.label, target_label))
        edge_map.append((f"photon:{edge.label}", f"photon:{target_label}"))

    if len(label_map) != len(target.photon_edges):
        raise ValueError("photon-edge counts differ")
    if len({dst for _, dst in label_map}) != len(label_map):
        raise ValueError("loop-label map is not one-to-one")

    segment_map = tuple((i, n - i) for i in range(1, n))
    return ReflectionPropagatorMap(
        source_id=source.diagram_id,
        target_id=target.diagram_id,
        loop_label_map=tuple(sorted(label_map)),
        electron_segment_map=segment_map,
        external_vertex_map=(source.external_vertex, target.external_vertex),
        photon_edge_map=tuple(sorted(edge_map)),
        physical_propagators_verified=True,
    )


def verify_candidate_pairs(
    topologies: Iterable[tuple[ThreeLoopTopology, ThreeLoopTopology]],
) -> tuple[ReflectionPropagatorMap, ...]:
    return tuple(
        verify_reflection_physical_propagators(source, target)
        for source, target in topologies
    )
