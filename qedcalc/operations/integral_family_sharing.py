"""Reusable structural integral-family sharing helpers.

This module deliberately has no dependency on QEDCalc's three-loop diagram IDs.
It canonicalizes open-chain chord topologies while preserving structural tags.
The result is a *structural* family classification: it is suitable for finding
IBP/Kira family-sharing candidates, but propagator-level momentum mappings must
still be verified before reductions are reused.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True, order=True)
class ChainEdge:
    """An unlabeled chord on an ordered open chain.

    ``role`` distinguishes physically different edges (for example a photon
    line carrying a vacuum-polarization insertion).  Arbitrary momentum labels
    such as k/l/r should not be encoded in ``role``.
    """

    a: int
    b: int
    role: str = "ordinary"

    def normalized(self) -> "ChainEdge":
        return ChainEdge(min(self.a, self.b), max(self.a, self.b), self.role)


@dataclass(frozen=True)
class OpenChainFamilyDescriptor:
    """Diagram-independent descriptor used by the canonicalizer."""

    item_id: str
    open_vertices: int
    external_vertex: int
    edges: tuple[ChainEdge, ...]
    tags: tuple[tuple[str, str], ...] = ()

    def validate(self) -> None:
        if self.open_vertices < 1:
            raise ValueError(f"{self.item_id}: open_vertices must be positive")
        if not 1 <= self.external_vertex <= self.open_vertices:
            raise ValueError(f"{self.item_id}: external vertex is outside the chain")
        for edge in self.edges:
            edge = edge.normalized()
            if not (1 <= edge.a < edge.b <= self.open_vertices):
                raise ValueError(f"{self.item_id}: invalid edge {edge}")


def _orientation_signature(
    descriptor: OpenChainFamilyDescriptor,
    *,
    reflected: bool,
) -> tuple[object, ...]:
    descriptor.validate()
    n = descriptor.open_vertices

    def vertex(v: int) -> int:
        return n + 1 - v if reflected else v

    external = vertex(descriptor.external_vertex)
    edges = []
    for edge in descriptor.edges:
        a = vertex(edge.a)
        b = vertex(edge.b)
        edges.append((min(a, b), max(a, b), edge.role))
    return (
        n,
        external,
        tuple(sorted(edges)),
        tuple(sorted(descriptor.tags)),
    )


def structural_family_signature(
    descriptor: OpenChainFamilyDescriptor,
    *,
    allow_chain_reflection: bool = False,
) -> tuple[object, ...]:
    """Return a deterministic topology signature.

    Photon/momentum labels are absent by construction.  With
    ``allow_chain_reflection=False`` the external-fermion orientation is kept.
    With reflection enabled, the lexicographically smaller of the two chain
    orientations is used.  The latter is intentionally a *candidate* sharing
    relation until the corresponding external-momentum/propagator map has been
    verified.
    """
    direct = _orientation_signature(descriptor, reflected=False)
    if not allow_chain_reflection:
        return direct
    reflected = _orientation_signature(descriptor, reflected=True)
    return min(direct, reflected)


def group_structural_families(
    descriptors: Iterable[OpenChainFamilyDescriptor],
    *,
    allow_chain_reflection: bool = False,
) -> tuple[tuple[str, ...], ...]:
    """Group item IDs by structural family signature."""
    groups: dict[tuple[object, ...], list[str]] = {}
    for descriptor in descriptors:
        signature = structural_family_signature(
            descriptor,
            allow_chain_reflection=allow_chain_reflection,
        )
        groups.setdefault(signature, []).append(descriptor.item_id)
    ordered = [tuple(sorted(ids)) for ids in groups.values()]
    return tuple(sorted(ordered, key=lambda ids: (ids[0], len(ids), ids)))


def multi_member_groups(groups: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
    """Return only groups that can actually share work."""
    return tuple(tuple(group) for group in groups if len(group) > 1)
