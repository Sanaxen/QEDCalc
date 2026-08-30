from qedcalc import render_latex
from qedcalc.core.expression import Symbol
from qedcalc.operations.counterterm import qed_counterterm_library, counterterm_contribution


def test_internal_counterterm_identifiers_render_as_qed_latex():
    assert render_latex(Symbol("deltaZ1")) == r"\delta Z_{1}"
    assert render_latex(Symbol("deltaZ2")) == r"\delta Z_{2}"
    assert render_latex(Symbol("deltaZ3")) == r"\delta Z_{3}"
    assert render_latex(Symbol("delta_m")) == r"\delta m"


def test_plain_greek_internal_names_render_with_backslash():
    assert render_latex(Symbol("zeta")) == r"\zeta"
    assert render_latex(Symbol("eta")) == r"\eta"
    assert render_latex(Symbol("omega")) == r"\omega"


def test_qed_counterterm_library_uses_conventional_latex():
    lib = qed_counterterm_library()
    assert r"\delta Z_{1}" in render_latex(counterterm_contribution(lib["vertex"]))
    assert r"\delta Z_{2}" in render_latex(counterterm_contribution(lib["electron_wavefunction"]))
    assert render_latex(counterterm_contribution(lib["mass"])) == r"\delta m"
    assert r"\delta Z_{3}" in render_latex(counterterm_contribution(lib["photon_wavefunction"]))


def test_symbolic_scalarmul_coefficient_does_not_crash_inside_product():
    from qedcalc.core.expression import ScalarMul, Product, Symbol, Gamma, Index
    from qedcalc.latex.renderer import render_latex
    expr = Product(Symbol('A'), ScalarMul(Symbol('deltaZ1'), Gamma(Index('mu','down'))))
    text = render_latex(expr)
    assert r'\delta Z_{1}' in text
