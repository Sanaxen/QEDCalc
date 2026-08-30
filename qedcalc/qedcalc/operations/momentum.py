from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Slash, VectorComponent, ScalarProduct,
    Add, Product, NCProduct, ScalarMul, Fraction, Power, Metric,
    SpinorSandwich
)
from qedcalc.operations.simplify import expand_commutative, simplify_expression


def substitute_vector(expr: QEDExpr, name: str, replacement: QEDExpr):
    """Substitute a four-vector and expand vector-linear structures.

    The replacement may be a Vector or an Add of vector terms. Scalar
    products are expanded bilinearly. Non-commutative factor order is kept.
    """
    def vec_terms(v):
        if isinstance(v, Vector):
            return [(Symbol("1"), v)]
        if isinstance(v, Add):
            out=[]
            for t in v.terms:
                if isinstance(t, Vector):
                    out.append((Symbol("1"), t))
                elif isinstance(t, Product):
                    vectors=[f for f in t.factors if isinstance(f, Vector)]
                    if len(vectors) == 1:
                        coeffs=[f for f in t.factors if f is not vectors[0]]
                        coeff=Product(*coeffs) if len(coeffs)>1 else (coeffs[0] if coeffs else Symbol("1"))
                        out.append((coeff, vectors[0]))
                    else:
                        raise ValueError("Vector replacement contains an unsupported product.")
                elif isinstance(t, ScalarMul) and isinstance(t.expr, Vector):
                    out.append((Symbol(str(t.coeff)), t.expr))
                else:
                    raise ValueError("Vector replacement must be linear in vectors.")
            return out
        raise ValueError("Vector replacement must be a vector or a linear vector sum.")

    repl_terms = vec_terms(replacement)

    def rec(e):
        if isinstance(e, Vector) and e.name == name:
            return replacement
        if isinstance(e, Slash) and isinstance(e.arg, Vector) and e.arg.name == name:
            terms=[]
            for c,v in repl_terms:
                term=Slash(v)
                terms.append(term if isinstance(c,Symbol) and c.name=="1" else Product(c,term))
            return terms[0] if len(terms)==1 else Add(*terms)
        if isinstance(e, VectorComponent) and isinstance(e.vector, Vector) and e.vector.name == name:
            terms=[]
            for c,v in repl_terms:
                term=VectorComponent(v,e.index)
                terms.append(term if isinstance(c,Symbol) and c.name=="1" else Product(c,term))
            return terms[0] if len(terms)==1 else Add(*terms)
        if isinstance(e, ScalarProduct):
            left_repl = isinstance(e.left,Vector) and e.left.name==name
            right_repl = isinstance(e.right,Vector) and e.right.name==name
            if left_repl or right_repl:
                lt = repl_terms if left_repl else [(Symbol("1"), e.left)]
                rt = repl_terms if right_repl else [(Symbol("1"), e.right)]
                terms=[]
                for ca,va in lt:
                    for cb,vb in rt:
                        factors=[]
                        if not (isinstance(ca,Symbol) and ca.name=="1"): factors.append(ca)
                        if not (isinstance(cb,Symbol) and cb.name=="1"): factors.append(cb)
                        factors.append(ScalarProduct(va,vb))
                        terms.append(Product(*factors) if len(factors)>1 else factors[0])
                return expand_commutative(Add(*terms)) if len(terms)>1 else terms[0]
            return ScalarProduct(rec(e.left),rec(e.right))
        if isinstance(e, Add): return simplify_expression(Add(*(rec(t) for t in e.terms)))
        if isinstance(e, Product): return expand_commutative(Product(*(rec(f) for f in e.factors)))
        if isinstance(e, NCProduct): return NCProduct(*(rec(f) for f in e.factors))
        if isinstance(e, ScalarMul): return simplify_expression(ScalarMul(e.coeff,rec(e.expr)))
        if isinstance(e, Fraction): return Fraction(rec(e.numerator),rec(e.denominator))
        if isinstance(e, Power): return Power(rec(e.base),e.exponent)
        if isinstance(e, Metric): return e
        if isinstance(e, SpinorSandwich):
            # Momentum labels of the external spinors are deliberately not
            # changed here; the substitution acts on the operator only.
            return SpinorSandwich(rec(e.operator), e.outgoing, e.incoming)
        return e
    return simplify_expression(rec(expr))


def introduce_q(expr: QEDExpr, outgoing="p'", incoming="p", q="q"):
    """Introduce q = p' - p by substituting p' = p + q in the expression."""
    return substitute_vector(expr, outgoing, Add(Vector(incoming), Vector(q)))


def take_q_zero(expr: QEDExpr, q="q"):
    """Set the momentum-transfer vector q to zero structurally."""
    qv=Vector(q)
    def rec(e):
        if isinstance(e, Vector) and e.name==q: return Symbol("0")
        if isinstance(e, Slash) and isinstance(e.arg,Vector) and e.arg.name==q: return Symbol("0")
        if isinstance(e, VectorComponent) and isinstance(e.vector,Vector) and e.vector.name==q: return Symbol("0")
        if isinstance(e, ScalarProduct):
            if (isinstance(e.left,Vector) and e.left.name==q) or (isinstance(e.right,Vector) and e.right.name==q):
                return Symbol("0")
            return e
        if isinstance(e,Add): return simplify_expression(Add(*(rec(t) for t in e.terms)))
        if isinstance(e,Product): return simplify_expression(Product(*(rec(f) for f in e.factors)))
        if isinstance(e,NCProduct): return simplify_expression(NCProduct(*(rec(f) for f in e.factors)))
        if isinstance(e,ScalarMul): return simplify_expression(ScalarMul(e.coeff,rec(e.expr)))
        if isinstance(e,Fraction): return Fraction(rec(e.numerator),rec(e.denominator))
        if isinstance(e,Power): return Power(rec(e.base),e.exponent)
        if isinstance(e,SpinorSandwich): return SpinorSandwich(rec(e.operator),e.outgoing,e.incoming)
        return e
    return simplify_expression(rec(expr))
