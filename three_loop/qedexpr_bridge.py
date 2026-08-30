"""Bridge three-loop structural amplitudes into QEDCalc's expression tree.

The registry and ordered-amplitude layers intentionally remain simple and
inspectable.  This module is the first integration layer with the restored
QEDCalc symbolic backend.

For now the bridge is exact for the quenched open-electron-line family Q01-Q50.
Closed-loop VP/LBL kernels remain explicit structural objects and will be
connected in later stages rather than guessed here.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import sympy as sp

from qedcalc.core.expression import (
    Add,
    FermionPropagator,
    Gamma,
    Index,
    LoopIntegralExpression,
    Metric,
    NCProduct,
    PhotonPropagator,
    Power,
    ScalarMul,
    Slash,
    Symbol,
    Vector,
)

from .amplitude import OrderedAmplitude, build_ordered_amplitude
from .projector import MagneticProjector, three_loop_magnetic_projector
from .registry import ThreeLoopTopology


@dataclass(frozen=True)
class ProjectorReadyAmplitude:
    """One three-loop bare amplitude represented in the QEDCalc backend."""

    topology: ThreeLoopTopology
    ordered: OrderedAmplitude
    loop_integral: LoopIntegralExpression
    projector: MagneticProjector


def _momentum_expr(text: str):
    """Convert strings such as ``p' - k - l`` to a QEDExpr linear sum."""
    tokens = re.findall(r"[+-]?\s*[^+-]+", text.strip())
    terms = []
    for token in tokens:
        token = token.strip()
        sign = 1
        if token.startswith("+"):
            token = token[1:].strip()
        elif token.startswith("-"):
            sign = -1
            token = token[1:].strip()
        if not token:
            continue
        vec = Vector(token)
        terms.append(vec if sign == 1 else ScalarMul(-1, vec))
    if not terms:
        raise ValueError(f"empty momentum expression: {text!r}")
    return terms[0] if len(terms) == 1 else Add(*terms)


def _gamma_from_label(label: str) -> Gamma:
    """Map structural gamma labels to shared Lorentz indices."""
    if label == "gamma_mu":
        return Gamma(Index("mu", "down"))
    match = re.fullmatch(r"gamma_([^_]+)(?:_[LR])?", label)
    if not match:
        raise ValueError(f"unsupported gamma label: {label}")
    return Gamma(Index(match.group(1), "up"))


def _fermion_propagator(momentum_text: str) -> FermionPropagator:
    momentum = _momentum_expr(momentum_text)
    denominator = Add(
        Symbol("m"),
        ScalarMul(-1, Slash(momentum)),
        ScalarMul(-1, Symbol("i_epsilon")),
    )
    return FermionPropagator(denominator)


def _photon_propagator(label: str) -> PhotonPropagator:
    """Build the Feynman-gauge metric part of a photon propagator.

    Gauge-dependent longitudinal pieces are intentionally not invented here;
    the topology-to-QEDExpr bridge records the same metric propagator structure
    used by the existing raw-diagram symbolic machinery.
    """
    numerator = Metric(Index(label, "down"), Index(label, "down"))
    denominator = Add(
        ScalarMul(-1, Power(Vector(label), 2)),
        ScalarMul(-1, Symbol("i_epsilon")),
    )
    return PhotonPropagator(numerator, denominator)


def ordered_amplitude_to_qedexpr(
    topology: ThreeLoopTopology,
    *,
    prefactor_latex: str = "C_3",
    dimension="D",
) -> LoopIntegralExpression:
    """Convert an ordered quenched three-loop amplitude to QEDCalc QEDExpr.

    ``C_3`` is deliberately kept as a normalization placeholder at this bridge
    layer.  Coupling, loop-measure, gauge and sign ownership are convention
    concerns and must be supplied explicitly before physical assembly.
    """
    if topology.family != "quenched":
        raise NotImplementedError(
            "QEDExpr bridge currently supports the quenched Q01-Q50 family; "
            "VP/LBL kernels require their explicit closed-loop builders."
        )

    ordered = build_ordered_amplitude(topology)
    open_factors = []
    for factor in ordered.open_line:
        if factor.kind == "gamma":
            open_factors.append(_gamma_from_label(factor.value))
        elif factor.kind == "electron_propagator":
            open_factors.append(_fermion_propagator(factor.value))
        else:
            raise ValueError(f"unexpected open-line factor kind: {factor.kind}")

    # Keep the ordered electron chain first.  Photon propagators carry paired
    # indices with the same labels as the gamma endpoints, so later Lorentz
    # contraction can operate on the shared names.
    photon_factors = [_photon_propagator(f.value) for f in ordered.photon_factors]
    integrand = NCProduct(*(open_factors + photon_factors))
    if ordered.sign == -1:
        integrand = ScalarMul(-1, integrand)

    loops = tuple(Vector(edge.label) for edge in topology.photon_edges)
    return LoopIntegralExpression(
        prefactor_latex=prefactor_latex,
        loops=loops,
        integrand=integrand,
        dimension=dimension,
    )


def build_projector_ready_amplitude(
    topology: ThreeLoopTopology,
    *,
    D=None,
    z=None,
    prefactor_latex: str = "C_3",
) -> ProjectorReadyAmplitude:
    """Build topology -> ordered amplitude -> QEDExpr -> projector metadata."""
    ordered = build_ordered_amplitude(topology)
    loop_integral = ordered_amplitude_to_qedexpr(
        topology,
        prefactor_latex=prefactor_latex,
        dimension="D" if D is None else D,
    )
    projector = three_loop_magnetic_projector(D=D, z=z)
    return ProjectorReadyAmplitude(topology, ordered, loop_integral, projector)


def q01_bridge_checkpoint(topology: ThreeLoopTopology) -> dict[str, object]:
    """Small inspectable checkpoint used before heavy three-loop algebra."""
    ready = build_projector_ready_amplitude(topology)
    nodes = tuple(ready.loop_integral.integrand.walk())
    return {
        "diagram_id": topology.diagram_id,
        "loop_names": tuple(v.name for v in ready.loop_integral.loops),
        "gamma_count": sum(isinstance(n, Gamma) for n in nodes),
        "fermion_propagator_count": sum(isinstance(n, FermionPropagator) for n in nodes),
        "photon_propagator_count": sum(isinstance(n, PhotonPropagator) for n in nodes),
        "projector_has_finite_q": bool(
            ready.projector.a.has(sp.Symbol("z")) and ready.projector.b.has(sp.Symbol("z"))
        ),
    }
