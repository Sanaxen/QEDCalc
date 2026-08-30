from qedcalc.core.expression import Add, Product, NCProduct, ScalarMul, Slash, Vector, Fraction

def expand_expression(expr):
    """Distribute NCProduct over Add. Minimal first implementation."""
    if isinstance(expr, Add):
        return Add(*(expand_expression(t) for t in expr.terms))

    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, expand_expression(expr.expr))

    if isinstance(expr, Product):
        factors = [expand_expression(f) for f in expr.factors]
        for i, f in enumerate(factors):
            if isinstance(f, Add):
                terms = []
                for term in f.terms:
                    new_factors = factors[:i] + [term] + factors[i+1:]
                    terms.append(expand_expression(Product(*new_factors)))
                return Add(*terms)
        return Product(*factors)

    if isinstance(expr, Fraction):
        return Fraction(expand_expression(expr.numerator), expand_expression(expr.denominator))

    if isinstance(expr, NCProduct):
        factors = [expand_expression(f) for f in expr.factors]
        for i, f in enumerate(factors):
            if isinstance(f, Add):
                terms = []
                for term in f.terms:
                    new_factors = factors[:i] + [term] + factors[i+1:]
                    terms.append(expand_expression(NCProduct(*new_factors)))
                return Add(*terms)
        return NCProduct(*factors)

    return expr


def expand_slash(expr):
    """Expand Slash(Add(...)) linearly."""
    from qedcalc.core.expression import Add, NCProduct, ScalarMul, Slash
    if isinstance(expr, Slash) and isinstance(expr.arg, Add):
        return Add(*(Slash(t) if not isinstance(t, ScalarMul)
                     else ScalarMul(t.coeff, Slash(t.expr))
                     for t in expr.arg.terms))
    if isinstance(expr, Add):
        return Add(*(expand_slash(t) for t in expr.terms))
    if isinstance(expr, NCProduct):
        return NCProduct(*(expand_slash(f) for f in expr.factors))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, expand_slash(expr.expr))
    return expr


def normalize_noncommutative_products(expr):
    """Hoist commutative scalar factors out of Dirac chains.

    Loop-momentum shifts naturally create temporary objects such as
    Product(x, Slash(p)).  For Dirac algebra, that means the scalar x times a
    non-commutative slash matrix.  This function rewrites such structures so
    the slash/gamma chain is explicit while preserving its factor order.
    """
    from qedcalc.core.expression import (
        QEDExpr, Symbol, Vector, Index, Gamma, Metric, Slash, ScalarProduct,
        VectorComponent, Product, NCProduct, Add, ScalarMul, Fraction, Power,
        SpinorSandwich, PauliTerm
    )
    from qedcalc.operations.simplify import simplify_expression

    def is_nc(e):
        return isinstance(e, (Gamma, Slash, NCProduct, PauliTerm))

    def split_factor(e):
        e = rec(e)
        if isinstance(e, Product):
            scalars=[]; nc=[]
            for f in e.factors:
                if is_nc(f): nc.append(f)
                else: scalars.append(f)
            return scalars, nc
        if isinstance(e, ScalarMul) and is_nc(e.expr):
            return [Symbol(str(e.coeff))], [e.expr]
        if is_nc(e):
            return [], [e]
        return [e], []

    def rec(e):
        if isinstance(e, Add):
            return simplify_expression(Add(*(rec(t) for t in e.terms)))
        if isinstance(e, ScalarMul):
            return simplify_expression(ScalarMul(e.coeff, rec(e.expr)))
        if isinstance(e, Product):
            return simplify_expression(Product(*(rec(f) for f in e.factors)))
        if isinstance(e, NCProduct):
            scalar_factors=[]; chain=[]
            for f in e.factors:
                scalars, ncs = split_factor(f)
                scalar_factors.extend(scalars)
                for n in ncs:
                    if isinstance(n, NCProduct): chain.extend(n.factors)
                    else: chain.append(n)
            core = Symbol("1") if not chain else (chain[0] if len(chain)==1 else NCProduct(*chain))
            if not scalar_factors:
                return core
            return simplify_expression(Product(*scalar_factors, core))
        if isinstance(e, Fraction):
            return Fraction(rec(e.numerator), rec(e.denominator))
        if isinstance(e, Power):
            return Power(rec(e.base), e.exponent)
        if isinstance(e, SpinorSandwich):
            return SpinorSandwich(rec(e.operator), e.outgoing, e.incoming)
        return e

    return rec(expr)
