import sympy as sp

from qedcalc.operations.crossed_ladder import (
    crossed_projective_forms,
    crossed_h_log_argument,
    crossed_tq_transform,
    crossed_tq_log_argument,
    crossed_half_sector_result,
    crossed_dilog_reflection_sum,
    crossed_endpoint_finite_result,
    crossed_endpoint_asymptotics,
    crossed_endpoint_total_result,
    crossed_final_result,
    crossed_expected_result,
    crossed_result_difference,
)


def test_projective_forms_linear_in_v():
    R,S,U,V = sp.symbols("R S U V")
    f = crossed_projective_forms(R,S,U,V)
    assert sp.degree(f.Delta, V) == 1
    assert sp.degree(f.W, V) == 1
    assert sp.expand(f.Delta - (f.Delta0 + (R+U)*V)) == 0
    assert sp.expand(f.W - (f.W0 + R**2*V)) == 0


def test_h_and_tq_log_arguments_match():
    t,q = sp.symbols("t q", positive=True)
    h,R,j = crossed_tq_transform(t,q)
    from_h = sp.simplify(crossed_h_log_argument(h,R))
    direct = crossed_tq_log_argument(t,q)
    assert sp.simplify(from_h-direct) == 0
    assert j == t**-3


def test_half_sector_result():
    expected = sp.pi**2 - sp.Rational(5,6)*sp.pi**2*sp.log(2) - sp.Rational(35,12)*sp.zeta(3)
    assert sp.simplify(crossed_half_sector_result()-expected) == 0


def test_dilog_reflection_closed_form_shape():
    q = sp.Symbol("q", positive=True)
    expected = sp.pi**2/6 + sp.log(q)**2/2 + sp.log(1-q)**2/2 - 2*sp.log(q)*sp.log(1-q)
    assert sp.simplify(crossed_dilog_reflection_sum(q)-expected) == 0


def test_endpoint_finite_result():
    expected = sp.Rational(25,6)*sp.zeta(3) - sp.Rational(19,36)*sp.pi**2
    assert sp.simplify(crossed_endpoint_finite_result()-expected) == 0


def test_endpoint_log_divergences_cancel():
    a = crossed_endpoint_asymptotics()
    assert sp.simplify(a.divergent_sum) == 0
    assert sp.simplify(a.finite_boundary - (sp.Rational(1,6)-sp.pi**2/9)) == 0


def test_endpoint_total():
    expected = sp.Rational(1,6) - sp.Rational(23,36)*sp.pi**2 + sp.Rational(25,6)*sp.zeta(3)
    assert sp.simplify(crossed_endpoint_total_result()-expected) == 0


def test_crossed_final_result():
    assert crossed_result_difference() == 0
    assert sp.simplify(crossed_final_result()-crossed_expected_result()) == 0


def test_v044_raw_crossed_bridge_and_family_rules():
    from pathlib import Path
    from qedcalc.parser.qed_latex import parse_loop_integral_latex
    from qedcalc.operations.crossed_ladder import (
        analyze_raw_crossed_ladder,
        derive_crossed_scalar_product_rules_from_family,
        crossed_ladder_ibp_family,
    )
    root=Path(__file__).resolve().parents[1]
    raw=analyze_raw_crossed_ladder(parse_loop_integral_latex((root/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')))
    assert raw.electron_labels == ('E1','E2','E3','E4')
    assert raw.base_integral_index.as_tuple() == (1,1,0,1,1,1,1)
    rules=derive_crossed_scalar_product_rules_from_family()
    K,L,H,E1,E2,E3,E4=sp.symbols('K L H E1 E2 E3 E4')
    assert sp.simplify(rules[sp.Symbol('lp')]-(E4-L)/2)==0
    assert sp.simplify(rules[sp.Symbol('kp')]-(E3-H-E4+L)/2)==0
    fam=crossed_ladder_ibp_family()
    assert fam.denominator_names == ('K','L','H','E1','E2','E3','E4')


def test_v044_raw_crossed_corrected_projector_generates_95_monomials():
    from pathlib import Path
    from qedcalc.parser.qed_latex import parse_loop_integral_latex
    from qedcalc.operations.crossed_ladder import analyze_raw_crossed_ladder, crossed_general_q_projector_result
    root=Path(__file__).resolve().parents[1]
    raw=analyze_raw_crossed_ladder(parse_loop_integral_latex((root/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')))
    result=crossed_general_q_projector_result(raw)
    assert result.trace_order == 'spin_sum'
    assert len(result.integral_table) == 95


def test_crossed_bare_scalar_parametric_bridge():
    from qedcalc.operations.crossed_ladder import (
        crossed_bare_scalar_parametric_representation,
        crossed_bare_scalar_parametric_checks,
    )
    rep = crossed_bare_scalar_parametric_representation()
    checks = crossed_bare_scalar_parametric_checks()
    assert rep.active_denominators == ('K','L','E1','E2','E3','E4')
    assert checks['U_total_degree'] == 2
    assert checks['F_total_degree'] == 3
    assert checks['U_homogeneous'] is True
    assert checks['F_homogeneous'] is True


def test_crossed_ladder_reversal_symmetry():
    from qedcalc.operations.crossed_ladder import (
        crossed_ladder_integral_symmetries,
        canonicalize_crossed_ladder_integral,
    )
    from qedcalc.operations.ibp import IntegralIndex
    group = crossed_ladder_integral_symmetries()
    assert len(group) == 2
    a = IntegralIndex((1,0,0,2,3,4,5))
    b = IntegralIndex((0,1,0,5,4,3,2))
    assert canonicalize_crossed_ladder_integral(a) == canonicalize_crossed_ladder_integral(b)
