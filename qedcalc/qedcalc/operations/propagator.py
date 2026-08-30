from qedcalc.core.expression import (
    Fraction, Symbol, Metric, FermionPropagator, PhotonPropagator,
    ScalarMul, Add, Product, NCProduct, Slash, Vector, Power, DiracTrace
)

def recognize_propagators(expr):
    """Recognize common propagator-shaped fractions without altering display algebra."""
    if isinstance(expr, Fraction):
        if isinstance(expr.numerator, Symbol) and expr.numerator.name == "1":
            # A scalar photon denominator such as 1/(-k^2-i eps) must not
            # be mistaken for a fermion propagator.  Require both the mass
            # symbol and a Feynman slash in the denominator.
            has_mass = any(isinstance(n, Symbol) and n.name == "m" for n in expr.denominator.walk())
            has_slash = any(isinstance(n, Slash) for n in expr.denominator.walk())
            if has_mass and has_slash:
                return FermionPropagator(expr.denominator)
            return expr
        if isinstance(expr.numerator, Metric):
            return PhotonPropagator(expr.numerator, expr.denominator)
        return expr
    if isinstance(expr, DiracTrace): return DiracTrace(recognize_propagators(expr.argument))
    if isinstance(expr, Add): return Add(*(recognize_propagators(t) for t in expr.terms))
    if isinstance(expr, NCProduct): return NCProduct(*(recognize_propagators(f) for f in expr.factors))
    if isinstance(expr, ScalarMul): return ScalarMul(expr.coeff, recognize_propagators(expr.expr))
    return expr

def _signed_slash(term):
    if isinstance(term, Slash) and isinstance(term.arg, Vector):
        return 1, term.arg
    if isinstance(term, ScalarMul) and term.coeff == -1 and isinstance(term.expr, Slash) and isinstance(term.expr.arg, Vector):
        return -1, term.expr.arg
    return None

def _neg_expr(expr):
    if isinstance(expr, ScalarMul) and expr.coeff == -1:
        return expr.expr
    return ScalarMul(-1, expr)

def scalarize_fermion_propagator(prop: FermionPropagator):
    """
    Convert 1/(m + slash(X) - i eps) into
    (m - slash(X))/(m^2 - X^2 - i eps).

    v0.4 handles X as a linear sum of individually slashed momenta.
    """
    den = prop.denominator
    terms = den.terms if isinstance(den, Add) else (den,)
    mass = None
    x_terms = []
    remainder = []

    for t in terms:
        if isinstance(t, Symbol) and t.name == "m" and mass is None:
            mass = t
            continue
        sv = _signed_slash(t)
        if sv:
            sign, vec = sv
            x_terms.append(vec if sign == 1 else ScalarMul(-1, vec))
            continue
        remainder.append(t)

    if mass is None or not x_terms:
        return prop

    x = x_terms[0] if len(x_terms) == 1 else Add(*x_terms)
    numerator_terms = [mass]
    for t in x_terms:
        if isinstance(t, ScalarMul) and t.coeff == -1:
            numerator_terms.append(Slash(t.expr))
        else:
            numerator_terms.append(ScalarMul(-1, Slash(t)))
    numerator = Add(*numerator_terms)

    scalar_den_terms = [Power(mass, 2), ScalarMul(-1, Power(x, 2))]
    scalar_den_terms.extend(remainder)
    scalar_den = Add(*scalar_den_terms)
    return Fraction(numerator, scalar_den)

def scalarize_fermion_propagators(expr):
    if isinstance(expr, FermionPropagator):
        return scalarize_fermion_propagator(expr)
    if isinstance(expr, PhotonPropagator):
        return Fraction(expr.numerator, expr.denominator)
    if isinstance(expr, DiracTrace): return DiracTrace(scalarize_fermion_propagators(expr.argument))
    if isinstance(expr, Add): return Add(*(scalarize_fermion_propagators(t) for t in expr.terms))
    if isinstance(expr, NCProduct): return NCProduct(*(scalarize_fermion_propagators(f) for f in expr.factors))
    if isinstance(expr, ScalarMul): return ScalarMul(expr.coeff, scalarize_fermion_propagators(expr.expr))
    return expr

def separate_numerator_denominator(expr):
    """Collect top-level fraction factors into one numerator and denominator."""
    factors = expr.factors if isinstance(expr, NCProduct) else (expr,)
    num_factors, den_factors = [], []
    overall_sign = 1

    for f in factors:
        if isinstance(f, Fraction):
            num_factors.append(f.numerator)
            den_factors.append(f.denominator)
        elif isinstance(f, ScalarMul) and f.coeff == -1 and isinstance(f.expr, Fraction):
            overall_sign *= -1
            num_factors.append(f.expr.numerator)
            den_factors.append(f.expr.denominator)
        else:
            num_factors.append(f)

    numerator = num_factors[0] if len(num_factors) == 1 else NCProduct(*num_factors)
    if overall_sign == -1:
        numerator = ScalarMul(-1, numerator)
    if not den_factors:
        denominator = Symbol("1")
    else:
        denominator = den_factors[0] if len(den_factors) == 1 else Product(*den_factors)
    return Fraction(numerator, denominator)
