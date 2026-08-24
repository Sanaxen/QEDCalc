from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Index, Gamma, Slash, VectorComponent, ScalarProduct,
    Add, Product, NCProduct, ScalarMul, Fraction, Power, SpinorSandwich
)
from qedcalc.operations.algebra import expand_expression
from qedcalc.operations.simplify import simplify_expression


def sandwich(expr: QEDExpr, outgoing="p'", incoming="p"):
    return SpinorSandwich(expr, Vector(outgoing), Vector(incoming))


def _chain(*parts):
    fs=[]
    for p in parts:
        if p is None: continue
        if isinstance(p,(list,tuple)): fs.extend(p)
        else: fs.append(p)
    if not fs: return Symbol("1")
    return fs[0] if len(fs)==1 else NCProduct(*fs)


def _anticommutator_term(a, b):
    """Return the scalar/tensor term in {a,b}=2(...), for gamma-like a,b."""
    if isinstance(a,Slash) and isinstance(b,Gamma):
        return VectorComponent(a.arg,b.index)
    if isinstance(a,Gamma) and isinstance(b,Slash):
        return VectorComponent(b.arg,a.index)
    if isinstance(a,Slash) and isinstance(b,Slash):
        return ScalarProduct(a.arg,b.arg)
    return None


def _rewrite_external_once(expr: QEDExpr, outgoing="p'", incoming="p"):
    """Move one external slash one position toward its on-shell spinor."""
    if isinstance(expr,Add):
        for i,t in enumerate(expr.terms):
            nt=_rewrite_external_once(t,outgoing,incoming)
            if nt != t:
                terms=list(expr.terms); terms[i]=nt
                return Add(*terms)
        return expr
    if isinstance(expr,ScalarMul):
        inner=_rewrite_external_once(expr.expr,outgoing,incoming)
        return ScalarMul(expr.coeff,inner) if inner != expr.expr else expr
    if isinstance(expr,Product):
        for i,f in enumerate(expr.factors):
            nf=_rewrite_external_once(f,outgoing,incoming)
            if nf != f:
                fs=list(expr.factors); fs[i]=nf
                return Product(*fs)
        return expr
    if not isinstance(expr,NCProduct): return expr

    fs=list(expr.factors)
    # Move incoming slash to the right.
    for i in range(len(fs)-1):
        a,b=fs[i],fs[i+1]
        if isinstance(a,Slash) and isinstance(a.arg,Vector) and a.arg.name==incoming:
            anti=_anticommutator_term(a,b)
            if anti is not None:
                prefix=fs[:i]; suffix=fs[i+2:]
                first=_chain(prefix, ScalarMul(2,anti), suffix)
                second=ScalarMul(-1,_chain(prefix,b,a,suffix))
                return Add(first,second)
    # Move outgoing slash to the left.
    for i in range(1,len(fs)):
        a,b=fs[i-1],fs[i]
        if isinstance(b,Slash) and isinstance(b.arg,Vector) and b.arg.name==outgoing:
            anti=_anticommutator_term(a,b)
            if anti is not None:
                prefix=fs[:i-1]; suffix=fs[i+1:]
                first=_chain(prefix, ScalarMul(2,anti), suffix)
                second=ScalarMul(-1,_chain(prefix,b,a,suffix))
                return Add(first,second)
    return expr


def commute_external_slashes(expr: QEDExpr, outgoing="p'", incoming="p", max_steps=64):
    """Use gamma anticommutation to move external slashes to spinor-adjacent edges."""
    cur=expr
    for _ in range(max_steps):
        nxt=simplify_expression(expand_expression(_rewrite_external_once(cur,outgoing,incoming)))
        if nxt==cur: return cur
        cur=nxt
    raise RuntimeError("External-slash anticommutation did not converge.")


def _apply_edge_dirac(expr: QEDExpr, outgoing="p'", incoming="p", mass="m"):
    if isinstance(expr,Add): return simplify_expression(Add(*(_apply_edge_dirac(t,outgoing,incoming,mass) for t in expr.terms)))
    if isinstance(expr,ScalarMul): return simplify_expression(ScalarMul(expr.coeff,_apply_edge_dirac(expr.expr,outgoing,incoming,mass)))
    if isinstance(expr,Product): return simplify_expression(Product(*(_apply_edge_dirac(f,outgoing,incoming,mass) for f in expr.factors)))
    if not isinstance(expr,NCProduct):
        if isinstance(expr,Slash) and isinstance(expr.arg,Vector) and expr.arg.name in (outgoing,incoming):
            return Symbol(mass)
        return expr
    fs=list(expr.factors); m=Symbol(mass); coeff=[]
    if fs and isinstance(fs[0],Slash) and isinstance(fs[0].arg,Vector) and fs[0].arg.name==outgoing:
        fs=fs[1:]; coeff.append(m)
    if fs and isinstance(fs[-1],Slash) and isinstance(fs[-1].arg,Vector) and fs[-1].arg.name==incoming:
        fs=fs[:-1]; coeff.append(m)
    core=_chain(fs)
    if coeff:
        return simplify_expression(Product(*coeff,core))
    return expr


def apply_dirac_equations(s: SpinorSandwich, mass="m"):
    """Apply on-shell Dirac equations only at the external spinor edges."""
    if not isinstance(s,SpinorSandwich):
        raise TypeError("apply_dirac_equations() requires a SpinorSandwich.")
    op=_apply_edge_dirac(s.operator,s.outgoing.name,s.incoming.name,mass)
    return SpinorSandwich(simplify_expression(op),s.outgoing,s.incoming)


def reduce_external_dirac(s: SpinorSandwich, mass="m"):
    """Commute external slashes to the edges, then apply both Dirac equations."""
    if not isinstance(s,SpinorSandwich):
        raise TypeError("reduce_external_dirac() requires a SpinorSandwich.")
    moved=commute_external_slashes(s.operator,s.outgoing.name,s.incoming.name)
    return apply_dirac_equations(SpinorSandwich(moved,s.outgoing,s.incoming),mass)


def _apply_post_q_edge_dirac(expr: QEDExpr, incoming="p", q="q", mass="m"):
    """Apply external Dirac equations after p' = p + q has been introduced.

    Between bar u(p') and u(p), the edge rules are

        /p u(p) = m u(p),
        bar u(p') /p = bar u(p') (m - /q),

    because /p' = /p + /q and bar u(p') /p' = m bar u(p').
    """
    if isinstance(expr, Add):
        return simplify_expression(Add(*(_apply_post_q_edge_dirac(t, incoming, q, mass) for t in expr.terms)))
    if isinstance(expr, ScalarMul):
        return simplify_expression(ScalarMul(expr.coeff, _apply_post_q_edge_dirac(expr.expr, incoming, q, mass)))
    if isinstance(expr, Product):
        return simplify_expression(Product(*(_apply_post_q_edge_dirac(f, incoming, q, mass) for f in expr.factors)))
    if not isinstance(expr, NCProduct):
        return expr

    fs = list(expr.factors)
    m = Symbol(mass)
    changed = False

    # Incoming slash at the right edge.
    if fs and isinstance(fs[-1], Slash) and isinstance(fs[-1].arg, Vector) and fs[-1].arg.name == incoming:
        fs = fs[:-1]
        core = _chain(fs)
        return simplify_expression(Product(m, core))

    # At the left edge, bar u(p') /p = bar u(p') (m - /q).
    if fs and isinstance(fs[0], Slash) and isinstance(fs[0].arg, Vector) and fs[0].arg.name == incoming:
        rest = _chain(fs[1:])
        mass_term = Product(m, rest)
        q_term = ScalarMul(-1, _chain(Slash(Vector(q)), rest))
        return simplify_expression(Add(mass_term, q_term))

    return expr


def commute_incoming_slash_after_q(expr: QEDExpr, incoming="p", max_steps=64):
    """Move /p toward either external spinor after p' = p + q substitution.

    The routine reuses the anticommutation relations.  A /p at the right edge
    is immediately on shell.  A /p at the left edge is converted with
    bar u(p') /p = bar u(p') (m - /q) by reduce_external_dirac_after_q().
    """
    cur = expr
    for _ in range(max_steps):
        if isinstance(cur, Add):
            nxt = simplify_expression(Add(*(commute_incoming_slash_after_q(t, incoming, 1) for t in cur.terms)))
            if nxt == cur:
                return cur
            cur = nxt
            continue
        nxt = _rewrite_external_once(cur, outgoing="__no_outgoing__", incoming=incoming)
        nxt = simplify_expression(expand_expression(nxt))
        if nxt == cur:
            return cur
        cur = nxt
    raise RuntimeError("Post-q incoming-slash anticommutation did not converge.")


def reduce_external_dirac_after_q(s: SpinorSandwich, incoming="p", q="q", mass="m", max_steps=64):
    """Reduce /p factors after q = p' - p has been introduced.

    This is a second-stage reducer for an operator that no longer contains
    explicit p'.  It repeatedly moves /p to an external edge and applies the
    appropriate incoming/outgoing on-shell relation, leaving /q explicit.
    """
    if not isinstance(s, SpinorSandwich):
        raise TypeError("reduce_external_dirac_after_q() requires a SpinorSandwich.")

    cur = s.operator
    for _ in range(max_steps):
        moved = commute_incoming_slash_after_q(cur, incoming=incoming, max_steps=64)
        reduced = _apply_post_q_edge_dirac(moved, incoming=incoming, q=q, mass=mass)
        reduced = simplify_expression(expand_expression(reduced))
        if reduced == cur:
            return SpinorSandwich(reduced, s.outgoing, s.incoming)
        cur = reduced
    raise RuntimeError("Post-q external Dirac reduction did not converge.")


def reduce_external_dirac_exact(s: SpinorSandwich, mass="m"):
    """Deterministically reduce external /p' and /p in Dirac chains.

    Unlike the older iterative mover, this routine uses a recursive measure
    that strictly decreases whenever an external slash is commuted toward its
    spinor.  It is therefore suitable for the expanded one-loop numerator.
    Commutative scalar factors should preferably be normalized out of NCProduct
    chains beforehand with normalize_noncommutative_products().
    """
    if not isinstance(s, SpinorSandwich):
        raise TypeError("reduce_external_dirac_exact() requires a SpinorSandwich.")
    outgoing = s.outgoing.name
    incoming = s.incoming.name
    m = Symbol(mass)

    def chain(fs):
        fs = list(fs)
        if not fs:
            return Symbol("1")

        # Apply edge equations first.
        if isinstance(fs[0], Slash) and isinstance(fs[0].arg, Vector) and fs[0].arg.name == outgoing:
            return simplify_expression(Product(m, chain(fs[1:])))
        if isinstance(fs[-1], Slash) and isinstance(fs[-1].arg, Vector) and fs[-1].arg.name == incoming:
            return simplify_expression(Product(m, chain(fs[:-1])))

        # Move the nearest outgoing slash left by one position.
        for i in range(1, len(fs)):
            b = fs[i]
            if isinstance(b, Slash) and isinstance(b.arg, Vector) and b.arg.name == outgoing:
                a = fs[i-1]
                anti = _anticommutator_term(a, b)
                if anti is None:
                    continue
                prefix = fs[:i-1]
                suffix = fs[i+1:]
                first = Product(ScalarMul(2, anti), chain(prefix + suffix))
                second = ScalarMul(-1, chain(prefix + [b, a] + suffix))
                return simplify_expression(expand_expression(Add(first, second)))

        # Move the nearest incoming slash right by one position.
        for i in range(len(fs)-1):
            a = fs[i]
            if isinstance(a, Slash) and isinstance(a.arg, Vector) and a.arg.name == incoming:
                b = fs[i+1]
                anti = _anticommutator_term(a, b)
                if anti is None:
                    continue
                prefix = fs[:i]
                suffix = fs[i+2:]
                first = Product(ScalarMul(2, anti), chain(prefix + suffix))
                second = ScalarMul(-1, chain(prefix + [b, a] + suffix))
                return simplify_expression(expand_expression(Add(first, second)))

        return fs[0] if len(fs) == 1 else NCProduct(*fs)

    def rec(e):
        if isinstance(e, Add):
            return simplify_expression(Add(*(rec(t) for t in e.terms)))
        if isinstance(e, ScalarMul):
            return simplify_expression(ScalarMul(e.coeff, rec(e.expr)))
        if isinstance(e, Product):
            return simplify_expression(Product(*(rec(f) for f in e.factors)))
        if isinstance(e, NCProduct):
            return chain(e.factors)
        return e

    return SpinorSandwich(simplify_expression(expand_expression(rec(s.operator))), s.outgoing, s.incoming)
