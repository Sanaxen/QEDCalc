from sympy import Rational
from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Index, Gamma, Slash, VectorComponent, ScalarProduct,
    Add, Product, NCProduct, ScalarMul, Fraction, Power, Metric,
    VectorLinearCombination
)
from qedcalc.operations.simplify import simplify_expression, expand_commutative


def shift_loop_momentum_in_numerator(expr: QEDExpr, completed, new_loop="l"):
    """Apply k = l + A to numerator structures after square completion.

    Supported loop-dependent structures are Slash(k), k_mu and scalar
    products involving k.  The first implementation is sufficient for the
    one-loop vertex numerator workflow.
    """
    old = completed.loop.name
    shift = completed.shift
    lvec = Vector(new_loop)

    def shift_slash():
        terms = [Slash(lvec)]
        for coeff, vec in shift.terms:
            terms.append(Product(coeff, Slash(vec)))
        return Add(*terms)

    def shift_component(index):
        terms = [VectorComponent(lvec, index)]
        for coeff, vec in shift.terms:
            terms.append(Product(coeff, VectorComponent(vec, index)))
        return Add(*terms)

    def rec(e):
        if isinstance(e, Slash) and isinstance(e.arg, Vector) and e.arg.name == old:
            return shift_slash()
        if isinstance(e, VectorComponent) and isinstance(e.vector, Vector) and e.vector.name == old:
            return shift_component(e.index)
        if isinstance(e, ScalarProduct):
            left, right = e.left, e.right
            # Scalar products involving k are expanded bilinearly.
            left_is = isinstance(left, Vector) and left.name == old
            right_is = isinstance(right, Vector) and right.name == old
            if left_is or right_is:
                left_terms = [(Symbol("1"), lvec)] + list(shift.terms) if left_is else [(Symbol("1"), left)]
                right_terms = [(Symbol("1"), lvec)] + list(shift.terms) if right_is else [(Symbol("1"), right)]
                terms=[]
                for ca, va in left_terms:
                    for cb, vb in right_terms:
                        coeff = Product(ca, cb)
                        terms.append(Product(coeff, ScalarProduct(va, vb)))
                return expand_commutative(Add(*terms))
            return e
        if isinstance(e, Add): return Add(*(rec(t) for t in e.terms))
        if isinstance(e, Product): return Product(*(rec(f) for f in e.factors))
        if isinstance(e, NCProduct): return NCProduct(*(rec(f) for f in e.factors))
        if isinstance(e, ScalarMul): return ScalarMul(e.coeff, rec(e.expr))
        if isinstance(e, Fraction): return Fraction(rec(e.numerator), rec(e.denominator))
        if isinstance(e, Power): return Power(rec(e.base), e.exponent)
        return e

    return simplify_expression(rec(expr))


def _loop_degree(expr: QEDExpr, loop="l"):
    """Count explicit loop-vector factors in a monomial."""
    if isinstance(expr, Slash) and isinstance(expr.arg, Vector) and expr.arg.name == loop:
        return 1
    if isinstance(expr, VectorComponent) and isinstance(expr.vector, Vector) and expr.vector.name == loop:
        return 1
    if isinstance(expr, ScalarProduct):
        n=0
        if isinstance(expr.left, Vector) and expr.left.name == loop: n += 1
        if isinstance(expr.right, Vector) and expr.right.name == loop: n += 1
        return n
    if isinstance(expr, (Product, NCProduct)):
        return sum(_loop_degree(f, loop) for f in expr.factors)
    if isinstance(expr, ScalarMul): return _loop_degree(expr.expr, loop)
    return 0


def drop_odd_loop_terms(expr: QEDExpr, loop="l"):
    """Drop monomials odd under l -> -l for a symmetric loop integral."""
    if isinstance(expr, Add):
        kept=[]
        for t in expr.terms:
            t=drop_odd_loop_terms(t, loop)
            if not (isinstance(t, Symbol) and t.name == "0"):
                kept.append(t)
        if not kept: return Symbol("0")
        return kept[0] if len(kept)==1 else Add(*kept)
    if isinstance(expr, ScalarMul):
        inner = drop_odd_loop_terms(expr.expr, loop)
        if isinstance(inner, Symbol) and inner.name == "0":
            return inner
        return ScalarMul(expr.coeff, inner)
    # At this point expr is a monomial.  Test its total loop degree before
    # recursively touching factors, because an odd monomial must vanish as a whole.
    if _loop_degree(expr, loop) % 2 == 1:
        return Symbol("0")
    return expr


def symmetric_rank2(expr: QEDExpr, loop="l"):
    """Apply selected four-dimensional rank-2 symmetric-integration rules.

    Rules include
        /l gamma_mu /l -> -(1/2) l^2 gamma_mu
    under the symmetric integral, and
        l^mu l^nu -> (1/4) g^{mu nu} l^2.
    """
    lvec=Vector(loop)
    l2=ScalarProduct(lvec,lvec)
    if isinstance(expr, Add):
        return Add(*(symmetric_rank2(t,loop) for t in expr.terms))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, symmetric_rank2(expr.expr,loop))
    if isinstance(expr, Product):
        fs=list(expr.factors)
        # component pair inside a commutative product
        comps=[(i,f) for i,f in enumerate(fs) if isinstance(f,VectorComponent) and isinstance(f.vector,Vector) and f.vector.name==loop]
        if len(comps)>=2:
            (i,a),(j,b)=comps[0],comps[1]
            repl=ScalarMul(Rational(1,4), Product(Metric(a.index,b.index),l2))
            new=[f for n,f in enumerate(fs) if n not in (i,j)] + [repl]
            return simplify_expression(Product(*new))
        return Product(*(symmetric_rank2(f,loop) for f in fs))
    if isinstance(expr, NCProduct):
        fs=list(expr.factors)
        for i in range(len(fs)-2):
            a,b,c=fs[i:i+3]
            if (isinstance(a,Slash) and isinstance(a.arg,Vector) and a.arg.name==loop and
                isinstance(b,Gamma) and isinstance(c,Slash) and isinstance(c.arg,Vector) and c.arg.name==loop):
                repl=ScalarMul(Rational(-1,2), Product(l2,b))
                new=fs[:i]+[repl]+fs[i+3:]
                return simplify_expression(NCProduct(*new) if len(new)>1 else new[0])
        return NCProduct(*(symmetric_rank2(f,loop) for f in fs))
    return expr



def symmetric_rank4(expr: QEDExpr, loop="l", dimension=4):
    """Apply the isotropic rank-4 tensor average.

    l^mu l^nu l^rho l^sigma ->
      l^4/[D(D+2)] * (g^{mu nu}g^{rho sigma}
                    + g^{mu rho}g^{nu sigma}
                    + g^{mu sigma}g^{nu rho}).

    The current implementation recognizes four VectorComponent factors inside
    a commutative Product.  D=4 gives the coefficient 1/24.
    """
    from sympy import Rational
    if dimension <= 0:
        raise ValueError("dimension must be positive.")
    lvec = Vector(loop)
    l2 = ScalarProduct(lvec, lvec)
    coeff = Rational(1, dimension * (dimension + 2))

    if isinstance(expr, Add):
        return Add(*(symmetric_rank4(t, loop, dimension) for t in expr.terms))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, symmetric_rank4(expr.expr, loop, dimension))
    if isinstance(expr, Product):
        fs = list(expr.factors)
        comps = [(i, f) for i, f in enumerate(fs)
                 if isinstance(f, VectorComponent)
                 and isinstance(f.vector, Vector)
                 and f.vector.name == loop]
        if len(comps) >= 4:
            selected = comps[:4]
            indices = [item.index for _, item in selected]
            remove = {i for i, _ in selected}
            mu, nu, rho, sigma = indices
            metric_sum = Add(
                Product(Metric(mu, nu), Metric(rho, sigma)),
                Product(Metric(mu, rho), Metric(nu, sigma)),
                Product(Metric(mu, sigma), Metric(nu, rho)),
            )
            repl = ScalarMul(coeff, Product(Power(l2, 2), metric_sum))
            new = [f for i, f in enumerate(fs) if i not in remove] + [repl]
            return simplify_expression(Product(*new))
        return Product(*(symmetric_rank4(f, loop, dimension) for f in fs))
    return expr


def _pairings(items):
    """Return all unordered complete pairings of an even-length sequence."""
    items = tuple(items)
    if not items:
        return ((),)
    if len(items) % 2:
        raise ValueError("A complete pairing requires an even number of items.")
    first = items[0]
    out = []
    for i in range(1, len(items)):
        second = items[i]
        rest = items[1:i] + items[i+1:]
        for tail in _pairings(rest):
            out.append(((first, second),) + tail)
    return tuple(out)


def symmetric_even_rank(expr: QEDExpr, loop="l", dimension=4, rank=None):
    r"""Apply the isotropic tensor reduction for any even tensor rank.

    For rank 2n,

      l^{mu1}...l^{mu(2n)} ->
        (l^2)^n / [D(D+2)...(D+2n-2)]
        times the sum over all complete metric pairings.

    The implementation currently recognizes VectorComponent factors of the
    selected loop momentum inside a commutative Product.  If ``rank`` is not
    supplied, all matching components in the monomial are reduced and their
    number must be even.  ``dimension`` may be a positive integer or a SymPy
    scalar expression such as ``4-2*epsilon``.
    """
    import sympy as sp

    D = sp.sympify(dimension)
    if D.is_number and D.is_positive is False:
        raise ValueError("dimension must be positive.")
    if rank is not None and (rank < 2 or rank % 2):
        raise ValueError("rank must be a positive even integer of at least 2.")

    lvec = Vector(loop)
    l2 = ScalarProduct(lvec, lvec)

    if isinstance(expr, Add):
        return Add(*(symmetric_even_rank(t, loop, dimension, rank) for t in expr.terms))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, symmetric_even_rank(expr.expr, loop, dimension, rank))
    if not isinstance(expr, Product):
        return expr

    fs = list(expr.factors)
    comps = [(i, f) for i, f in enumerate(fs)
             if isinstance(f, VectorComponent)
             and isinstance(f.vector, Vector)
             and f.vector.name == loop]

    selected_rank = len(comps) if rank is None else rank
    if selected_rank == 0:
        return Product(*(symmetric_even_rank(f, loop, dimension, rank) for f in fs))
    if selected_rank % 2:
        raise ValueError("The selected loop tensor rank is odd; symmetric even-rank reduction is not applicable.")
    if len(comps) < selected_rank:
        return expr

    selected = comps[:selected_rank]
    indices = [item.index for _, item in selected]
    remove = {i for i, _ in selected}
    n = selected_rank // 2

    denominator = sp.Integer(1)
    for j in range(n):
        denominator *= D + 2*j
    coeff = sp.simplify(1 / denominator)

    pairing_terms = []
    for pairing in _pairings(indices):
        metrics = [Metric(a, b) for a, b in pairing]
        pairing_terms.append(Product(*metrics))
    metric_sum = pairing_terms[0] if len(pairing_terms) == 1 else Add(*pairing_terms)

    repl = ScalarMul(coeff, Product(Power(l2, n), metric_sum))
    new = [f for i, f in enumerate(fs) if i not in remove] + [repl]
    return simplify_expression(Product(*new))
