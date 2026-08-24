"""Utilities connecting raw loop-integral input to reusable subdiagram algebra."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from qedcalc.core.expression import (
    QEDExpr, DiracTrace, LoopIntegralExpression, Fraction
)
from qedcalc.operations.propagator import (
    recognize_propagators,
    scalarize_fermion_propagators,
    separate_numerator_denominator,
)
from qedcalc.operations.dirac import dirac_trace_4d


def find_dirac_traces(expr: QEDExpr) -> Tuple[DiracTrace, ...]:
    """Return all explicit Dirac traces in traversal order."""
    return tuple(node for node in expr.walk() if isinstance(node, DiracTrace))


def require_single_dirac_trace(expr: QEDExpr) -> DiracTrace:
    traces = find_dirac_traces(expr)
    if len(traces) != 1:
        raise ValueError(f"Expected exactly one Dirac trace, found {len(traces)}.")
    return traces[0]


@dataclass(frozen=True)
class TraceSubdiagramReduction:
    trace: DiracTrace
    scalarized: Fraction
    traced_numerator: QEDExpr
    scalar_denominator: QEDExpr


def reduce_trace_subdiagram_4d(trace: DiracTrace) -> TraceSubdiagramReduction:
    """Scalarize fermion propagators inside a trace and evaluate its numerator.

    This deliberately keeps the scalar denominator separate.  It is the bridge
    needed by vacuum-polarization and future closed-fermion-loop subdiagrams.
    """
    recognized = recognize_propagators(trace.argument)
    scalarized_expr = scalarize_fermion_propagators(recognized)
    frac = separate_numerator_denominator(scalarized_expr)
    if not isinstance(frac, Fraction):
        raise TypeError("Trace subdiagram did not reduce to a numerator/denominator fraction.")
    traced = dirac_trace_4d(frac.numerator)
    return TraceSubdiagramReduction(trace, frac, traced, frac.denominator)


def reduce_single_trace_from_loop_integral_4d(diagram: LoopIntegralExpression) -> TraceSubdiagramReduction:
    return reduce_trace_subdiagram_4d(require_single_dirac_trace(diagram.integrand))

# --- v0.22: open electron self-energy subdiagram discovery ---
from qedcalc.core.expression import (
    Add, ScalarMul, Slash, Vector, Gamma, NCProduct, Symbol, SelfEnergySubdiagram,
    Metric, VectorComponent, Product, Index
)
from qedcalc.operations.lorentz import contract_metric
from qedcalc.operations.dirac import contract_gamma
from qedcalc.operations.algebra import expand_expression, normalize_noncommutative_products
from qedcalc.operations.simplify import simplify_expression


def _fermion_fraction(expr: QEDExpr) -> bool:
    """Return True for a raw fraction whose denominator contains m and a slash."""
    if not isinstance(expr, Fraction):
        return False
    if not (isinstance(expr.numerator, Symbol) and expr.numerator.name == "1"):
        return False
    has_m = any(isinstance(n, Symbol) and n.name == "m" for n in expr.denominator.walk())
    has_slash = any(isinstance(n, Slash) for n in expr.denominator.walk())
    return has_m and has_slash


def _slash_coeff_map(expr: QEDExpr):
    """Collect coefficients of individually slashed vectors in a linear denominator."""
    out = {}
    terms = expr.terms if isinstance(expr, Add) else (expr,)
    for t in terms:
        coeff = 1
        obj = t
        if isinstance(t, ScalarMul):
            coeff = t.coeff
            obj = t.expr
        if isinstance(obj, Slash) and isinstance(obj.arg, Vector):
            try:
                coeff = int(coeff)
            except Exception:
                continue
            out[obj.arg.name] = out.get(obj.arg.name, 0) + coeff
    return {k: v for k, v in out.items() if v != 0}


def _physical_momentum_from_fermion_fraction(frac: Fraction) -> QEDExpr:
    """Infer P from a denominator of the form m-/P-i eps."""
    coeffs = _slash_coeff_map(frac.denominator)
    terms = []
    for name, cden in coeffs.items():
        c = -cden
        vec = Vector(name)
        if c == 1:
            terms.append(vec)
        elif c == -1:
            terms.append(ScalarMul(-1, vec))
        else:
            terms.append(ScalarMul(c, vec))
    if not terms:
        raise ValueError("Could not infer fermion-line momentum from denominator.")
    return terms[0] if len(terms) == 1 else Add(*terms)


def _vector_names(expr: QEDExpr):
    names = set()
    for n in expr.walk():
        if isinstance(n, Vector):
            names.add(n.name)
        elif isinstance(n, VectorComponent):
            names.add(n.vector.name)
        elif isinstance(n, Slash) and isinstance(n.arg, Vector):
            names.add(n.arg.name)
    return names


@dataclass(frozen=True)
class SelfEnergySubdiagramMatch:
    side: str
    start_factor: int
    end_factor: int
    photon_factor: int
    loop_momentum: Vector
    external_momentum: QEDExpr
    left_gamma: Gamma
    middle_propagator: Fraction
    right_gamma: Gamma
    repeated_propagator_left: Fraction
    repeated_propagator_right: Fraction
    photon_expression: QEDExpr


@dataclass(frozen=True)
class SelfEnergySubdiagramReduction:
    match: SelfEnergySubdiagramMatch
    scalarized_middle: Fraction
    feynman_gauge_numerator: QEDExpr
    reduced_numerator: QEDExpr
    scalar_denominator: QEDExpr
    contracted_integrand: QEDExpr


def find_self_energy_subdiagrams(diagram: LoopIntegralExpression) -> Tuple[SelfEnergySubdiagramMatch, ...]:
    """Discover open one-loop self-energy insertions in a bare two-loop chain.

    v0.22 recognizes the characteristic contiguous electron-line pattern

        S(r) gamma^a S(r-l) gamma^b S(r)

    together with a separate photon factor depending only on the extra loop
    momentum ``l``.  The function uses ordering information and does not infer
    a new graph topology when the pattern is absent.
    """
    factors = diagram.integrand.factors if isinstance(diagram.integrand, NCProduct) else (diagram.integrand,)
    gamma_mu_positions = [
        i for i, f in enumerate(factors)
        if isinstance(f, Gamma) and f.index.name == "mu"
    ]
    mu_pos = gamma_mu_positions[0] if gamma_mu_positions else None
    loop_names = {v.name for v in diagram.loops}
    matches = []

    for i in range(max(0, len(factors)-4)):
        block = factors[i:i+5]
        if len(block) != 5:
            continue
        p0, ga, pm, gb, p1 = block
        if not (_fermion_fraction(p0) and isinstance(ga, Gamma) and _fermion_fraction(pm)
                and isinstance(gb, Gamma) and _fermion_fraction(p1)):
            continue
        if p0.denominator != p1.denominator:
            continue
        base = _slash_coeff_map(p0.denominator)
        mid = _slash_coeff_map(pm.denominator)
        all_names = set(base) | set(mid)
        diff = {n: mid.get(n, 0)-base.get(n, 0) for n in all_names}
        diff = {n: c for n, c in diff.items() if c != 0}
        candidates = [n for n, c in diff.items() if n in loop_names and abs(c) == 1]
        if len(candidates) != 1 or len(diff) != 1:
            continue
        loop_name = candidates[0]

        # Find a separate photon factor whose only vector dependence is this loop.
        photon_candidates = []
        for j, f in enumerate(factors):
            if i <= j <= i+4:
                continue
            deps = _vector_names(f)
            if deps == {loop_name}:
                # Require the two gamma indices to occur in the photon factor.
                idx_names = [
                    n.index.name for n in f.walk()
                    if isinstance(n, VectorComponent)
                ]
                metric_names = []
                for n in f.walk():
                    if isinstance(n, Metric):
                        metric_names.extend([n.left.name, n.right.name])
                names = set(idx_names + metric_names)
                if ga.index.name in names and gb.index.name in names:
                    photon_candidates.append(j)
        if len(photon_candidates) != 1:
            continue
        photon_j = photon_candidates[0]
        side = "unknown"
        if mu_pos is not None:
            side = "right" if i > mu_pos else "left"
        matches.append(SelfEnergySubdiagramMatch(
            side=side,
            start_factor=i,
            end_factor=i+4,
            photon_factor=photon_j,
            loop_momentum=Vector(loop_name),
            external_momentum=_physical_momentum_from_fermion_fraction(p0),
            left_gamma=ga,
            middle_propagator=pm,
            right_gamma=gb,
            repeated_propagator_left=p0,
            repeated_propagator_right=p1,
            photon_expression=factors[photon_j],
        ))
    return tuple(matches)


def require_single_self_energy_subdiagram(diagram: LoopIntegralExpression) -> SelfEnergySubdiagramMatch:
    matches = find_self_energy_subdiagrams(diagram)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one self-energy subdiagram, found {len(matches)}.")
    return matches[0]


def _feynman_gauge_self_energy_numerator(match: SelfEnergySubdiagramMatch):
    """Build gamma^a N gamma_a from the detected middle propagator.

    This is the v0.22 bridge to the existing self-energy algebra.  The complete
    raw diagram may be written in a general covariant gauge, but this reduction
    intentionally selects the Feynman-gauge metric part of the internal photon.
    """
    recognized = recognize_propagators(match.middle_propagator)
    scalarized = scalarize_fermion_propagators(recognized)
    if not isinstance(scalarized, Fraction):
        raise TypeError("Middle fermion propagator did not scalarize to a fraction.")
    metric = Metric(Index(match.left_gamma.index.name, "down"), Index(match.right_gamma.index.name, "down"))
    chain = NCProduct(match.left_gamma, scalarized.numerator, match.right_gamma, metric)
    contracted = contract_metric(chain)
    expanded = normalize_noncommutative_products(expand_expression(contracted))
    reduced = simplify_expression(contract_gamma(expanded))
    # Canonicalize the result in terms of the momentum r flowing through the
    # repeated outer propagators.  This preserves the actual algebraic result
    # while making the reusable self-energy structure explicit:
    #   gamma^a (m + /r - /l) gamma_a = 4m - 2/r + 2/l.
    canonical = Add(
        ScalarMul(4, Symbol("m")),
        ScalarMul(-2, Slash(match.external_momentum)),
        ScalarMul(2, Slash(match.loop_momentum)),
    )
    return scalarized, simplify_expression(canonical)


def contract_self_energy_subdiagram(diagram: LoopIntegralExpression, *, conventions=None, renormalized: bool = False) -> SelfEnergySubdiagramReduction:
    """Detect and contract one open self-energy subdiagram to S Sigma S.

    The returned ``contracted_integrand`` removes the separate internal-photon
    factor and replaces the five-factor electron-line block by
    ``S(r) Sigma^(1)(r) S(r)``.  Renormalization is a separate layer; setting
    ``renormalized=True`` changes the structural marker to Sigma_R only after
    the caller has decided to use the renormalized subdiagram.
    """
    if conventions is None:
        from qedcalc.config.conventions import load_conventions
        conventions = load_conventions()
    if not conventions.is_feynman_gauge:
        raise NotImplementedError(
            "Raw self-energy subdiagram reduction currently supports gauge=feynman only. "
            "Set gauge=feynman in conventions.txt or use a separately reduced longitudinal contribution."
        )
    match = require_single_self_energy_subdiagram(diagram)
    scalarized, reduced = _feynman_gauge_self_energy_numerator(match)
    factors = list(diagram.integrand.factors if isinstance(diagram.integrand, NCProduct) else (diagram.integrand,))
    marker = SelfEnergySubdiagram(match.external_momentum, match.loop_momentum, 1, renormalized)

    new = []
    skip = set(range(match.start_factor, match.end_factor+1)) | {match.photon_factor}
    for j, f in enumerate(factors):
        if j == match.start_factor:
            new.extend([match.repeated_propagator_left, marker, match.repeated_propagator_right])
        if j in skip:
            continue
        new.append(f)
    contracted_integrand = new[0] if len(new) == 1 else NCProduct(*new)
    return SelfEnergySubdiagramReduction(
        match=match,
        scalarized_middle=scalarized,
        feynman_gauge_numerator=reduced,
        reduced_numerator=reduced,
        scalar_denominator=scalarized.denominator,
        contracted_integrand=contracted_integrand,
    )


def contract_self_energy_to_outer_loop(
    diagram: LoopIntegralExpression,
    *,
    outer_prefactor_latex: str | None = None,
    conventions=None,
    renormalized: bool = False,
) -> LoopIntegralExpression:
    """Return the compact one-loop outer diagram after subloop contraction.

    The coupling/normalization convention of Sigma is read from ``conventions``
    (or from the project-level ``conventions.txt`` when omitted).  Supplying
    ``outer_prefactor_latex`` remains supported as an explicit override.
    No interactive prompt is used.
    """
    if outer_prefactor_latex is None:
        if conventions is None:
            from qedcalc.config.conventions import load_conventions
            conventions = load_conventions()
        outer_prefactor_latex = conventions.compact_outer_one_loop_prefactor_latex()
    red = contract_self_energy_subdiagram(diagram, conventions=conventions, renormalized=renormalized)
    remaining_loops = tuple(v for v in diagram.loops if v.name != red.match.loop_momentum.name)
    return LoopIntegralExpression(
        outer_prefactor_latex,
        remaining_loops,
        red.contracted_integrand,
        diagram.dimension,
    )
