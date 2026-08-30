"""Candidate divergent-subgraph discovery for three-loop vertex topologies.

This is a planning/audit layer. It discovers candidate UV subgraphs from
explicit topology and QED power counting. It does not yet apply finite
on-shell counterterms or claim that every power-counting candidate survives
Ward identities.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from .registry import ThreeLoopTopology


@dataclass(frozen=True)
class DivergentSubgraph:
    kind: str
    vertices: tuple[int, ...]
    photon_labels: tuple[str, ...]
    external_photon_legs: int
    superficial_degree: int
    source: str


def _qed_degree(external_electron_legs: int, external_photon_legs: int) -> int:
    # QED in D=4: omega = 4 - 3/2 E_f - E_b.
    return 4 - (3 * external_electron_legs) // 2 - external_photon_legs


def discover_candidate_subgraphs(topology: ThreeLoopTopology) -> tuple[DivergentSubgraph, ...]:
    found: list[DivergentSubgraph] = []

    if topology.family == "vp1_insert":
        found.append(DivergentSubgraph("vacuum_polarization", (), (topology.metadata["insert_on"],), 2, 2, "declared-vp1"))
    elif topology.family == "vp2_insert":
        found.append(DivergentSubgraph("vacuum_polarization", (), ("k",), 2, 2, "declared-vp2"))
    elif topology.family == "vp1_double":
        found.extend([
            DivergentSubgraph("vacuum_polarization", (), ("k",), 2, 2, "declared-vp1-first"),
            DivergentSubgraph("vacuum_polarization", (), ("k",), 2, 2, "declared-vp1-second"),
        ])
    elif topology.family == "external_lbl":
        found.append(DivergentSubgraph(
            "light_by_light_audit", (), tuple(e.label for e in topology.photon_edges),
            4, 0, "declared-lbl"
        ))

    interval_edges = [e for e in topology.photon_edges if e.interval is not None]
    vertices = range(1, topology.open_vertices + 1)

    for a, b in combinations(vertices, 2):
        if a == 1 and b == topology.open_vertices:
            continue

        inside = lambda x: a <= x <= b
        internal = [
            e for e in interval_edges
            if e.a is not None and e.b is not None and inside(e.a) and inside(e.b)
        ]
        if not internal:
            continue

        crossing = [
            e for e in interval_edges
            if e.a is not None and e.b is not None and (inside(e.a) ^ inside(e.b))
        ]
        external_photons = len(crossing)
        if isinstance(topology.external_vertex, int) and inside(topology.external_vertex):
            external_photons += 1

        omega = _qed_degree(2, external_photons)
        if omega < 0:
            continue
        if external_photons == 0:
            kind = "self_energy"
        elif external_photons == 1:
            kind = "vertex"
        else:
            kind = "electron_multiphoto"

        found.append(
            DivergentSubgraph(
                kind=kind,
                vertices=tuple(range(a, b + 1)),
                photon_labels=tuple(e.label for e in internal),
                external_photon_legs=external_photons,
                superficial_degree=omega,
                source="open-line-interval",
            )
        )

    unique = {}
    for sg in found:
        key = (sg.kind, sg.vertices, sg.photon_labels, sg.source)
        unique[key] = sg
    return tuple(unique.values())
