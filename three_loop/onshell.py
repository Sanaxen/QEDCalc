"""Finite-q on-shell reduction for projected three-loop scalar numerators.

Only exact external-electron kinematics are applied here.  In particular this
module does *not* set q=0, because the finite-q magnetic projector contains
1/z poles with z=q^2/m^2.
"""
from __future__ import annotations

from dataclasses import dataclass
import sympy as sp


@dataclass(frozen=True)
class OnShellScalarReduction:
    expression: sp.Expr
    before_operation_count: int
    after_operation_count: int
    before_scalar_product_atoms: tuple[str, ...]
    after_scalar_product_atoms: tuple[str, ...]


def finite_q_onshell_substitutions(*, mass=None, z=None) -> dict[sp.Symbol, sp.Expr]:
    """Return exact finite-q on-shell substitutions for external momenta.

    With

        p^2 = p'^2 = m^2,
        q = p' - p,
        q^2 = z m^2,

    one has

        p.p' = m^2 (1 - z/2).

    Loop-momentum scalar products with p and p' remain untouched.
    """
    m = sp.Symbol("m") if mass is None else sp.sympify(mass)
    zsym = sp.Symbol("z") if z is None else sp.sympify(z)
    return {
        sp.Symbol("SP__p__p"): m**2,
        sp.Symbol("SP__p'__p'"): m**2,
        sp.Symbol("SP__p__p'"): m**2 * (1 - zsym / 2),
    }


def _scalar_product_atoms(expr: sp.Expr) -> tuple[str, ...]:
    return tuple(sorted(
        str(symbol)
        for symbol in expr.free_symbols
        if str(symbol).startswith("SP__")
    ))


def apply_finite_q_onshell(
    expr: sp.Expr,
    *,
    mass=None,
    z=None,
    expand_result: bool = False,
) -> OnShellScalarReduction:
    """Apply exact external on-shell conditions without taking q->0.

    ``xreplace`` is used deliberately: only the three named external scalar
    products are changed.  No loop scalar product and no projector z-dependence
    is inferred or simplified away.
    """
    expression = sp.sympify(expr)
    before_atoms = _scalar_product_atoms(expression)
    before_ops = int(sp.count_ops(expression))
    reduced = expression.xreplace(
        finite_q_onshell_substitutions(mass=mass, z=z)
    )
    if expand_result:
        reduced = sp.expand(reduced)
    after_atoms = _scalar_product_atoms(reduced)
    after_ops = int(sp.count_ops(reduced))
    return OnShellScalarReduction(
        expression=reduced,
        before_operation_count=before_ops,
        after_operation_count=after_ops,
        before_scalar_product_atoms=before_atoms,
        after_scalar_product_atoms=after_atoms,
    )
