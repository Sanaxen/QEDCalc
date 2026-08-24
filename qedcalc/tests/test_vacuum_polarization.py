import sympy as sp
from qedcalc import parse_latex, Symbol, Vector, Index, Gamma, Slash, Add, NCProduct
from qedcalc.operations.dirac import dirac_trace_4d
from qedcalc.operations.vacuum_polarization import (
    vp_gminus2_double_integrand,
    vp_z_integrated_kernel,
    vp_numeric_coefficient,
    vp_recognize_analytic,
    vp_expected_analytic,
)


def test_vp_electron_loop_trace_has_expected_basic_terms():
    expr = parse_latex(r"(m+\rlap{/}l+\rlap{/}k)\gamma^\alpha(m+\rlap{/}l)\gamma^\beta")
    result = dirac_trace_4d(expr)
    text = repr(result)
    assert "Metric" in text
    assert "VectorComponent" in text
    assert "ScalarProduct" in text


def test_vp_double_kernel_is_finite_at_small_x_series():
    x, z = sp.symbols("x z", positive=True)
    kernel = vp_gminus2_double_integrand(x, z)
    series = sp.series(kernel, x, 0, 4).removeO()
    assert not series.has(sp.zoo, sp.oo, -sp.oo)


def test_vp_z_kernel_reference_formula():
    x = sp.symbols("x", positive=True)
    H = vp_z_integrated_kernel(x)
    assert sp.simplify(H - (
        3*x**3*sp.log(1-x)-5*x**3-12*x**2-18*x*sp.log(1-x)+12*x+12*sp.log(1-x)
    )/(9*x**3)) == 0


def test_vp_numeric_recognition():
    value = vp_numeric_coefficient(28)
    recognized = vp_recognize_analytic(value, 28)
    assert sp.simplify(recognized - vp_expected_analytic()) == 0
