from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import csv
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex,
    IntegralFamily,
    factorized_one_denominator_per_loop,
    factorized_euclidean_scalar_value,
    _loop_quadratic_matrix,
    sp_atom,
)
from qedcalc.operations.ladder import ordinary_ladder_ibp_family


@dataclass(frozen=True)
class ParametricRepresentation:
    """Convention-free Feynman-parameter representation of a scalar family integral.

    The representation assumes positive denominator powers and uses the
    projective simplex sum(x_i)=1.  Overall i factors, Wick-rotation signs,
    (2*pi)^D normalization, and renormalization-scale factors are deliberately
    excluded and belong to the convention layer.
    """
    index: IntegralIndex
    active_denominators: tuple[str, ...]
    powers: tuple[int, ...]
    parameters: tuple[sp.Symbol, ...]
    U: sp.Expr
    F: sp.Expr
    delta: sp.Expr
    prefactor: sp.Expr
    integrand: sp.Expr
    loop_count: int
    total_power: int


@dataclass(frozen=True)
class BasisIntegralClassification:
    basis_index: int
    index: IntegralIndex
    kind: str
    factorized_value: sp.Expr | None = None
    parametric: ParametricRepresentation | None = None


def _external_dot(family: IntegralFamily, a: str, b: str) -> sp.Expr:
    key = sp_atom(a, b)
    if key in family.scalar_product_rules:
        return sp.sympify(family.scalar_product_rules[key])
    if a == b:
        return key
    return sp_atom(a, b)


def _combined_quadratic_data(
    family: IntegralFamily,
    index: IntegralIndex | Sequence[int],
    parameter_prefix: str = "x",
):
    idx = family.validate_index(index)
    if any(n < 0 for n in idx.powers):
        raise ValueError("Parametric representation currently requires non-negative denominator powers.")
    active = [i for i, n in enumerate(idx.powers) if n > 0]
    if not active:
        raise ValueError("At least one positive denominator is required.")
    xs = sp.symbols(" ".join(f"{parameter_prefix}{j+1}" for j in range(len(active))))
    if len(active) == 1:
        xs = (xs,)
    S = sp.expand(sum(x * family.denominator_exprs[i] for x, i in zip(xs, active)))
    loops = family.loop_momenta
    externals = family.external_momenta
    L = len(loops)

    # S = - l^T A l + 2 l^T B.  _loop_quadratic_matrix extracts Q in l^T Q l.
    # Build Q directly from the combined expression, then A=-Q.
    Q = sp.zeros(L, L)
    for i, li in enumerate(loops):
        Q[i, i] = sp.expand(S).coeff(sp_atom(li, li))
        for j in range(i + 1, L):
            lj = loops[j]
            c = sp.expand(S).coeff(sp_atom(li, lj))
            Q[i, j] = sp.simplify(c / 2)
            Q[j, i] = Q[i, j]
    A = -Q

    # B_i is an external-vector linear combination.  The coefficient of
    # li·p in S is 2 * coeff(B_i,p).
    Bcoeff = []
    for li in loops:
        row = {}
        for p in externals:
            c = sp.expand(S).coeff(sp_atom(li, p))
            if c != 0:
                row[p] = sp.simplify(c / 2)
        Bcoeff.append(row)

    U = sp.factor(A.det())
    if sp.simplify(U) == 0:
        raise ValueError("Combined quadratic form is singular for this active sector.")
    Ainv = sp.simplify(A.inv())
    delta = sp.Integer(0)
    for i in range(L):
        for j in range(L):
            bij = sp.Integer(0)
            for pa, ca in Bcoeff[i].items():
                for pb, cb in Bcoeff[j].items():
                    bij += ca * cb * _external_dot(family, pa, pb)
            delta += Ainv[i, j] * bij
    delta = sp.factor(sp.cancel(delta))
    F = sp.factor(sp.cancel(U * delta))
    return idx, tuple(active), tuple(xs), sp.factor(U), F, delta


def scalar_feynman_parametric_representation(
    family: IntegralFamily,
    index: IntegralIndex | Sequence[int],
    parameter_prefix: str = "x",
) -> ParametricRepresentation:
    r"""Return the standard projective scalar Feynman-parameter representation.

    For nu=sum n_i and L loops,

      I = pi^(LD/2) Gamma(nu-LD/2)/prod Gamma(n_i)
          int_simplex prod x_i^(n_i-1)
          U^(nu-(L+1)D/2) / F^(nu-LD/2).

    The formula is convention-free with respect to Minkowski i factors and
    loop-measure normalizations.  It is intended as the analytic/numerical
    entry point for master-integral evaluation.
    """
    idx, active, xs, U, F, delta = _combined_quadratic_data(
        family, index, parameter_prefix=parameter_prefix
    )
    powers = tuple(idx.powers[i] for i in active)
    nu = int(sum(powers))
    L = len(family.loop_momenta)
    D = sp.sympify(family.dimension_symbol)
    pref = sp.pi ** (sp.Rational(L, 2) * D) * sp.gamma(nu - sp.Rational(L, 2) * D)
    for n in powers:
        pref /= sp.gamma(n)
    monomial = sp.prod(x ** (n - 1) for x, n in zip(xs, powers))
    integrand = sp.factor(
        monomial
        * U ** (nu - sp.Rational(L + 1, 2) * D)
        / F ** (nu - sp.Rational(L, 2) * D)
    )
    return ParametricRepresentation(
        index=idx,
        active_denominators=tuple(family.denominator_names[i] for i in active),
        powers=powers,
        parameters=xs,
        U=U,
        F=F,
        delta=delta,
        prefactor=sp.factor(pref),
        integrand=integrand,
        loop_count=L,
        total_power=nu,
    )


def ordinary_ladder_terminal_basis() -> tuple[IntegralIndex, ...]:
    """The v0.41 corrected ordinary-ladder 12-terminal basis ordering."""
    rows = (
        (0,0,0,0,0,1,1),
        (0,0,0,0,1,0,1),
        (0,0,0,0,1,1,1),
        (0,0,0,0,2,0,3),
        (0,0,0,1,1,1,1),
        (0,1,0,0,1,0,1),
        (0,1,0,0,1,0,2),
        (0,1,1,0,0,0,1),
        (0,1,1,0,1,0,1),
        (0,1,1,1,0,0,1),
        (0,1,1,1,0,1,1),
        (0,1,1,1,1,0,2),
    )
    return tuple(IntegralIndex(r) for r in rows)


def classify_ordinary_ladder_terminal_basis(D=None, z=None, mass_squared=None):
    """Classify and prepare evaluation data for all 12 v0.41 terminal integrals."""
    family = ordinary_ladder_ibp_family(D=D, z=z, mass_squared=mass_squared)
    m2 = sp.Symbol("m2") if mass_squared is None else sp.sympify(mass_squared)
    out = []
    for i, idx in enumerate(ordinary_ladder_terminal_basis()):
        fac = factorized_one_denominator_per_loop(family, idx)
        if fac is not None:
            value = factorized_euclidean_scalar_value(fac, dimension=family.dimension_symbol, delta=m2)
            kind = "factorized_lower"
            param = scalar_feynman_parametric_representation(family, idx, parameter_prefix=f"b{i+1}x")
            out.append(BasisIntegralClassification(i, idx, kind, sp.factor(value), param))
        else:
            param = scalar_feynman_parametric_representation(family, idx, parameter_prefix=f"b{i+1}x")
            out.append(BasisIntegralClassification(i, idx, "genuine_two_loop_candidate", None, param))
    return tuple(out)


def factorized_ladder_basis_epsilon_series(epsilon=None, mass_squared=None, order=0):
    """Laurent-series values for the three factorized ordinary-ladder basis integrals.

    Uses D=4-2 epsilon and returns convention-free Euclidean expressions.
    """
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    data = classify_ordinary_ladder_terminal_basis(D=4-2*eps, z=sp.Symbol("z"), mass_squared=m2)
    out = {}
    for entry in data:
        if entry.kind != "factorized_lower":
            continue
        out[entry.basis_index] = sp.series(entry.factorized_value, eps, 0, int(order)+1)
    return out


def write_ladder_basis_classification_csv(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["basis_index","index","kind","active_denominators","U","F","delta","factorized_value"])
        for r in rows:
            p = r.parametric
            w.writerow([
                r.basis_index,
                str(r.index.powers),
                r.kind,
                ";".join(p.active_denominators) if p else "",
                str(p.U) if p else "",
                str(p.F) if p else "",
                str(p.delta) if p else "",
                str(r.factorized_value) if r.factorized_value is not None else "",
            ])
    return path

@dataclass(frozen=True)
class BasisZ0Evaluation:
    basis_index: int
    index: IntegralIndex
    status: str
    method: str
    value: sp.Expr | None


def massive_tadpole_euclidean(power, D=None, mass_squared=None):
    """Convention-free Euclidean massive one-loop tadpole integral."""
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    n = sp.sympify(power)
    return sp.factor(sp.pi**(D/2) * m2**(D/2-n) * sp.gamma(n-D/2) / sp.gamma(n))


def one_massless_two_massive_vacuum_euclidean(a, b, c, D=None, mass_squared=None):
    r"""Two-loop vacuum with one massless and two equal-mass denominators.

    Convention-free Euclidean form of

      int d^D l d^D r /
          [(l^2)^a ((r-l)^2+m^2)^b (r^2+m^2)^c].

    The result follows by Schwinger parameters, integrating the massless-line
    parameter first and then the common massive scale.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    a,b,c = map(sp.sympify, (a,b,c))
    return sp.factor(
        sp.pi**D * m2**(D-a-b-c)
        * sp.gamma(D/2-a)
        * sp.gamma(a+b-D/2)
        * sp.gamma(a+c-D/2)
        * sp.gamma(a+b+c-D)
        / (
            sp.gamma(D/2)
            * sp.gamma(b)
            * sp.gamma(c)
            * sp.gamma(2*a+b+c-D)
        )
    )


def massless_bubble_on_shell_electron_euclidean(electron_power, D=None, mass_squared=None):
    r"""Massless bubble followed by an on-shell massive electron denominator.

    Evaluates the ordinary-ladder subtopology with L and H to unit power and
    E4 to ``electron_power`` at p^2=m^2.  The l bubble is integrated first;
    the remaining k integral is a generalized one-loop on-shell integral.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    b = sp.sympify(electron_power)
    bubble = (
        sp.pi**(D/2)
        * sp.gamma(2-D/2)
        * sp.gamma(D/2-1)**2
        / sp.gamma(D-2)
    )
    a = 2-D/2
    outer = (
        sp.pi**(D/2)
        * m2**(D/2-a-b)
        * sp.gamma(a+b-D/2)
        * sp.gamma(D-2*a-b)
        / (sp.gamma(b) * sp.gamma(D-a-b))
    )
    return sp.factor(bubble * outer)


def massless_two_point_then_on_shell_electron_euclidean(a, b, electron_power, D=None, mass_squared=None):
    r"""Massless two-point subloop followed by an on-shell electron line.

    Convention-free Euclidean value of the reduced z=0 ladder lower sector

      int d^Dq d^Dk /[(q^2)^a ((q-k)^2)^b E(k)^n],

    with p^2=m^2 and E(k) the on-shell electron denominator.  The q loop is
    integrated first and the remaining generalized on-shell one-loop integral
    is evaluated in Gamma functions.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    a, b, n = map(sp.sympify, (a, b, electron_power))
    alpha = a + b - D/2
    bubble = (
        sp.pi**(D/2)
        * sp.gamma(alpha)
        * sp.gamma(D/2-a)
        * sp.gamma(D/2-b)
        / (sp.gamma(a)*sp.gamma(b)*sp.gamma(D-a-b))
    )
    outer = (
        sp.pi**(D/2)
        * m2**(D/2-alpha-n)
        * sp.gamma(alpha+n-D/2)
        * sp.gamma(D-2*alpha-n)
        / (sp.gamma(n)*sp.gamma(D-alpha-n))
    )
    return sp.factor(bubble*outer)


def ordinary_ladder_T1_z0_euclidean(D=None, mass_squared=None):
    r"""Exact z=0 value of the remaining four-denominator ladder master T1.

    T1 = int d^Dk d^Dl / (L H E2 E4).

    Write D=4-2 epsilon.  Cheng--Wu gauge x_E2+x_E4=1 followed by the two
    massless-parameter integrations reduces the projective integral to a
    one-dimensional Gauss-hypergeometric form.  Both resulting 3F2(1)
    functions contain a cancellable upper/lower parameter and reduce to 2F1(1);
    Gauss' theorem then gives the Gamma-only expression implemented here.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    eps = sp.simplify(2-D/2)
    term1 = (
        (sp.gamma(eps)**2/sp.gamma(2*eps))
        * sp.gamma(2-eps)
        * sp.gamma(1-2*eps)
        / (sp.gamma(1-eps)*sp.gamma(2-2*eps))
    )
    term2 = (
        (sp.gamma(eps)*sp.gamma(1-eps))
        * sp.gamma(2-eps)
        * sp.gamma(2-4*eps)
        / (sp.gamma(2-3*eps)*sp.gamma(2-2*eps))
    )
    parameter_integral = sp.factor((term1-term2)/((1-eps)*(1-2*eps)))
    return sp.factor(sp.pi**D * sp.gamma(4-D) * m2**(D-4) * parameter_integral)


def ordinary_ladder_T2_z0_euclidean(D=None, mass_squared=None):
    """Exact z=0 T2=1/(L H E2 E4^2), reduced by the dedicated z=0 IBP."""
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    T1 = ordinary_ladder_T1_z0_euclidean(D, m2)
    lower = massless_two_point_then_on_shell_electron_euclidean(1, 2, 1, D, m2)
    return sp.factor(-(D-3)*T1/(2*m2) - lower/(2*m2))


def ordinary_ladder_T3_z0_euclidean(D=None, mass_squared=None):
    """Exact z=0 T3=1/(L H E2 E4^3), reduced by the dedicated z=0 IBP."""
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    T1 = ordinary_ladder_T1_z0_euclidean(D, m2)
    lower_121 = massless_two_point_then_on_shell_electron_euclidean(1, 2, 1, D, m2)
    lower_122 = massless_two_point_then_on_shell_electron_euclidean(2, 1, 2, D, m2)
    return sp.factor(
        (D-6)*(D-4)*(D-3)*T1/(8*m2**2*(D-5))
        + (D-4)**2*lower_121/(2*m2**2*(D-5))
        + (D-4)*lower_122/(4*m2*(D-5))
    )


def ordinary_ladder_basis_z0_evaluations(D=None, mass_squared=None):
    """Analytic z=0 values currently known for the 12 terminal basis integrals.

    Values are convention-free Euclidean integrals.  All twelve basis integrals
    are closed analytically.  The former basis-8 master is reduced by Cheng--Wu
    plus Gauss hypergeometric summation; basis 10 and 11 reduce to basis 8 and
    Gamma-function lower sectors through the dedicated z=0 IBP family.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    basis = ordinary_ladder_terminal_basis()
    T = lambda n: massive_tadpole_euclidean(n, D=D, mass_squared=m2)
    vals: dict[int, tuple[str, str, sp.Expr | None]] = {
        0: ("exact", "factorized_tadpoles_T1xT1", sp.factor(T(1)*T(1))),
        1: ("exact", "factorized_tadpoles_T1xT1", sp.factor(T(1)*T(1))),
        2: ("exact", "z0_degenerate_factorization_T2xT1", sp.factor(T(2)*T(1))),
        3: ("exact", "factorized_tadpoles_T2xT3", sp.factor(T(2)*T(3))),
        4: ("exact", "z0_degenerate_factorization_T2xT2", sp.factor(T(2)*T(2))),
        5: ("exact", "one_massless_two_massive_vacuum_111", one_massless_two_massive_vacuum_euclidean(1,1,1,D,m2)),
        6: ("exact", "one_massless_two_massive_vacuum_112", one_massless_two_massive_vacuum_euclidean(1,1,2,D,m2)),
        7: ("exact", "massless_bubble_then_on_shell_E4", massless_bubble_on_shell_electron_euclidean(1,D,m2)),
        8: ("exact", "cheng_wu_hypergeometric_to_gamma_T1", ordinary_ladder_T1_z0_euclidean(D,m2)),
        9: ("exact", "z0_E1_equals_E4_massless_bubble_E4_squared", massless_bubble_on_shell_electron_euclidean(2,D,m2)),
        10: ("exact", "z0_reduced_T2_to_T1_and_lower", ordinary_ladder_T2_z0_euclidean(D,m2)),
        11: ("exact", "z0_reduced_T3_to_T1_and_lower", ordinary_ladder_T3_z0_euclidean(D,m2)),
    }
    return tuple(BasisZ0Evaluation(i, basis[i], *vals[i]) for i in range(12))


def ordinary_ladder_basis_z0_epsilon_series(epsilon=None, mass_squared=None, order=0):
    """Laurent-expand all twelve exact z=0 basis values around D=4-2 epsilon."""
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    out = {}
    for item in ordinary_ladder_basis_z0_evaluations(D=4-2*eps, mass_squared=m2):
        if item.value is not None:
            out[item.basis_index] = sp.series(item.value, eps, 0, int(order)+1)
    return out


def write_ladder_basis_z0_evaluation_csv(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["basis_index","index","status","method","value"])
        for r in rows:
            w.writerow([r.basis_index, str(r.index.powers), r.status, r.method, "" if r.value is None else str(sp.factor(r.value))])
    return path


def ordinary_ladder_z0_reduced_ibp_family(D=None, mass_squared=None):
    """Five-denominator z=0 ladder family (K,L,H,E2,E4).

    At q^2=0 one has p'=p, E1=E4 and E3=E2.  K is retained only as an
    auxiliary denominator so that all scalar products generated by IBP close
    linearly in the reduced family.
    """
    from qedcalc.operations.ibp import IntegralFamily, sp_atom
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2") if mass_squared is None else sp.sympify(mass_squared)
    K,L,H,E2,E4 = sp.symbols("K L H E2 E4")
    kk=sp_atom("k","k"); ll=sp_atom("l","l"); kl=sp_atom("k","l")
    kp=sp_atom("k","p"); lp=sp_atom("l","p")
    denominators=(
        -kk,
        -ll,
        -(kk+ll+2*kl),
        2*kp+2*lp-kk-ll-2*kl,
        2*kp-kk,
    )
    rules={
        kk:-K,
        ll:-L,
        kl:(K+L-H)/2,
        kp:(E4-K)/2,
        lp:(E2-H-E4+K)/2,
        sp_atom("p","p"):m2,
    }
    return IntegralFamily(
        "ordinary_ladder_z0_reduced",
        ("K","L","H","E2","E4"),
        denominators,
        ("k","l"),
        ("p",),
        rules,
        D,
    )


def ordinary_ladder_z0_T_ibp_reductions(D=None, mass_squared=None):
    """Regenerate the symbolic z=0 IBP reductions of T2 and T3.

    T1=(0,1,1,1,1), T2=(0,1,1,1,2), T3=(0,1,1,1,3) in the reduced
    (K,L,H,E2,E4) family.  T1 is protected; degree-1 seeds are sufficient to
    pivot both T2 and T3.  The returned mappings are symbolic in D and m^2.
    """
    from qedcalc.operations.ibp import (
        IntegralIndex, bounded_seed_domain, generate_ibp_system,
        laporta_forward_eliminate, reduce_integral,
    )
    family=ordinary_ladder_z0_reduced_ibp_family(D=D,mass_squared=mass_squared)
    T1=IntegralIndex((0,1,1,1,1))
    T2=IntegralIndex((0,1,1,1,2))
    T3=IntegralIndex((0,1,1,1,3))
    seeds=bounded_seed_domain(T1,max_extra_degree=1,include_numerator_slots=True)
    equations=generate_ibp_system(family,seeds)
    rules=laporta_forward_eliminate(equations,protected=(T1,))
    return {
        "family": family,
        "T1": T1,
        "T2": T2,
        "T3": T3,
        "rules": rules,
        "T2_reduction": dict(reduce_integral(T2,rules)),
        "T3_reduction": dict(reduce_integral(T3,rules)),
    }


def ordinary_ladder_z0_lower_sector_value(index, D=None, mass_squared=None):
    """Evaluate lower sectors appearing in the reduced z=0 T-family IBP.

    The index ordering is (K,L,H,E2,E4).  For K=0 and E4=0, the change of
    variables q=k+l leaves the k integration with only a single massless L
    denominator, hence the integral is scaleless and vanishes.  For E2=0 and
    E4>0, the q subloop is a standard massless two-point function followed by
    a generalized on-shell electron integral.
    """
    from qedcalc.operations.ibp import IntegralIndex
    idx=index if isinstance(index,IntegralIndex) else IntegralIndex(index)
    if len(idx.powers)!=5:
        raise ValueError("Reduced z=0 lower-sector index must have five powers (K,L,H,E2,E4).")
    nK,nL,nH,nE2,nE4=idx.powers
    if nK==0 and nE4==0 and nL>0:
        return sp.Integer(0)
    if nK==0 and nE2==0 and nL>0 and nH>0 and nE4>0:
        return massless_two_point_then_on_shell_electron_euclidean(nH,nL,nE4,D,mass_squared)
    return None


def one_massless_two_massive_vacuum_z_derivative_euclidean(electron_power, D=None, mass_squared=None):
    r"""First z derivative at z=0 of ladder basis (L,E2,E4^b).

    This evaluates

      d/dz J(0,1,0,0,1,0,b) |_{z=0}

    in the convention-free Euclidean normalization used by the master-integral
    layer.  The derivation starts from the projective representation.  At z=0,

      F = m^2 U (x_E2 + x_E4),
      dF/dz = -m^2 x_L x_E2 x_E4.

    With x_E2+x_E4=s and x_E2=s t, the s integral collapses by
    2F1(c,a;c;u)=(1-u)^(-a), leaving a beta integral in t.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    b = sp.sympify(electron_power)
    return sp.factor(
        sp.pi**D
        * m2**(D-b-2)
        * sp.gamma(3-D/2)
        * sp.gamma(b+2-D/2)
        / (
            sp.gamma(b)
            * (b+4-D)
            * (b+3-D)
            * (D/2-1)
            * (D/2)
        )
    )



def ordinary_ladder_basis8_z_derivative_shifted_reduction(D=None, mass_squared=None):
    r"""Exact first z derivative of terminal basis 8 at z=0.

    For basis 8, J_D(0,1,1,0,1,0,1), differentiating the projective
    representation inserts x_L x_E2 x_E4 and raises the power of F by one.
    This is exactly a dimensional shift:

        dJ_D/dz|_0 = (m^2/pi^2) J_{D+2}(0,2,1,0,2,0,2)|_0.

    The shifted integral is reduced in the five-denominator z=0 family
    (K,L,H,E2,E4) to T1 plus lower sectors.  The rational coefficients were
    reconstructed from exact-rational Laporta probes and independently
    validated away from the reconstruction grid.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Symbol("m2", positive=True) if mass_squared is None else sp.sympify(mass_squared)
    d = sp.expand(D + 2)

    c_a = -((d-4)*(d-3)*(5*d**2-51*d+128))/(16*(d-6)*(d-5)*(2*d-9))
    c_b = -((d-4)*(9*d**3-151*d**2+834*d-1516))/(8*(d-7)*(d-6)*(d-5)*(2*d-9))
    c_c = -((d-4)*(14*d**4-297*d**3+2332*d**2-8037*d+10268))/(16*(d-7)*(d-6)*(d-5)*(2*d-9))
    c_t = -((d-4)*(d-3)*(d**2-12*d+37))/(8*(d-7)*(d-5))

    # Shifted-family lower sectors at dimension d=D+2.  Their coefficient
    # powers of m^2 follow from dimensional homogeneity relative to the
    # shifted target (total denominator power 7).
    A = massless_two_point_then_on_shell_electron_euclidean(2,1,1,d,m2)  # (0,1,2,0,1)
    B = massless_two_point_then_on_shell_electron_euclidean(2,1,2,d,m2)  # (0,1,2,0,2)
    C = massless_two_point_then_on_shell_electron_euclidean(1,2,1,d,m2)  # (0,2,1,0,1)
    T1 = ordinary_ladder_T1_z0_euclidean(d,m2)

    shifted = sp.factor(c_a*A/m2**3 + c_b*B/m2**2 + c_c*C/m2**3 + c_t*T1/m2**3)
    return sp.factor(m2*shifted/sp.pi**2)

def ordinary_ladder_basis_z_derivative_evaluations(D=None, mass_squared=None):
    """Classify/evaluate first z derivatives of the 12 terminal basis integrals.

    Exact zero derivatives are returned for basis 0,1,3 (factorized and
    z-independent) and basis 7 (its projective F polynomial is z-independent).
    Basis 5 and 6 use the analytic three-denominator formula above.  Basis 8
    is mapped exactly to a D+2 shifted z=0 integral and reduced by IBP to T1
    plus Gamma-function lower sectors.  Bases whose projector
    residue is zero are marked ``not_required`` rather than evaluated.
    """
    D = sp.Symbol("D") if D is None else sp.sympify(D)
    m2 = sp.Integer(1) if mass_squared is None else sp.sympify(mass_squared)
    basis = ordinary_ladder_terminal_basis()
    required = {0,1,3,5,6,7,8}
    rows = []
    for i, idx in enumerate(basis):
        if i not in required:
            rows.append(BasisZ0Evaluation(i, idx, "not_required", "zero_projector_residue", None))
        elif i in {0,1,3}:
            rows.append(BasisZ0Evaluation(i, idx, "exact", "z_independent_factorized_lower", sp.Integer(0)))
        elif i == 7:
            rows.append(BasisZ0Evaluation(i, idx, "exact", "z_independent_projective_F", sp.Integer(0)))
        elif i == 5:
            rows.append(BasisZ0Evaluation(i, idx, "exact", "three_denominator_projective_beta", one_massless_two_massive_vacuum_z_derivative_euclidean(1,D,m2)))
        elif i == 6:
            rows.append(BasisZ0Evaluation(i, idx, "exact", "three_denominator_projective_beta", one_massless_two_massive_vacuum_z_derivative_euclidean(2,D,m2)))
        elif i == 8:
            rows.append(BasisZ0Evaluation(i, idx, "exact", "dimension_shift_Dplus2_then_z0_IBP", ordinary_ladder_basis8_z_derivative_shifted_reduction(D,m2)))
    return tuple(rows)
