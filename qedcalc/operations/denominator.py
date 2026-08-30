from math import factorial
from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, Add, Product, NCProduct, ScalarMul, Power,
    ScalarProduct, Fraction, FeynmanParamIntegral
)


def _signed_vector(term):
    if isinstance(term, Vector):
        return 1, term
    if isinstance(term, ScalarMul) and isinstance(term.expr, Vector):
        return term.coeff, term.expr
    return None


def _mul_coeff_expr(coeff, expr):
    if coeff == 1:
        return expr
    if coeff == -1:
        return ScalarMul(-1, expr)
    return ScalarMul(coeff, expr)


def expand_vector_square(expr: QEDExpr):
    """Expand (a +/- b +/- ...)^2 into Lorentz scalar products."""
    if isinstance(expr, Power) and expr.exponent == 2 and isinstance(expr.base, Add):
        vec_terms = []
        other_terms = []
        for t in expr.base.terms:
            sv = _signed_vector(t)
            if sv is None:
                other_terms.append(t)
            else:
                vec_terms.append(sv)
        if vec_terms and not other_terms:
            out = []
            for i, (ci, vi) in enumerate(vec_terms):
                out.append(_mul_coeff_expr(ci * ci, ScalarProduct(vi, vi)))
                for cj, vj in vec_terms[i + 1:]:
                    out.append(_mul_coeff_expr(2 * ci * cj, ScalarProduct(vi, vj)))
            return Add(*out)
    if isinstance(expr, Add):
        return Add(*(expand_vector_square(t) for t in expr.terms))
    if isinstance(expr, Product):
        return Product(*(expand_vector_square(f) for f in expr.factors))
    if isinstance(expr, NCProduct):
        return NCProduct(*(expand_vector_square(f) for f in expr.factors))
    if isinstance(expr, ScalarMul):
        return ScalarMul(expr.coeff, expand_vector_square(expr.expr))
    if isinstance(expr, Fraction):
        return Fraction(expand_vector_square(expr.numerator), expand_vector_square(expr.denominator))
    return expr


def expand_denominator(expr: QEDExpr):
    """Expand vector squares in scalar denominators."""
    return expand_vector_square(expr)


def feynman_parameterize(expr: Fraction, parameters=("x", "y")):
    """Feynman-parameterize a fraction with exactly three denominator factors.

    1/(D1 D2 D3) -> 2 int_0^1 dx int_0^(1-x) dy /
                       [x D1 + y D2 + (1-x-y) D3]^3
    The numerator is preserved.
    """
    den = expr.denominator
    factors = den.factors if isinstance(den, Product) else (den,)
    if len(factors) != 3:
        raise ValueError("feynman_parameterize currently requires exactly three denominator factors.")
    if len(parameters) != 2:
        raise ValueError("The current three-denominator implementation requires two independent parameters.")
    x, y = (Symbol(parameters[0]), Symbol(parameters[1]))
    one_minus = Add(Symbol("1"), ScalarMul(-1, x), ScalarMul(-1, y))
    combined = Add(
        Product(x, factors[0]),
        Product(y, factors[1]),
        Product(one_minus, factors[2]),
    )
    return FeynmanParamIntegral((x, y), expr.numerator, combined, 3, factorial(2))


def distribute_scalar_products(expr: QEDExpr):
    """Distribute commutative scalar products over sums."""
    from qedcalc.operations.simplify import expand_commutative
    return expand_commutative(expr)



def feynman_parameterize_n(expr: Fraction, parameters=None):
    """Feynman-parameterize N denominator factors of unit power.

    1/(D1...DN) = (N-1)! * integral_simplex dx1...dx_{N-1}
                   / [x1 D1 + ... + xN DN]^N,
    with xN = 1 - x1 - ... - x_{N-1}.

    This function is intended as the multi-loop foundation.  Repeated powers
    and non-unit propagator exponents will be added separately.
    """
    den = expr.denominator
    factors = den.factors if isinstance(den, Product) else (den,)
    n = len(factors)
    if n < 2:
        raise ValueError("feynman_parameterize_n requires at least two denominator factors.")
    if parameters is None:
        parameters = tuple(f"x{i+1}" for i in range(n-1))
    if len(parameters) != n-1:
        raise ValueError("N denominator factors require N-1 independent simplex parameters.")
    pars = tuple(Symbol(x) for x in parameters)
    last = Add(Symbol("1"), *(ScalarMul(-1, x) for x in pars))
    weights = list(pars) + [last]
    combined = Add(*(Product(w, d) for w, d in zip(weights, factors)))
    return FeynmanParamIntegral(pars, expr.numerator, combined, n, factorial(n-1))


def feynman_parameterize_powers(expr: Fraction, exponents=None, parameters=None):
    """Feynman-parameterize arbitrary positive integer denominator powers.

    For A = sum_i a_i,

      1 / prod_i D_i^{a_i}
        = Gamma(A)/prod_i Gamma(a_i)
          * int_simplex prod_i x_i^{a_i-1}
            / (sum_i x_i D_i)^A.

    The implementation currently accepts positive integer exponents.  Powers
    may be supplied explicitly or inferred from positive Power(...) factors.
    """
    from qedcalc.core.expression import GeneralFeynmanParamIntegral, Fraction as QFraction

    if not isinstance(expr, Fraction):
        raise TypeError("feynman_parameterize_powers expects a Fraction expression.")

    den = expr.denominator
    raw_factors = den.factors if isinstance(den, Product) else (den,)
    bases = []
    inferred = []
    for factor in raw_factors:
        if isinstance(factor, Power):
            if not isinstance(factor.exponent, int) or factor.exponent <= 0:
                raise ValueError("Denominator powers must be positive integers.")
            bases.append(factor.base)
            inferred.append(factor.exponent)
        else:
            bases.append(factor)
            inferred.append(1)

    if exponents is None:
        exponents = tuple(inferred)
    else:
        exponents = tuple(exponents)
        if len(exponents) != len(bases):
            raise ValueError("The exponent list must match the number of denominator factors.")
        if any((not isinstance(a, int) or a <= 0) for a in exponents):
            raise ValueError("All denominator exponents must be positive integers.")

    n = len(bases)
    if n < 2:
        raise ValueError("At least two denominator factors are required.")
    if parameters is None:
        parameters = tuple(f"x{i+1}" for i in range(n-1))
    if len(parameters) != n - 1:
        raise ValueError("N denominator factors require N-1 independent simplex parameters.")

    pars = tuple(Symbol(x) for x in parameters)
    last = Add(Symbol("1"), *(ScalarMul(-1, x) for x in pars))
    weights = list(pars) + [last]
    combined = Add(*(Product(w, d) for w, d in zip(weights, bases)))

    weight_terms = []
    for x, a in zip(weights, exponents):
        if a == 1:
            continue
        weight_terms.append(Power(x, a - 1))
    parameter_weight = Symbol("1") if not weight_terms else (
        weight_terms[0] if len(weight_terms) == 1 else Product(*weight_terms)
    )

    total = sum(exponents)
    pref_num = factorial(total - 1)
    pref_den = 1
    for a in exponents:
        pref_den *= factorial(a - 1)
    from math import gcd
    g = gcd(pref_num, pref_den)
    pref_num //= g
    pref_den //= g
    if pref_den == 1:
        prefactor = Symbol(str(pref_num))
    else:
        prefactor = QFraction(Symbol(str(pref_num)), Symbol(str(pref_den)))

    return GeneralFeynmanParamIntegral(
        pars,
        expr.numerator,
        combined,
        total,
        tuple(exponents),
        parameter_weight,
        prefactor,
    )
