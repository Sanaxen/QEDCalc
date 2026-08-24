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
