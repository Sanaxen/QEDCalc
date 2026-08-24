import sympy as sp
from pathlib import Path

from qedcalc import Gamma, Index, NCProduct
from qedcalc.operations.ladder import (
    ladder_projector_coefficients, contract_outer_gamma_ddim_one,
    contract_outer_gamma_ddim_two, ladder_scalar_product_rules,
    load_ladder_coefficient_table, ladder_coefficient,
    one_loop_f2_dimensional, one_loop_z1_dimensional,
    ladder_subtraction_series, ladder_renormalized_checkpoint,
)


def test_projector_coefficients():
    D,z=sp.symbols('D z')
    a,b=ladder_projector_coefficients(D,z)
    assert sp.simplify(a - 2/(z*(D-2)*(z-4))) == 0
    assert sp.simplify(b - (D*z-2*z+4)/(z*(D-2)*(z-4)**2)) == 0


def test_ddim_outer_gamma_one_two():
    D=sp.Symbol('D')
    rho_u=Gamma(Index('rho','up')); rho_d=Gamma(Index('rho','down'))
    a=Gamma(Index('alpha','up')); b=Gamma(Index('beta','up'))
    one=contract_outer_gamma_ddim_one(NCProduct(rho_u,a,rho_d))
    assert str(one.coeff) in ('2 - D','2-D')
    two=contract_outer_gamma_ddim_two(NCProduct(rho_u,a,b,rho_d))
    assert two is not None


def test_scalar_product_rules():
    rules=ladder_scalar_product_rules()
    s={str(k):v for k,v in rules.items()}
    assert sp.simplify(s['kl'] - (sp.Symbol('K')+sp.Symbol('L')-sp.Symbol('H'))/2) == 0


def test_75_coefficient_table():
    p=Path(__file__).parents[1]/'data'/'ladder_Ddim_75_coefficients.csv'
    table=load_ladder_coefficient_table(p)
    assert len(table)==75
    D,z=sp.symbols('D z')
    assert sp.simplify(ladder_coefficient(table,1,1,0,1,1,1,1) + 16*(z-2)) == 0
    assert sp.simplify(ladder_coefficient(table,1,0,-1,1,1,1,1) - 8*(D-4)/(z-4)) == 0
    assert sp.simplify(ladder_coefficient(table,0,0,-1,1,1,1,1) - 8*(D-2)*(D-1)/(z-4)**2) == 0


def test_dimensional_subtraction_and_final():
    D,delta=sp.symbols('D delta')
    assert sp.simplify(one_loop_f2_dimensional(D) - (5-D)/(2*(D-3))) == 0
    assert sp.simplify(one_loop_z1_dimensional(D) + sp.Rational(1,2)*(D-1)/((D-3)*(D-4))) == 0
    s=ladder_subtraction_series(delta,1).removeO()
    assert sp.limit(delta*s, delta, 0) == -sp.Rational(3,4)
    assert sp.limit(s + sp.Rational(3,4)/delta, delta, 0) == 2
    final=ladder_renormalized_checkpoint(delta)
    assert sp.simplify(final - (sp.Rational(11,48)+sp.pi**2/18)) == 0

from qedcalc import parse_loop_integral_latex, render_latex
from qedcalc.operations.ladder import analyze_raw_ordinary_ladder, derive_ladder_scalar_product_rules_from_family


def test_raw_ladder_symbolic_dimension_and_family_detection():
    root=Path(__file__).parents[1]
    src=(root/'input'/'ordinary_ladder_2loop_bare.tex').read_text(encoding='utf-8')
    diagram=parse_loop_integral_latex(src)
    assert diagram.dimension == 'D'
    assert [v.name for v in diagram.loops] == ['k','l']
    raw=analyze_raw_ordinary_ladder(diagram)
    assert raw.electron_labels == ('E1','E2','E3','E4')
    assert sorted(raw.photon_labels) == ['K','L']
    assert raw.base_integral_index.as_tuple() == (1,1,0,1,1,1,1)
    assert len(raw.scalarized_integrand.denominator.factors) == 6


def test_derived_scalar_product_rules_match_reference_rules():
    derived=derive_ladder_scalar_product_rules_from_family()
    reference=ladder_scalar_product_rules()
    assert set(derived) == set(reference)
    for key in derived:
        assert sp.simplify(derived[key]-reference[key]) == 0

from qedcalc.operations.ladder import raw_ladder_q0_numerator


def test_raw_ladder_generates_q0_dirac_numerator_without_pprime():
    root=Path(__file__).parents[1]
    diagram=parse_loop_integral_latex((root/'input'/'ordinary_ladder_2loop_bare.tex').read_text(encoding='utf-8'))
    raw=analyze_raw_ordinary_ladder(diagram)
    q0=raw_ladder_q0_numerator(raw)
    text=render_latex(q0)
    assert "p'" not in text
    assert r"\gamma^{\rho}" in text
    assert r"\gamma^{\alpha}" in text
    assert r"\gamma_{\mu}" in text


def test_raw_ladder_a0_generates_29_integrals():
    from pathlib import Path
    from qedcalc.parser.qed_latex import parse_loop_integral_latex
    from qedcalc.operations.ladder import analyze_raw_ordinary_ladder, ladder_a0_integral_table
    root=Path(__file__).parents[1]
    diagram=parse_loop_integral_latex((root/'input'/'ordinary_ladder_2loop_bare.tex').read_text(encoding='utf-8'))
    raw=analyze_raw_ordinary_ladder(diagram)
    table=ladder_a0_integral_table(raw)
    assert len(table)==29
