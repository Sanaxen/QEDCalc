from __future__ import annotations

from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Slash, VectorComponent, ScalarProduct,
    Add, Product, NCProduct, ScalarMul, Fraction, Power, SpinorSandwich
)
from qedcalc.operations.algebra import expand_expression
from qedcalc.operations.simplify import simplify_expression, expand_commutative


def q_degree(expr: QEDExpr, q: str = "q") -> int:
    """Return the explicit polynomial degree in the momentum-transfer vector q.

    The degree is counted structurally.  Slash(q), q_mu, p.q count as one,
    while q.q counts as two.  Products add degrees.  For sums, the maximum
    degree is returned.
    """
    if isinstance(expr, Vector) and expr.name == q:
        return 1
    if isinstance(expr, Slash) and isinstance(expr.arg, Vector) and expr.arg.name == q:
        return 1
    if isinstance(expr, VectorComponent) and isinstance(expr.vector, Vector) and expr.vector.name == q:
        return 1
    if isinstance(expr, ScalarProduct):
        n = 0
        if isinstance(expr.left, Vector) and expr.left.name == q:
            n += 1
        if isinstance(expr.right, Vector) and expr.right.name == q:
            n += 1
        return n
    if isinstance(expr, (Product, NCProduct)):
        return sum(q_degree(f, q) for f in expr.factors)
    if isinstance(expr, ScalarMul):
        return q_degree(expr.expr, q)
    if isinstance(expr, Power):
        d = q_degree(expr.base, q)
        return d * max(expr.exponent, 0)
    if isinstance(expr, Add):
        return max((q_degree(t, q) for t in expr.terms), default=0)
    if isinstance(expr, Fraction):
        # q-expansion of a denominator is a separate operation.  For a
        # numerator/current polynomial, count only the numerator here.
        return q_degree(expr.numerator, q)
    if isinstance(expr, SpinorSandwich):
        return q_degree(expr.operator, q)
    return 0


def truncate_q_order(expr: QEDExpr, max_order: int = 1, q: str = "q") -> QEDExpr:
    """Discard polynomial monomials above the requested explicit q order.

    This routine is intentionally conservative: it expands sums/products but
    does not Taylor-expand inverse denominators.  Use it for numerators and
    already-expanded currents.  Denominator Taylor expansion should be done
    explicitly in a later integration stage.
    """
    if max_order < 0:
        raise ValueError("max_order must be non-negative.")

    def rec(e: QEDExpr) -> QEDExpr:
        if isinstance(e, Add):
            kept = []
            for t in e.terms:
                rt = rec(t)
                if q_degree(rt, q) <= max_order:
                    if not (isinstance(rt, Symbol) and rt.name == "0"):
                        kept.append(rt)
            if not kept:
                return Symbol("0")
            return simplify_expression(kept[0] if len(kept) == 1 else Add(*kept))
        if isinstance(e, ScalarMul):
            inner = rec(e.expr)
            if q_degree(inner, q) > max_order:
                return Symbol("0")
            return simplify_expression(ScalarMul(e.coeff, inner))
        if isinstance(e, Product):
            out = Product(*(rec(f) for f in e.factors))
            return Symbol("0") if q_degree(out, q) > max_order else simplify_expression(out)
        if isinstance(e, NCProduct):
            out = NCProduct(*(rec(f) for f in e.factors))
            return Symbol("0") if q_degree(out, q) > max_order else simplify_expression(out)
        if isinstance(e, Fraction):
            num = rec(e.numerator)
            return Fraction(num, e.denominator)
        if isinstance(e, SpinorSandwich):
            return SpinorSandwich(rec(e.operator), e.outgoing, e.incoming)
        return Symbol("0") if q_degree(e, q) > max_order else e

    # First distribute products over sums so every additive term has a definite
    # q order.  expand_commutative handles scalar products; expand_expression
    # preserves non-commutative factor order while distributing NCProduct.
    expanded = expand_expression(expand_commutative(expr))
    return simplify_expression(rec(expanded))


def apply_elastic_onshell_q(expr: QEDExpr, incoming: str = "p", q: str = "q", mass: str = "m") -> QEDExpr:
    """Apply elastic on-shell scalar identities after p' = p + q.

    For p^2 = p'^2 = m^2 and p' = p + q,

        p.p = m^2,
        p.q = q.p = -q.q/2.

    Keeping the exact q.q term is useful before truncation.  At first order in
    q, truncate_q_order(..., 1) then removes p.q automatically.
    """
    p = Vector(incoming)
    qv = Vector(q)
    m2 = Power(Symbol(mass), 2)
    q2 = ScalarProduct(qv, qv)

    def rec(e: QEDExpr) -> QEDExpr:
        if isinstance(e, ScalarProduct):
            if e.left == p and e.right == p:
                return m2
            if (e.left == p and e.right == qv) or (e.left == qv and e.right == p):
                return ScalarMul(-0.5, q2)
            return e
        if isinstance(e, Add):
            return simplify_expression(Add(*(rec(t) for t in e.terms)))
        if isinstance(e, Product):
            return simplify_expression(Product(*(rec(f) for f in e.factors)))
        if isinstance(e, NCProduct):
            return simplify_expression(NCProduct(*(rec(f) for f in e.factors)))
        if isinstance(e, ScalarMul):
            return simplify_expression(ScalarMul(e.coeff, rec(e.expr)))
        if isinstance(e, Fraction):
            return Fraction(rec(e.numerator), rec(e.denominator))
        if isinstance(e, Power):
            return Power(rec(e.base), e.exponent)
        if isinstance(e, SpinorSandwich):
            return SpinorSandwich(rec(e.operator), e.outgoing, e.incoming)
        return e

    return simplify_expression(rec(expr))
