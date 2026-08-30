from qedcalc import render_latex
from qedcalc.core.expression import (
    Symbol, Vector, Index, Gamma, Slash, ScalarProduct, VectorComponent,
    Add, Product, NCProduct, ScalarMul, SpinorSandwich
)
from qedcalc.operations.qexpansion import q_degree, truncate_q_order, apply_elastic_onshell_q
from qedcalc.operations.spinor import reduce_external_dirac_after_q
from qedcalc.operations.current import decompose_q_basis, pair_coefficient_from_q_basis


def test_q_degree_and_first_order_truncation():
    q=Vector('q'); p=Vector('p'); mu=Index('mu','down')
    expr=Add(
        Gamma(mu),
        VectorComponent(q,mu),
        Product(ScalarProduct(p,q),Gamma(mu)),
        Product(ScalarProduct(q,q),Gamma(mu)),
    )
    out=truncate_q_order(expr,1)
    text=render_latex(out)
    assert r'q\cdot q' not in text
    assert r'p\cdot q' in text
    assert q_degree(Product(ScalarProduct(q,q),Gamma(mu)))==2


def test_elastic_onshell_then_truncate_removes_p_dot_q():
    p=Vector('p'); q=Vector('q'); mu=Index('mu','down')
    expr=Add(ScalarProduct(p,p), Product(ScalarProduct(p,q),Gamma(mu)))
    out=truncate_q_order(apply_elastic_onshell_q(expr),1)
    text=render_latex(out)
    assert r'm^{2}' in text
    assert r'p\cdot q' not in text
    assert r'q\cdot q' not in text


def test_post_q_external_dirac_left_and_right_rules():
    mu=Index('mu','down')
    # left /p -> m - /q
    left=SpinorSandwich(NCProduct(Slash(Vector('p')),Gamma(mu)),Vector("p'"),Vector('p'))
    left_out=reduce_external_dirac_after_q(left)
    text=render_latex(left_out)
    assert r'\rlap{/}p' not in text
    assert r'p_{\mu}' in text
    assert 'm' in text
    # right /p -> m
    right=SpinorSandwich(NCProduct(Gamma(mu),Slash(Vector('p'))),Vector("p'"),Vector('p'))
    right_out=reduce_external_dirac_after_q(right)
    assert r'\rlap{/}p' not in render_latex(right_out)


def test_q_basis_pair_coefficient():
    idx=Index('mu','down'); B=Symbol('B'); A=Symbol('A')
    expr=Add(
        Product(A,Gamma(idx)),
        Product(ScalarMul(2,B),VectorComponent(Vector('p'),idx)),
        Product(B,VectorComponent(Vector('q'),idx)),
    )
    d=decompose_q_basis(expr)
    assert d.gamma==A
    assert pair_coefficient_from_q_basis(d)==B


def test_sympy_scalar_factor_bridge():
    from qedcalc.core.expression import Power
    from qedcalc.operations.scalar_sympy import factor_scalar_polynomial
    x=Symbol('x'); y=Symbol('y'); m=Symbol('m')
    expr=Add(
        Product(Power(x,2),Power(m,2)),
        ScalarMul(2,Product(x,y,Power(m,2))),
        Product(Power(y,2),Power(m,2)),
    )
    out=factor_scalar_polynomial(expr)
    text=render_latex(out)
    assert r'\left(x + y\right)^{2}' in text or r'\left(y + x\right)^{2}' in text


def test_normalize_scalar_factors_out_of_dirac_chain():
    from qedcalc.operations.algebra import normalize_noncommutative_products
    idx=Index('mu','down'); x=Symbol('x')
    expr=NCProduct(Product(x,Slash(Vector('p'))),Gamma(idx))
    out=normalize_noncommutative_products(expr)
    text=render_latex(out)
    assert text.startswith('x')
    assert r'\rlap{/}p\,\gamma_{\mu}' in text


def test_exact_external_dirac_reducer_terminates():
    from qedcalc.operations.spinor import sandwich, reduce_external_dirac_exact
    idx=Index('mu','down')
    op=NCProduct(Slash(Vector('p')),Gamma(idx),Slash(Vector("p'")))
    out=reduce_external_dirac_exact(sandwich(op))
    text=render_latex(out)
    assert r'\rlap{/}p' not in text
    assert r"\rlap{/}p'" not in text


def test_q_basis_gordon_split_and_f2_projection():
    from qedcalc.operations.current import decompose_q_basis, split_q_basis_into_gordon, project_f2_from_q_basis
    from qedcalc.operations.scalar_sympy import simplify_scalar_with_sympy
    idx=Index('mu','down'); m=Symbol('m'); x=Symbol('x'); y=Symbol('y')
    cp=ScalarMul(4,Product(m,Add(x,y),Add(Symbol('-1'),x,y)))
    cq=Symbol('Cq')
    expr=Add(Product(cp,VectorComponent(Vector('p'),idx)),Product(cq,VectorComponent(Vector('q'),idx)))
    d=decompose_q_basis(expr)
    split=split_q_basis_into_gordon(d)
    assert split.residual==Symbol('0')
    f2=simplify_scalar_with_sympy(project_f2_from_q_basis(d),'factor')
    assert 'm^{2}' in render_latex(f2)


def test_triangle_integral_gives_two_and_qed_prefactor_schwinger():
    from qedcalc.operations.integral import triangle_integral_ratio, qed_vertex_prefactor_after_n3_loop
    from qedcalc.core.expression import Power
    x=Symbol('x'); y=Symbol('y'); m=Symbol('m')
    s=Add(x,y)
    numerator=ScalarMul(4,Product(Power(m,2),s,Add(Symbol('1'),ScalarMul(-1,s))))
    delta=Product(Power(m,2),Power(s,2))
    integrand,value=triangle_integral_ratio(numerator,delta)
    assert value==2
    final=render_latex(qed_vertex_prefactor_after_n3_loop(value))
    assert r'\frac{\alpha}{2\,\pi}' in final or (r'\alpha' in final and r'\pi' in final)
