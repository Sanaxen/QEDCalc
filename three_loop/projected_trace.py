"""Finite-q magnetic-projector trace for three-loop vertex amplitudes.

This module constructs the spin-summed Pauli-projector trace and provides a
fast reduction path to a SymPy scalar-product numerator.  The reduction reuses
QEDCalc's optimized arbitrary-length D-dimensional Clifford trace.
"""
from __future__ import annotations

from dataclasses import dataclass
import sympy as sp

from qedcalc.core.expression import (
    Add,
    DiracTrace,
    Fraction,
    Gamma,
    Index,
    NCProduct,
    ScalarMul,
    Slash,
    Symbol,
    Vector,
    VectorComponent,
)
from qedcalc.operations.dirac import dirac_trace_fully_contracted_sympy
from qedcalc.operations.lorentz import contract_metric
from qedcalc.operations.propagator import (
    scalarize_fermion_propagators,
    separate_numerator_denominator,
)

from .projector import MagneticProjector
from .qedexpr_bridge import ProjectorReadyAmplitude, build_projector_ready_amplitude
from .registry import ThreeLoopTopology


@dataclass(frozen=True)
class ProjectedTraceStructure:
    """Unexpanded finite-q Pauli-projector trace and scalar denominator."""

    diagram_id: str
    projector: MagneticProjector
    trace: DiracTrace
    scalar_denominator: object
    loop_integral: object
    vertex_numerator: object


@dataclass(frozen=True)
class ScalarProjectedNumerator:
    """Finite-q projected numerator after D-dimensional trace contraction."""

    diagram_id: str
    expression: sp.Expr
    gamma_branch: sp.Expr
    pair_branch: sp.Expr
    scalar_product_atoms: tuple[str, ...]


def _spin_sum(momentum_name: str):
    """Return /p + m for an on-shell external electron spin sum."""
    return Add(Slash(Vector(momentum_name)), Symbol("m"))


def magnetic_projector_kernel(projector: MagneticProjector):
    """Return the finite-q projector kernel in inspectable QEDExpr form."""
    mu = Index("mu", "up")
    pair_mu = Add(
        VectorComponent(Vector("p'"), mu),
        VectorComponent(Vector("p"), mu),
    )
    return Add(
        ScalarMul(projector.a, Gamma(mu)),
        ScalarMul(projector.b / sp.Symbol("m"), pair_mu),
    )


def _replace_vertex_mu_by_pair_slash(expr):
    """Contract (p'+p)^mu with the unique external vertex gamma_mu.

    For the scalar projector branch,

        (p'+p)^mu Gamma_mu  ->  /p' + /p.

    Performing this replacement before the optimized trace removes the only
    explicit VectorComponent from the Clifford problem while preserving the
    exact Lorentz contraction and matrix ordering at the vertex position.
    """
    if isinstance(expr, Gamma) and expr.index.name == "mu" and expr.index.position == "down":
        return Add(Slash(Vector("p'")), Slash(Vector("p")))
    if isinstance(expr, Add):
        return Add(*(_replace_vertex_mu_by_pair_slash(t) for t in expr.terms))
    if isinstance(expr, NCProduct):
        return NCProduct(*(_replace_vertex_mu_by_pair_slash(f) for f in expr.factors))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, _replace_vertex_mu_by_pair_slash(expr.expr))
    return expr


def build_projected_trace(ready: ProjectorReadyAmplitude) -> ProjectedTraceStructure:
    """Construct the spin-summed finite-q projector trace.

    Propagators are scalarized, denominators are separated, and the three
    photon metrics are contracted against their gamma endpoints before the
    Clifford trace is formed.  This gives the long-trace engine paired dummy
    indices rather than a separate metric tensor network.
    """
    scalarized = scalarize_fermion_propagators(ready.loop_integral.integrand)
    separated = separate_numerator_denominator(scalarized)
    if not isinstance(separated, Fraction):
        raise TypeError("three-loop integrand did not separate into numerator/denominator")

    vertex_numerator = contract_metric(separated.numerator)
    trace_word = NCProduct(
        _spin_sum("p'"),
        magnetic_projector_kernel(ready.projector),
        _spin_sum("p"),
        vertex_numerator,
    )
    trace = DiracTrace(trace_word)

    normalized_integrand = Fraction(
        ScalarMul(1 / sp.Symbol("m")**2, trace),
        separated.denominator,
    )
    loop_integral = type(ready.loop_integral)(
        prefactor_latex=ready.loop_integral.prefactor_latex,
        loops=ready.loop_integral.loops,
        integrand=normalized_integrand,
        dimension=ready.loop_integral.dimension,
    )
    return ProjectedTraceStructure(
        diagram_id=ready.topology.diagram_id,
        projector=ready.projector,
        trace=trace,
        scalar_denominator=separated.denominator,
        loop_integral=loop_integral,
        vertex_numerator=vertex_numerator,
    )


def build_topology_projected_trace(
    topology: ThreeLoopTopology,
    *,
    D=None,
    z=None,
    prefactor_latex: str = "C_3",
) -> ProjectedTraceStructure:
    """Convenience path: topology -> QEDExpr -> finite-q projector trace."""
    ready = build_projector_ready_amplitude(
        topology,
        D=D,
        z=z,
        prefactor_latex=prefactor_latex,
    )
    return build_projected_trace(ready)


def reduce_projected_trace_to_scalar_products(
    projected: ProjectedTraceStructure,
    *,
    D_name: str = "D",
) -> ScalarProjectedNumerator:
    """Reduce the finite-q projector trace directly to scalar products.

    The two projector structures are evaluated separately:

    1. ``a gamma^mu`` is a pure Clifford trace;
    2. ``b (p'+p)^mu/m`` is converted by contracting the vertex gamma_mu to
       ``/p' + /p`` at its original matrix position.

    QEDCalc's optimized trace routine then performs the complete D-dimensional
    Clifford/Lorentz contraction directly to SymPy atoms named
    ``SP__<momentum1>__<momentum2>``.  No q->0 or on-shell scalar-product
    substitution is made here.
    """
    p_out = _spin_sum("p'")
    p_in = _spin_sum("p")

    gamma_word = NCProduct(
        p_out,
        Gamma(Index("mu", "up")),
        p_in,
        projected.vertex_numerator,
    )
    gamma_trace = dirac_trace_fully_contracted_sympy(gamma_word, D_name=D_name)

    pair_vertex = _replace_vertex_mu_by_pair_slash(projected.vertex_numerator)
    pair_word = NCProduct(p_out, p_in, pair_vertex)
    pair_trace = dirac_trace_fully_contracted_sympy(pair_word, D_name=D_name)

    m = sp.Symbol("m")
    gamma_branch = sp.expand(projected.projector.a * gamma_trace / m**2)
    pair_branch = sp.expand(projected.projector.b * pair_trace / m**3)
    expression = sp.expand(gamma_branch + pair_branch)
    atoms = tuple(sorted(
        str(s) for s in expression.free_symbols
        if str(s).startswith("SP__")
    ))
    return ScalarProjectedNumerator(
        diagram_id=projected.diagram_id,
        expression=expression,
        gamma_branch=gamma_branch,
        pair_branch=pair_branch,
        scalar_product_atoms=atoms,
    )


def projected_trace_checkpoint(projected: ProjectedTraceStructure) -> dict[str, object]:
    """Return cheap structural invariants before expensive trace expansion."""
    trace_nodes = tuple(projected.trace.argument.walk())
    return {
        "diagram_id": projected.diagram_id,
        "loop_names": tuple(v.name for v in projected.loop_integral.loops),
        "has_dirac_trace": isinstance(projected.trace, DiracTrace),
        "external_spin_slashes": sum(
            isinstance(n, Slash)
            and isinstance(n.arg, Vector)
            and n.arg.name in {"p", "p'"}
            for n in trace_nodes
        ),
        "projector_gamma_mu_up": any(
            isinstance(n, Gamma)
            and n.index.name == "mu"
            and n.index.position == "up"
            for n in trace_nodes
        ),
        "vertex_gamma_mu_down": any(
            isinstance(n, Gamma)
            and n.index.name == "mu"
            and n.index.position == "down"
            for n in trace_nodes
        ),
        "finite_q_not_substituted": bool(
            projected.projector.a.has(projected.projector.z)
            and projected.projector.b.has(projected.projector.z)
        ),
    }
