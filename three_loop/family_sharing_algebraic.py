"""Algebraic denominator/ISP verification for three-loop Q-family sharing.

This stage upgrades open-chain reflection candidates by checking the physical
propagators algebraically and then analysing the rank of the scalar-product
span.  A nine-propagator graph with physical rank nine needs three auxiliary
ISPs to form the usual 12-dimensional IBP family.  Some topologies have a
lower physical rank; those are still reflection-equivalent, but they require
preprocessing (for example a dependent-propagator/partial-fraction treatment)
before they can be represented by a standard 12-denominator Kira family.

For Q01 the existing QEDCalc ISP basis (k.r, l.q, q.r) is kept exactly so the
current Q01 Kira work remains the canonical representative.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import sympy as sp

from qedcalc.operations.ibp import sp_atom
from three_loop.family_sharing_propagator import ReflectionPropagatorMap
from three_loop.registry import ThreeLoopTopology


VECTOR_NAMES = ("p", "q", "k", "l", "r")
LOOP_NAMES = ("k", "l", "r")
SP_PAIRS = (
    ("k", "k"), ("l", "l"), ("r", "r"),
    ("k", "l"), ("k", "r"), ("l", "r"),
    ("k", "p"), ("l", "p"), ("p", "r"),
    ("k", "q"), ("l", "q"), ("q", "r"),
)
SP_ATOMS = tuple(sp_atom(a, b) for a, b in SP_PAIRS)
Q01_ISP_PAIRS = (("k", "r"), ("l", "q"), ("q", "r"))


def _zero_vector() -> dict[str, int]:
    return {name: 0 for name in VECTOR_NAMES}


def _basis_vector(name: str) -> dict[str, int]:
    out = _zero_vector()
    out[name] = 1
    return out


def _add_scaled(dst: dict[str, int], src: Mapping[str, int], scale: int) -> None:
    for name, value in src.items():
        dst[name] += scale * value


def _dot(a: Mapping[str, int], b: Mapping[str, int]) -> sp.Expr:
    """Bilinear scalar product in the (p,q,k,l,r) basis."""
    m = sp.Symbol("m")
    z = sp.Symbol("z")
    result = sp.Integer(0)
    for i, left in enumerate(VECTOR_NAMES):
        for right in VECTOR_NAMES[i:]:
            coefficient = a[left] * b[right]
            if right != left:
                coefficient += a[right] * b[left]
            if not coefficient:
                continue
            pair = {left, right}
            if left == right == "p":
                atom = m**2
            elif left == right == "q":
                atom = z * m**2
            elif pair == {"p", "q"}:
                atom = -z * m**2 / 2
            else:
                atom = sp_atom(left, right)
            result += coefficient * atom
    return sp.expand(result)


def _square(vector: Mapping[str, int]) -> sp.Expr:
    return _dot(vector, vector)


def q_physical_denominators(topology: ThreeLoopTopology) -> tuple[sp.Expr, ...]:
    """Construct six electron and three photon denominators for a quenched Q graph."""
    if topology.family != "quenched":
        raise ValueError(f"{topology.diagram_id}: expected quenched topology")
    if topology.open_vertices != 7 or not isinstance(topology.external_vertex, int):
        raise ValueError(f"{topology.diagram_id}: expected seven-vertex open chain")

    events: dict[int, list[tuple[str, int]]] = {i: [] for i in range(1, 8)}
    for edge in topology.photon_edges:
        if edge.label not in LOOP_NAMES or edge.a is None or edge.b is None:
            raise ValueError(f"{topology.diagram_id}: unsupported photon edge {edge}")
        a, b = min(edge.a, edge.b), max(edge.a, edge.b)
        events[a].append((edge.label, -1))
        events[b].append((edge.label, +1))

    current = _zero_vector()
    current["p"] = 1
    current["q"] = 1
    electron: list[sp.Expr] = []
    m = sp.Symbol("m")
    for vertex in range(1, 7):
        if vertex == topology.external_vertex:
            current["q"] -= 1
        for label, sign in events[vertex]:
            current[label] += sign
        electron.append(sp.expand(m**2 - _square(current)))

    photons = tuple(-sp_atom(label, label) for label in LOOP_NAMES)
    return tuple(electron) + photons


def _source_vector_transform(label_map: Mapping[str, str]) -> dict[str, dict[str, int]]:
    transform: dict[str, dict[str, int]] = {}
    p = _zero_vector()
    p["p"] = -1
    p["q"] = -1
    transform["p"] = p
    transform["q"] = _basis_vector("q")
    for source_label in LOOP_NAMES:
        target_label = label_map[source_label]
        vec = _zero_vector()
        vec[target_label] = -1
        transform[source_label] = vec
    return transform


def _transformed_pair(
    pair: tuple[str, str], transform: Mapping[str, Mapping[str, int]]
) -> sp.Expr:
    return sp.expand(_dot(transform[pair[0]], transform[pair[1]]))


def _linear_rank(expressions: tuple[sp.Expr, ...] | list[sp.Expr]) -> int:
    rows = [[sp.expand(expr).coeff(atom) for atom in SP_ATOMS] for expr in expressions]
    return int(sp.Matrix(rows).rank())


def _choose_completion_isps(
    topology: ThreeLoopTopology, physical: tuple[sp.Expr, ...]
) -> tuple[tuple[str, str], ...]:
    """Choose as many auxiliary scalar products as needed to reach rank 12.

    For a standard nine-independent-propagator family this returns exactly three
    ISPs.  If the physical propagators have rank < 9 it returns more than three;
    that is diagnostic evidence that dependent-propagator preprocessing is
    required before a conventional 12-denominator Kira family can be built.
    """
    if topology.diagram_id == "Q01":
        expressions = list(physical) + [sp_atom(a, b) for a, b in Q01_ISP_PAIRS]
        if _linear_rank(expressions) != 12:
            raise ValueError("Q01 legacy ISP basis is not full rank")
        return Q01_ISP_PAIRS

    chosen: list[tuple[str, str]] = []
    expressions = list(physical)
    rank = _linear_rank(expressions)
    for pair in SP_PAIRS:
        candidate = sp_atom(*pair)
        new_rank = _linear_rank(expressions + [candidate])
        if new_rank > rank:
            chosen.append(pair)
            expressions.append(candidate)
            rank = new_rank
        if rank == 12:
            break
    if rank != 12:
        raise ValueError(f"{topology.diagram_id}: could not complete scalar-product rank to 12")
    return tuple(chosen)


@dataclass(frozen=True)
class AlgebraicFamilyMap:
    source_id: str
    target_id: str
    loop_label_map: tuple[tuple[str, str], ...]
    external_transform: tuple[str, str]
    physical_index_map: tuple[tuple[int, int], ...]
    representative_isp_pairs: tuple[tuple[str, str], ...]
    induced_target_isps: tuple[str, ...]
    source_physical_rank: int
    target_physical_rank: int
    auxiliary_count_needed: int
    source_completed_rank: int
    target_completed_rank: int
    physical_verified: bool
    reflection_equivalent: bool
    direct_12_denominator_kira_ready: bool
    requires_dependent_propagator_preprocessing: bool
    q01_legacy_basis_preserved: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "loop_label_map": dict(self.loop_label_map),
            "external_transform": {
                "p_source": self.external_transform[0],
                "q_source": self.external_transform[1],
            },
            "physical_index_map": [list(item) for item in self.physical_index_map],
            "representative_isp_pairs": [list(pair) for pair in self.representative_isp_pairs],
            "induced_target_isps": list(self.induced_target_isps),
            "source_physical_rank": self.source_physical_rank,
            "target_physical_rank": self.target_physical_rank,
            "auxiliary_count_needed": self.auxiliary_count_needed,
            "source_completed_rank": self.source_completed_rank,
            "target_completed_rank": self.target_completed_rank,
            "physical_verified": self.physical_verified,
            "reflection_equivalent": self.reflection_equivalent,
            "direct_12_denominator_kira_ready": self.direct_12_denominator_kira_ready,
            "requires_dependent_propagator_preprocessing": self.requires_dependent_propagator_preprocessing,
            "q01_legacy_basis_preserved": self.q01_legacy_basis_preserved,
            # Backward-compatible aliases used by the earlier report printer.
            "source_family_rank": self.source_completed_rank,
            "target_family_rank": self.target_completed_rank,
            "full_family_verified": self.direct_12_denominator_kira_ready,
        }


def verify_q_reflection_family_algebraically(
    source: ThreeLoopTopology,
    target: ThreeLoopTopology,
    propagator_map: ReflectionPropagatorMap,
) -> AlgebraicFamilyMap:
    """Verify reflection equivalence and classify Kira-family readiness."""
    if not source.diagram_id.startswith("Q") or not target.diagram_id.startswith("Q"):
        raise ValueError("algebraic Q verifier only accepts Q diagrams")
    label_map = dict(propagator_map.loop_label_map)
    transform = _source_vector_transform(label_map)

    source_physical = q_physical_denominators(source)
    target_physical = q_physical_denominators(target)

    substitutions = {
        sp_atom(a, b): _transformed_pair((a, b), transform)
        for a, b in SP_PAIRS
    }
    index_map: list[tuple[int, int]] = []
    for i in range(1, 7):
        target_i = 7 - i
        transformed = sp.expand(source_physical[i - 1].xreplace(substitutions))
        if sp.simplify(transformed - target_physical[target_i - 1]) != 0:
            raise ValueError(
                f"{source.diagram_id}->{target.diagram_id}: electron D{i} does not map to D{target_i}"
            )
        index_map.append((i, target_i))

    target_photon_index = {label: 7 + pos for pos, label in enumerate(LOOP_NAMES)}
    source_photon_index = {label: 7 + pos for pos, label in enumerate(LOOP_NAMES)}
    for source_label in LOOP_NAMES:
        target_label = label_map[source_label]
        i = source_photon_index[source_label]
        j = target_photon_index[target_label]
        transformed = sp.expand(source_physical[i - 1].xreplace(substitutions))
        if sp.simplify(transformed - target_physical[j - 1]) != 0:
            raise ValueError(
                f"{source.diagram_id}->{target.diagram_id}: photon D{i} does not map to D{j}"
            )
        index_map.append((i, j))

    source_physical_rank = _linear_rank(list(source_physical))
    target_physical_rank = _linear_rank(list(target_physical))
    if source_physical_rank != target_physical_rank:
        raise ValueError(
            f"{source.diagram_id}->{target.diagram_id}: physical ranks differ "
            f"source={source_physical_rank}, target={target_physical_rank}"
        )

    isp_pairs = _choose_completion_isps(source, source_physical)
    source_isps = tuple(sp_atom(a, b) for a, b in isp_pairs)
    induced_target_isps = tuple(_transformed_pair(pair, transform) for pair in isp_pairs)
    source_rank = _linear_rank(list(source_physical) + list(source_isps))
    target_rank = _linear_rank(list(target_physical) + list(induced_target_isps))
    if source_rank != 12 or target_rank != 12:
        raise ValueError(
            f"{source.diagram_id}->{target.diagram_id}: incomplete completed rank "
            f"source={source_rank}, target={target_rank}"
        )

    auxiliary_count = len(isp_pairs)
    direct_ready = source_physical_rank == 9 and target_physical_rank == 9 and auxiliary_count == 3
    return AlgebraicFamilyMap(
        source_id=source.diagram_id,
        target_id=target.diagram_id,
        loop_label_map=tuple(sorted(label_map.items())),
        external_transform=("-(p+q)", "q"),
        physical_index_map=tuple(sorted(index_map)),
        representative_isp_pairs=isp_pairs,
        induced_target_isps=tuple(str(sp.expand(expr)) for expr in induced_target_isps),
        source_physical_rank=source_physical_rank,
        target_physical_rank=target_physical_rank,
        auxiliary_count_needed=auxiliary_count,
        source_completed_rank=source_rank,
        target_completed_rank=target_rank,
        physical_verified=True,
        reflection_equivalent=True,
        direct_12_denominator_kira_ready=direct_ready,
        requires_dependent_propagator_preprocessing=not direct_ready,
        q01_legacy_basis_preserved=(source.diagram_id != "Q01" or isp_pairs == Q01_ISP_PAIRS),
    )
