"""Finite-q magnetic-projector trace for three-loop vertex amplitudes.

This module turns a projector-ready quenched amplitude into the standard
spin-summed Dirac trace used to isolate F2.  It deliberately stops before
expanding the very large three-loop trace into scalar products; that reduction
is the next computational step and can reuse QEDCalc's D-dimensional trace and
Lorentz-contraction engines.
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
    Product,
    ScalarMul,
    Slash,
    Symbol,
    Vector,
    VectorComponent,
)
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


def _spin_sum(momentum_name: str):
    """Return /p + m for an on-shell external electron spin sum."""
    return Add(Slash(Vector(momentum_name)), Symbol("m"))


def magnetic_projector_kernel(projector: MagneticProjector):
    """Return a gamma^mu + b (p'+p)^mu/m in QEDCalc expression form.

    This is the bracketed kernel in

        P^mu = 1/m^2 (/p' + m)
               [a gamma^mu + b (p'+p)^mu/m]
               (/p + m).

    The overall 1/m^2 is kept outside the Dirac trace in
    ``build_projected_trace`` so it remains an explicit scalar normalization.
    """
    mu = Index("mu", "up")
    pair_mu = Add(
        VectorComponent(Vector("p'"), mu),
        VectorComponent(Vector("p"), mu),
    )
    return Add(
        ScalarMul(projector.a, Gamma(mu)),
        ScalarMul(projector.b / sp.Symbol("m"), pair_mu),
    )


def build_projected_trace(ready: ProjectorReadyAmplitude) -> ProjectedTraceStructure:
    """Construct the spin-summed finite-q projector trace.

    Electron and photon propagators are first scalarized so all denominators
    are outside the Clifford word.  The resulting numerator is inserted into

        Tr[(/p'+m) K^mu (/p+m) Gamma_mu^(3)],

    with K^mu the finite-q magnetic-projector kernel.

    No q->0 substitution is made here.
    """
    scalarized = scalarize_fermion_propagators(ready.loop_integral.integrand)
    separated = separate_numerator_denominator(scalarized)
    if not isinstance(separated, Fraction):
        raise TypeError("three-loop integrand did not separate into numerator/denominator")

    trace_word = NCProduct(
        _spin_sum("p'"),
        magnetic_projector_kernel(ready.projector),
        _spin_sum("p"),
        separated.numerator,
    )
    trace = DiracTrace(trace_word)

    # Keep 1/m^2 explicit rather than hiding it inside a projector coefficient.
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
