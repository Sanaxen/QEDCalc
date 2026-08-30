from __future__ import annotations

from dataclasses import dataclass

from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Index, Gamma, Slash, VectorComponent,
    Add, Product, NCProduct, ScalarMul, SpinorSandwich
)
from qedcalc.operations.simplify import simplify_expression


@dataclass(frozen=True)
class QBasisDecomposition:
    """A conservative decomposition of a q-expanded current.

    The supported explicit current structures are gamma_mu, p_mu and q_mu.
    Terms containing remaining slash matrices or any other current structure
    are returned as residual instead of being guessed away.
    """
    gamma: QEDExpr
    p: QEDExpr
    q: QEDExpr
    residual: QEDExpr


def _coefficient_of_target(term: QEDExpr, target: QEDExpr):
    if term == target:
        return Symbol("1")
    if isinstance(term, ScalarMul):
        if term.expr == target:
            return Symbol(str(term.coeff))
        inner = _coefficient_of_target(term.expr, target)
        if inner is not None:
            return simplify_expression(ScalarMul(term.coeff, inner))
        return None
    if isinstance(term, Product):
        matches = [i for i, f in enumerate(term.factors) if f == target]
        if len(matches) == 1:
            i = matches[0]
            rest = [f for j, f in enumerate(term.factors) if j != i]
            if not rest:
                return Symbol("1")
            return simplify_expression(rest[0] if len(rest) == 1 else Product(*rest))
    return None


def _sum(xs):
    if not xs:
        return Symbol("0")
    return simplify_expression(xs[0] if len(xs) == 1 else Add(*xs))


def decompose_q_basis(expr: QEDExpr, index="mu", incoming="p", q="q") -> QBasisDecomposition:
    """Decompose a first-order current into gamma_mu, p_mu, q_mu + residual.

    If a SpinorSandwich is supplied, its operator is analyzed.  No term with
    remaining slash matrices is silently projected onto a basis.
    """
    if isinstance(expr, SpinorSandwich):
        expr = expr.operator

    idx = Index(index, "down")
    targets = {
        "gamma": Gamma(idx),
        "p": VectorComponent(Vector(incoming), idx),
        "q": VectorComponent(Vector(q), idx),
    }
    buckets = {k: [] for k in targets}
    residual = []
    terms = list(expr.terms) if isinstance(expr, Add) else [expr]

    for term in terms:
        matched = False
        for key, target in targets.items():
            c = _coefficient_of_target(term, target)
            if c is not None:
                buckets[key].append(c)
                matched = True
                break
        if not matched:
            residual.append(term)

    return QBasisDecomposition(
        _sum(buckets["gamma"]),
        _sum(buckets["p"]),
        _sum(buckets["q"]),
        _sum(residual),
    )


def pair_coefficient_from_q_basis(decomp: QBasisDecomposition):
    """Return B for B(p'+p)_mu = B(2p+q)_mu when the q basis is consistent.

    Requires coefficient(p_mu) = 2*coefficient(q_mu).  Residual terms must be
    zero; otherwise the current has not yet been fully reduced.
    """
    if not (isinstance(decomp.residual, Symbol) and decomp.residual.name == "0"):
        raise ValueError("Current still contains residual structures outside gamma_mu, p_mu, q_mu.")
    expected_p = simplify_expression(ScalarMul(2, decomp.q))
    if decomp.p != expected_p:
        raise ValueError("q-basis coefficients are not consistent with B(p'+p)_mu = B(2p+q)_mu.")
    return decomp.q


@dataclass(frozen=True)
class GordonQSplit:
    """Split of A gamma_mu + Cp p_mu + Cq q_mu into Gordon + longitudinal parts."""
    gamma: QEDExpr
    pair: QEDExpr
    longitudinal_q: QEDExpr
    residual: QEDExpr


def split_q_basis_into_gordon(decomp: QBasisDecomposition) -> GordonQSplit:
    """Rewrite Cp p_mu + Cq q_mu as B(p'+p)_mu + L q_mu.

    After p' = p + q,

        (p'+p)_mu = 2 p_mu + q_mu,

    so B = Cp/2 and L = Cq - Cp/2.  This decomposition is algebraic and does
    not assume the longitudinal q_mu coefficient vanishes.
    """
    from sympy import Rational
    B = simplify_expression(ScalarMul(Rational(1, 2), decomp.p))
    L = simplify_expression(Add(decomp.q, ScalarMul(-1, B)))
    return GordonQSplit(decomp.gamma, B, L, decomp.residual)


def project_f2_from_q_basis(decomp: QBasisDecomposition, mass="m") -> QEDExpr:
    """Project the Pauli-form-factor numerator from a reduced q-basis current.

    Residual non-basis structures are rejected.  A longitudinal q_mu term is
    separated and does not enter F2.  With the project convention used by
    QEDCalc, F2 numerator = -2 m B, where B multiplies (p'+p)_mu.
    """
    split = split_q_basis_into_gordon(decomp)
    if not (isinstance(split.residual, Symbol) and split.residual.name == "0"):
        raise ValueError("Cannot project F2 while residual current structures remain.")
    return simplify_expression(ScalarMul(-2, Product(Symbol(mass), split.pair)))
