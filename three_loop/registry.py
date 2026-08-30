"""Three-loop QED vertex topology registry.

This module is intentionally dependency-free.  It provides a stable data model
for the 72 sixth-order electron-vertex diagrams so the symbolic backend can be
connected later without making graph-specific code the primary representation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping
import json
from pathlib import Path


@dataclass(frozen=True)
class PhotonEdge:
    label: str
    a: int | None = None
    b: int | None = None
    open_vertex: int | None = None

    @property
    def interval(self) -> tuple[int, int] | None:
        if self.a is None or self.b is None:
            return None
        return (min(self.a, self.b), max(self.a, self.b))


@dataclass(frozen=True)
class ThreeLoopTopology:
    diagram_id: str
    family: str
    external_vertex: int | str
    open_vertices: int
    photon_edges: tuple[PhotonEdge, ...]
    closed_fermion_loops: int
    metadata: Mapping[str, Any]

    @property
    def fermion_loop_sign(self) -> int:
        return -1 if self.closed_fermion_loops % 2 else 1

    def validate(self) -> None:
        if self.open_vertices < 1:
            raise ValueError(f"{self.diagram_id}: open_vertices must be positive")
        if isinstance(self.external_vertex, int):
            if not 1 <= self.external_vertex <= self.open_vertices:
                raise ValueError(f"{self.diagram_id}: invalid external vertex")
        labels = [e.label for e in self.photon_edges]
        if len(labels) != len(set(labels)):
            raise ValueError(f"{self.diagram_id}: duplicate photon labels")
        for edge in self.photon_edges:
            if edge.interval is not None:
                a, b = edge.interval
                if not (1 <= a < b <= self.open_vertices):
                    raise ValueError(f"{self.diagram_id}: invalid edge {edge.label}")


class ThreeLoopRegistry:
    def __init__(self, topologies: Iterable[ThreeLoopTopology]):
        self._items = {t.diagram_id: t for t in topologies}
        if len(self._items) != 72:
            raise ValueError(f"expected 72 diagrams, got {len(self._items)}")
        for topology in self._items.values():
            topology.validate()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items.values())

    def get(self, diagram_id: str) -> ThreeLoopTopology:
        return self._items[diagram_id]

    def by_family(self, family: str) -> tuple[ThreeLoopTopology, ...]:
        return tuple(t for t in self._items.values() if t.family == family)

    @classmethod
    def from_json(cls, path: str | Path) -> "ThreeLoopRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        items = []
        for raw in payload["diagrams"]:
            edges = tuple(PhotonEdge(**e) for e in raw.get("photon_edges", []))
            known = {
                "id", "family", "external_vertex", "open_vertices",
                "photon_edges", "closed_fermion_loops"
            }
            metadata = {k: v for k, v in raw.items() if k not in known}
            items.append(
                ThreeLoopTopology(
                    diagram_id=raw["id"],
                    family=raw["family"],
                    external_vertex=raw["external_vertex"],
                    open_vertices=raw["open_vertices"],
                    photon_edges=edges,
                    closed_fermion_loops=raw["closed_fermion_loops"],
                    metadata=metadata,
                )
            )
        return cls(items)
