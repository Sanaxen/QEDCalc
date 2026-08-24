import sympy as sp

from qedcalc.operations.master_integrals import (
    ordinary_ladder_terminal_basis,
    classify_ordinary_ladder_terminal_basis,
    ordinary_ladder_basis_z0_evaluations,
    massive_tadpole_euclidean,
    one_massless_two_massive_vacuum_euclidean,
    massless_bubble_on_shell_electron_euclidean,
    massless_two_point_then_on_shell_electron_euclidean,
    ordinary_ladder_T1_z0_euclidean,
    ordinary_ladder_T2_z0_euclidean,
    ordinary_ladder_T3_z0_euclidean,
    ordinary_ladder_z0_T_ibp_reductions,
)


def test_terminal_basis_classification_and_parametric_homogeneity():
    D,z,m2 = sp.symbols('D z m2')
    rows = classify_ordinary_ladder_terminal_basis(D=D,z=z,mass_squared=m2)
    assert len(rows) == 12
    assert [r.basis_index for r in rows if r.kind == 'factorized_lower'] == [0,1,3]
    for r in rows:
        p = r.parametric
        scale = sp.Symbol('lam', positive=True)
        sub = {x: scale*x for x in p.parameters}
        assert sp.simplify(p.U.subs(sub) / p.U - scale**2) == 0
        assert sp.simplify(p.F.subs(sub) / p.F - scale**3) == 0


def test_factorized_terminal_values_match_tadpole_products():
    D,m2 = sp.symbols('D m2', positive=True)
    rows = classify_ordinary_ladder_terminal_basis(D=D,mass_squared=m2)
    T1 = massive_tadpole_euclidean(1,D,m2)
    T2 = massive_tadpole_euclidean(2,D,m2)
    T3 = massive_tadpole_euclidean(3,D,m2)
    assert sp.simplify(rows[0].factorized_value - T1*T1) == 0
    assert sp.simplify(rows[1].factorized_value - T1*T1) == 0
    assert sp.simplify(rows[3].factorized_value - T2*T3) == 0


def test_z0_analytic_basis_count_and_unresolved_indices():
    rows = ordinary_ladder_basis_z0_evaluations()
    assert len(rows) == 12
    assert [r.basis_index for r in rows if r.status == 'exact'] == list(range(12))
    assert [r.basis_index for r in rows if r.status == 'unresolved'] == []


def test_z0_degenerate_factorizations():
    D,m2 = sp.symbols('D m2', positive=True)
    rows = ordinary_ladder_basis_z0_evaluations(D,m2)
    T1 = massive_tadpole_euclidean(1,D,m2)
    T2 = massive_tadpole_euclidean(2,D,m2)
    assert sp.simplify(rows[2].value - T2*T1) == 0
    assert sp.simplify(rows[4].value - T2*T2) == 0


def test_vacuum_and_bubble_closed_forms_are_used():
    D,m2 = sp.symbols('D m2', positive=True)
    rows = ordinary_ladder_basis_z0_evaluations(D,m2)
    assert sp.simplify(rows[5].value - one_massless_two_massive_vacuum_euclidean(1,1,1,D,m2)) == 0
    assert sp.simplify(rows[6].value - one_massless_two_massive_vacuum_euclidean(1,1,2,D,m2)) == 0
    assert sp.simplify(rows[7].value - massless_bubble_on_shell_electron_euclidean(1,D,m2)) == 0
    assert sp.simplify(rows[9].value - massless_bubble_on_shell_electron_euclidean(2,D,m2)) == 0


def test_z0_parametric_polynomials_show_expected_degeneracies():
    D,z,m2 = sp.symbols('D z m2')
    rows = classify_ordinary_ladder_terminal_basis(D=D,z=z,mass_squared=m2)
    # Basis 5/6 become the one-massless/two-massive vacuum family at z=0:
    # F = U * m^2 * (x_E2 + x_E4).
    for bi in (5,6):
        p = rows[bi].parametric
        # active denominators are L,E2,E4
        xL,xE2,xE4 = p.parameters
        expected = sp.factor(p.U * m2 * (xE2+xE4))
        assert sp.simplify(p.F.subs(z,0) - expected) == 0
    # Basis 7 is z-independent.
    assert z not in rows[7].parametric.F.free_symbols


def test_z0_T_family_symbolic_ibp_reduces_T2_and_T3():
    D,m2 = sp.symbols('D m2', positive=True)
    data = ordinary_ladder_z0_T_ibp_reductions(D,m2)
    T1,T2,T3 = data['T1'],data['T2'],data['T3']
    r2=data['T2_reduction']; r3=data['T3_reduction']
    assert sp.factor(r2[T1] + (D-3)/(2*m2)) == 0
    assert sp.factor(r3[T1] - (D-6)*(D-4)*(D-3)/(8*m2**2*(D-5))) == 0
    assert T2 not in r2 and T3 not in r3


def test_z0_remaining_three_basis_values_are_exact():
    D,m2 = sp.symbols('D m2', positive=True)
    rows = ordinary_ladder_basis_z0_evaluations(D,m2)
    assert sp.simplify(rows[8].value - ordinary_ladder_T1_z0_euclidean(D,m2)) == 0
    assert sp.simplify(rows[10].value - ordinary_ladder_T2_z0_euclidean(D,m2)) == 0
    assert sp.simplify(rows[11].value - ordinary_ladder_T3_z0_euclidean(D,m2)) == 0


def test_general_massless_bubble_then_on_shell_contains_previous_special_case():
    D,m2 = sp.symbols('D m2', positive=True)
    old = massless_bubble_on_shell_electron_euclidean(1,D,m2)
    new = massless_two_point_then_on_shell_electron_euclidean(1,1,1,D,m2)
    assert sp.simplify(old-new) == 0


def test_T1_gamma_formula_matches_gauss_hypergeometric_representation_at_generic_point():
    # epsilon=1/5 => D=18/5 lies safely inside the convergence strip used by the derivation.
    eps=sp.Rational(1,5); D=4-2*eps
    term1 = sp.gamma(eps)**2/sp.gamma(2*eps) * sp.hyper([1,eps],[2-eps],1)
    term2 = sp.gamma(eps)*sp.gamma(1-eps) * sp.hyper([2*eps,eps],[2-eps],1)
    param = (term1-term2)/((1-eps)*(1-2*eps))
    hyper_value = sp.pi**D * sp.gamma(2*eps) * param
    gamma_value = ordinary_ladder_T1_z0_euclidean(D,1)
    assert abs(complex(sp.N(hyper_value-gamma_value,40))) < 1e-30


def test_v044_required_basis_z_derivatives_are_all_closed():
    from qedcalc.operations.master_integrals import ordinary_ladder_basis_z_derivative_evaluations
    rows = ordinary_ladder_basis_z_derivative_evaluations()
    exact = [r.basis_index for r in rows if r.status == 'exact']
    unresolved = [r.basis_index for r in rows if r.status == 'unresolved']
    assert exact == [0,1,3,5,6,7,8]
    assert unresolved == []
    assert rows[0].value == rows[1].value == rows[3].value == rows[7].value == 0


def test_v044_basis5_basis6_z_derivative_closed_forms():
    from qedcalc.operations.master_integrals import (
        ordinary_ladder_basis_z_derivative_evaluations,
        one_massless_two_massive_vacuum_z_derivative_euclidean,
    )
    D,m2 = sp.symbols('D m2', positive=True)
    rows = ordinary_ladder_basis_z_derivative_evaluations(D,m2)
    assert sp.simplify(rows[5].value-one_massless_two_massive_vacuum_z_derivative_euclidean(1,D,m2)) == 0
    assert sp.simplify(rows[6].value-one_massless_two_massive_vacuum_z_derivative_euclidean(2,D,m2)) == 0


def test_v044_basis8_z_derivative_dimension_shift_is_exact_expression():
    from qedcalc.operations.master_integrals import (
        ordinary_ladder_basis_z_derivative_evaluations,
        ordinary_ladder_basis8_z_derivative_shifted_reduction,
    )
    D,m2 = sp.symbols('D m2', positive=True)
    rows = ordinary_ladder_basis_z_derivative_evaluations(D,m2)
    assert rows[8].status == 'exact'
    assert sp.simplify(rows[8].value-ordinary_ladder_basis8_z_derivative_shifted_reduction(D,m2)) == 0
