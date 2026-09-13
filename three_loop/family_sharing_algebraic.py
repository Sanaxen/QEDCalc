"""Algebraic denominator/ISP verification for three-loop Q-family sharing.

This stage upgrades open-chain reflection candidates to exact reusable integral
family maps.  It constructs the physical propagators directly from the topology,
derives the reflection momentum transformation, and completes the nine physical
propagators to a full 12-dimensional scalar-product basis.

For Q01 the existing QEDCalc ISP basis (k.r, l.q, q.r) is kept exactly so the
current Q01 Kira work remains the canonical representative.  Partner families
receive the ISP basis induced by the reflection map; this is what allows target
integrals to be translated into the representative Kira family without guessing.
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


def _scalar_atom(left: str, right: str) -> sp.Expr:
    """Return one scalar product after applying the finite-q on-shell rules."""
    m = sp.Symbol("m")
    z = sp.Symbol("z")
    if left == right == "p":
        return m**2
    if left == right == "q":
        return z * m**2
    if {left, right} == {"p", "q"}:
        return -z * m**2 / 2
    return sp_atom(left, right)


def _dot(a: Mapping[str, int], b: Mapping[str, int]) -> sp.Expr:
    """Exact bilinear scalar product of two integer momentum combinations.

    Do not skip a basis direction merely because its coefficient in ``a`` is
    zero: for an off-diagonal pair the contribution ``a[j] * b[i]`` may still
    be non-zero.  The previous triangular implementation made exactly that
    mistake and therefore lost terms such as ``(-r).(-(p+q))``.
    """
    result = sp.Integer(0)
    for i, left in enumerate(VECTOR_NAMES):
        diagonal = a[left] * b[left]
        if diagonal:
            result += diagonal * _scalar_atom(left, left)
        for right in VECTOR_NAMES[i + 1:]:
            coefficient = a[left] * b[right] + a[right] * b[left]
            if coefficient:
                result += coefficient * _scalar_atom(left, right)
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
    """Return source-vector expressions in target variables for chain reflection."""
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


def _transform_vector(
    vector: Mapping[str, int], transform: Mapping[str, Mapping[str, int]]
) -> dict[str, int]:
    out = _zero_vector()
    for source_name, coefficient in vector.items():
        if coefficient:
            _add_scaled(out, transform[source_name], coefficient)
    return out


def _transformed_pair(
    pair: tuple[str, str], transform: Mapping[str, Mapping[str, int]]
) -> sp.Expr:
    return sp.expand(_dot(transform[pair[0]], transform[pair[1]]))


def _linear_rank(expressions: tuple[sp.Expr, ...] | list[sp.Expr]) -> int:
    rows = [[sp.expand(expr).coeff(atom) for atom in SP_ATOMS] for expr in expressions]
    return int(sp.Matrix(rows).rank())


def _choose_representative_isps(
    topology: ThreeLoopTopology, physical: tuple[sp.Expr, ...]
) -> tuple[tuple[str, str], ...]:
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
    if rank != 12 or len(chosen) != 3:
        raise ValueError(f"{topology.diagram_id}: could not construct 12-dimensional family basis")
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
    source_family_rank: int
    target_family_rank: int
    physical_verified: bool
    full_family_verified: bool
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
            "source_family_rank": self.source_family_rank,
            "target_family_rank": self.target_family_rank,
            "physical_verified": self.physical_verified,
            "full_family_verified": self.full_family_verified,
            "q01_legacy_basis_preserved": self.q01_legacy_basis_preserved,
        }


def verify_q_reflection_family_algebraically(
    source: ThreeLoopTopology,
    target: ThreeLoopTopology,
    propagator_map: ReflectionPropagatorMap,
) -> AlgebraicFamilyMap:
    """Prove a Q reflection pair is one reusable 12-dimensional IBP family."""
    if not source.diagram_id.startswith("Q") or not target.diagram_id.startswith("Q"):
        raise ValueError("algebraic Q verifier only accepts Q diagrams")
    label_map = dict(propagator_map.loop_label_map)
    transform = _source_vector_transform(label_map)

    source_physical = q_physical_denominators(source)
    target_physical = q_physical_denominators(target)

    index_map: list[tuple[int, int]] = []
    substitutions = {
        sp_atom(a, b): _transformed_pair((a, b), transform)
        for a, b in SP_PAIRS
    }

    # Electron segment i -> 7-i under reversal (1-based denominator indices).
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

    isp_pairs = _choose_representative_isps(source, source_physical)
    source_isps = tuple(sp_atom(a, b) for a, b in isp_pairs)
    induced_target_isps = tuple(_transformed_pair(pair, transform) for pair in isp_pairs)
    source_rank = _linear_rank(list(source_physical) + list(source_isps))
    target_rank = _linear_rank(list(target_physical) + list(induced_target_isps))
    if source_rank != 12 or target_rank != 12:
        raise ValueError(
            f"{source.diagram_id}->{target.diagram_id}: incomplete family rank "
            f"source={source_rank}, target={target_rank}"
        )

    return AlgebraicFamilyMap(
        source_id=source.diagram_id,
        target_id=target.diagram_id,
        loop_label_map=tuple(sorted(label_map.items())),
        external_transform=("-(p+q)", "q"),
        physical_index_map=tuple(sorted(index_map)),
        representative_isp_pairs=isp_pairs,
        induced_target_isps=tuple(str(sp.expand(expr)) for expr in induced_target_isps),
        source_family_rank=source_rank,
        target_family_rank=target_rank,
        physical_verified=True,
        full_family_verified=True,
        q01_legacy_basis_preserved=(source.diagram_id != "Q01" or isp_pairs == Q01_ISP_PAIRS),
    )
