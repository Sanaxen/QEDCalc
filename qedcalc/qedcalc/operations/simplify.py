from qedcalc.core.expression import (
    QEDExpr, Symbol, Add, Product, NCProduct, ScalarMul, Fraction, Power
)


def simplify_expression(expr: QEDExpr):
    """Conservative structural simplifier.

    It combines numeric signs, removes factors of one and zero, flattens
    products/additions, and cancels exact opposite additive terms.  It does
    not reorder NCProduct factors.
    """
    if isinstance(expr, Fraction):
        return Fraction(simplify_expression(expr.numerator), simplify_expression(expr.denominator))
    if isinstance(expr, ScalarMul):
        inner = simplify_expression(expr.expr)
        c = expr.coeff
        if c == 0:
            return Symbol("0")
        if c == 1:
            return inner
        if isinstance(inner, ScalarMul):
            return simplify_expression(ScalarMul(c * inner.coeff, inner.expr))
        if isinstance(inner, Symbol) and inner.name == "0":
            return inner
        return ScalarMul(c, inner)
    if isinstance(expr, Product):
        factors=[]; coeff=1
        for f in expr.factors:
            f=simplify_expression(f)
            if isinstance(f, Symbol) and f.name == "0": return f
            if isinstance(f, Symbol) and f.name == "1": continue
            if isinstance(f, Symbol):
                try:
                    coeff *= int(f.name)
                    continue
                except ValueError:
                    pass
            if isinstance(f, ScalarMul):
                coeff *= f.coeff; f=f.expr
                if isinstance(f, Symbol) and f.name == "0": return f
                if isinstance(f, Symbol) and f.name == "1": continue
            if isinstance(f, Product): factors.extend(f.factors)
            else: factors.append(f)
        if not factors: return Symbol(str(coeff))
        base=factors[0] if len(factors)==1 else Product(*factors)
        return base if coeff==1 else ScalarMul(coeff, base)
    if isinstance(expr, NCProduct):
        factors=[]; coeff=1
        for f in expr.factors:
            f=simplify_expression(f)
            if isinstance(f, Symbol) and f.name == "0": return f
            if isinstance(f, Symbol) and f.name == "1": continue
            if isinstance(f, Symbol):
                try:
                    coeff *= int(f.name)
                    continue
                except ValueError:
                    pass
            if isinstance(f, ScalarMul):
                coeff *= f.coeff; f=f.expr
                if isinstance(f, Symbol) and f.name == "0": return f
                if isinstance(f, Symbol) and f.name == "1": continue
            factors.append(f)
        if not factors: return Symbol(str(coeff))
        base=factors[0] if len(factors)==1 else NCProduct(*factors)
        return base if coeff==1 else ScalarMul(coeff, base)
    if isinstance(expr, Add):
        terms=[]
        for t in expr.terms:
            t=simplify_expression(t)
            if isinstance(t, Symbol) and t.name == "0": continue
            if isinstance(t, Add): terms.extend(t.terms)
            else: terms.append(t)
        # Exact cancellation A + (-A).
        used=[False]*len(terms); kept=[]
        for i,t in enumerate(terms):
            if used[i]: continue
            target = t.expr if isinstance(t, ScalarMul) and t.coeff == -1 else ScalarMul(-1,t)
            found=False
            for j in range(i+1,len(terms)):
                if not used[j] and terms[j] == target:
                    used[j]=True; found=True; break
                if isinstance(target, ScalarMul) and target.coeff == -1 and isinstance(terms[j], ScalarMul) and terms[j].coeff == -1 and terms[j].expr == t:
                    used[j]=True; found=True; break
            if not found: kept.append(t)
        if not kept: return Symbol("0")
        return kept[0] if len(kept)==1 else Add(*kept)
    return expr


def expand_commutative(expr: QEDExpr):
    """Expand Product/ScalarMul over Add while preserving NCProduct order."""
    if isinstance(expr, Add):
        return simplify_expression(Add(*(expand_commutative(t) for t in expr.terms)))
    if isinstance(expr, ScalarMul):
        inner=expand_commutative(expr.expr)
        if isinstance(inner, Add):
            return simplify_expression(Add(*(expand_commutative(ScalarMul(expr.coeff,t)) for t in inner.terms)))
        return simplify_expression(ScalarMul(expr.coeff, inner))
    if isinstance(expr, Product):
        factors=[expand_commutative(f) for f in expr.factors]
        for i,f in enumerate(factors):
            if isinstance(f, Add):
                return simplify_expression(Add(*(expand_commutative(Product(*(factors[:i]+[t]+factors[i+1:]))) for t in f.terms)))
        return simplify_expression(Product(*factors))
    if isinstance(expr, Fraction):
        return Fraction(expand_commutative(expr.numerator), expand_commutative(expr.denominator))
    return simplify_expression(expr)
