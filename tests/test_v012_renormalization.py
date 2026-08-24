import sympy as sp

from qedcalc import render_latex
from qedcalc.core.expression import (
    Symbol, Vector, Index, VectorComponent, Product, Power, ScalarProduct
)
from qedcalc.operations.loop import symmetric_even_rank
from qedcalc.operations.renormalization import (
    dimreg_scale_factor, renormalized_dimreg_series
)
from qedcalc.operations.dimreg import bookkeep_uv_ir
from qedcalc.operations.counterterm import qed_counterterm_library, counterterm_contribution


def test_general_even_rank6_d4_has_15_pairings_and_1_over_192():
    names = ("mu", "nu", "rho", "sigma", "alpha", "beta")
    idx = [Index(n, "up") for n in names]
    l = Vector("l")
    expr = Product(*(VectorComponent(l, i) for i in idx))
    out = symmetric_even_rank(expr, "l", 4)
    text = render_latex(out)
    assert "192" in text  # 4*6*8
    # rank six has 15 complete pairings; renderer should therefore have 45 metric index occurrences.
    assert text.count("g_{") == 45  # 15 pairings, 3 metric tensors per pairing
    assert "l\\cdot l" in text


def test_general_even_rank_symbolic_dimension():
    idx = [Index(n, "up") for n in ("mu", "nu", "rho", "sigma")]
    l = Vector("l")
    expr = Product(*(VectorComponent(l, i) for i in idx))
    D = sp.Symbol("D")
    out = symmetric_even_rank(expr, "l", D)
    text = render_latex(out)
    assert "D" in text
    assert "D + 2" in text or "D+2" in text


def test_msbar_scale_factor_convention():
    eps, mu = sp.symbols("epsilon mu", positive=True)
    f = dimreg_scale_factor(2, eps, mu, "MSbar")
    expected = mu**(4*eps) * (4*sp.pi*sp.exp(-sp.EulerGamma))**(2*eps)
    assert sp.simplify(f/expected - 1) == 0


def test_ms_scale_factor_has_no_msbar_constant():
    eps, mu = sp.symbols("epsilon mu", positive=True)
    f = dimreg_scale_factor(1, eps, mu, "MS")
    assert sp.simplify(f - mu**(2*eps)) == 0


def test_renormalized_series_subtracts_poles():
    eps = sp.Symbol("epsilon")
    expr = 1/eps + 3 + 2*eps
    out = renormalized_dimreg_series(expr, 1, eps, sp.Integer(1), "MS", expansion_order=1)
    assert sp.simplify(out["pole_part"] - 1/eps) == 0
    assert sp.simplify(out["subtracted"] - (3 + 2*eps)) == 0


def test_uv_ir_bookkeeping_separates_mixed_terms():
    u, r = sp.symbols("epsilon_UV epsilon_IR")
    expr = 2/u**2 + 3/r + 5/(u*r) + 7 + 11*u
    out = bookkeep_uv_ir(expr)
    assert sp.simplify(sum(out.uv_terms) - 2/u**2) == 0
    assert sp.simplify(sum(out.ir_terms) - 3/r) == 0
    assert sp.simplify(sum(out.mixed_terms) - 5/(u*r)) == 0
    assert out.finite == 7
    assert out.regular_remainder == 11*u


def test_qed_counterterm_library_has_four_standard_entries():
    lib = qed_counterterm_library()
    assert set(lib) == {"vertex", "electron_wavefunction", "mass", "photon_wavefunction"}
    assert r"\delta Z_{1}" in render_latex(counterterm_contribution(lib["vertex"]))
    assert r"\delta Z_{2}" in render_latex(counterterm_contribution(lib["electron_wavefunction"]))
    assert r"\delta m" in render_latex(counterterm_contribution(lib["mass"]))
    photon = render_latex(counterterm_contribution(lib["photon_wavefunction"]))
    assert r"\delta Z_{3}" in photon and "g_{" in photon
