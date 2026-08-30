from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Mapping, Sequence, Tuple
import sympy as sp

from qedcalc.operations.subdiagram import Subdiagram, enumerate_forests, is_forest


@dataclass(frozen=True)
class ContractedGraph:
    """Topology-only representation of G/F for a Zimmermann forest F.

    ``members`` are the surviving topology identifiers after every declared
    subdiagram in ``forest`` has been replaced by one local contracted vertex.
    QEDCalc deliberately keeps this separate from algebraic amplitude
    reconstruction: topology contraction is exact bookkeeping, while the
    amplitude associated with the contracted graph is supplied by an explicit
    provider/evaluator.
    """
    original_name: str
    original_members: frozenset[str]
    forest: Tuple[Subdiagram, ...]
    members: frozenset[str]
    contraction_vertices: Tuple[str, ...]


@dataclass(frozen=True)
class TaylorSubtractionSpec:
    """Taylor subtraction data for one divergent subdiagram."""
    subdiagram: Subdiagram
    variables: Tuple[sp.Symbol, ...]
    degree: int
    expansion_point: Tuple[object, ...]

    def __init__(self, subdiagram: Subdiagram, variables: Sequence[object],
                 degree: int | None = None, expansion_point: Sequence[object] | None = None):
        vars_ = tuple(sp.sympify(v) for v in variables)
        if not vars_ or not all(v.is_Symbol for v in vars_):
            raise ValueError("variables must contain at least one SymPy symbol.")
        deg = subdiagram.superficial_degree if degree is None else degree
        if deg is None:
            raise ValueError("Taylor subtraction degree is not specified and the subdiagram has no superficial_degree.")
        deg = int(deg)
        if deg < 0:
            raise ValueError("Taylor subtraction degree must be non-negative.")
        if expansion_point is None:
            point = tuple(sp.Integer(0) for _ in vars_)
        else:
            point = tuple(sp.sympify(x) for x in expansion_point)
            if len(point) != len(vars_):
                raise ValueError("expansion_point must have the same length as variables.")
        object.__setattr__(self, "subdiagram", subdiagram)
        object.__setattr__(self, "variables", vars_)
        object.__setattr__(self, "degree", deg)
        object.__setattr__(self, "expansion_point", point)


@dataclass(frozen=True)
class ForestContribution:
    forest: Tuple[Subdiagram, ...]
    contracted_graph: ContractedGraph
    sign: int
    amplitude: object
    signed_amplitude: object


@dataclass(frozen=True)
class ForestFormulaResult:
    graph_name: str
    contributions: Tuple[ForestContribution, ...]
    total: object


def contract_graph(graph_name: str, graph_members: Iterable[str],
                   forest: Iterable[Subdiagram]) -> ContractedGraph:
    """Contract a compatible forest into local topology vertices.

    Nested forests are handled from inner to outer.  A parent contraction
    consumes any child contraction vertex that lies inside its member set and
    leaves only the parent's local vertex in the final topology.
    """
    members = frozenset(str(x) for x in graph_members)
    forest_tuple = tuple(forest)
    if not is_forest(forest_tuple):
        raise ValueError("The supplied subdiagrams do not form a Zimmermann-compatible forest.")
    for sub in forest_tuple:
        if not sub.members <= members:
            missing = sorted(sub.members - members)
            raise ValueError(f"Subdiagram '{sub.name}' contains members outside graph '{graph_name}': {missing}")

    # Inner subgraphs first.  For equal-sized disjoint graphs the name gives a
    # deterministic order without changing the result.
    ordered = tuple(sorted(forest_tuple, key=lambda s: (len(s.members), s.name)))
    current = set(members)
    active_vertices: dict[str, tuple[Subdiagram, str]] = {}

    for sub in ordered:
        # Remove original members of this subdiagram.
        current.difference_update(sub.members)
        # Nested child CT vertices live inside this parent and disappear when
        # the parent itself is contracted.
        for child_name, (child, token) in list(active_vertices.items()):
            if child.members < sub.members:
                current.discard(token)
                del active_vertices[child_name]
        token = f"CT[{sub.name}]"
        current.add(token)
        active_vertices[sub.name] = (sub, token)

    vertices = tuple(sorted(token for _, token in active_vertices.values()))
    return ContractedGraph(
        original_name=str(graph_name),
        original_members=members,
        forest=forest_tuple,
        members=frozenset(current),
        contraction_vertices=vertices,
    )


def _multiindices(nvars: int, max_degree: int):
    """Yield all non-negative multiindices with total degree <= max_degree."""
    for powers in product(range(max_degree + 1), repeat=nvars):
        if sum(powers) <= max_degree:
            yield powers


def taylor_operator(expr, variables: Sequence[object], degree: int,
                    expansion_point: Sequence[object] | None = None):
    r"""Return the multivariate Taylor polynomial of total degree <= ``degree``.

    The operator is the BPHZ-style local Taylor projector

        t^omega f(p) = sum_{|a|<=omega} (p-p0)^a/a! * d^a f(p0).

    It acts only on the explicitly supplied commuting SymPy variables.  QEDCalc
    does not infer which external momenta a subgraph depends on.
    """
    vars_ = tuple(sp.sympify(v) for v in variables)
    if not vars_ or not all(v.is_Symbol for v in vars_):
        raise ValueError("variables must contain at least one SymPy symbol.")
    degree = int(degree)
    if degree < 0:
        raise ValueError("degree must be non-negative.")
    if expansion_point is None:
        point = tuple(sp.Integer(0) for _ in vars_)
    else:
        point = tuple(sp.sympify(x) for x in expansion_point)
        if len(point) != len(vars_):
            raise ValueError("expansion_point must have the same length as variables.")

    f = sp.sympify(expr)
    result = sp.Integer(0)
    substitutions = dict(zip(vars_, point))
    for powers in _multiindices(len(vars_), degree):
        deriv = f
        monomial = sp.Integer(1)
        factorial = sp.Integer(1)
        for var, p0, power in zip(vars_, point, powers):
            if power:
                deriv = sp.diff(deriv, var, power)
                monomial *= (var - p0) ** power
                factorial *= sp.factorial(power)
        coefficient = sp.simplify(deriv.subs(substitutions))
        result += coefficient * monomial / factorial
    return sp.simplify(sp.expand(result))


def apply_taylor_spec(expr, spec: TaylorSubtractionSpec):
    return taylor_operator(expr, spec.variables, spec.degree, spec.expansion_point)



def bphz_local_counterterm(expr, spec: TaylorSubtractionSpec):
    r"""Return the local BPHZ counterterm ``-t^omega expr`` for one subdiagram.

    This is a momentum-subtraction/BPHZ building block.  It is distinct from
    MS/MS-bar pole subtraction and therefore should be selected explicitly by
    the caller according to the intended renormalization scheme.
    """
    return sp.simplify(-apply_taylor_spec(expr, spec))


def bphz_subtract(expr, spec: TaylorSubtractionSpec):
    r"""Return ``(1 - t^omega) expr`` for one declared subdiagram amplitude."""
    f = sp.sympify(expr)
    return sp.simplify(sp.expand(f - apply_taylor_spec(f, spec)))


def forest_formula(graph_name: str, graph_members: Iterable[str],
                   subdiagrams: Iterable[Subdiagram],
                   amplitude_provider: Callable[[ContractedGraph], object],
                   include_empty: bool = True) -> ForestFormulaResult:
    r"""Assemble a topology-driven Zimmermann forest sum from explicit amplitudes.

    For each compatible forest F this routine constructs G/F and asks
    ``amplitude_provider`` for the *already local-subtracted amplitude assigned
    to that contracted topology*.  QEDCalc then supplies the forest sign
    (-1)^|F| and sums the contributions.

    This separation is intentional.  A plain algebraic bare amplitude does not
    retain enough graph topology to manufacture all contracted amplitudes
    safely.  ``taylor_operator`` and ``TaylorSubtractionSpec`` provide the local
    subtraction building blocks, while the provider explicitly connects them
    to each contracted topology.
    """
    subs = tuple(subdiagrams)
    forests = enumerate_forests(subs, include_empty=include_empty)
    contributions = []
    total = sp.Integer(0)
    for forest in forests:
        contracted = contract_graph(graph_name, graph_members, forest)
        amplitude = sp.sympify(amplitude_provider(contracted))
        sign = -1 if len(forest) % 2 else 1
        signed = sp.expand(sign * amplitude)
        contributions.append(ForestContribution(forest, contracted, sign, amplitude, signed))
        total += signed
    return ForestFormulaResult(str(graph_name), tuple(contributions), sp.simplify(sp.expand(total)))
