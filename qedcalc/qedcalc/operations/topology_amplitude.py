from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence, Tuple

from qedcalc.core.expression import QEDExpr, NCProduct, Product
from qedcalc.operations.forest import ContractedGraph
from qedcalc.operations.subdiagram import Subdiagram


@dataclass(frozen=True)
class TopologyFactor:
    """One explicitly ordered factor in a graph amplitude template.

    ``factor_id`` is the topology identifier used by ``Subdiagram.members``.
    ``expression`` is the algebraic QED expression attached to that factor.
    ``commutative`` should be true only for factors that may be moved freely.
    """
    factor_id: str
    expression: QEDExpr
    commutative: bool = False


@dataclass(frozen=True)
class QEDAmplitudeTemplate:
    """Ordered topology-to-algebra bridge for one graph.

    QEDCalc deliberately requires an explicit factor order.  A bare algebraic
    expression does not retain enough graph topology to reconstruct this order
    safely after subgraph contractions.
    """
    graph_name: str
    factors: Tuple[TopologyFactor, ...]

    def __init__(self, graph_name: str, factors: Sequence[TopologyFactor]):
        items = tuple(factors)
        if not items:
            raise ValueError("An amplitude template must contain at least one factor.")
        ids = [x.factor_id for x in items]
        if len(set(ids)) != len(ids):
            raise ValueError("Topology factor identifiers must be unique.")
        object.__setattr__(self, "graph_name", str(graph_name))
        object.__setattr__(self, "factors", items)

    @property
    def member_ids(self) -> frozenset[str]:
        return frozenset(x.factor_id for x in self.factors)


@dataclass(frozen=True)
class LocalVertexReplacement:
    """Algebraic local vertex assigned to one contracted subdiagram."""
    subdiagram_name: str
    expression: QEDExpr


@dataclass(frozen=True)
class BuiltAmplitude:
    graph_name: str
    contracted_members: Tuple[str, ...]
    expression: QEDExpr


def _compose(expressions: Sequence[tuple[QEDExpr, bool]]) -> QEDExpr:
    """Compose ordered non-commuting factors with separated scalar factors."""
    comm = [expr for expr, is_comm in expressions if is_comm]
    noncomm = [expr for expr, is_comm in expressions if not is_comm]
    scalar = None if not comm else (comm[0] if len(comm) == 1 else Product(*comm))
    chain = None if not noncomm else (noncomm[0] if len(noncomm) == 1 else NCProduct(*noncomm))
    if scalar is None:
        return chain
    if chain is None:
        return scalar
    return Product(scalar, chain)


def build_bare_amplitude(template: QEDAmplitudeTemplate) -> BuiltAmplitude:
    """Build the bare algebraic amplitude from an explicit topology template."""
    expression = _compose([(x.expression, x.commutative) for x in template.factors])
    return BuiltAmplitude(template.graph_name, tuple(x.factor_id for x in template.factors), expression)


def _contiguous_block(ids: Sequence[str], members: frozenset[str]):
    positions = [i for i, item in enumerate(ids) if item in members]
    if not positions:
        return None
    lo, hi = min(positions), max(positions)
    if set(ids[lo:hi+1]) != set(members):
        return None
    return lo, hi


def build_contracted_amplitude(
    template: QEDAmplitudeTemplate,
    contracted: ContractedGraph,
    subdiagrams: Iterable[Subdiagram],
    local_vertices: Mapping[str, QEDExpr],
) -> BuiltAmplitude:
    """Build an algebraic amplitude for ``G/F`` using explicit local vertices.

    Safety rule: every contracted subdiagram must correspond to a contiguous
    block in the ordered amplitude template at the moment it is replaced.
    This is sufficient for ordered fermion-line chains and prevents QEDCalc
    from guessing a non-local rearrangement.  More general graph topologies
    should use a richer topology template rather than bypassing this check.
    """
    if contracted.original_name != template.graph_name:
        raise ValueError("Contracted graph and amplitude template refer to different graphs.")
    if contracted.original_members != template.member_ids:
        raise ValueError("Contracted graph members do not match the amplitude template.")

    sub_by_name = {s.name: s for s in subdiagrams}
    items = [(f.factor_id, f.expression, f.commutative) for f in template.factors]

    # Inner subgraphs first, consistent with contract_graph().
    forest = tuple(sorted(contracted.forest, key=lambda s: (len(s.members), s.name)))
    for sub in forest:
        if sub.name not in local_vertices:
            raise ValueError(f"No local vertex expression was supplied for subdiagram '{sub.name}'.")
        ids = [x[0] for x in items]
        block = _contiguous_block(ids, sub.members)
        if block is None:
            # A nested parent may contain already-contracted CT child tokens.
            expanded_members = set(sub.members)
            child_tokens = []
            for child in forest:
                if child.members < sub.members:
                    token = f"CT[{child.name}]"
                    if token in ids:
                        child_tokens.append(token)
                        expanded_members.difference_update(child.members)
                        expanded_members.add(token)
            block = _contiguous_block(ids, frozenset(expanded_members))
        if block is None:
            raise ValueError(
                f"Subdiagram '{sub.name}' is not a contiguous block in the ordered amplitude template. "
                "Provide a topology template that preserves the required graph ordering."
            )
        lo, hi = block
        token = f"CT[{sub.name}]"
        items[lo:hi+1] = [(token, local_vertices[sub.name], False)]

    final_ids = tuple(x[0] for x in items)
    if frozenset(final_ids) != contracted.members:
        raise RuntimeError("Constructed amplitude topology does not match ContractedGraph bookkeeping.")
    expression = _compose([(x[1], x[2]) for x in items])
    return BuiltAmplitude(template.graph_name, final_ids, expression)
