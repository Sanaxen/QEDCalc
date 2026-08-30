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


@dataclass(frozen=True)
class ExternalBasisReduction:
    """Rewrite p' scalar products in the canonical external basis (p,q)."""

    expression: sp.Expr
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


def finite_q_pq_basis_substitutions() -> dict[sp.Symbol, sp.Expr]:
    """Rewrite loop dot-products with p' using p' = p + q.

    Only scalar products that can remain after the external on-shell reduction
    are mapped.  Pure external products have already been eliminated there.
    """
    return {
        sp.Symbol("SP__k__p'"): sp.Symbol("SP__k__p") + sp.Symbol("SP__k__q"),
        sp.Symbol("SP__l__p'"): sp.Symbol("SP__l__p") + sp.Symbol("SP__l__q"),
        sp.Symbol("SP__p'__r"): sp.Symbol("SP__p__r") + sp.Symbol("SP__q__r"),
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
    """Apply exact external on-shell conditions without taking q->0."""
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


def rewrite_to_pq_external_basis(
    expr: sp.Expr,
    *,
    expand_result: bool = False,
) -> ExternalBasisReduction:
    """Canonicalize finite-q scalar products to the external basis (p,q).

    This is an exact change of variables, not a small-q expansion.  It removes
    p' from loop scalar products while introducing q explicitly, which is the
    natural finite-q basis for later integral-family generation.
    """
    expression = sp.sympify(expr)
    before_atoms = _scalar_product_atoms(expression)
    reduced = expression.xreplace(finite_q_pq_basis_substitutions())
    if expand_result:
        reduced = sp.expand(reduced)
    after_atoms = _scalar_product_atoms(reduced)
    return ExternalBasisReduction(
        expression=reduced,
        before_scalar_product_atoms=before_atoms,
        after_scalar_product_atoms=after_atoms,
    )
