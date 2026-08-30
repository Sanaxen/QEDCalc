from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Add, Product, ScalarMul, ScalarProduct,
    FeynmanParamIntegral
)
from qedcalc.operations.denominator import distribute_scalar_products


def _contains_vector(sp, name):
    return isinstance(sp, ScalarProduct) and (
        isinstance(sp.left, Vector) and sp.left.name == name or
        isinstance(sp.right, Vector) and sp.right.name == name
    )


def collect_loop_terms(expr: QEDExpr, loop_momentum="k"):
    """Classify an expanded scalar denominator into k^2, k-linear and constant terms.

    This returns a dictionary instead of silently performing a shift.  It is
    intended as an inspection/verification step before complete_square().
    """
    if isinstance(expr, FeynmanParamIntegral):
        expr = expr.combined_denominator
    expr = distribute_scalar_products(expr)
    terms = expr.terms if isinstance(expr, Add) else (expr,)
    result = {"quadratic": [], "linear": [], "constant": []}
    for t in terms:
        nodes = list(t.walk()) if hasattr(t, "walk") else [t]
        sps = [n for n in nodes if isinstance(n, ScalarProduct)]
        if any(isinstance(sp.left, Vector) and isinstance(sp.right, Vector) and
               sp.left.name == loop_momentum and sp.right.name == loop_momentum for sp in sps):
            result["quadratic"].append(t)
        elif any(_contains_vector(sp, loop_momentum) for sp in sps):
            result["linear"].append(t)
        else:
            result["constant"].append(t)
    return result


def _extract_linear_coeff(term, loop_momentum):
    """Return coefficient and external vector from 2*c*(v.k), if recognized."""
    numeric = 1
    base = term
    if isinstance(base, ScalarMul):
        numeric = base.coeff
        base = base.expr
    factors = list(base.factors) if isinstance(base, Product) else [base]
    sp = next((f for f in factors if isinstance(f, ScalarProduct)), None)
    if sp is None:
        return None
    if isinstance(sp.left, Vector) and sp.left.name == loop_momentum and isinstance(sp.right, Vector):
        ext = sp.right
    elif isinstance(sp.right, Vector) and sp.right.name == loop_momentum and isinstance(sp.left, Vector):
        ext = sp.left
    else:
        return None
    coeff_factors = [f for f in factors if f is not sp]
    coeff = Symbol("1") if not coeff_factors else (coeff_factors[0] if len(coeff_factors)==1 else Product(*coeff_factors))
    # linear term is 2 A.k for the current -k^2 convention
    if numeric != 2:
        return None
    return coeff, ext


def complete_square(expr: QEDExpr, loop_momentum="k"):
    """Complete the square for the current one-loop denominator convention.

    Recognizes
        -k^2 + 2 c1 v1.k + 2 c2 v2.k + C
    and returns
        -(k-A)^2 + A^2 + C,
    where A = c1 v1 + c2 v2.
    """
    from qedcalc.core.expression import VectorLinearCombination, CompletedSquare, Power
    from qedcalc.operations.simplify import expand_commutative, simplify_expression

    if isinstance(expr, FeynmanParamIntegral):
        expr = expr.combined_denominator
    expr = expand_commutative(expr)
    terms = list(expr.terms) if isinstance(expr, Add) else [expr]

    quadratic_found = False
    linear = []
    remainder_terms = []
    for t in terms:
        numeric = t.coeff if isinstance(t, ScalarMul) else 1
        base = t.expr if isinstance(t, ScalarMul) else t
        if (numeric == -1 and isinstance(base, ScalarProduct) and
            isinstance(base.left, Vector) and isinstance(base.right, Vector) and
            base.left.name == loop_momentum and base.right.name == loop_momentum):
            quadratic_found = True
            continue
        item = _extract_linear_coeff(t, loop_momentum)
        if item is not None:
            linear.append(item)
            continue
        remainder_terms.append(t)

    if not quadratic_found:
        raise ValueError(f"No -{loop_momentum}^2 term was found for square completion.")
    if not linear:
        raise ValueError(f"No linear {loop_momentum} term was found for square completion.")

    shift = VectorLinearCombination(tuple(linear))
    square_terms = []
    for i, (ci, vi) in enumerate(linear):
        square_terms.append(Product(Power(ci, 2), ScalarProduct(vi, vi)))
        for cj, vj in linear[i+1:]:
            square_terms.append(ScalarMul(2, Product(ci, cj, ScalarProduct(vi, vj))))
    a2 = simplify_expression(Add(*square_terms))
    rem0 = Symbol("0") if not remainder_terms else (remainder_terms[0] if len(remainder_terms)==1 else Add(*remainder_terms))
    remainder = simplify_expression(Add(a2, rem0))
    return CompletedSquare(Vector(loop_momentum), shift, remainder, -1)


def shift_loop_momentum(completed, new_loop="l"):
    """Represent the substitution l = k - A after complete_square()."""
    from qedcalc.core.expression import CompletedSquare, Vector
    if not isinstance(completed, CompletedSquare):
        raise TypeError("shift_loop_momentum expects a CompletedSquare expression.")
    # After l = k - A, only -l^2 + remainder remains in the denominator.
    return Add(ScalarMul(-1, ScalarProduct(Vector(new_loop), Vector(new_loop))), completed.remainder)
