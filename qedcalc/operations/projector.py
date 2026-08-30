from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Index, Gamma, VectorComponent,
    Add, Product, ScalarMul, PauliTerm, FormFactorDecomposition
)
from qedcalc.operations.simplify import simplify_expression


def gordon_rhs(index="mu", outgoing="p'", incoming="p", q="q", mass="m"):
    """Return the RHS of (p'+p)_mu = 2m gamma_mu - i sigma_{mu nu} q^nu."""
    idx=Index(index,"down")
    return Add(
        ScalarMul(2,Product(Symbol(mass),Gamma(idx))),
        ScalarMul(-1,PauliTerm(idx,Vector(q)))
    )


def gordon_reduce_pair_coefficient(pair_coefficient: QEDExpr, index="mu", q="q", mass="m"):
    """Apply Gordon reduction to B (p'+p)_mu.

    Returns B[2m gamma_mu - i sigma_{mu nu}q^nu].
    """
    B=pair_coefficient; idx=Index(index,"down")
    return simplify_expression(Add(
        Product(B,ScalarMul(2,Product(Symbol(mass),Gamma(idx)))),
        Product(B,ScalarMul(-1,PauliTerm(idx,Vector(q))))
    ))


def extract_f2_from_gordon_basis(pair_coefficient: QEDExpr, mass="m"):
    """Extract F2 from A gamma_mu + B (p'+p)_mu.

    With the convention
      Gamma_mu = gamma_mu F1 + i sigma_{mu nu}q^nu/(2m) F2
    and
      (p'+p)_mu = 2m gamma_mu - i sigma_{mu nu}q^nu,
    one obtains F2 = -2m B.
    """
    return simplify_expression(ScalarMul(-2,Product(Symbol(mass),pair_coefficient)))


def form_factors_from_gordon_basis(gamma_coefficient: QEDExpr, pair_coefficient: QEDExpr,
                                    index="mu", q="q", mass="m"):
    """Convert A gamma_mu + B(p'+p)_mu into F1,F2 coefficients."""
    m=Symbol(mass)
    f1=simplify_expression(Add(gamma_coefficient,ScalarMul(2,Product(m,pair_coefficient))))
    f2=extract_f2_from_gordon_basis(pair_coefficient,mass)
    return FormFactorDecomposition(Index(index,"down"),Vector(q),f1,f2,m)


def _target_coefficient(term: QEDExpr, target: QEDExpr):
    """Return the commutative coefficient multiplying one exact basis target."""
    if term == target:
        return Symbol("1")
    if isinstance(term, ScalarMul):
        if term.expr == target:
            return Symbol(str(term.coeff))
        inner=_target_coefficient(term.expr,target)
        if inner is not None:
            return ScalarMul(term.coeff,inner)
        return None
    if isinstance(term, Product):
        matches=[i for i,f in enumerate(term.factors) if f==target]
        if len(matches)==1:
            i=matches[0]
            rest=[f for j,f in enumerate(term.factors) if j!=i]
            if not rest: return Symbol("1")
            return rest[0] if len(rest)==1 else Product(*rest)
    return None


def decompose_gordon_basis(expr: QEDExpr, index="mu", outgoing="p'", incoming="p"):
    """Decompose a clean current A gamma_mu + B(p'+p)_mu.

    The expression must already have been reduced to the three supported
    basis objects gamma_mu, p'_mu and p_mu. Any other current structure is
    rejected rather than guessed.
    """
    idx=Index(index,"down")
    gamma=Gamma(idx)
    pout=VectorComponent(Vector(outgoing),idx)
    pin=VectorComponent(Vector(incoming),idx)
    terms=list(expr.terms) if isinstance(expr,Add) else [expr]
    cg=[]; co=[]; ci=[]; unknown=[]
    for t in terms:
        c=_target_coefficient(t,gamma)
        if c is not None: cg.append(c); continue
        c=_target_coefficient(t,pout)
        if c is not None: co.append(c); continue
        c=_target_coefficient(t,pin)
        if c is not None: ci.append(c); continue
        unknown.append(t)
    if unknown:
        raise ValueError("Current is not yet in the supported Gordon basis: gamma_mu, p'_mu, p_mu.")
    zero=Symbol("0")
    def total(xs):
        if not xs: return zero
        return simplify_expression(xs[0] if len(xs)==1 else Add(*xs))
    A=total(cg); Bo=total(co); Bi=total(ci)
    if Bo != Bi:
        raise ValueError("Coefficients of p'_mu and p_mu differ; the current is not B(p'+p)_mu.")
    return A,Bo


def project_f2_gordon_basis(expr: QEDExpr, index="mu", outgoing="p'", incoming="p", mass="m"):
    """Extract F2 from an already reduced A gamma_mu + B(p'+p)_mu current."""
    _,B=decompose_gordon_basis(expr,index,outgoing,incoming)
    return extract_f2_from_gordon_basis(B,mass)
