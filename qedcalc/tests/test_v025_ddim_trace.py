import sympy as sp
from qedcalc.core.expression import Gamma, Slash, Index, Vector, NCProduct, ScalarProduct, Product, Metric, VectorComponent
from qedcalc.operations.dirac import dirac_trace_ddim
from qedcalc.operations.lorentz import contract_fully_scalar_lorentz
from qedcalc.latex.renderer import render_latex


def test_ddim_trace_six_gamma_supported():
    inds=[Index(x,'up') for x in ('a','b','c','d','e','f')]
    expr=NCProduct(*(Gamma(i) for i in inds))
    out=dirac_trace_ddim(expr)
    # six-gamma trace has 15 metric-pairing terms
    assert len(out.terms) == 15


def test_ddim_trace_slash_four():
    p,q,r,s=(Vector(x) for x in ('p','q','r','s'))
    out=contract_fully_scalar_lorentz(dirac_trace_ddim(NCProduct(Slash(p),Slash(q),Slash(r),Slash(s))))
    text=render_latex(out)
    assert 'p\\cdot q' in text
    assert 'r\\cdot s' in text
    assert 'p\\cdot r' in text


def test_closed_metric_loop_gives_D():
    a=Index('a','up'); ad=Index('a','down')
    out=contract_fully_scalar_lorentz(Metric(a,ad))
    assert 'D' in render_latex(out)


def test_metric_vector_network_to_scalar_product():
    a=Index('a','up'); b=Index('b','down')
    p=Vector('p'); q=Vector('q')
    expr=Product(Metric(a,b),VectorComponent(p,Index('a','down')),VectorComponent(q,Index('b','up')))
    out=contract_fully_scalar_lorentz(expr)
    assert isinstance(out, ScalarProduct)
