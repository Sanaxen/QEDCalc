from qedcalc import parse_latex, render_latex, Fraction
from qedcalc.operations.propagator import recognize_propagators, scalarize_fermion_propagators, separate_numerator_denominator

def test_fermion_scalarization():
    e = parse_latex(r"\frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon}")
    e = scalarize_fermion_propagators(recognize_propagators(e))
    assert isinstance(e, Fraction)
    out = render_latex(e)
    assert r"m^{2}" in out
    assert r"\rlap{/}p" in out
    assert r"\rlap{/}k" in out

def test_separate_fraction_product():
    e = parse_latex(r"\gamma^\rho\frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon}\gamma_\rho")
    e = scalarize_fermion_propagators(recognize_propagators(e))
    e = separate_numerator_denominator(e)
    assert isinstance(e, Fraction)
    out = render_latex(e)
    assert r"\gamma^{\rho}" in out and r"\gamma_{\rho}" in out
