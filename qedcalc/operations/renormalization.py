from __future__ import annotations

from dataclasses import dataclass
import sympy as sp


@dataclass(frozen=True)
class RenormalizationConvention:
    """Dimensional-regularization convention used by QEDCalc.

    The MS-bar convention implemented here uses

        S_epsilon = (4*pi*exp(-EulerGamma))**epsilon

    per loop, so an L-loop expression receives

        mu**(2*L*epsilon) * S_epsilon**L.

    With this convention, MS and MS-bar subtraction both remove pure negative
    powers of epsilon after the corresponding scale factor has been applied.
    """
    scheme: str = "MSbar"
    loop_order: int = 1

    def normalized_scheme(self):
        s = self.scheme.strip().upper().replace("OVERLINE{MS}", "MSBAR").replace("MS-BAR", "MSBAR")
        if s not in {"MS", "MSBAR"}:
            raise ValueError("scheme must be 'MS' or 'MSbar'.")
        if self.loop_order < 1:
            raise ValueError("loop_order must be at least 1.")
        return s


def _resolve_dimreg_scheme(scheme=None, conventions=None):
    if scheme is not None:
        return scheme
    if conventions is not None:
        selected = conventions.dimreg_subtraction
        if selected == "none":
            raise ValueError("dimreg_subtraction=none does not define an MS-style scale factor.")
        return selected
    return "MSbar"


def dimreg_scale_factor(loop_order=1, epsilon=None, mu=None, scheme=None, conventions=None):
    r"""Return the dimensional-regularization scale factor for L loops.

    MS:
        mu^(2 L epsilon)

    MS-bar (QEDCalc convention):
        mu^(2 L epsilon) (4 pi e^{-gamma_E})^(L epsilon)
    """
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    scale = sp.Symbol("mu", positive=True) if mu is None else sp.sympify(mu)
    scheme = _resolve_dimreg_scheme(scheme, conventions)
    conv = RenormalizationConvention(scheme, int(loop_order))
    normalized = conv.normalized_scheme()
    factor = scale ** (2 * conv.loop_order * eps)
    if normalized == "MSBAR":
        use_msbar_factor = True if conventions is None else bool(conventions.msbar_factor)
        if use_msbar_factor:
            factor *= (4 * sp.pi * sp.exp(-sp.EulerGamma)) ** (conv.loop_order * eps)
    return sp.simplify(factor)


def apply_dimreg_convention(expr, loop_order=1, epsilon=None, mu=None, scheme=None, conventions=None):
    """Multiply a SymPy expression by the selected dimensional scale factor."""
    return sp.simplify(sp.sympify(expr) * dimreg_scale_factor(loop_order, epsilon, mu, scheme, conventions))


def pole_part(expr, epsilon=None, max_order=6):
    """Return the sum of negative epsilon powers in an expanded Laurent expression."""
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    expanded = sp.expand(sp.sympify(expr))
    result = sp.Integer(0)
    for n in range(1, max_order + 1):
        c = sp.simplify(expanded.coeff(eps, -n))
        if c != 0:
            result += c * eps**(-n)
    return sp.simplify(result)


def minimal_subtract(expr, epsilon=None, max_order=6):
    """Subtract pure Laurent poles from an expression (MS-style operation)."""
    return sp.simplify(sp.expand(sp.sympify(expr)) - pole_part(expr, epsilon, max_order))


def renormalized_dimreg_series(expr, loop_order=1, epsilon=None, mu=None,
                               scheme=None, conventions=None, expansion_order=0, max_pole_order=6):
    """Apply the convention factor, expand around epsilon=0, and minimally subtract poles.

    The returned dictionary keeps the convention factor, bare Laurent series,
    pole part, and subtracted finite/regular series explicit so no convention
    step is hidden.
    """
    eps = sp.Symbol("epsilon") if epsilon is None else sp.sympify(epsilon)
    scheme = _resolve_dimreg_scheme(scheme, conventions)
    factor = dimreg_scale_factor(loop_order, eps, mu, scheme, conventions)
    scaled = sp.simplify(sp.sympify(expr) * factor)
    series = sp.series(scaled, eps, 0, expansion_order + 1).removeO().expand()
    poles = pole_part(series, eps, max_pole_order)
    subtracted = sp.simplify(series - poles)
    return {
        "scheme": RenormalizationConvention(scheme, int(loop_order)).normalized_scheme(),
        "scale_factor": factor,
        "series": series,
        "pole_part": poles,
        "subtracted": subtracted,
    }
