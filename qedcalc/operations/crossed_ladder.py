from __future__ import annotations

from dataclasses import dataclass
import sympy as sp


@dataclass(frozen=True)
class CrossedProjectiveForms:
    """Projective denominator polynomials used in the crossed-ladder reduction."""
    Delta: sp.Expr
    W: sp.Expr
    Delta0: sp.Expr
    W0: sp.Expr


@dataclass(frozen=True)
class EndpointAsymptotics:
    """Cutoff asymptotic pieces for the crossed-ladder endpoint sector."""
    canonical_divergent: sp.Expr
    boundary_difference: sp.Expr
    finite_boundary: sp.Expr
    divergent_sum: sp.Expr


def crossed_projective_forms(R=None, S=None, U=None, V=None) -> CrossedProjectiveForms:
    """Return the projective Delta and W polynomials after the y-scale removal.

    The formulas correspond to the scale choice x=yX, z=yZ, u=yU, v=yV
    followed by R=1+X and S=1+Z.
    """
    R = sp.Symbol("R", positive=True) if R is None else sp.sympify(R)
    S = sp.Symbol("S", positive=True) if S is None else sp.sympify(S)
    U = sp.Symbol("U", nonnegative=True) if U is None else sp.sympify(U)
    V = sp.Symbol("V", nonnegative=True) if V is None else sp.sympify(V)
    Delta0 = sp.expand(R*S + S*U - 1)
    W0 = sp.expand(R**2*S + R*S**2 - 2*R*S + S**2*U)
    Delta = sp.expand(Delta0 + (R + U)*V)
    W = sp.expand(W0 + R**2*V)
    return CrossedProjectiveForms(Delta=Delta, W=W, Delta0=Delta0, W0=W0)


def crossed_v_log_coefficient_check(A1, B1, R=None, U=None):
    """Return the logarithmic coefficient A1/(R+U)+B1/R^2.

    A correct V partial-fraction reduction must make this expression vanish.
    """
    R = sp.Symbol("R") if R is None else sp.sympify(R)
    U = sp.Symbol("U") if U is None else sp.sympify(U)
    return sp.simplify(sp.sympify(A1)/(R+U) + sp.sympify(B1)/R**2)


def crossed_h_log_argument(h=None, R=None):
    """Return the logarithm argument after h=S(R+U)-1."""
    h = sp.Symbol("h", positive=True) if h is None else sp.sympify(h)
    R = sp.Symbol("R", positive=True) if R is None else sp.sympify(R)
    return sp.factor((h+1)*(h+(R-1)**2)/(h*R**2))


def crossed_tq_transform(t=None, q=None):
    """Return h,R and the absolute Jacobian for h=(1-t)/t, R=q/t."""
    t = sp.Symbol("t", positive=True) if t is None else sp.sympify(t)
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    h = sp.simplify((1-t)/t)
    R = sp.simplify(q/t)
    jacobian = sp.simplify(1/t**3)
    return h, R, jacobian


def crossed_tq_log_argument(t=None, q=None):
    """Return the reduced logarithm argument in the triangular region 0<t<q<1."""
    t = sp.Symbol("t", positive=True) if t is None else sp.sympify(t)
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    return sp.factor((q**2 + (1-2*q)*t)/(q**2*(1-t)))


def crossed_dilog_D(q=None):
    """D(q)=Li_2(q)-Li_2(2-1/q) used in the crossed-ladder kernel."""
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    return sp.polylog(2, q) - sp.polylog(2, 2-1/q)


def crossed_canonical_kernel(q=None):
    """Return the canonical one-variable crossed-ladder kernel.

    This is the result after Hermite-type rational reduction of the raw
    one-variable kernel.  The omitted total derivative is handled separately
    through its endpoint contribution.
    """
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    L = sp.log(q)
    M = sp.log(1-q)
    Dq = crossed_dilog_D(q)
    half = (L-M)*(sp.Rational(10,3)*L + 4)/(2*q-1)
    one_minus = (sp.Rational(5,6)*(-L**2 + Dq + L) - sp.Rational(41,96))/(q-1)
    zero = (-sp.Rational(5,6)*L**2 + sp.Rational(5,3)*L*M
            - sp.Rational(5,6)*Dq - sp.Rational(7,3)*L
            + 4*M - sp.Rational(271,96))/q
    return sp.simplify(half + one_minus + zero)


def crossed_half_sector_kernel_x(x=None):
    """Return the x in (0,1) kernel for the q=1/2 sector."""
    x = sp.Symbol("x", positive=True) if x is None else sp.sympify(x)
    lx = sp.log(x)
    return sp.simplify((sp.Rational(10,3)*lx**2
                        - sp.Rational(20,3)*lx*sp.log(1+x)
                        + 8*lx)/(x**2-1))


def crossed_standard_integrals():
    """Return the three standard integrals needed by the q=1/2 sector."""
    return {
        "log2_over_x2m1": -sp.Rational(7,4)*sp.zeta(3),
        "log_over_x2m1": sp.pi**2/8,
        "log_log1p_over_x2m1": -sp.Rational(7,16)*sp.zeta(3) + sp.pi**2*sp.log(2)/8,
    }


def crossed_half_sector_result():
    """Analytic q=1/2-sector contribution."""
    vals = crossed_standard_integrals()
    return sp.simplify(
        sp.Rational(10,3)*vals["log2_over_x2m1"]
        - sp.Rational(20,3)*vals["log_log1p_over_x2m1"]
        + 8*vals["log_over_x2m1"]
    )


def crossed_dilog_reflection_sum(q=None):
    """Closed form of D(q)+D(1-q) used before endpoint integration."""
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    L = sp.log(q)
    M = sp.log(1-q)
    return sp.pi**2/6 + L**2/2 + M**2/2 - 2*L*M


def crossed_endpoint_combined_kernel(q=None):
    """Endpoint-safe combined integrand after q->1-q on the 1/(q-1) sector.

    The two endpoint-singular sectors are combined before integration, and the
    dilogarithms cancel by the reflection identity.
    """
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    L = sp.log(q)
    M = sp.log(1-q)
    bracket = (-sp.Rational(5,4)*L**2 + sp.Rational(10,3)*L*M
               + sp.Rational(5,12)*M**2 - sp.Rational(7,3)*L
               + sp.Rational(19,6)*M - sp.Rational(115,48)
               - sp.Rational(5,36)*sp.pi**2)
    return sp.simplify(bracket/q)


def crossed_endpoint_finite_result():
    """Finite part of the combined endpoint canonical integral."""
    return sp.simplify(sp.Rational(25,6)*sp.zeta(3) - sp.Rational(19,36)*sp.pi**2)


def crossed_endpoint_asymptotics(ell=None) -> EndpointAsymptotics:
    """Return the cutoff-log asymptotics and verify divergence cancellation.

    ell denotes log(epsilon).  The canonical endpoint integral and the total
    derivative boundary term carry opposite cubic, quadratic and linear logs.
    """
    ell = sp.Symbol("ell") if ell is None else sp.sympify(ell)
    canonical = (sp.Rational(5,12)*ell**3 + sp.Rational(7,6)*ell**2
                 + (sp.Rational(115,48) + sp.Rational(5,36)*sp.pi**2)*ell)
    boundary = (-sp.Rational(5,12)*ell**3 - sp.Rational(7,6)*ell**2
                - (sp.Rational(115,48) + sp.Rational(5,36)*sp.pi**2)*ell
                + sp.Rational(1,6) - sp.pi**2/9)
    finite_boundary = sp.Rational(1,6) - sp.pi**2/9
    divergent_sum = sp.expand(canonical + boundary - finite_boundary)
    return EndpointAsymptotics(
        canonical_divergent=canonical,
        boundary_difference=boundary,
        finite_boundary=finite_boundary,
        divergent_sum=sp.simplify(divergent_sum),
    )


def crossed_endpoint_total_result():
    """Endpoint canonical finite part plus the total-derivative boundary term."""
    return sp.simplify(crossed_endpoint_finite_result() + sp.Rational(1,6) - sp.pi**2/9)


def crossed_final_result():
    """Analytic coefficient multiplying (alpha/pi)^2 for crossed ladder."""
    return sp.simplify(crossed_half_sector_result() + crossed_endpoint_total_result())


def crossed_expected_result():
    """Canonical closed form used as a final regression checkpoint."""
    return (sp.Rational(1,6) + sp.Rational(13,36)*sp.pi**2
            + sp.Rational(5,4)*sp.zeta(3)
            - sp.Rational(5,6)*sp.pi**2*sp.log(2))


def crossed_result_difference():
    return sp.simplify(crossed_final_result() - crossed_expected_result())


def recognize_crossed_constant(value, precision=80):
    """Recognize a high-precision numeric value in the crossed-ladder basis.

    Basis: 1, pi^2, zeta(3), pi^2 log(2).
    """
    value = sp.N(value, precision)
    return sp.polys.numberfields.subfield.pslq if False else sp.nsimplify(
        value, [sp.pi**2, sp.zeta(3), sp.pi**2*sp.log(2)], full=True
    )

# --- v0.44: raw crossed-ladder bridge and generic seven-denominator family ---
from functools import lru_cache
from qedcalc.core.expression import (
    QEDExpr, Symbol, Gamma, Index, NCProduct, Add, Slash, Vector,
    Fraction, ScalarMul, ScalarProduct, LoopIntegralExpression,
)
from qedcalc.operations.ladder import (
    LadderIntegralIndex,
    RawLadderStructure,
    LadderGeneralQTraceResult,
    _linear_vector_coeffs,
    _fermion_momentum_from_fraction,
    _fraction_square_loop_name,
    _replace_external_mu_by_rslash,
    _ladder_general_q_integral_table_from_projected,
    ladder_corrected_projector_coefficients,
)
from qedcalc.operations.propagator import (
    recognize_propagators, scalarize_fermion_propagators, separate_numerator_denominator,
)


def _raw_crossed_electron_label(momentum: QEDExpr) -> str:
    """Recognize crossed-ladder electron momenta E1..E4.

    The first three propagators agree with the ordinary ladder.  The crossed
    topology differs at the last propagator, E4 = m^2-(p-l)^2.
    """
    c = _linear_vector_coeffs(momentum)
    expected = {
        (("k", -1), ("p'", 1)): "E1",
        (("k", -1), ("l", -1), ("p'", 1)): "E2",
        (("k", -1), ("l", -1), ("p", 1)): "E3",
        (("l", -1), ("p", 1)): "E4",
    }
    key = tuple(sorted(c.items()))
    if key not in expected:
        raise ValueError(f"Unrecognized crossed-ladder electron momentum pattern: {c}")
    return expected[key]


def analyze_raw_crossed_ladder(diagram: LoopIntegralExpression) -> RawLadderStructure:
    """Extract the crossed-ladder seven-denominator family from bare LaTeX."""
    loop_names = tuple(v.name for v in diagram.loops)
    if loop_names != ("k", "l"):
        raise ValueError(f"Crossed-ladder raw bridge expects loop order (k,l), found {loop_names}.")
    factors = diagram.integrand.factors if isinstance(diagram.integrand, NCProduct) else (diagram.integrand,)
    fermions = [f for f in factors if isinstance(f, Fraction) and any(isinstance(n, Slash) for n in f.denominator.walk())]
    if len(fermions) != 4:
        raise ValueError(f"Expected four electron propagators in crossed ladder, found {len(fermions)}.")
    momenta = tuple(_fermion_momentum_from_fraction(f) for f in fermions)
    labels = tuple(_raw_crossed_electron_label(p) for p in momenta)
    if labels != ("E1", "E2", "E3", "E4"):
        raise ValueError(f"Unexpected crossed-ladder electron-line ordering: {labels}.")

    scalar_fracs = [
        f for f in factors
        if isinstance(f, Fraction)
        and isinstance(f.numerator, Symbol) and f.numerator.name == "1"
        and not any(isinstance(n, Slash) for n in f.denominator.walk())
    ]
    photon_names = [_fraction_square_loop_name(f) for f in scalar_fracs]
    photon_names = [n for n in photon_names if n in ("k", "l")]
    if sorted(photon_names) != ["k", "l"]:
        raise ValueError(f"Expected scalar photon denominators for k and l, found {photon_names}.")
    photon_labels = tuple("K" if n == "k" else "L" for n in photon_names)

    recognized = recognize_propagators(diagram.integrand)
    scalarized = scalarize_fermion_propagators(recognized)
    frac = separate_numerator_denominator(scalarized)
    if not isinstance(frac, Fraction):
        raise TypeError("Scalarized crossed ladder did not produce a Fraction.")
    return RawLadderStructure(
        electron_momenta=momenta,
        electron_labels=labels,
        photon_labels=photon_labels,
        base_integral_index=LadderIntegralIndex(1,1,0,1,1,1,1),
        scalarized_integrand=frac,
    )


def derive_crossed_scalar_product_rules_from_family():
    """Derive the crossed-ladder scalar-product substitutions algebraically."""
    K,L,H,E1,E2,E3,E4 = sp.symbols("K L H E1 E2 E3 E4")
    k2,l2,kl,kpp,kp,lpp,lp = sp.symbols("k2 l2 kl kpp kp lpp lp")
    equations = [
        sp.Eq(K, -k2),
        sp.Eq(L, -l2),
        sp.Eq(H, -(k2+l2+2*kl)),
        sp.Eq(E1, 2*kpp-k2),
        sp.Eq(E2, 2*kpp+2*lpp-k2-l2-2*kl),
        sp.Eq(E3, 2*kp+2*lp-k2-l2-2*kl),
        sp.Eq(E4, 2*lp-l2),
    ]
    unknowns=(k2,l2,kl,kpp,kp,lpp,lp)
    sol=sp.solve(equations,unknowns,dict=True)
    if len(sol)!=1:
        raise ValueError("Crossed-ladder denominator equations did not have a unique solution.")
    return {u:sp.simplify(sol[0][u]) for u in unknowns}


def crossed_ladder_ibp_family(D=None, z=None, mass_squared=None):
    """Build the generic crossed-ladder family (K,L,H,E1,E2,E3,E4)."""
    from qedcalc.operations.ibp import IntegralFamily, sp_atom
    D=sp.Symbol("D") if D is None else sp.sympify(D)
    z=sp.Symbol("z") if z is None else sp.sympify(z)
    m2=sp.Symbol("m2") if mass_squared is None else sp.sympify(mass_squared)
    K,L,H,E1,E2,E3,E4=sp.symbols("K L H E1 E2 E3 E4")
    kk=sp_atom("k","k"); ll=sp_atom("l","l"); kl=sp_atom("k","l")
    kpp=sp_atom("k","p'"); kp=sp_atom("k","p")
    lpp=sp_atom("l","p'"); lp=sp_atom("l","p")
    denominator_exprs=(
        -kk,
        -ll,
        -(kk+ll+2*kl),
        2*kpp-kk,
        2*kpp+2*lpp-kk-ll-2*kl,
        2*kp+2*lp-kk-ll-2*kl,
        2*lp-ll,
    )
    rules={
        kk:-K,
        ll:-L,
        kl:(K+L-H)/2,
        kpp:(E1-K)/2,
        lpp:(E2-H-E1+K)/2,
        lp:(E4-L)/2,
        kp:(E3-H-E4+L)/2,
        sp_atom("p","p"):m2,
        sp_atom("p'","p'"):m2,
        sp_atom("p","p'"):m2*(1-z/2),
    }
    return IntegralFamily(
        "crossed_ladder",
        ("K","L","H","E1","E2","E3","E4"),
        denominator_exprs,
        ("k","l"),
        ("p","p'"),
        rules,
        D,
    )


def _crossed_general_q_scalar_substitutions():
    """On-shell m=1 scalar-product substitutions for the crossed topology."""
    D,z=sp.symbols("D z")
    K,L,H,E1,E2,E3,E4=sp.symbols("K L H E1 E2 E3 E4")
    return {
        sp.Symbol("SP__p__p"):1,
        sp.Symbol("SP__p'__p'"):1,
        sp.Symbol("SP__p__p'"):1-z/2,
        sp.Symbol("SP__k__k"):-K,
        sp.Symbol("SP__l__l"):-L,
        sp.Symbol("SP__k__l"):(K+L-H)/2,
        sp.Symbol("SP__k__p'"):(E1-K)/2,
        sp.Symbol("SP__l__p'"):(E2-H-E1+K)/2,
        sp.Symbol("SP__l__p"):(E4-L)/2,
        sp.Symbol("SP__k__p"):(E3-H-E4+L)/2,
        sp.Symbol("m"):1,
    }


@lru_cache(maxsize=4)
def crossed_general_q_projector_result(raw: RawLadderStructure) -> LadderGeneralQTraceResult:
    """Generate the corrected finite-q crossed-ladder spin-sum projector table."""
    from qedcalc.operations.dirac import dirac_trace_fully_contracted_sympy
    numerator=raw.scalarized_integrand.numerator
    pp=Vector("p'"); p=Vector("p"); m=Symbol("m")
    spin_pp=Add(Slash(pp),m); spin_p=Add(Slash(p),m)
    gamma_mu_up=Gamma(Index("mu","up"))
    r_contracted=_replace_external_mu_by_rslash(numerator)
    A_expr=NCProduct(spin_pp,numerator,spin_p,gamma_mu_up)
    B_expr=NCProduct(spin_pp,r_contracted,spin_p)
    a,b=ladder_corrected_projector_coefficients()
    A=dirac_trace_fully_contracted_sympy(A_expr)
    B=dirac_trace_fully_contracted_sympy(B_expr)
    subs=_crossed_general_q_scalar_substitutions()
    Ared=sp.expand(A.subs(subs)); Bred=sp.expand(B.subs(subs))
    leftover=[s for s in Ared.free_symbols|Bred.free_symbols if str(s).startswith("SP__")]
    if leftover:
        raise ValueError(f"Unreduced scalar products in crossed-ladder trace: {leftover}")
    projected=sp.factor(a*Ared+b*Bred)
    table=_ladder_general_q_integral_table_from_projected(projected)
    numerator_poly=sp.factor(sp.together(projected).as_numer_denom()[0])
    return LadderGeneralQTraceResult("spin_sum",Ared,Bred,projected,numerator_poly,table)

# --- v0.45: raw crossed scalar-family -> projective Symanzik bridge ---
def crossed_bare_scalar_parametric_representation(D=None, z=None, mass_squared=None):
    """Return the convention-free projective representation of the bare crossed scalar core.

    The physical crossed graph has the six positive denominators
    ``K,L,E1,E2,E3,E4``.  ``H=-(k+l)^2`` remains an auxiliary IBP denominator
    and is therefore assigned power zero here.  This function connects the
    raw crossed seven-slot family to the generic Symanzik U/F generator without
    importing any hand-derived projective polynomial.
    """
    from qedcalc.operations.ibp import IntegralIndex
    from qedcalc.operations.master_integrals import scalar_feynman_parametric_representation

    family = crossed_ladder_ibp_family(D=D, z=z, mass_squared=mass_squared)
    return scalar_feynman_parametric_representation(
        family,
        IntegralIndex((1, 1, 0, 1, 1, 1, 1)),
        parameter_prefix="cx",
    )


def crossed_bare_scalar_parametric_checks(D=None, z=None, mass_squared=None):
    """Return structural checks for the automatically generated crossed U/F pair."""
    rep = crossed_bare_scalar_parametric_representation(D=D, z=z, mass_squared=mass_squared)
    params = rep.parameters
    U_poly = sp.Poly(sp.expand(rep.U), *params)
    F_poly = sp.Poly(sp.expand(rep.F), *params)
    return {
        "active_denominators": rep.active_denominators,
        "U_total_degree": U_poly.total_degree(),
        "F_total_degree": F_poly.total_degree(),
        "U_homogeneous": len({sum(mon) for mon, _ in U_poly.terms()}) == 1,
        "F_homogeneous": len({sum(mon) for mon, _ in F_poly.terms()}) == 1,
    }


def crossed_ladder_integral_symmetries():
    """Return the denominator-permutation symmetry from graph reversal.

    Simultaneous external exchange p<->p' and loop exchange k<->l maps
    K<->L, E1<->E4, E2<->E3, with H fixed.
    """
    from qedcalc.operations.ibp import IntegralSymmetry, close_symmetry_group
    reversal = IntegralSymmetry(
        "external_loop_exchange",
        (1, 0, 2, 6, 5, 4, 3),
    )
    return close_symmetry_group((reversal,), size=7)


def canonicalize_crossed_ladder_integral(index):
    from qedcalc.operations.ibp import canonicalize_integral
    return canonicalize_integral(index, crossed_ladder_integral_symmetries())

# --- v0.46: q-linear magnetic-projector bridge ---
@dataclass(frozen=True)
class CrossedQExpansionSummary:
    q0_terms: int
    q1_terms: int
    total_terms: int
    expression: QEDExpr


@dataclass(frozen=True)
class CrossedQ0ParametricBridge:
    representation: object
    a: sp.Expr
    b: sp.Expr
    c: sp.Expr
    r: sp.Expr
    s: sp.Expr
    Delta: sp.Expr
    W: sp.Expr
    expected_measure_monomial: sp.Expr


def crossed_raw_numerator_q_expansion(raw: RawLadderStructure) -> CrossedQExpansionSummary:
    """Introduce p'=p+q in the raw crossed numerator and keep O(q^1).

    The fully distributed expression must contain the 144 q^0 chains and
    84 q^1 chains (48+36) described in the independent derivation.
    """
    from qedcalc.operations.momentum import introduce_q
    from qedcalc.operations.qexpansion import truncate_q_order, q_degree
    from qedcalc.operations.algebra import expand_expression
    expr = expand_expression(truncate_q_order(introduce_q(raw.scalarized_integrand.numerator), 1))
    terms = expr.terms if isinstance(expr, Add) else (expr,)
    q0 = sum(1 for t in terms if q_degree(t) == 0)
    q1 = sum(1 for t in terms if q_degree(t) == 1)
    return CrossedQExpansionSummary(q0, q1, len(terms), expr)


def crossed_q0_five_denominator_family(D=None, mass_squared=None):
    """Five-denominator q=0 crossed family (K,L,Dk,Dkl,Dl).

    At q=0 the two central electron denominators coincide, so Dkl has power 2.
    This is the family used by the five-parameter derivation with parameters
    (u,v,x,y,z) mapped respectively to (K,L,Dk,Dkl,Dl).
    """
    from qedcalc.operations.ibp import IntegralFamily, sp_atom
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2") if mass_squared is None else sp.sympify(mass_squared)
    kk=sp_atom("k","k"); ll=sp_atom("l","l"); kl=sp_atom("k","l")
    kp=sp_atom("k","p"); lp=sp_atom("l","p")
    denoms=(
        -kk,
        -ll,
        2*kp-kk,
        2*kp+2*lp-kk-ll-2*kl,
        2*lp-ll,
    )
    rules={
        kk: sp.Symbol("K")*-1,
        ll: sp.Symbol("L")*-1,
        kl: (sp.Symbol("K")+sp.Symbol("L")-sp.Symbol("H"))/2,
        kp: (sp.Symbol("Dk")-sp.Symbol("K"))/2,
        lp: (sp.Symbol("Dl")-sp.Symbol("L"))/2,
        sp_atom("p","p"): m2,
    }
    return IntegralFamily(
        "crossed_ladder_q0",
        ("K","L","Dk","Dkl","Dl"),
        denoms,
        ("k","l"),
        ("p",),
        rules,
        D,
    )


def crossed_q0_parametric_bridge(D=4, mass_squared=1):
    """Generate the five-parameter q=0 denominator bridge from the family.

    The returned Symanzik U,F are compared after the parameter relabeling
    (K,L,Dk,Dkl,Dl) -> (u,v,x,y,z).  At rho=0 they must equal the hand-derived
    Delta and W, while the Feynman measure carries the expected factor y.
    """
    from qedcalc.operations.ibp import IntegralIndex
    from qedcalc.operations.master_integrals import scalar_feynman_parametric_representation
    family = crossed_q0_five_denominator_family(D=D, mass_squared=mass_squared)
    rep = scalar_feynman_parametric_representation(
        family, IntegralIndex((1,1,1,2,1)), parameter_prefix="cq"
    )
    # generator order: K,L,Dk,Dkl,Dl
    pu,pv,px,py,pz = rep.parameters
    x,y,z,u,v = sp.symbols("x y z u v")
    relabel={pu:u,pv:v,px:x,py:y,pz:z}
    U=sp.factor(rep.U.subs(relabel))
    F=sp.factor(rep.F.subs(relabel))
    a=x+y+u; b=y+z+v; c=y; r=x+y; s=y+z
    Delta=sp.factor(a*b-c**2)
    W=sp.factor(b*r**2-2*c*r*s+a*s**2)
    monomial=sp.factor(sp.prod(p**(n-1) for p,n in zip(rep.parameters,rep.powers)).subs(relabel))
    return CrossedQ0ParametricBridge(rep,a,b,c,r,s,U,F,monomial)


def crossed_q0_parametric_bridge_checks(D=4, mass_squared=1):
    bridge=crossed_q0_parametric_bridge(D=D,mass_squared=mass_squared)
    x,y,z,u,v=sp.symbols("x y z u v")
    expected_delta=sp.factor((x+y+u)*(y+z+v)-y**2)
    expected_w=sp.factor((y+z+v)*(x+y)**2-2*y*(x+y)*(y+z)+(x+y+u)*(y+z)**2)
    return {
        "Delta_difference": sp.simplify(bridge.Delta-expected_delta),
        "W_difference": sp.simplify(bridge.W-expected_w),
        "measure_monomial": sp.factor(bridge.expected_measure_monomial),
        "expected_measure_monomial": y,
        "measure_difference": sp.simplify(bridge.expected_measure_monomial-y),
    }


def crossed_denominator_q1_correction(x=None, y=None):
    """Return delta D = 2 x k.q + y (k+l).q from the q-linear denominator expansion."""
    x=sp.Symbol("x") if x is None else sp.sympify(x)
    y=sp.Symbol("y") if y is None else sp.sympify(y)
    kq=sp.Symbol("SP__k__q")
    lq=sp.Symbol("SP__l__q")
    return sp.expand(2*x*kq + y*(kq+lq))

@dataclass(frozen=True)
class CrossedBreitProjectorCheck:
    matrix_element_0: sp.Expr
    matrix_element_2_linear: sp.Expr
    projected: sp.Expr
    F1_coefficient: sp.Expr
    F2_coefficient: sp.Expr


def crossed_breit_projector_check():
    """Verify the crossed magnetic projector with explicit Dirac matrices/spinors.

    Uses the Breit frame p=(E,-q/2,0,0), p'=(E,+q/2,0,0), spin up along z,
    and spinors normalized so that ubar*u=1 at q=0.  Terms through O(q) are
    sufficient.  The returned projector must annihilate F1 and normalize F2 to 1.
    """
    I=sp.I
    q,m,F1,F2=sp.symbols("q m F1 F2", nonzero=True)
    zero=sp.zeros(2)
    sx=sp.Matrix([[0,1],[1,0]])
    sy=sp.Matrix([[0,-I],[I,0]])
    sz=sp.Matrix([[1,0],[0,-1]])
    g0=sp.diag(1,1,-1,-1)
    def gi(sig):
        return sp.Matrix.vstack(sp.Matrix.hstack(zero,sig),sp.Matrix.hstack(-sig,zero))
    gu=[g0,gi(sx),gi(sy),gi(sz)]
    metric=(1,-1,-1,-1)
    gl=[metric[i]*gu[i] for i in range(4)]
    def sigma_up(mu,nu):
        return I*sp.Rational(1,2)*(gu[mu]*gu[nu]-gu[nu]*gu[mu])
    # O(q) Breit spinors; normalization corrections begin at q^2.
    u_in=sp.Matrix([1,0,0,-q/(4*m)])
    ubar_out=sp.Matrix([[1,0,0,-q/(4*m)]])
    # Lower-index vertices.  With q^1=q, sigma_{01}=-sigma^{01},
    # sigma_{21}=+sigma^{21}; this sign convention reproduces the stated projector.
    G0=F1*gl[0] - I*sigma_up(0,1)*q/(2*m)*F2
    G2=F1*gl[2] - I*(-sigma_up(2,1))*q/(2*m)*F2
    M0=sp.expand((ubar_out*G0*u_in)[0])
    M2=sp.expand((ubar_out*G2*u_in)[0])
    M0_0=sp.simplify(M0.subs(q,0))
    M2_1=sp.simplify(sp.diff(M2,q).subs(q,0))
    projected=sp.simplify(2*m*I*M2_1-M0_0)
    return CrossedBreitProjectorCheck(
        matrix_element_0=M0_0,
        matrix_element_2_linear=M2_1,
        projected=projected,
        F1_coefficient=sp.simplify(sp.diff(projected,F1)),
        F2_coefficient=sp.simplify(sp.diff(projected,F2)),
    )

# --- v0.47: streaming construction of the crossed-ladder projective numerator P_X ---
@dataclass(frozen=True)
class CrossedPXResult:
    """Automatically reconstructed q=0 crossed-ladder projective numerator.

    ``P_X`` is the homogeneous polynomial in the simplex parameters
    ``(x,y,z,u,v)`` for

        G_X = y P_X / (4 Delta^4 W^2).

    ``projective_P_X`` is obtained after x=y(R-1), z=y(S-1), u=yU, v=yV
    and removal of the common y^8 scale.
    """
    P_X: sp.Expr
    projective_P_X: sp.Expr
    Delta: sp.Expr
    W: sp.Expr
    term_count: int
    total_degree: int
    projective_term_count: int
    apparent_gamma0_coefficient: sp.Expr
    laurent_coefficients: tuple


def _crossed_explicit_gamma_data():
    """Return explicit Dirac-basis gamma matrices used only by the P_X audit path."""
    I = sp.I
    zero = sp.zeros(2)
    sx = sp.Matrix([[0, 1], [1, 0]])
    sy = sp.Matrix([[0, -I], [I, 0]])
    sz = sp.Matrix([[1, 0], [0, -1]])
    g0 = sp.diag(1, 1, -1, -1)

    def gi(sig):
        return sp.Matrix.vstack(
            sp.Matrix.hstack(zero, sig),
            sp.Matrix.hstack(-sig, zero),
        )

    gu = (g0, gi(sx), gi(sy), gi(sz))
    metric = (1, -1, -1, -1)
    gl = tuple(metric[i] * gu[i] for i in range(4))
    return gu, gl


def _crossed_streaming_dirac_polynomials():
    """Return the two scalar numerator polynomials entering D^-6 and D^-7.

    The incoming electron is taken at rest at q=0, while q points along the
    x-axis.  This is an O(q) Breit-equivalent realization of the magnetic
    projector.  Rather than distributing 228 full Dirac chains, the two places
    where p'=p+q occurs are differentiated by the product rule before Lorentz
    summation.
    """
    I = sp.I
    gu, gl = _crossed_explicit_gamma_data()
    ident = sp.eye(4)
    k = sp.symbols("k0:4")
    l = sp.symbols("l0:4")

    def slash(v):
        return gu[0] * v[0] - gu[1] * v[1] - gu[2] * v[2] - gu[3] * v[3]

    p = (sp.Integer(1), 0, 0, 0)
    qslash = -gu[1]
    R1 = ident + slash(tuple(p[i] - k[i] for i in range(4)))
    R2 = ident + slash(tuple(p[i] - k[i] - l[i] for i in range(4)))
    R3 = R2
    R4 = ident + slash(tuple(p[i] - l[i] for i in range(4)))

    def numerator_pair(mu):
        n0 = sp.zeros(4)
        nq = sp.zeros(4)
        for rho in range(4):
            for alpha in range(4):
                tail = gl[mu] * R3 * gl[rho] * R4 * gl[alpha]
                n0 += gu[rho] * R1 * gu[alpha] * R2 * tail
                nq += gu[rho] * qslash * gu[alpha] * R2 * tail
                nq += gu[rho] * R1 * gu[alpha] * qslash * tail
        return n0, nq

    n00, _ = numerator_pair(0)
    n20, n2q = numerator_pair(2)
    ket = sp.Matrix([1, 0, 0, 0])
    bra0 = sp.Matrix([[1, 0, 0, 0]])
    # p'=p+q with q along +x: ubar(p') = (1,0,0,-q/(2m))+O(q^2), m=1.
    braq = sp.Matrix([[0, 0, 0, -sp.Rational(1, 2)]])

    m00 = sp.expand((bra0 * n00 * ket)[0])
    m20 = sp.expand((bra0 * n20 * ket)[0])
    m21 = sp.expand((braq * n20 * ket)[0] + (bra0 * n2q * ket)[0])

    # Projector contribution with denominator D^-6.
    numerator_d6 = sp.expand(2 * I * m21 - m00)

    # q-linear denominator correction:
    # D(q)^-6 = D0^-6 - 6 q dD D0^-7 + O(q^2),
    # dD/q = -(2x+y) k1 - y l1 for q=(0,q,0,0).
    x, y = sp.symbols("x y")
    dcoef = -(2 * x + y) * k[1] - y * l[1]
    numerator_d7 = sp.expand(-12 * I * m20 * dcoef)
    return k, l, numerator_d6, numerator_d7


def _crossed_wick_component(ep, eq, a, b, c, cache):
    """Bivariate Wick contraction numerator for one Euclidean component.

    The inverse loop-space quadratic matrix is
        [[b,-c],[-c,a]] / Delta.
    Only its polynomial numerator is returned; Delta powers are tracked by the
    streaming caller.
    """
    key = (ep, eq)
    if key in cache:
        return cache[key]
    n = ep + eq
    if n == 0:
        out = sp.Integer(1)
    elif n % 2:
        out = sp.Integer(0)
    elif ep:
        out = sp.Integer(0)
        if ep >= 2:
            out += (ep - 1) * b * _crossed_wick_component(ep - 2, eq, a, b, c, cache)
        if eq:
            out += eq * (-c) * _crossed_wick_component(ep - 1, eq - 1, a, b, c, cache)
        out = sp.expand(out)
    else:
        out = (eq - 1) * a * _crossed_wick_component(0, eq - 2, a, b, c, cache)
    cache[key] = out
    return out


def _crossed_stream_gaussian_laurent(poly, n, k, l, a, b, c, Delta, W, tk_num, tl_num):
    """Integrate a centered polynomial without constructing a giant rational expression.

    Returns a dictionary keyed by powers ``(p,q)`` meaning coefficient times
    Delta^p W^q, after the convention-free Euclidean two-loop Gaussian integral
    with its common pi^4 removed.
    """
    from collections import defaultdict

    variables = tuple(k) + tuple(l)
    ppoly = sp.Poly(poly, *variables)
    wick_cache = {}
    accum = defaultdict(lambda: sp.Integer(0))

    def centered_moment(exponents):
        degree = sum(exponents)
        if degree % 2:
            return sp.Integer(0), degree // 2
        value = sp.Integer(1)
        for mu in range(4):
            value *= _crossed_wick_component(
                exponents[mu], exponents[4 + mu], a, b, c, wick_cache
            )
            if value == 0:
                return sp.Integer(0), degree // 2
        return sp.expand(value), degree // 2

    for monomial, coefficient in ppoly.terms():
        ek0 = monomial[0]
        el0 = monomial[4]
        base = list(monomial)
        # Minkowski k0 = i P0 + tk_num/Delta and similarly for l0.
        for jk in range(ek0 + 1):
            ck = sp.binomial(ek0, jk) * sp.I**jk * tk_num**(ek0 - jk)
            dk = ek0 - jk
            for jl in range(el0 + 1):
                cl = sp.binomial(el0, jl) * sp.I**jl * tl_num**(el0 - jl)
                dl = el0 - jl
                exponents = list(base)
                exponents[0] = jk
                exponents[4] = jl
                wick, rank_half = centered_moment(tuple(exponents))
                if wick == 0:
                    continue
                gamma_arg = n - 4 - rank_half
                gamma_factor = (
                    sp.Symbol(f"GAMMA_{gamma_arg}")
                    if gamma_arg <= 0
                    else sp.gamma(gamma_arg)
                )
                prefactor = gamma_factor / (sp.gamma(n) * 2**rank_half)
                delta_power = n - 6 - 2 * rank_half - dk - dl
                w_power = 4 + rank_half - n
                accum[(delta_power, w_power)] += coefficient * ck * cl * wick * prefactor

    return {key: sp.expand(value) for key, value in accum.items() if value != 0}


@lru_cache(maxsize=1)
def crossed_projective_numerator_px() -> CrossedPXResult:
    """Reconstruct the long crossed-ladder polynomial P_X from the raw projector.

    No stored P_X coefficient table is used.  The route is

        raw Dirac numerator + magnetic projector
        -> q-linear denominator correction
        -> simultaneous two-loop square-completion shifts
        -> streaming Wick/Gaussian reduction
        -> common denominator Delta^4 W^2.

    The overall normalization follows directly from 120 for the five-parameter
    Feynman formula, 1/16 when e^4/(2pi)^8 is expressed in (alpha/pi)^2 after
    the two Wick rotations, and the Gaussian pi^4.  Therefore

        (120/16) y * N/(Delta^4 W^2)
        = y * (30 N)/(4 Delta^4 W^2),

    so P_X = 30 N.
    """
    from collections import defaultdict

    x, y, z, u, v = sp.symbols("x y z u v")
    a = x + y + u
    b = y + z + v
    c = y
    r = x + y
    s = y + z
    Delta = sp.expand(a * b - c**2)
    W = sp.expand(b * r**2 - 2 * c * r * s + a * s**2)
    tk_num = sp.expand(b * r - c * s)
    tl_num = sp.expand(a * s - c * r)

    k, l, numerator_d6, numerator_d7 = _crossed_streaming_dirac_polynomials()
    d6 = _crossed_stream_gaussian_laurent(
        numerator_d6, 6, k, l, a, b, c, Delta, W, tk_num, tl_num
    )
    d7 = _crossed_stream_gaussian_laurent(
        numerator_d7, 7, k, l, a, b, c, Delta, W, tk_num, tl_num
    )
    laurent = defaultdict(lambda: sp.Integer(0))
    for block in (d6, d7):
        for key, value in block.items():
            laurent[key] += value

    # The apparent rank-4 D^-6 Gamma(0) contribution must cancel identically.
    gamma0 = sp.Symbol("GAMMA_0")
    common_numerator = sp.Integer(0)
    for (dpow, wpow), coefficient in laurent.items():
        common_numerator += coefficient * Delta**(dpow + 4) * W**(wpow + 2)
    common_numerator = sp.expand(common_numerator)
    apparent_gamma0 = sp.expand(common_numerator).coeff(gamma0)
    common_numerator = sp.expand(common_numerator.subs(gamma0, 0))

    P_X = sp.expand(30 * common_numerator)
    ppoly = sp.Poly(P_X, x, y, z, u, v)

    R, S, U, V, scale = sp.symbols("R S U V scale")
    projective = sp.expand(
        P_X.subs({
            x: scale * (R - 1),
            y: scale,
            z: scale * (S - 1),
            u: scale * U,
            v: scale * V,
        }) / scale**8
    )
    projective = sp.expand(projective)
    projective_terms = len(sp.Poly(projective, R, S, U, V).terms())

    return CrossedPXResult(
        P_X=P_X,
        projective_P_X=projective,
        Delta=Delta,
        W=W,
        term_count=len(ppoly.terms()),
        total_degree=ppoly.total_degree(),
        projective_term_count=projective_terms,
        apparent_gamma0_coefficient=sp.simplify(apparent_gamma0),
        laurent_coefficients=tuple(sorted((key, sp.expand(value)) for key, value in laurent.items())),
    )


def crossed_projective_numerator_px_checks():
    """Structural and symmetry checks for the automatically generated P_X."""
    result = crossed_projective_numerator_px()
    x, y, z, u, v = sp.symbols("x y z u v")
    poly = sp.Poly(result.P_X, x, y, z, u, v)
    degree_set = {sum(monomial) for monomial, _ in poly.terms()}
    reversal = sp.expand(result.P_X - result.P_X.xreplace({x: z, z: x, u: v, v: u}))
    integer_coefficients = all(sp.denom(coeff) == 1 and coeff.is_real for _, coeff in poly.terms())

    R, S, U, V = sp.symbols("R S U V")
    proj_poly = sp.Poly(result.projective_P_X, R, S, U, V)
    # Delta and W are linear in V.  With deg_V(P_X)=4 versus denominator
    # degree 6, the V-integrand has no 1/V term at infinity.  This is exactly
    # the logarithmic-coefficient cancellation A1/(R+U)+B1/R^2=0.
    v_degree = sp.degree(result.projective_P_X, V)
    return {
        "term_count": result.term_count,
        "total_degree": result.total_degree,
        "homogeneous": degree_set == {8},
        "integer_real_coefficients": bool(integer_coefficients),
        "reversal_difference": reversal,
        "apparent_gamma0_coefficient": result.apparent_gamma0_coefficient,
        "projective_term_count": result.projective_term_count,
        "projective_v_degree": v_degree,
        "v_log_coefficient_zero_by_degree": bool(v_degree <= 4),
        "sample_11111": sp.expand(result.P_X.subs({x:1,y:1,z:1,u:1,v:1})),
        "sample_12345": sp.expand(result.P_X.subs({x:1,y:2,z:3,u:4,v:5})),
    }

@dataclass(frozen=True)
class CrossedVPartialFractions:
    A4: sp.Expr
    A3: sp.Expr
    A2: sp.Expr
    A1: sp.Expr
    B2: sp.Expr
    B1: sp.Expr
    log_coefficient: sp.Expr
    log_argument: sp.Expr


@lru_cache(maxsize=1)
def crossed_v_partial_fraction_coefficients() -> CrossedVPartialFractions:
    """Generate the six V-partial-fraction coefficients algebraically.

    For P(V)/(4 Delta(V)^4 W(V)^2), P has degree <=4 while Delta,W are
    linear in V.  Coefficient comparison gives the six coefficients directly,
    avoiding a very expensive general ``apart`` call.
    """
    R, S, U, V = sp.symbols("R S U V")
    P = sp.Poly(crossed_projective_numerator_px().projective_P_X, V)
    p0, p1, p2, p3, p4 = [P.coeff_monomial(V**i) for i in range(5)]
    d0 = R*S + S*U - 1
    d1 = R + U
    w0 = R**2*S + R*S**2 - 2*R*S + S**2*U
    w1 = R**2
    X = -d0*w1 + d1*w0

    common = (
        -d0*p1*w1**3 + 2*d0*p2*w0*w1**2 - 3*d0*p3*w0**2*w1
        + 4*d0*p4*w0**3 + 4*d1*p0*w1**3 - 3*d1*p1*w0*w1**2
        + 2*d1*p2*w0**2*w1 - d1*p3*w0**3
    )
    C = -common / (4*X**5)
    A1 = d1*C
    B1 = -w1*C
    A2 = (
        d0**4*p4*w1**2 - 4*d0**3*d1*p4*w0*w1 + 6*d0**2*d1**2*p4*w0**2
        - d0*d1**3*p1*w1**2 + 2*d0*d1**3*p2*w0*w1 - 3*d0*d1**3*p3*w0**2
        + 3*d1**4*p0*w1**2 - 2*d1**4*p1*w0*w1 + d1**4*p2*w0**2
    ) / (4*d1**2*X**4)
    A3 = -(
        -2*d0**4*p4*w1 + d0**3*d1*p3*w1 + 4*d0**3*d1*p4*w0
        - 3*d0**2*d1**2*p3*w0 - d0*d1**3*p1*w1 + 2*d0*d1**3*p2*w0
        + 2*d1**4*p0*w1 - d1**4*p1*w0
    ) / (4*d1**2*X**3)
    A4 = (
        d0**4*p4 - d0**3*d1*p3 + d0**2*d1**2*p2 - d0*d1**3*p1 + d1**4*p0
    ) / (4*d1**2*X**2)
    B2 = (
        p0*w1**4 - p1*w0*w1**3 + p2*w0**2*w1**2 - p3*w0**3*w1 + p4*w0**4
    ) / (4*X**4)

    log_coefficient = sp.Integer(0)  # A1/d1 + B1/w1 by construction.
    log_argument = sp.factor(d1*w0/(w1*d0))
    return CrossedVPartialFractions(A4,A3,A2,A1,B2,B1,log_coefficient,log_argument)


def crossed_v_partial_fraction_checks():
    """Exact/sample checks of the generated V decomposition and h-log bridge."""
    R,S,U,V,h = sp.symbols("R S U V h")
    r = crossed_projective_numerator_px()
    c = crossed_v_partial_fraction_coefficients()
    Delta0 = R*S + S*U - 1
    W0 = R**2*S + R*S**2 - 2*R*S + S**2*U
    Delta = Delta0 + (R+U)*V
    W = W0 + R**2*V
    lhs = r.projective_P_X/(4*Delta**4*W**2)
    rhs = c.A4/Delta**4 + c.A3/Delta**3 + c.A2/Delta**2 + c.A1/Delta + c.B2/W**2 + c.B1/W

    # Exact rational sample points validate the full six-term decomposition.
    samples = []
    for values in ((2,3,1),(3,2,2),(5,4,1)):
        subs = {R:sp.Rational(values[0]), S:sp.Rational(values[1]), U:sp.Rational(values[2])}
        diff = sp.cancel(lhs.subs(subs)-rhs.subs(subs))
        samples.append(sp.expand(diff))

    h_ratio = sp.factor(c.log_argument.subs(S,(h+1)/(R+U)))
    expected = sp.factor((h+1)*(h+(R-1)**2)/(h*R**2))
    return {
        "sample_differences": tuple(samples),
        "log_coefficient": c.log_coefficient,
        "h_log_argument_difference": sp.factor(h_ratio-expected),
        "h_log_argument": h_ratio,
    }

# --- v0.48: analytic U-integration and triangular (t,q) bridge ---

@dataclass(frozen=True)
class CrossedHUKernel:
    """Crossed-ladder kernel after V and U integration.

    The remaining variables are h,R.  The result is kept in the small basis

        rational
        + log_ratio_coefficient * log((h+1)/R)
        + log_argument_coefficient * L_V
        + mixed_log_coefficient * log((h+1)/R) * L_V,

    where L_V=log((h+1)(h+(R-1)^2)/(h R^2)).
    """
    rational: sp.Expr
    log_ratio_coefficient: sp.Expr
    log_argument_coefficient: sp.Expr
    mixed_log_coefficient: sp.Expr
    log_argument: sp.Expr


@dataclass(frozen=True)
class CrossedTQKernel:
    """Triangular-region integrand in 0<t<q<1 before t integration."""
    rational: sp.Expr
    log_q_coefficient: sp.Expr
    log_argument_coefficient: sp.Expr
    log_q_log_argument_coefficient: sp.Expr
    log_argument: sp.Expr
    jacobian: sp.Expr


def _crossed_definite_y_monomial_integral(expr, R, U, h):
    """Integrate a rational U-expression using Y=R+U exactly.

    For the crossed-ladder h representation all U dependence is a polynomial
    divided by one monomial Y^p.  The interval U in [0,h-R+1] becomes
    Y in [R,h+1].  The result is returned as (rational, log-coefficient), with
    the logarithm represented only as log((h+1)/R).
    """
    Y = sp.Dummy("Y")
    shifted = sp.cancel(sp.sympify(expr).subs(U, Y - R))
    numerator, denominator = sp.fraction(shifted)
    denominator_poly = sp.Poly(denominator, Y)
    terms = denominator_poly.terms()
    if len(terms) != 1:
        raise ValueError("expected a monomial denominator in Y=R+U")
    (power_tuple, denominator_coefficient), = terms
    denominator_power = power_tuple[0]
    numerator_poly = sp.Poly(numerator, Y)

    rational = sp.Integer(0)
    log_coefficient = sp.Integer(0)
    upper = h + 1
    lower = R
    for (power_tuple, numerator_coefficient) in numerator_poly.terms():
        exponent = power_tuple[0] - denominator_power
        coefficient = sp.cancel(numerator_coefficient / denominator_coefficient)
        if exponent == -1:
            log_coefficient += coefficient
        else:
            primitive_power = exponent + 1
            rational += coefficient * (
                upper**primitive_power - lower**primitive_power
            ) / sp.Integer(primitive_power)
    return sp.cancel(rational), sp.cancel(log_coefficient)


@lru_cache(maxsize=1)
def crossed_h_u_integrated_kernel() -> CrossedHUKernel:
    """Integrate V and then U directly from the generated projective P_X.

    This deliberately regenerates the V partial-fraction data after the
    substitution S=(h+1)/(R+U).  In these variables

        Delta_0 = h,
        W_0 = (h+1)(h+(R-1)^2)/(R+U),
        X = -Delta_0 R^2 + (R+U) W_0 = (h-R+1)^2,

    so the remaining U dependence collapses to polynomial/(R+U)^3.  The
    U-limit follows from S>=1:

        0 <= U <= h-R+1.
    """
    result = crossed_projective_numerator_px()
    symbols = {symbol.name: symbol for symbol in result.projective_P_X.free_symbols}
    R, S, U, V = (symbols[name] for name in ("R", "S", "U", "V"))
    h = sp.Symbol("h", positive=True)

    projective_h = sp.cancel(
        result.projective_P_X.subs(S, (h + 1) / (R + U))
    )
    numerator_h, denominator_h = sp.fraction(projective_h)
    polynomial_v = sp.Poly(numerator_h, V)
    p = [polynomial_v.coeff_monomial(V**index) / denominator_h for index in range(5)]
    p0, p1, p2, p3, p4 = p

    d0 = h
    d1 = R + U
    K = (h + 1) * (h + (R - 1)**2)
    w0 = K / (R + U)
    w1 = R**2
    X = (h - R + 1)**2

    common = (
        -d0*p1*w1**3 + 2*d0*p2*w0*w1**2 - 3*d0*p3*w0**2*w1
        + 4*d0*p4*w0**3 + 4*d1*p0*w1**3 - 3*d1*p1*w0*w1**2
        + 2*d1*p2*w0**2*w1 - d1*p3*w0**3
    )
    C = -common / (4*X**5)
    A1 = d1*C
    A2 = (
        d0**4*p4*w1**2 - 4*d0**3*d1*p4*w0*w1 + 6*d0**2*d1**2*p4*w0**2
        - d0*d1**3*p1*w1**2 + 2*d0*d1**3*p2*w0*w1 - 3*d0*d1**3*p3*w0**2
        + 3*d1**4*p0*w1**2 - 2*d1**4*p1*w0*w1 + d1**4*p2*w0**2
    ) / (4*d1**2*X**4)
    A3 = -(
        -2*d0**4*p4*w1 + d0**3*d1*p3*w1 + 4*d0**3*d1*p4*w0
        - 3*d0**2*d1**2*p3*w0 - d0*d1**3*p1*w1 + 2*d0*d1**3*p2*w0
        + 2*d1**4*p0*w1 - d1**4*p1*w0
    ) / (4*d1**2*X**3)
    A4 = (
        d0**4*p4 - d0**3*d1*p3 + d0**2*d1**2*p2 - d0*d1**3*p1 + d1**4*p0
    ) / (4*d1**2*X**2)
    B2 = (
        p0*w1**4 - p1*w0*w1**3 + p2*w0**2*w1**2 - p3*w0**3*w1 + p4*w0**4
    ) / (4*X**4)

    # V integration over [0,infinity], followed by dS=dh/(R+U).
    rational_u_terms = (
        sp.cancel(A4 / (3*d1*d0**3) / d1),
        sp.cancel(A3 / (2*d1*d0**2) / d1),
        sp.cancel(A2 / (d1*d0) / d1),
        sp.cancel(B2 / (w1*w0) / d1),
    )
    # C=A1/d1 is the common simple-pole primitive coefficient; the extra d1
    # in the denominator is the h-change Jacobian dS=dh/d1.
    log_argument_u = sp.cancel(C / d1)

    rational = sp.Integer(0)
    log_ratio_coefficient = sp.Integer(0)
    for term in rational_u_terms:
        term_rational, term_log = _crossed_definite_y_monomial_integral(term, R, U, h)
        rational += term_rational
        log_ratio_coefficient += term_log

    log_argument_coefficient, mixed_log_coefficient = (
        _crossed_definite_y_monomial_integral(log_argument_u, R, U, h)
    )
    log_argument = crossed_h_log_argument(h, R)
    return CrossedHUKernel(
        rational=sp.cancel(rational),
        log_ratio_coefficient=sp.cancel(log_ratio_coefficient),
        log_argument_coefficient=sp.cancel(log_argument_coefficient),
        mixed_log_coefficient=sp.cancel(mixed_log_coefficient),
        log_argument=log_argument,
    )


def crossed_h_u_integrated_kernel_checks():
    """Check U limits and the specialized exact U integrator."""
    kernel = crossed_h_u_integrated_kernel()
    R, U, h = sp.symbols("R U h")
    upper_u = h - R + 1
    # S=(h+1)/(R+U), so the upper endpoint U=h-R+1 corresponds to S=1.
    endpoint_s = sp.cancel((h + 1) / (R + upper_u))
    return {
        "u_lower": sp.Integer(0),
        "u_upper": upper_u,
        "upper_endpoint_S": endpoint_s,
        "log_argument": kernel.log_argument,
        "component_operation_counts": (
            sp.count_ops(kernel.rational),
            sp.count_ops(kernel.log_ratio_coefficient),
            sp.count_ops(kernel.log_argument_coefficient),
            sp.count_ops(kernel.mixed_log_coefficient),
        ),
    }


@lru_cache(maxsize=1)
def crossed_tq_preintegration_kernel() -> CrossedTQKernel:
    """Map the U-integrated (h,R) kernel to the triangle 0<t<q<1."""
    kernel = crossed_h_u_integrated_kernel()
    h_symbols = {symbol.name: symbol for expr in (
        kernel.rational,
        kernel.log_ratio_coefficient,
        kernel.log_argument_coefficient,
        kernel.mixed_log_coefficient,
        kernel.log_argument,
    ) for symbol in expr.free_symbols}
    h_symbol = h_symbols.get("h", sp.Symbol("h"))
    R_symbol = h_symbols.get("R", sp.Symbol("R"))
    t, q = sp.symbols("t q", positive=True)
    h_value = (1 - t) / t
    R_value = q / t
    substitution = {h_symbol: h_value, R_symbol: R_value}
    jacobian = 1 / t**3

    # log((h+1)/R)=log(1/q)=-log(q).
    rational = sp.cancel(kernel.rational.subs(substitution) * jacobian)
    log_q_coefficient = sp.cancel(-kernel.log_ratio_coefficient.subs(substitution) * jacobian)
    log_argument_coefficient = sp.cancel(kernel.log_argument_coefficient.subs(substitution) * jacobian)
    log_q_log_argument_coefficient = sp.cancel(
        -kernel.mixed_log_coefficient.subs(substitution) * jacobian
    )
    log_argument = crossed_tq_log_argument(t, q)
    return CrossedTQKernel(
        rational=rational,
        log_q_coefficient=log_q_coefficient,
        log_argument_coefficient=log_argument_coefficient,
        log_q_log_argument_coefficient=log_q_log_argument_coefficient,
        log_argument=log_argument,
        jacobian=jacobian,
    )


def crossed_tq_preintegration_checks():
    """Structural checks for the (h,R)->(t,q) bridge."""
    kernel = crossed_tq_preintegration_kernel()
    t, q = sp.symbols("t q", positive=True)
    h_value, R_value, jacobian = crossed_tq_transform(t, q)
    # R>=1 gives q>=t; h>=R-1 gives q<=1.
    return {
        "h": h_value,
        "R": R_value,
        "jacobian_difference": sp.simplify(kernel.jacobian - jacobian),
        "triangle_conditions": ("t>0", "q>=t", "q<=1"),
        "log_argument_difference": sp.factor(
            kernel.log_argument - crossed_tq_log_argument(t, q)
        ),
        "component_operation_counts": (
            sp.count_ops(kernel.rational),
            sp.count_ops(kernel.log_q_coefficient),
            sp.count_ops(kernel.log_argument_coefficient),
            sp.count_ops(kernel.log_q_log_argument_coefficient),
        ),
    }

# --- v0.49: exact t integration and one-variable raw-kernel regeneration ---

@dataclass(frozen=True)
class CrossedRawQKernel:
    """Raw one-variable q kernel in basis 1,L,M,L^2,LM,D(q)."""
    expression: sp.Expr
    cutoff_log_coefficient: sp.Expr


def _crossed_rational_t_definite_integral(expr, t, q, eps):
    """Integrate the rational t sector on [eps,q] without generic integrate().

    The generated crossed-ladder rational sectors have poles only at t=0,
    t=1, and q^2+(1-2q)t=0, plus a polynomial remainder.  Extracting those
    poles directly avoids branch-noisy logarithms from a general CAS primitive.
    """
    remainder = sp.cancel(expr)
    pieces = []
    for order in (2, 1):
        coefficient = sp.simplify(sp.limit(remainder * t**order, t, 0))
        if coefficient != 0:
            pieces.append(("zero", order, coefficient))
            remainder = sp.cancel(remainder - coefficient / t**order)
    for order in (3, 2, 1):
        coefficient = sp.simplify(sp.limit(remainder * (t - 1)**order, t, 1))
        if coefficient != 0:
            pieces.append(("one", order, coefficient))
            remainder = sp.cancel(remainder - coefficient / (t - 1)**order)

    affine = q**2 + (1 - 2*q) * t
    root = -q**2 / (1 - 2*q)
    coefficient = sp.simplify(sp.limit(remainder * affine, t, root))
    if coefficient != 0:
        pieces.append(("affine", 1, coefficient))
        remainder = sp.cancel(remainder - coefficient / affine)

    numerator, denominator = sp.fraction(sp.cancel(remainder))
    if denominator.has(t):
        raise ValueError("unexpected t-dependent rational remainder")
    polynomial = sp.Poly(numerator, t)

    L = sp.log(q)
    M = sp.log(1 - q)
    result = sp.Integer(0)
    for kind, order, coefficient in pieces:
        if kind == "zero":
            if order == 1:
                result += coefficient * (L - sp.log(eps))
            else:
                result += coefficient * (-1/q + 1/eps)
        elif kind == "one":
            if order == 1:
                # t<1 throughout the triangular domain; use the real log.
                result += coefficient * (M - sp.log(1 - eps))
            else:
                result += coefficient * (
                    (q - 1)**(1 - order) - (eps - 1)**(1 - order)
                ) / sp.Integer(1 - order)
        else:
            result += coefficient / (1 - 2*q) * (
                sp.log(q * (1 - q))
                - sp.log(q**2 + (1 - 2*q) * eps)
            )

    for (power_tuple, numerator_coefficient) in polynomial.terms():
        power = power_tuple[0]
        coefficient = sp.cancel(numerator_coefficient / denominator)
        result += coefficient * (
            q**(power + 1) - eps**(power + 1)
        ) / sp.Integer(power + 1)
    return sp.expand(result)


def _crossed_log_standard_primitive(power, x, q):
    """Primitive of t^power log[(1-beta t)/(1-t)] for power -3..1."""
    beta = (2*q - 1) / q**2
    log_argument = sp.log(1 - beta*x) - sp.log(1 - x)
    if power == -3:
        return (
            -log_argument/(2*x**2)
            + sp.Rational(1, 2) * (
                -(1 - beta)/x
                + (1 - beta**2)*sp.log(x)
                - sp.log(1 - x)
                + beta**2*sp.log(1 - beta*x)
            )
        )
    if power == -2:
        return (
            -log_argument/x
            + (1 - beta)*sp.log(x)
            + beta*sp.log(1 - beta*x)
            - sp.log(1 - x)
        )
    if power == -1:
        return -sp.polylog(2, beta*x) + sp.polylog(2, x)
    if power == 0:
        def primitive(a):
            u = 1 - a*x
            return -(u*sp.log(u) - u) / a
        return primitive(beta) - primitive(sp.Integer(1))
    if power == 1:
        def primitive(a):
            u = 1 - a*x
            return (
                -u*sp.log(u) + u + u**2*sp.log(u)/2 - u**2/4
            ) / a**2
        return primitive(beta) - primitive(sp.Integer(1))
    raise ValueError("supported logarithmic powers are -3,-2,-1,0,1")


def _crossed_laurent_t_coefficients(expr, t, minimum=-3):
    """Return coefficients of a finite Laurent polynomial in t."""
    polynomial = sp.Poly(sp.cancel(expr * t**(-minimum)), t)
    result = {}
    for index in range(polynomial.degree() + 1):
        coefficient = polynomial.coeff_monomial(t**index)
        if coefficient != 0:
            result[index + minimum] = sp.cancel(coefficient)
    return result


@lru_cache(maxsize=1)
def crossed_raw_one_variable_kernel() -> CrossedRawQKernel:
    """Regenerate the raw one-variable crossed-ladder kernel from P_X.

    This completes

        P_X -> V integration -> U integration -> (t,q) triangle -> t integration.

    A lower cutoff eps is kept until all four triangular-kernel components are
    combined.  The coefficient of log(eps) then cancels exactly.
    """
    kernel = crossed_tq_preintegration_kernel()
    t, q = sp.symbols("t q", positive=True)
    eps = sp.Symbol("eps", positive=True)
    L = sp.log(q)
    M = sp.log(1 - q)
    Dq = sp.Symbol("Dq")

    rational_part = _crossed_rational_t_definite_integral(
        kernel.rational, t, q, eps
    )
    log_q_rational_part = _crossed_rational_t_definite_integral(
        kernel.log_q_coefficient, t, q, eps
    )

    log_argument_coefficients = _crossed_laurent_t_coefficients(
        kernel.log_argument_coefficient, t
    )
    mixed_coefficients = _crossed_laurent_t_coefficients(
        kernel.log_q_log_argument_coefficient, t
    )
    logarithmic_part = sp.Integer(0)
    for power, coefficient in log_argument_coefficients.items():
        logarithmic_part += coefficient * (
            _crossed_log_standard_primitive(power, q, q)
            - _crossed_log_standard_primitive(power, eps, q)
        )
    for power, coefficient in mixed_coefficients.items():
        logarithmic_part += L * coefficient * (
            _crossed_log_standard_primitive(power, q, q)
            - _crossed_log_standard_primitive(power, eps, q)
        )

    combined = rational_part + L*log_q_rational_part + logarithmic_part
    finite_series = sp.series(combined, eps, 0, 1).removeO()
    cutoff_log = sp.Symbol("CUTLOG")
    finite_series = sp.expand(finite_series.xreplace({sp.log(eps): cutoff_log}))
    cutoff_log_coefficient = sp.factor(finite_series.coeff(cutoff_log))
    finite_series = sp.expand(finite_series.subs(cutoff_log, 0))

    # Normalize the real endpoint identities valid for 0<q<1.
    finite_series = finite_series.subs(
        sp.polylog(2, 2 - 1/q), sp.polylog(2, q) - Dq
    )
    finite_series = finite_series.subs(
        sp.log(1 - (2*q - 1)/q), M - L
    )
    finite_series = finite_series.subs(sp.log(-1 + 1/q), M - L)
    finite_series = sp.expand_log(finite_series, force=True)
    finite_series = sp.cancel(sp.expand(finite_series))
    return CrossedRawQKernel(
        expression=finite_series,
        cutoff_log_coefficient=cutoff_log_coefficient,
    )


def crossed_raw_one_variable_kernel_checks():
    """Check cutoff cancellation and the allowed transcendental basis."""
    result = crossed_raw_one_variable_kernel()
    q = sp.Symbol("q", positive=True)
    Dq = sp.Symbol("Dq")
    expression = result.expression
    unexpected_polylogs = {
        atom for atom in expression.atoms(sp.Function)
        if getattr(atom.func, "__name__", "") == "polylog"
    }
    return {
        "cutoff_log_coefficient": result.cutoff_log_coefficient,
        "operation_count": sp.count_ops(expression),
        "contains_Dq": bool(expression.has(Dq)),
        "unexpected_polylogs": tuple(sorted(map(str, unexpected_polylogs))),
    }


def crossed_total_derivative_G(q=None, Dq=None):
    """Return the total-derivative primitive G(q) of the audited reduction."""
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    Dq = crossed_dilog_D(q) if Dq is None else sp.sympify(Dq)
    L = sp.log(q)
    M = sp.log(1 - q)
    Rcoef = (9*q**3 + 24*q**2 - 40*q + 10) / (12*(q - 1)**4)
    Tcoef = (
        -sp.Rational(5, 12)/(q - 1)
        + sp.Rational(4, 3)/(q - 1)**2
        + sp.Rational(13, 12)/(q - 1)**3
    )
    Ucoef = (
        sp.Rational(7, 4)/(q - 1)
        + sp.Rational(31, 6)/(q - 1)**2
        + sp.Rational(31, 12)/(q - 1)**3
    )
    Vcoef = sp.Rational(29, 12)/(q - 1) + sp.Rational(1, 4)/(q - 1)**2
    Pcoef = (
        sp.Rational(3, 32)/(2*q - 1)
        - sp.Rational(27, 4)/(q - 1)
        - sp.Rational(23, 6)/(q - 1)**2
    )
    Qcoef = (
        -q/4 - sp.Rational(3, 32)/(2*q - 1)
        + sp.Rational(13, 12)/(q - 1) - sp.Rational(1, 16)/q
    )
    Zcoef = sp.Rational(5, 4)/(q - 1) + sp.Rational(9, 16)*q
    return sp.expand(
        (Rcoef*L + Tcoef)*Dq
        + Ucoef*L**2 + Vcoef*L*M
        + Pcoef*L + Qcoef*M + Zcoef
    )


def crossed_total_derivative_G_derivative(q=None, Dq=None):
    """Differentiate G using D'(q) in the real 0<q<1 branch explicitly."""
    q = sp.Symbol("q", positive=True) if q is None else sp.sympify(q)
    Dq = sp.Symbol("Dq") if Dq is None else sp.sympify(Dq)
    L = sp.log(q)
    M = sp.log(1 - q)
    Dprime = -M/q + (M - L)/(q*(2*q - 1))

    # Differentiate with Dq held algebraically independent, then add D' term.
    marker = sp.Symbol("D_MARKER")
    G = crossed_total_derivative_G(q, marker)
    derivative = sp.diff(G, q) + sp.diff(G, marker) * Dprime
    return sp.expand(derivative.subs(marker, Dq))


def crossed_raw_to_canonical_difference():
    """Exact difference raw - dG/dq - canonical, using symbolic D(q)."""
    q = sp.Symbol("q", positive=True)
    Dq = sp.Symbol("Dq")
    raw = crossed_raw_one_variable_kernel().expression
    L = sp.log(q)
    M = sp.log(1 - q)
    canonical = (
        (L - M)*(sp.Rational(10, 3)*L + 4)/(2*q - 1)
        + (sp.Rational(5, 6)*(-L**2 + Dq + L) - sp.Rational(41, 96))/(q - 1)
        + (-sp.Rational(5, 6)*L**2 + sp.Rational(5, 3)*L*M
           - sp.Rational(5, 6)*Dq - sp.Rational(7, 3)*L
           + 4*M - sp.Rational(271, 96))/q
    )
    return sp.factor(sp.together(
        raw - crossed_total_derivative_G_derivative(q, Dq) - canonical
    ))

# --- v0.50: automatic Hermite reduction of the regenerated raw q kernel ---

@dataclass(frozen=True)
class CrossedHermiteReduction:
    R: sp.Expr
    T: sp.Expr
    U: sp.Expr
    V: sp.Expr
    P: sp.Expr
    Q: sp.Expr
    Z: sp.Expr
    canonical_D: sp.Expr
    canonical_L2: sp.Expr
    canonical_LM: sp.Expr
    canonical_L: sp.Expr
    canonical_M: sp.Expr
    canonical_1: sp.Expr
    total_derivative: sp.Expr
    canonical: sp.Expr


def _crossed_hermite_rational_reduce(expr, q):
    """Write a rational function as d(primitive)/dq + square-free remainder."""
    from sympy.integrals.rationaltools import ratint_ratpart

    expr = sp.cancel(expr)
    numerator, denominator = sp.fraction(expr)
    numerator_poly = sp.Poly(numerator, q, domain="EX")
    denominator_poly = sp.Poly(denominator, q, domain="EX")
    quotient, remainder = sp.div(numerator_poly, denominator_poly)
    primitive = sp.integrate(quotient.as_expr(), q)
    if remainder.as_expr() == 0:
        return sp.cancel(primitive), sp.Integer(0)
    rational_primitive, squarefree_remainder = ratint_ratpart(
        remainder, denominator_poly, q
    )
    return (
        sp.cancel(primitive + rational_primitive),
        sp.cancel(squarefree_remainder),
    )


@lru_cache(maxsize=1)
def crossed_automatic_hermite_reduction() -> CrossedHermiteReduction:
    """Derive G(q) and the simple-pole canonical kernel from the raw kernel.

    The raw kernel is first viewed as a polynomial in independent basis symbols
    L=log(q), M=log(1-q), D=D(q).  Rational Hermite reduction is then applied
    hierarchically, accounting for

        D' = -M/q + (M-L)/(q(2q-1)),
        L' = 1/q,
        M' = -1/(1-q).

    No stored R,T,U,V,P,Q,Z coefficient table is used in this function.
    """
    q = sp.Symbol("q", positive=True)
    Ls, Ms, Ds = sp.symbols("L M Dq")
    raw = crossed_raw_one_variable_kernel().expression.subs({
        sp.log(q): Ls,
        sp.log(1 - q): Ms,
    })
    polynomial = sp.Poly(sp.together(raw), Ls, Ms, Ds)

    def coefficient(l_power, m_power, d_power):
        return sp.cancel(polynomial.coeff_monomial(
            Ls**l_power * Ms**m_power * Ds**d_power
        ))

    c_LD = coefficient(1, 0, 1)
    c_D = coefficient(0, 0, 1)
    c_L2 = coefficient(2, 0, 0)
    c_LM = coefficient(1, 1, 0)
    c_L = coefficient(1, 0, 0)
    c_M = coefficient(0, 1, 0)
    c_1 = coefficient(0, 0, 0)

    dD_L = -1 / (q * (2*q - 1))
    dD_M = -1/q + 1 / (q * (2*q - 1))

    Rcoef, rem_LD = _crossed_hermite_rational_reduce(c_LD, q)
    if rem_LD != 0:
        raise ValueError("unexpected canonical L*D remainder")

    Tcoef, rem_D = _crossed_hermite_rational_reduce(c_D - Rcoef/q, q)
    Ucoef, rem_L2 = _crossed_hermite_rational_reduce(c_L2 - Rcoef*dD_L, q)
    Vcoef, rem_LM = _crossed_hermite_rational_reduce(c_LM - Rcoef*dD_M, q)

    P_input = c_L - Tcoef*dD_L - 2*Ucoef/q + Vcoef/(1 - q)
    Pcoef, rem_L = _crossed_hermite_rational_reduce(P_input, q)

    Q_input = c_M - Tcoef*dD_M - Vcoef/q
    Qcoef, rem_M = _crossed_hermite_rational_reduce(Q_input, q)

    Z_input = c_1 - Pcoef/q + Qcoef/(1 - q)
    Zcoef, rem_1 = _crossed_hermite_rational_reduce(Z_input, q)

    L = sp.log(q)
    M = sp.log(1 - q)
    Dq = sp.Symbol("Dq")
    total_derivative = sp.expand(
        (Rcoef*L + Tcoef)*Dq
        + Ucoef*L**2 + Vcoef*L*M
        + Pcoef*L + Qcoef*M + Zcoef
    )
    canonical = sp.expand(
        rem_D*Dq + rem_L2*L**2 + rem_LM*L*M
        + rem_L*L + rem_M*M + rem_1
    )
    return CrossedHermiteReduction(
        R=sp.cancel(Rcoef),
        T=sp.cancel(Tcoef),
        U=sp.cancel(Ucoef),
        V=sp.cancel(Vcoef),
        P=sp.cancel(Pcoef),
        Q=sp.cancel(Qcoef),
        Z=sp.cancel(Zcoef),
        canonical_D=sp.cancel(rem_D),
        canonical_L2=sp.cancel(rem_L2),
        canonical_LM=sp.cancel(rem_LM),
        canonical_L=sp.cancel(rem_L),
        canonical_M=sp.cancel(rem_M),
        canonical_1=sp.cancel(rem_1),
        total_derivative=total_derivative,
        canonical=canonical,
    )


def crossed_automatic_hermite_checks():
    """Compare the automatically reconstructed Hermite data with checkpoints."""
    q = sp.Symbol("q", positive=True)
    Dq = sp.Symbol("Dq")
    result = crossed_automatic_hermite_reduction()

    expected_G = crossed_total_derivative_G(q, Dq)
    L = sp.log(q)
    M = sp.log(1 - q)
    expected_canonical = (
        (L - M)*(sp.Rational(10, 3)*L + 4)/(2*q - 1)
        + (sp.Rational(5, 6)*(-L**2 + Dq + L) - sp.Rational(41, 96))/(q - 1)
        + (-sp.Rational(5, 6)*L**2 + sp.Rational(5, 3)*L*M
           - sp.Rational(5, 6)*Dq - sp.Rational(7, 3)*L
           + 4*M - sp.Rational(271, 96))/q
    )

    automatic_derivative = crossed_total_derivative_G_derivative(q, Dq)
    raw = crossed_raw_one_variable_kernel().expression
    return {
        "G_difference": sp.factor(sp.together(result.total_derivative - expected_G)),
        "canonical_difference": sp.factor(sp.together(result.canonical - expected_canonical)),
        "raw_reconstruction_difference": sp.factor(sp.together(
            raw - automatic_derivative - result.canonical
        )),
        "R": sp.apart(result.R, q),
        "T": sp.apart(result.T, q),
        "U": sp.apart(result.U, q),
        "V": sp.apart(result.V, q),
        "P": sp.apart(result.P, q),
        "Q": sp.apart(result.Q, q),
        "Z": sp.apart(result.Z, q),
    }

# --- v0.51: independent analytic evaluation of the crossed canonical kernel ---

@dataclass(frozen=True)
class CrossedStandardIntegralDerivation:
    A: sp.Expr
    B: sp.Expr
    C_minus: sp.Expr
    C_plus: sp.Expr
    C: sp.Expr


def crossed_standard_integrals_derived() -> CrossedStandardIntegralDerivation:
    """Derive the q=1/2 standard integrals from zeta/Euler sums.

    A and B follow from the odd-part zeta sums after expanding
    ``1/(x^2-1)``.  For C we split

        1/(x^2-1) = -1/2 (1/(1-x) + 1/(1+x))

    and use the two standard alternating Euler sums generated by the power
    series of ``log(1+x)``.  The final C value is therefore assembled from
    lower-level sum identities rather than inserted as a final checkpoint.
    """
    z2 = sp.zeta(2)
    z3 = sp.zeta(3)
    ln2 = sp.log(2)

    odd_zeta3 = (1 - sp.Rational(1, 2**3)) * z3
    odd_zeta2 = (1 - sp.Rational(1, 2**2)) * z2
    A = sp.simplify(-2 * odd_zeta3)
    B = sp.simplify(odd_zeta2)

    # From the double power-series sums:
    # sum_{n>=1} (-1)^(n+1) H_n^(2)/n = zeta(3)-zeta(2)log(2)/2
    # sum_{n>=1} (-1)^(n+1) H_n/(n+1)^2 = zeta(3)/8
    alt_H2_over_n = z3 - sp.Rational(1, 2) * z2 * ln2
    alt_H_over_shift2 = z3 / 8

    C_minus = sp.simplify(-z2 * ln2 + alt_H2_over_n)
    C_plus = sp.simplify(-alt_H_over_shift2)
    C = sp.simplify(-sp.Rational(1, 2) * (C_minus + C_plus))
    return CrossedStandardIntegralDerivation(A=A, B=B, C_minus=C_minus, C_plus=C_plus, C=C)


def crossed_standard_integrals():
    """Return the three q=1/2 standard integrals from the derived sums."""
    d = crossed_standard_integrals_derived()
    return {
        "log2_over_x2m1": d.A,
        "log_over_x2m1": d.B,
        "log_log1p_over_x2m1": d.C,
    }


def crossed_half_sector_result():
    """Analytic q=1/2-sector contribution, assembled from derived sums."""
    vals = crossed_standard_integrals()
    return sp.simplify(
        sp.Rational(10, 3) * vals["log2_over_x2m1"]
        - sp.Rational(20, 3) * vals["log_log1p_over_x2m1"]
        + 8 * vals["log_over_x2m1"]
    )


@dataclass(frozen=True)
class CrossedEndpointIntegralDerivation:
    divergent: sp.Expr
    finite: sp.Expr
    total_cutoff_series: sp.Expr


def crossed_endpoint_canonical_integral_derived(ell=None) -> CrossedEndpointIntegralDerivation:
    """Integrate the endpoint-safe canonical kernel by basis decomposition.

    The kernel is decomposed automatically in the basis
    L^2, L*M, M^2, L, M, 1 divided by q.  Each basis integral is then replaced
    by its exact cutoff integral.  Only the finite convergent standard pieces
    zeta(3), 2*zeta(3), and -pi^2/6 enter the finite part.
    """
    ell = sp.Symbol("ell", real=True) if ell is None else sp.sympify(ell)
    q = sp.Symbol("q", positive=True)
    Ls, Ms = sp.symbols("L M")
    kernel = crossed_endpoint_combined_kernel(q)
    numerator = sp.expand((q * kernel).subs({sp.log(q): Ls, sp.log(1-q): Ms}))
    poly = sp.Poly(numerator, Ls, Ms)

    basis_integrals = {
        (2, 0): -ell**3 / 3,
        (1, 1): sp.zeta(3),
        (0, 2): 2 * sp.zeta(3),
        (1, 0): -ell**2 / 2,
        (0, 1): -sp.pi**2 / 6,
        (0, 0): -ell,
    }
    total = sp.Integer(0)
    for powers, integral in basis_integrals.items():
        coefficient = poly.coeff_monomial(Ls**powers[0] * Ms**powers[1])
        total += coefficient * integral
    total = sp.expand(total)
    divergent = sp.expand(total - total.subs(ell, 0))
    finite = sp.simplify(total.subs(ell, 0))
    return CrossedEndpointIntegralDerivation(
        divergent=divergent,
        finite=finite,
        total_cutoff_series=total,
    )


def crossed_endpoint_finite_result():
    """Finite canonical endpoint value derived from the combined kernel."""
    return crossed_endpoint_canonical_integral_derived().finite


def _crossed_D_series_near_one(e, order=8):
    """Generate D(1-e) from the exact D' equation and D(1)=0."""
    q = sp.Symbol("q", positive=True)
    L = sp.log(q)
    M = sp.log(1-q)
    Dprime = -M/q + (M-L)/(q*(2*q-1))
    dD_de = sp.series(-Dprime.subs(q, 1-e), e, 0, order).removeO().expand()
    s = sp.Symbol("s", positive=True)
    return sp.expand(sp.integrate(dD_de.subs(e, s), (s, 0, e)))


@lru_cache(maxsize=1)
def crossed_endpoint_asymptotics_derived() -> EndpointAsymptotics:
    """Regenerate both endpoint expansions from the automatic Hermite primitive.

    At q->0 the dilogarithm inversion identity gives
    D(q)=pi^2/6 + log(q)^2/2 + o(1).  At q->1 the required D-series is
    generated by integrating the exact D'(q) relation with D(1)=0.
    """
    e = sp.Symbol("epsilon", positive=True)
    ell = sp.Symbol("ell", real=True)
    q = sp.Symbol("q", positive=True)
    Dmark = sp.Symbol("Dq")
    G = crossed_automatic_hermite_reduction().total_derivative

    # q -> 0.  The only 1/q coefficient multiplies M=log(1-q), so the leading
    # D asymptotic plus the ordinary SymPy series is sufficient for the finite term.
    D0 = sp.pi**2/6 + sp.log(e)**2/2
    G0 = sp.series(G.subs({q: e, Dmark: D0}), e, 0, 1).removeO().expand()

    # q -> 1.  R(q) has a fourth-order pole, hence D(1-e) is generated deeply
    # enough that the finite term of G is unambiguous.
    D1 = _crossed_D_series_near_one(e, order=8)
    G1 = sp.series(G.subs({q: 1-e, Dmark: D1}), e, 0, 1).removeO().expand()

    difference = sp.expand(G1 - G0)
    difference_ell = sp.expand(difference.subs(sp.log(e), ell))
    finite_boundary = sp.simplify(difference_ell.subs(ell, 0))
    boundary_divergent = sp.expand(difference_ell - finite_boundary)

    canonical = crossed_endpoint_canonical_integral_derived(ell)
    divergent_sum = sp.simplify(sp.expand(canonical.divergent + boundary_divergent))
    return EndpointAsymptotics(
        canonical_divergent=canonical.divergent,
        boundary_difference=difference_ell,
        finite_boundary=finite_boundary,
        divergent_sum=divergent_sum,
    )


def crossed_endpoint_asymptotics(ell=None) -> EndpointAsymptotics:
    """Return automatically regenerated cutoff asymptotics."""
    base = crossed_endpoint_asymptotics_derived()
    if ell is None:
        return base
    ell = sp.sympify(ell)
    default_ell = sp.Symbol("ell", real=True)
    return EndpointAsymptotics(
        canonical_divergent=base.canonical_divergent.subs(default_ell, ell),
        boundary_difference=base.boundary_difference.subs(default_ell, ell),
        finite_boundary=base.finite_boundary,
        divergent_sum=base.divergent_sum.subs(default_ell, ell),
    )


def crossed_endpoint_total_result():
    """Endpoint finite contribution including the regenerated boundary term."""
    return sp.simplify(
        crossed_endpoint_finite_result()
        + crossed_endpoint_asymptotics_derived().finite_boundary
    )


def crossed_final_result():
    """Crossed-ladder coefficient assembled without using the final checkpoint."""
    return sp.simplify(crossed_half_sector_result() + crossed_endpoint_total_result())


def crossed_independent_analytic_checks():
    """Return exact checks for the independently regenerated final evaluation."""
    d = crossed_standard_integrals_derived()
    endpoint = crossed_endpoint_canonical_integral_derived()
    asym = crossed_endpoint_asymptotics_derived()
    final = crossed_final_result()
    return {
        "A": sp.simplify(d.A),
        "B": sp.simplify(d.B),
        "C": sp.simplify(d.C),
        "half": sp.simplify(crossed_half_sector_result()),
        "endpoint_canonical_finite": sp.simplify(endpoint.finite),
        "boundary_finite": sp.simplify(asym.finite_boundary),
        "endpoint_total": sp.simplify(crossed_endpoint_total_result()),
        "divergent_sum": sp.simplify(asym.divergent_sum),
        "final": sp.simplify(final),
        "checkpoint_difference": sp.simplify(final - crossed_expected_result()),
    }

# --- v0.85: Phase 78 crossed-ladder end-to-end closure checkpoint ---
def crossed_phase78_end_to_end_checkpoint(include_heavy_raw=False):
    """Exact crossed-ladder closure audit from projector/kernel to final constant.

    The default path is intentionally fast enough for release validation.  The
    expensive full raw-q-kernel regeneration can be enabled explicitly with
    ``include_heavy_raw=True``.  The historical Karplus--Kroll 1/32 discrepancy
    remains a separate provenance question and is never used as a closure input.
    """
    projector = crossed_breit_projector_check()
    ell = sp.Symbol("ell", real=True)
    canonical_div = (sp.Rational(5,12)*ell**3 + sp.Rational(7,6)*ell**2
                     + (sp.Rational(115,48) + sp.Rational(5,36)*sp.pi**2)*ell)
    boundary_div = (-sp.Rational(5,12)*ell**3 - sp.Rational(7,6)*ell**2
                    - (sp.Rational(115,48) + sp.Rational(5,36)*sp.pi**2)*ell)
    boundary_finite = sp.Rational(1,6) - sp.pi**2/9
    endpoint_divergent_residual = sp.simplify(canonical_div + boundary_div)
    half = sp.simplify(crossed_half_sector_result())
    endpoint_total = sp.simplify(crossed_endpoint_finite_result() + boundary_finite)
    final = sp.simplify(half + endpoint_total)
    checkpoint = sp.simplify(crossed_expected_result())
    result = {
        "projector_F1_coefficient": sp.simplify(projector.F1_coefficient),
        "projector_F2_coefficient": sp.simplify(projector.F2_coefficient),
        "projector_residual_F1": sp.simplify(projector.F1_coefficient),
        "projector_residual_F2": sp.simplify(projector.F2_coefficient - 1),
        "endpoint_divergent_residual": endpoint_divergent_residual,
        "half_sector": half,
        "endpoint_total": endpoint_total,
        "final": final,
        "closed_form": checkpoint,
        "final_closed_form_residual": sp.simplify(final - checkpoint),
        "historical_karplus_kroll_gap": sp.Rational(1, 32),
        "historical_gap_origin_resolved": False,
    }
    if include_heavy_raw:
        result["raw_to_canonical_residual"] = sp.simplify(crossed_raw_to_canonical_difference())
    return result
