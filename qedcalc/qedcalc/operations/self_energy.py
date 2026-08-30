"""Reference-guided two-loop self-energy-insertion workflow.

The functions here are deliberately reusable building blocks: on-shell
counterterm formulas, UV cancellation checks, rationalization of logarithms,
and finite coefficient checks.  They do not hard-code the whole diagram as a
single black-box calculator.
"""
from __future__ import annotations
import sympy as sp


def self_energy_delta(a, r2, m, photon_mass):
    """Feynman-parameter denominator Delta(a,r^2)."""
    return sp.simplify(a*m**2 + (1-a)*photon_mass**2 - a*(1-a)*r2)


def self_energy_delta0(a, m, photon_mass):
    """On-shell denominator Delta_0(a)=Delta(a,m^2)."""
    return sp.simplify(m**2*a**2 + (1-a)*photon_mass**2)


def onshell_counterterms_from_ab(A, B, r2, m):
    """Return on-shell delta_m and delta_Z2 for Sigma=m A(r^2)+/r B(r^2)."""
    A0 = sp.simplify(A.subs(r2, m**2))
    B0 = sp.simplify(B.subs(r2, m**2))
    Ap = sp.simplify(sp.diff(A, r2).subs(r2, m**2))
    Bp = sp.simplify(sp.diff(B, r2).subs(r2, m**2))
    delta_m = sp.simplify(m*(A0+B0))
    delta_Z2 = sp.simplify(B0 + 2*m**2*(Ap+Bp))
    return delta_m, delta_Z2


def uv_cancellation_numerator(a, m, rslash):
    """UV numerator of Sigma_R after on-shell delta_m and delta_Z2 subtraction."""
    return sp.expand(
        4*m - 2*(1-a)*rslash - 2*m*(1+a)
        + 2*(rslash-m)*(1-a)
    )


def log_ratio_parameter_kernel(a, z, r2, m, photon_mass):
    """Rational denominator for log[Delta/Delta0] representation."""
    d0 = self_energy_delta0(a, m, photon_mass)
    return sp.simplify(d0 - z*a*(1-a)*(r2-m**2))


def log_ratio_prefactor(a, r2, m):
    """Prefactor in log(Delta/Delta0)=prefactor*int dz/kernel."""
    return sp.simplify(-a*(1-a)*(r2-m**2))


def finite_four_parameter_integrand(a, z, b, q):
    """Finite H_A four-parameter integrand from the reference derivation."""
    return sp.simplify(
        (a-1)*(q-b)*(q-1)
        / (a*b + q**2*z*(1-a))**2
        * (-4*a**2*b*q - 2*a**2*b + 3*a**2*q**3*z + 3*a**2*q**2*z
           + 4*a*b*q - 4*a*b - 6*a*q**3*z - 2*a*q**2*z
           + 3*q**3*z - q**2*z)
    )


def finite_b_integrated_kernel(a, z, q):
    """Analytic result of integrating the finite four-parameter kernel over b."""
    L = sp.log(1 + a/(q*z*(1-a)))
    C1 = q*(a-1)*(5*a*q+a-5*q+7)*z - 2*a*(2*a*q+a-2*q+2)
    C0 = a*(5*a*q+a-5*q+7)
    return sp.simplify(q*(a-1)*(q-1)/a**2 * (C1*L + C0))


def finite_one_variable_kernel(x):
    """Final one-variable finite kernel F(x)."""
    return sp.simplify(
        (x/sp.Integer(2)-sp.Rational(1,6)-1/(6*(x-1)))*sp.log(x)
        +(-x/sp.Integer(2)+sp.Rational(1,6)+1/(6*x)+1/(6*x**2))*sp.log(1-x)
        +x/sp.Integer(4)-sp.Rational(1,4)+1/(6*x)
    )


def finite_part_numeric(dps=60):
    """Numerically evaluate A_A from the final finite one-variable integral."""
    import mpmath as mp
    mp.mp.dps = dps
    def F(x):
        x=mp.mpf(x)
        return ((x/2-mp.mpf(1)/6-mp.mpf(1)/(6*(x-1)))*mp.log(x)
                +(-x/2+mp.mpf(1)/6+mp.mpf(1)/(6*x)+mp.mpf(1)/(6*x*x))*mp.log(1-x)
                +x/4-mp.mpf(1)/4+mp.mpf(1)/(6*x))
    eps=mp.mpf('1e-24')
    return mp.quad(F,[eps,mp.mpf('1e-10'),mp.mpf('1e-6'),mp.mpf('1e-3'),
                      mp.mpf('0.2'),mp.mpf('0.8'),mp.mpf('0.999'),1-eps])


def finite_part_expected():
    return -sp.Rational(1,24) - sp.pi**2/18


def finite_part_recognize(value, digits=50):
    return sp.nsimplify(sp.Float(str(value), digits), [sp.pi**2])


def ir_part_asymptotic(rho):
    """Asymptotic H_B coefficient retained symbolically."""
    return sp.log(rho) + sp.Rational(1,2)


def total_self_energy_coefficient(rho):
    """A_S(rho) through O(rho^0)."""
    return sp.simplify(sp.log(rho) + sp.Rational(11,24) - sp.pi**2/18)


def total_self_energy_coefficient_inverse_log(rho):
    """Equivalent form using -1/2 log(rho^-2)."""
    return -sp.Rational(1,2)*sp.log(rho**-2) + sp.Rational(11,24) - sp.pi**2/18
