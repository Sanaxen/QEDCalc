from qedcalc import parse_latex, render_latex


def test_negative_factor_in_product_is_grouped():
    expr = parse_latex(
        r"\gamma^\sigma(-\frac{g_{\rho\sigma}}{-k^2-i\varepsilon})"
    )
    out = render_latex(expr)
    assert r"\gamma^{\sigma}\,\left(-\frac{" in out
    assert r"\gamma^{\sigma}\,-" not in out
