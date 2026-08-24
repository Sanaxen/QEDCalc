import sympy as sp

from qedcalc import render_latex
from qedcalc.config import load_symbol_table
from qedcalc.core.expression import (
    Symbol, Vector, Index, VectorComponent, ScalarProduct, Add, Product,
    ScalarMul, Power, Fraction, Gamma
)
from qedcalc.operations.multiloop import (
    declare_loop_momenta, complete_multiloop_square, shifted_multiloop_denominator
)
from qedcalc.operations.loop import symmetric_rank4
from qedcalc.operations.denominator import feynman_parameterize_n
from qedcalc.operations.dimreg import extract_laurent_poles, pole_coefficient
from qedcalc.operations.counterterm import make_counterterm, counterterm_contribution


def test_declare_multiple_loop_momenta():
    table = load_symbol_table()
    loops = declare_loop_momenta(table, ("k", "l"))
    assert [v.name for v in loops.momenta] == ["k", "l"]


def test_two_loop_quadratic_square_completion_matrix():
    # -k^2 - l^2 + k.l + 2 k.p + 4 l.q + C
    k,l,p,q = map(Vector, ("k","l","p","q"))
    expr = Add(
        ScalarMul(-1, ScalarProduct(k,k)),
        ScalarMul(-1, ScalarProduct(l,l)),
        ScalarProduct(k,l),
        ScalarMul(2, ScalarProduct(k,p)),
        ScalarMul(4, ScalarProduct(l,q)),
        Symbol("m"),
    )
    out = complete_multiloop_square(expr, ("k","l"))
    assert len(out.matrix) == 2
    assert len(out.shifts) == 2
    shifted = shifted_multiloop_denominator(out, ("ell1","ell2"))
    text = render_latex(shifted)
    assert "ell1" in text and "ell2" in text


def test_rank4_symmetric_tensor_average_d4():
    idx = [Index(x,"up") for x in ("mu","nu","rho","sigma")]
    l = Vector("l")
    expr = Product(*(VectorComponent(l,i) for i in idx))
    out = symmetric_rank4(expr, "l", 4)
    text = render_latex(out)
    assert "1/24" in text or "24" in text
    assert "g_" in text


def test_n_denominator_feynman_parameterization():
    den = Product(Symbol("D1"), Symbol("D2"), Symbol("D3"), Symbol("D4"), Symbol("D5"))
    out = feynman_parameterize_n(Fraction(Symbol("N"), den))
    assert out.power == 5
    assert out.prefactor == 24
    assert len(out.parameters) == 4
    assert r"\Delta_{4}" in render_latex(out)


def test_dimreg_uv_pole_extraction():
    eps = Symbol("epsilon_UV")
    expr = Add(
        Product(Symbol("A"), Power(eps,-2)),
        Product(Symbol("B"), Power(eps,-1)),
        Symbol("C"),
    )
    out = extract_laurent_poles(expr, "epsilon_UV", "UV", 2)
    assert len(out.poles) == 2
    assert pole_coefficient(out,"UV",2) == Symbol("A")
    assert pole_coefficient(out,"UV",1) == Symbol("B")
    text = render_latex(out)
    assert r"\epsilon_{\mathrm{UV}}" in text


def test_counterterm_object_keeps_structure_explicit():
    mu = Index("mu","down")
    ct = make_counterterm("delta_Z1", Symbol("deltaZ1"), Gamma(mu), 1)
    contrib = counterterm_contribution(ct)
    text = render_latex(contrib)
    assert r"\delta Z_{1}" in text and r"\gamma_{\mu}" in text
    labeled = render_latex(ct)
    assert "delta" in labeled and r"\gamma_{\mu}" in labeled
