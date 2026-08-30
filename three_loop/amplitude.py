"""Ordered structural amplitude generation for three-loop vertex graphs.

The output is deliberately structural rather than a SymPy expression.  Gamma
matrix and propagator order is preserved explicitly, which is the invariant
needed before connecting the registry to QEDCalc's symbolic expression layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from .registry import ThreeLoopTopology


@dataclass(frozen=True)
class Factor:
    kind: str
    value: str


@dataclass(frozen=True)
class OrderedAmplitude:
    diagram_id: str
    sign: int
    open_line: tuple[Factor, ...]
    loop_factors: tuple[Factor, ...]
    photon_factors: tuple[Factor, ...]


def _vertex_label(topology: ThreeLoopTopology, vertex: int) -> str:
    if vertex == topology.external_vertex:
        return "gamma_mu"
    for edge in topology.photon_edges:
        if edge.a == vertex:
            return f"gamma_{edge.label}_L"
        if edge.b == vertex:
            return f"gamma_{edge.label}_R"
        if edge.open_vertex == vertex:
            return f"gamma_{edge.label}"
    return f"gamma_v{vertex}"


def _active_momenta(topology: ThreeLoopTopology, segment: int) -> tuple[str, ...]:
    active: list[str] = []
    for edge in topology.photon_edges:
        interval = edge.interval
        if interval is None:
            continue
        a, b = interval
        if a <= segment < b:
            active.append(edge.label)
    return tuple(active)


def build_ordered_amplitude(topology: ThreeLoopTopology) -> OrderedAmplitude:
    chain: list[Factor] = []
    if topology.family == "external_lbl":
        for vertex in range(1, topology.open_vertices + 1):
            chain.append(Factor("gamma", _vertex_label(topology, vertex)))
            if vertex < topology.open_vertices:
                momentum = "p' - " + " - ".join(
                    e.label for e in topology.photon_edges
                    if e.open_vertex is not None and e.open_vertex <= vertex
                )
                chain.append(Factor("electron_propagator", momentum))
        order = topology.metadata["closed_loop_order"]
        loops = (Factor("closed_lbl_trace", "order=" + ",".join(map(str, order))),)
        photons = tuple(Factor("photon_propagator", e.label) for e in topology.photon_edges)
        return OrderedAmplitude(topology.diagram_id, topology.fermion_loop_sign, tuple(chain), loops, photons)

    for vertex in range(1, topology.open_vertices + 1):
        chain.append(Factor("gamma", _vertex_label(topology, vertex)))
        if vertex < topology.open_vertices:
            active = _active_momenta(topology, vertex)
            side = "p'" if isinstance(topology.external_vertex, int) and vertex < topology.external_vertex else "p"
            mom = side
            if active:
                mom += " - " + " - ".join(active)
            chain.append(Factor("electron_propagator", mom))

    loops: list[Factor] = []
    if topology.family == "vp1_insert":
        loops.append(Factor("vacuum_polarization_1loop", topology.metadata["insert_on"]))
    elif topology.family == "vp2_insert":
        loops.append(Factor("vacuum_polarization_2loop", topology.metadata["vp2_kernel"]))
    elif topology.family == "vp1_double":
        loops.extend([
            Factor("vacuum_polarization_1loop", "first"),
            Factor("vacuum_polarization_1loop", "second"),
        ])

    photons = tuple(Factor("photon_propagator", e.label) for e in topology.photon_edges)
    return OrderedAmplitude(topology.diagram_id, topology.fermion_loop_sign, tuple(chain), tuple(loops), photons)
