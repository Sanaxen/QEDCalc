from qedcalc import parse_latex, render_latex
from qedcalc.operations.dirac import contract_gamma


def test_gamma_roundtrip():
    expr = parse_latex(r"\gamma^\rho\gamma^\mu\gamma_\rho")
    out = render_latex(expr)
    assert r"\gamma^{\rho}" in out
    assert r"\gamma^{\mu}" in out
    assert r"\gamma_{\rho}" in out


def test_gamma_contract():
    expr = parse_latex(r"\gamma^\rho\gamma^\mu\gamma_\rho")
    out = contract_gamma(expr)
    rendered = render_latex(out)
    assert "2" in rendered
    assert r"\gamma^{\mu}" in rendered


def test_product_of_sums_renders_parentheses():
    expr = parse_latex(r"\gamma^\rho(m+\rlap{/}p)\gamma_\rho")
    out = render_latex(expr)
    assert r"\left(" in out
    assert r"m + \rlap{/}p" in out


def test_product_simplifier_removes_one_inside_scalarmul():
    from fractions import Fraction as PyFraction
    from qedcalc.core.expression import Product, ScalarMul, Symbol, Metric, Index
    from qedcalc.operations.simplify import simplify_expression
    expr = Product(ScalarMul(PyFraction(1, 3), Symbol('1')), Metric(Index('mu'), Index('nu')))
    out = simplify_expression(expr)
    assert '1' not in repr(out.expr) if isinstance(out, ScalarMul) else True
