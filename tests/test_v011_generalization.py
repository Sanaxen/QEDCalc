import sympy as sp

from qedcalc import render_latex
from qedcalc.core.expression import (
    Symbol, Vector, Index, Gamma, Slash, ScalarProduct, Add, Product,
    NCProduct, ScalarMul, Power, Fraction
)
from qedcalc.operations.denominator import feynman_parameterize_powers
from qedcalc.operations.multiloop import complete_multiloop_square, shift_multiloop_momenta_in_numerator
from qedcalc.operations.integral import euclidean_scalar_loop_integral, dimensional_regularized_loop_series
from qedcalc.operations.counterterm import (
    make_counterterm, replace_factor_with_counterterm, insert_counterterm_factor
)


def test_general_feynman_parameterization_infers_powers():
    expr = Fraction(
        Symbol("N"),
        Product(Power(Symbol("D1"), 2), Symbol("D2"), Power(Symbol("D3"), 3)),
    )
    out = feynman_parameterize_powers(expr)
    assert out.exponents == (2, 1, 3)
    assert out.total_power == 6
    # Gamma(6)/(Gamma(2)Gamma(1)Gamma(3)) = 5!/(1!*0!*2!) = 60
    assert render_latex(out.prefactor) == "60"
    text = render_latex(out)
    assert "x1" in text and "x3" not in text  # x3 is dependent simplex coordinate
    assert "6" in text


def test_general_feynman_parameterization_explicit_exponents():
    expr = Fraction(Symbol("1"), Product(Symbol("A"), Symbol("B")))
    out = feynman_parameterize_powers(expr, exponents=(2, 2), parameters=("u",))
    assert out.total_power == 4
    assert out.exponents == (2, 2)
    assert render_latex(out.prefactor) == "6"
    assert "u" in render_latex(out.parameter_weight)


def test_euclidean_d_dimensional_scalar_integral_known_case():
    D, Delta = sp.symbols("D Delta", positive=True)
    out = euclidean_scalar_loop_integral(3, 0, D, Delta)
    expected = sp.pi**(D/2) * Delta**(D/2-3) * sp.gamma(3-D/2) / sp.gamma(3)
    assert sp.simplify(out - expected) == 0


def test_dimreg_series_has_uv_pole_for_n2_d4():
    eps, Delta = sp.symbols("epsilon Delta", positive=True)
    series = dimensional_regularized_loop_series(2, 0, eps, Delta, order=0)
    assert sp.simplify(series.removeO().coeff(eps, -1) - sp.pi**2) == 0


def test_simultaneous_multiloop_numerator_shift():
    k, l, p, q = map(Vector, ("k", "l", "p", "q"))
    quad = Add(
        ScalarMul(-1, ScalarProduct(k,k)),
        ScalarMul(-1, ScalarProduct(l,l)),
        ScalarProduct(k,l),
        ScalarMul(2, ScalarProduct(k,p)),
        ScalarMul(4, ScalarProduct(l,q)),
        Symbol("m"),
    )
    completed = complete_multiloop_square(quad, ("k", "l"))
    numerator = NCProduct(Slash(k), Gamma(Index("mu", "down")), Slash(l))
    shifted = shift_multiloop_momenta_in_numerator(numerator, completed, ("ell1", "ell2"))
    text = render_latex(shifted)
    assert "ell1" in text and "ell2" in text
    assert r"\rlap{/}k" not in text and r"\rlap{/}l" not in text


def test_counterterm_explicit_replace_and_insert():
    mu = Index("mu", "down")
    chain = NCProduct(Gamma(Index("rho", "up")), Gamma(mu), Gamma(Index("rho", "down")))
    ct = make_counterterm("delta_Z1", Symbol("deltaZ1"), Gamma(mu), 1)
    replaced = replace_factor_with_counterterm(chain, 1, ct)
    inserted = insert_counterterm_factor(chain, 1, ct, before=True)
    assert r"\delta Z_{1}" in render_latex(replaced.result)
    assert len(inserted.result.factors) == 4
    assert replaced.mode == "replace"
    assert inserted.mode == "insert_before"
