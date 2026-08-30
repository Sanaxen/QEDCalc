from __future__ import annotations

import sympy as sp

from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, ScalarProduct, Add, Product, NCProduct, ScalarMul, Fraction
)
from qedcalc.operations.simplify import simplify_expression
from qedcalc.operations.scalar_sympy import to_sympy_scalar, from_sympy_scalar, simplify_scalar_with_sympy


def _contains_symbol(expr: QEDExpr, name: str) -> bool:
    if isinstance(expr, Symbol):
        return expr.name == name
    if hasattr(expr, "walk"):
        return any(isinstance(n, Symbol) and n.name == name for n in expr.walk())
    return False


def extract_delta_from_shifted_denominator(expr: QEDExpr, loop="l", epsilon="varepsilon") -> QEDExpr:
    """Extract Delta from -l^2 + Delta - i epsilon.

    The loop-quadratic term and the i-epsilon term are removed.  Remaining
    scalar terms are simplified with SymPy.
    """
    terms = list(expr.terms) if isinstance(expr, Add) else [expr]
    kept = []
    for t in terms:
        base = t.expr if isinstance(t, ScalarMul) else t
        if isinstance(base, ScalarProduct):
            if (isinstance(base.left, Vector) and isinstance(base.right, Vector)
                    and base.left.name == loop and base.right.name == loop):
                continue
        if _contains_symbol(t, epsilon):
            continue
        kept.append(t)
    if not kept:
        raise ValueError("No Delta terms remain after removing loop-square and i-epsilon terms.")
    delta = kept[0] if len(kept) == 1 else Add(*kept)
    return simplify_scalar_with_sympy(simplify_expression(delta), "factor")


def triangle_integral_ratio(numerator: QEDExpr, delta: QEDExpr, parameters=("x", "y")):
    """Evaluate int_0^1 dx int_0^(1-x) dy numerator/delta with SymPy."""
    if len(parameters) != 2:
        raise ValueError("triangle_integral_ratio currently requires exactly two parameters.")
    atom_map = {}
    n, _ = to_sympy_scalar(numerator, atom_map)
    d, _ = to_sympy_scalar(delta, atom_map)
    xkey = f"S__{parameters[0]}"; ykey = f"S__{parameters[1]}"
    x = atom_map.get(xkey, sp.Symbol(xkey))
    y = atom_map.get(ykey, sp.Symbol(ykey))
    integrand = sp.cancel(sp.simplify(n / d))
    value = sp.simplify(sp.integrate(sp.integrate(integrand, (y, 0, 1-x)), (x, 0, 1)))
    return integrand, value


def qed_vertex_prefactor_after_n3_loop(triangle_value):
    """Apply the standard one-loop QED prefactor after the n=3 loop integral.

    Convention used:

      e^2 / ((2 pi)^4 i)
      x 2  [Feynman-parameter prefactor]
      x i pi^2 / (2 Delta)
      = alpha / (4 pi Delta).

    Therefore the remaining triangle integral is multiplied by alpha/(4 pi).
    """
    alpha = sp.Symbol("S__alpha")
    pi = sp.Symbol("S__pi")
    result = sp.simplify(triangle_value * alpha / (4*pi))
    if result == alpha / (2*pi):
        return Fraction(Symbol("alpha"), Product(Symbol("2"), Symbol("pi")))
    # Prefer a fraction-shaped internal representation for the common QED
    # result so LaTeX is rendered as alpha/(2 pi), not alpha*pi^{-1}/2.
    num, den = sp.fraction(result)
    reverse = {alpha: Symbol("alpha"), pi: Symbol("pi")}
    if den != 1:
        return Fraction(
            simplify_expression(from_sympy_scalar(num, reverse)),
            simplify_expression(from_sympy_scalar(den, reverse)),
        )
    return simplify_expression(from_sympy_scalar(result, reverse))


def euclidean_scalar_loop_integral(denominator_power, numerator_power=0, dimension=None, delta=None):
    r"""Return the standard Euclidean D-dimensional scalar loop integral.

    Computes

      int d^D l (l^2)^r / (l^2 + Delta)^n

    as

      pi^(D/2) Delta^(D/2+r-n)
      Gamma(r+D/2) Gamma(n-r-D/2)
      / [Gamma(D/2) Gamma(n)].

    The return value is a SymPy expression.  No i factors or Wick-rotation
    signs are inserted; those belong to the caller's convention layer.
    """
    n = sp.sympify(denominator_power)
    r = sp.sympify(numerator_power)
    D = sp.Symbol("D") if dimension is None else sp.sympify(dimension)
    Delta = sp.Symbol("Delta", positive=True) if delta is None else sp.sympify(delta)
    if n.is_integer is True and n.is_positive is False:
        raise ValueError("denominator_power must be positive.")
    if r.is_integer is True and r.is_nonnegative is False:
        raise ValueError("numerator_power must be non-negative.")
    return sp.simplify(
        sp.pi**(D/2)
        * Delta**(D/2 + r - n)
        * sp.gamma(r + D/2)
        * sp.gamma(n - r - D/2)
        / (sp.gamma(D/2) * sp.gamma(n))
    )


def dimensional_regularized_loop_series(denominator_power, numerator_power=0, epsilon=None, delta=None, order=1):
    r"""Expand the Euclidean standard loop integral around D=4-2 epsilon.

    Returns a SymPy Laurent series with terms through O(epsilon**order).
    This function deliberately excludes renormalization scales and convention
    factors such as (2*pi)^(-D), i, and MS-bar factors.  Those must be supplied
    explicitly by a higher-level convention layer.
    """
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    Delta = sp.Symbol("Delta", positive=True) if delta is None else sp.sympify(delta)
    D = 4 - 2*eps
    expr = euclidean_scalar_loop_integral(denominator_power, numerator_power, D, Delta)
    return sp.series(expr, eps, 0, order + 1)
