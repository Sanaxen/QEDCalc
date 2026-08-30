"""Reference-guided two-loop vacuum-polarization g-2 workflow.

The routines in this module are intentionally small.  They expose the finite
scalar kernels obtained after the tensor/subdiagram stages so they can be
checked independently with SymPy/mpmath.  They are not a replacement for the
generic QED algebra layers.
"""
from __future__ import annotations
import sympy as sp


def vp_hat_renormalized_integrand(k2, m, z):
    """Integrand of the on-shell-renormalized one-loop vacuum polarization.

    hat(Pi)_R(k^2) = 2 int_0^1 dz z(1-z)
      log[m^2/(m^2-k^2 z(1-z))].
    """
    return sp.simplify(2*z*(1-z)*sp.log(m**2/(m**2-k2*z*(1-z))))


def vp_gminus2_double_integrand(x, z):
    """Dimensionless coefficient kernel for the two-loop VP contribution."""
    return sp.simplify(2*(1-x)*z*(1-z)*sp.log(1 + x**2*z*(1-z)/(1-x)))


def vp_z_integrated_kernel(x):
    """Closed z-integrated kernel H(x), independently differentiable/checkable."""
    return sp.simplify(
        (3*x**3*sp.log(1-x) - 5*x**3 - 12*x**2
         - 18*x*sp.log(1-x) + 12*x + 12*sp.log(1-x)) / (9*x**3)
    )


def vp_numeric_coefficient(dps=50):
    """Numerically integrate the original finite two-parameter kernel."""
    import mpmath as mp
    mp.mp.dps = dps

    def f(xx, zz):
        if xx == 1:
            return mp.mpf('0')
        return 2*(1-xx)*zz*(1-zz)*mp.log(1 + xx*xx*zz*(1-zz)/(1-xx))

    return mp.quad(lambda xx: mp.quad(lambda zz: f(xx, zz), [0, 1]), [0, 1])


def vp_recognize_analytic(value, digits=50):
    """Recognize a high-precision numerical coefficient in the {1, pi^2} basis."""
    v = sp.Float(str(value), digits)
    return sp.nsimplify(v, [sp.pi**2])


def vp_expected_analytic():
    return sp.Rational(119, 36) - sp.pi**2/3


from dataclasses import dataclass
from qedcalc.core.expression import Symbol, Vector, ScalarMul, CompletedSquare, VectorLinearCombination
from qedcalc.operations.bare_diagram import reduce_single_trace_from_loop_integral_4d, TraceSubdiagramReduction
from qedcalc.operations.loop import shift_loop_momentum_in_numerator, drop_odd_loop_terms, symmetric_rank2
from qedcalc.operations.simplify import expand_commutative


@dataclass(frozen=True)
class BareVacuumPolarizationReduction:
    """Raw-diagram bridge for the one-loop VP subdiagram inside a two-loop vertex."""
    trace_reduction: TraceSubdiagramReduction
    shifted_trace_numerator: object
    even_trace_numerator: object
    tensor_reduced_trace_numerator: object


def reduce_vp_subdiagram_from_bare_2loop_4d(diagram, parameter_name="z", shifted_loop="r"):
    """Reduce the unique closed fermion trace directly from a parsed bare 2-loop diagram.

    The function performs only reusable algebraic stages:
      1. locate the unique Dirac trace,
      2. scalarize its fermion propagators,
      3. evaluate the four-dimensional trace numerator,
      4. apply l = r - z k,
      5. remove odd powers of r,
      6. apply rank-2 symmetric tensor reduction.

    Renormalization and the final scalar VP kernel remain separate operations.
    """
    tr = reduce_single_trace_from_loop_integral_4d(diagram)
    zq = Symbol(parameter_name)
    completed = CompletedSquare(
        loop=Vector("l"),
        shift=VectorLinearCombination(((ScalarMul(-1, zq), Vector("k")),)),
        remainder=Symbol("0"),
    )
    shifted = expand_commutative(
        shift_loop_momentum_in_numerator(tr.traced_numerator, completed, new_loop=shifted_loop)
    )
    even = drop_odd_loop_terms(shifted, loop=shifted_loop)
    reduced = symmetric_rank2(even, loop=shifted_loop)
    return BareVacuumPolarizationReduction(tr, shifted, even, reduced)

# ---------------------------------------------------------------------------
# v0.52.0: raw-trace -> dimensionally subtracted scalar -> analytic endpoint
# ---------------------------------------------------------------------------
from functools import lru_cache


@dataclass(frozen=True)
class VacuumPolarizationAnalyticAudit:
    """Inspectable checkpoints for the independent VP raw-to-final route."""
    transverse_metric_coefficient: sp.Expr
    transverse_kk_coefficient: sp.Expr
    transverse_residual: sp.Expr
    dimreg_subtracted_integrand: sp.Expr
    four_dimensional_integrand: sp.Expr
    double_kernel: sp.Expr
    z_kernel: sp.Expr
    x_integrand: sp.Expr
    primitive: sp.Expr
    primitive_derivative_residual: sp.Expr
    endpoint_one: sp.Expr
    endpoint_zero: sp.Expr
    final_coefficient: sp.Expr


def vp_shifted_even_tensor_coefficients(D, z, k2, m2, r2):
    r"""Coefficients after the raw trace shift and symmetric rank-2 reduction.

    The trace numerator is written as

        A_g g^{alpha beta} + A_kk k^alpha k^beta.

    This is the D-dimensional continuation of the directly parsed/shifted
    trace.  Setting D=4 gives the audited four-dimensional expression

        A_g = 4 m^2 - 2 r^2 + 4 z(1-z) k^2,
        A_kk = -8 z(1-z).
    """
    D = sp.sympify(D)
    z = sp.sympify(z)
    k2 = sp.sympify(k2)
    m2 = sp.sympify(m2)
    r2 = sp.sympify(r2)
    a = sp.expand(z * (1 - z))
    metric = sp.simplify(4 * ((sp.Rational(2, 1) / D - 1) * r2 + m2 + a * k2))
    kk = sp.simplify(-8 * a)
    return metric, kk


def vp_dimensional_transverse_reduction(D, z, k2, m2, J2=None):
    r"""Use the scalar loop IBP identity to expose exact transversality.

    Let Delta = m^2-z(1-z)k^2 and

        J2 = int d^D r / (Delta-r^2)^2.

    The total derivative identity gives

        int r^2/(Delta-r^2)^2 = D Delta/(D-2) J2.

    Substitution into the shifted trace makes the metric and kk coefficients
    exactly proportional to k^2 and -1, respectively.
    """
    D = sp.sympify(D)
    z = sp.sympify(z)
    k2 = sp.sympify(k2)
    m2 = sp.sympify(m2)
    if J2 is None:
        J2 = sp.Symbol("J_2")
    else:
        J2 = sp.sympify(J2)
    a = sp.expand(z * (1 - z))
    Delta = sp.simplify(m2 - a * k2)
    r2_integral = sp.simplify(D * Delta * J2 / (D - 2))
    metric = sp.simplify(4 * ((sp.Rational(2, 1) / D - 1) * r2_integral + (m2 + a * k2) * J2))
    kk = sp.simplify(-8 * a * J2)
    residual = sp.simplify(metric + kk * k2)
    scalar = sp.simplify(metric / k2)
    return {
        "Delta": Delta,
        "r2_integral": r2_integral,
        "metric": metric,
        "kk": kk,
        "scalar": scalar,
        "transverse_residual": residual,
    }


def vp_hat_dimreg_subtracted_integrand(D, k2, m2, z):
    r"""Dimensionally regulated on-shell-subtracted scalar VP integrand.

    Overall coupling/loop-measure normalization has already been factored so
    that Pi_R=(alpha/pi) * hat(Pi)_R.  The subtraction is performed before
    D->4, so no divergent standalone term is introduced.
    """
    D = sp.sympify(D)
    k2 = sp.sympify(k2)
    m2 = sp.sympify(m2)
    z = sp.sympify(z)
    a = sp.expand(z * (1 - z))
    power = sp.simplify(D / 2 - 2)
    M2 = sp.simplify(m2 - k2 * a)
    return sp.simplify(2 * a * sp.gamma(2 - D / 2) * (M2**power - m2**power))


def vp_hat_renormalized_integrand_from_dimreg(k2, m2, z):
    """Take the exact D->4 limit of the dimensionally subtracted integrand."""
    D = sp.Symbol("D", real=True)
    expr = vp_hat_dimreg_subtracted_integrand(D, k2, m2, z)
    return sp.simplify(sp.limit(expr, D, 4))


def vp_outer_magnetic_spacelike_k2(x, m2=1):
    """Spacelike photon invariant generated by the q->0 one-loop magnetic kernel."""
    x = sp.sympify(x)
    m2 = sp.sympify(m2)
    return sp.simplify(-m2 * x**2 / (1 - x))


def vp_gminus2_double_integrand_from_dimreg(x, z):
    """Generate the finite two-parameter g-2 kernel from the subtracted VP scalar."""
    x = sp.sympify(x)
    z = sp.sympify(z)
    m2 = sp.Symbol("m_2", positive=True)
    k2 = vp_outer_magnetic_spacelike_k2(x, m2)
    pi_hat = vp_hat_renormalized_integrand_from_dimreg(k2, m2, z)
    return sp.factor(sp.simplify(-(1 - x) * pi_hat))


def vp_z_integrated_kernel_derived(x):
    r"""Derive H(x) from the elementary beta=x/(2-x) representation.

    No stored final H(x) polynomial is used.  For 0<x<1 the t-integral gives

        I(beta) = 2/3 log(1-beta^2) - 16/9 + 2/(3 beta^2)
                  + (3 beta^2-1)/(3 beta^3) log((1+beta)/(1-beta)).

    The constant logarithm from the z=(1+t)/2 substitution cancels the first
    log term.  The interval identity (1+beta)/(1-beta)=1/(1-x) then gives H.
    """
    x = sp.sympify(x)
    beta = sp.simplify(x / (2 - x))
    # C = -log(1-beta^2) on 0<x<1, so the two 2/3 logarithms cancel.
    H = (
        -sp.Rational(8, 9)
        + sp.Rational(1, 3) / beta**2
        - (3 * beta**2 - 1) * sp.log(1 - x) / (6 * beta**3)
    )
    return sp.factor(sp.simplify(H))


def vp_x_integrand_derived(x):
    """One-variable integrand (1-x) H(x) generated from the derived z kernel."""
    x = sp.sympify(x)
    return sp.cancel(sp.expand((1 - x) * vp_z_integrated_kernel_derived(x)))


def _vp_real_interval_polylog_normalize(expr, x):
    """Normalize SymPy's exp_polar continuation to the real 0<x<1 branch."""
    expr = sp.sympify(expr)
    polar_arg = x * sp.exp_polar(2 * sp.I * sp.pi)
    return expr.xreplace({sp.polylog(2, polar_arg): sp.polylog(2, x)})


def _vp_log_monomial_primitive(power, x):
    """Real-branch antiderivatives of x**power*log(1-x), up to the VP Laurent depth."""
    L = sp.log(1 - x)
    p = int(power)
    if p == 1:
        return (x**2 - 1) * L / 2 - x**2 / 4 - x / 2
    if p == 0:
        # Integration constant chosen so the assembled primitive matches the
        # natural no-standalone-constant convention used by the derivation.
        return (x - 1) * L - x
    if p == -1:
        return -sp.polylog(2, x)
    if p == -2:
        return -L / x - sp.log(x) + L
    if p == -3:
        return -L / (2 * x**2) + sp.Rational(1, 2) / x - sp.log(x) / 2 + L / 2
    raise NotImplementedError(f"VP logarithmic Laurent power x^{p} is not supported")


@lru_cache(maxsize=8)
def _vp_x_primitive_cached(symbol_name):
    x = sp.Symbol(symbol_name, positive=True)
    f = sp.expand(vp_x_integrand_derived(x))
    L = sp.log(1 - x)
    log_coeff = sp.simplify(f.coeff(L))
    rational = sp.simplify(f - log_coeff * L)

    primitive = sp.integrate(rational, x)
    for term in sp.expand(log_coeff).as_ordered_terms():
        coeff, power = term.as_coeff_exponent(x)
        if not power.is_Integer:
            raise ValueError(f"Unexpected VP logarithmic term: {term}")
        primitive += coeff * _vp_log_monomial_primitive(int(power), x)
    return sp.expand(sp.simplify(primitive))


def vp_x_primitive_derived(x):
    """Construct the real-branch antiderivative from the generated x kernel."""
    x = sp.sympify(x)
    if not isinstance(x, sp.Symbol):
        y = sp.Symbol("x", positive=True)
        return sp.simplify(_vp_x_primitive_cached(y.name).subs(y, x))
    base = _vp_x_primitive_cached(x.name)
    symbols = list(base.free_symbols)
    if x not in base.free_symbols and symbols:
        base = base.subs(symbols[0], x)
    return sp.expand(base)

def vp_x_primitive_derivative_residual(x):
    """Exact derivative check on the physical real branch 0<x<1."""
    x = sp.sympify(x)
    F = vp_x_primitive_derived(x)
    residual = sp.diff(F, x) - vp_x_integrand_derived(x)
    residual = residual.xreplace({sp.polylog(1, x): -sp.log(1 - x)})
    return sp.simplify(residual)


def vp_x_endpoint_one_from_primitive(x):
    """Evaluate the x->1 endpoint by separating the cancelling log coefficient."""
    x = sp.sympify(x)
    F = sp.expand(vp_x_primitive_derived(x))
    L = sp.log(1 - x)
    A = sp.simplify(F.coeff(L))
    if sp.simplify(A.subs(x, 1)) != 0:
        raise ValueError("VP primitive has a non-cancelling log(1-x) coefficient at x=1")
    regular = sp.expand(F - A * L)
    regular = regular.xreplace({sp.polylog(2, x): sp.pi**2 / 6})
    return sp.simplify(regular.subs(x, 1))


def vp_x_endpoint_zero_from_primitive(x, series_order=7):
    """Evaluate x->0 by generated log/dilog power series; verify pole cancellation."""
    x = sp.sympify(x)
    F = sp.expand(vp_x_primitive_derived(x))
    nmax = int(series_order)
    log_series = -sum(x**n / sp.Integer(n) for n in range(1, nmax + 1))
    li2_series = sum(x**n / sp.Integer(n) ** 2 for n in range(1, nmax + 1))
    expanded = sp.expand(F.xreplace({sp.log(1 - x): log_series, sp.polylog(2, x): li2_series}))
    series = sp.series(expanded, x, 0, 2).removeO()
    # Negative powers must cancel before the finite endpoint is accepted.
    for p in range(-4, 0):
        if sp.simplify(series.coeff(x, p)) != 0:
            raise ValueError(f"VP x->0 endpoint retains x^{p} pole")
    return sp.simplify(series.coeff(x, 0))


def vp_final_coefficient_derived():
    """Independent analytic VP coefficient assembled from generated endpoints."""
    x = sp.Symbol("x", positive=True)
    return sp.simplify(vp_x_endpoint_one_from_primitive(x) - vp_x_endpoint_zero_from_primitive(x))


def vp_raw_to_final_audit():
    """Build all compact symbolic checkpoints of the v0.52 VP route."""
    D = sp.Symbol("D", real=True)
    z = sp.Symbol("z", positive=True)
    k2 = sp.Symbol("k_2", real=True)
    m2 = sp.Symbol("m_2", positive=True)
    J2 = sp.Symbol("J_2")
    trans = vp_dimensional_transverse_reduction(D, z, k2, m2, J2)
    dimreg = vp_hat_dimreg_subtracted_integrand(D, k2, m2, z)
    fourd = vp_hat_renormalized_integrand_from_dimreg(k2, m2, z)
    x = sp.Symbol("x", positive=True)
    double = vp_gminus2_double_integrand_from_dimreg(x, z)
    H = vp_z_integrated_kernel_derived(x)
    xint = vp_x_integrand_derived(x)
    F = vp_x_primitive_derived(x)
    derivative_residual = vp_x_primitive_derivative_residual(x)
    e1 = vp_x_endpoint_one_from_primitive(x)
    e0 = vp_x_endpoint_zero_from_primitive(x)
    final = sp.simplify(e1 - e0)
    return VacuumPolarizationAnalyticAudit(
        trans["metric"], trans["kk"], trans["transverse_residual"],
        dimreg, fourd, double, H, xint, F, derivative_residual, e1, e0, final,
    )

# --- v0.86: Phase 79 vacuum-polarization end-to-end closure checkpoint ---
def vp_phase79_end_to_end_checkpoint():
    """Exact VP closure audit from transverse subloop through the g-2 constant.

    The expensive raw LaTeX/topology parse remains covered by the earlier
    Phase-21 bridge tests.  This release checkpoint starts from the independently
    generated dimensionally transverse subloop and verifies every physical
    invariant through the final analytic coefficient.
    """
    D = sp.Symbol("D", real=True)
    z = sp.Symbol("z", positive=True)
    k2 = sp.Symbol("k_2", real=True)
    m2 = sp.Symbol("m_2", positive=True)
    J2 = sp.Symbol("J_2")
    x = sp.Symbol("x", positive=True)

    trans = vp_dimensional_transverse_reduction(D, z, k2, m2, J2)
    fourd = vp_hat_renormalized_integrand_from_dimreg(k2, m2, z)
    os_residual = sp.simplify(fourd.subs(k2, 0))

    expected_fourd = 2*z*(1-z)*sp.log(m2/(m2-k2*z*(1-z)))
    fourd_residual = sp.simplify(
        sp.expand_log(fourd, force=True) - sp.expand_log(expected_fourd, force=True)
    )

    double = vp_gminus2_double_integrand_from_dimreg(x, z)
    double_residual = sp.simplify(double - vp_gminus2_double_integrand(x, z))
    H = vp_z_integrated_kernel_derived(x)
    z_kernel_residual = sp.simplify(H - vp_z_integrated_kernel(x))
    primitive_residual = vp_x_primitive_derivative_residual(x)
    endpoint_one = vp_x_endpoint_one_from_primitive(x)
    endpoint_zero = vp_x_endpoint_zero_from_primitive(x)
    final = sp.simplify(endpoint_one - endpoint_zero)
    closed = sp.simplify(vp_expected_analytic())

    return {
        "transverse_metric": sp.simplify(trans["metric"]),
        "transverse_kk": sp.simplify(trans["kk"]),
        "transverse_residual": sp.simplify(trans["transverse_residual"]),
        "on_shell_subtraction_residual": os_residual,
        "four_dimensional_kernel_residual": fourd_residual,
        "outer_insertion_kernel_residual": double_residual,
        "z_kernel_residual": z_kernel_residual,
        "primitive_derivative_residual": primitive_residual,
        "endpoint_one": sp.simplify(endpoint_one),
        "endpoint_zero": sp.simplify(endpoint_zero),
        "final": final,
        "closed_form": closed,
        "final_closed_form_residual": sp.simplify(final - closed),
    }
