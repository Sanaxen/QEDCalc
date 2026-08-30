from qedcalc import render_latex
from qedcalc.core.expression import (
    Symbol, Vector, Index, Gamma, Slash, ScalarProduct, VectorComponent,
    Add, Product, NCProduct
)
from qedcalc.operations.momentum import introduce_q, take_q_zero
from qedcalc.operations.spinor import sandwich, reduce_external_dirac
from qedcalc.operations.projector import (
    gordon_rhs, extract_f2_from_gordon_basis, form_factors_from_gordon_basis
)


def test_introduce_q_vector_component_and_slash():
    expr=Add(VectorComponent(Vector("p'"),Index("mu","down")), Slash(Vector("p'")))
    out=introduce_q(expr)
    text=render_latex(out)
    assert r"p_{\mu}" in text
    assert r"q_{\mu}" in text
    assert r"\rlap{/}p" in text
    assert r"\rlap{/}q" in text


def test_take_q_zero():
    expr=Add(VectorComponent(Vector("q"),Index("mu","down")), ScalarProduct(Vector("p"),Vector("q")), Gamma(Index("mu","down")))
    out=take_q_zero(expr)
    assert render_latex(out)==r"\gamma_{\mu}"


def test_external_dirac_equations_after_commutation():
    mu=Index("mu","down")
    op=NCProduct(Slash(Vector("p'")),Gamma(mu),Slash(Vector("p")))
    out=reduce_external_dirac(sandwich(op))
    text=render_latex(out)
    assert r"m\,m" in text
    assert r"\gamma_{\mu}" in text
    assert r"\rlap{/}p" not in text


def test_incoming_slash_is_commuted_to_right():
    mu=Index("mu","down")
    op=NCProduct(Slash(Vector("p")),Gamma(mu))
    out=reduce_external_dirac(sandwich(op))
    text=render_latex(out)
    assert r"p_{\mu}" in text
    assert r"m" in text
    assert r"\gamma_{\mu}" in text


def test_gordon_rhs_and_f2_convention():
    rhs=render_latex(gordon_rhs())
    assert r"2" in rhs and r"\gamma_{\mu}" in rhs
    assert r"i\sigma_{\mu\nu}q^{\nu}" in rhs
    B=Symbol("B")
    f2=render_latex(extract_f2_from_gordon_basis(B))
    assert "-2" in f2 and "m" in f2 and "B" in f2


def test_form_factor_decomposition_rendering():
    ff=form_factors_from_gordon_basis(Symbol("A"),Symbol("B"))
    text=render_latex(ff)
    assert r"\gamma_{\mu}" in text
    assert r"\frac{i\sigma_{\mu\nu}q^{\nu}}{2m}" in text


def test_clean_gordon_basis_decomposition_and_projection():
    from qedcalc.operations.projector import decompose_gordon_basis, project_f2_gordon_basis
    A=Symbol("A"); B=Symbol("B"); idx=Index("mu","down")
    current=Add(
        Product(A,Gamma(idx)),
        Product(B,VectorComponent(Vector("p'"),idx)),
        Product(B,VectorComponent(Vector("p"),idx)),
    )
    a,b=decompose_gordon_basis(current)
    assert a==A and b==B
    text=render_latex(project_f2_gordon_basis(current))
    assert "-2" in text and "m" in text and "B" in text
