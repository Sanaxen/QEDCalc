import sympy as sp

from qedcalc.operations.corner import (
    corner_soft_kernel,
    corner_soft_spatial_kernel,
    corner_soft_integrate_S,
    corner_soft_integrate_R,
    corner_soft_ir_coefficient,
    corner_shifted_p_minus_k,
    corner_hard_primary_result,
    corner_shift_correction_result,
    corner_hard_total_result,
    corner_z_sector_result,
    corner_finite_result,
    corner_expected_finite_result,
    corner_result_difference,
    corner_self_energy_ir_cancellation,
)


def test_corner_soft_kernel_factorization():
    U,R,S,v = sp.symbols('U R S v', positive=True)
    lhs = corner_soft_kernel(U,R,S,v)
    rhs = sp.simplify(U/(1+U**2) * corner_soft_spatial_kernel(R,S,v))
    assert sp.simplify(lhs-rhs) == 0


def test_corner_soft_spatial_integrals():
    R,S,v = sp.symbols('R S v', positive=True)
    direct_S = sp.integrate(corner_soft_spatial_kernel(R,S,v), (S,0,sp.oo))
    assert sp.simplify(direct_S - corner_soft_integrate_S(R,v)) == 0
    direct_R = sp.integrate(corner_soft_integrate_S(R,v), (R,0,sp.oo))
    assert sp.simplify(direct_R - corner_soft_integrate_R(v)) == 0
    assert corner_soft_ir_coefficient() == 1


def test_corner_shift_coefficients():
    u,v = sp.symbols('u v')
    c = corner_shifted_p_minus_k(u,v)
    assert sp.simplify(c['p_prime']-(1-u*v)) == 0
    assert sp.simplify(c['p_double_prime']+u*(1-v)) == 0
    assert c['k'] == -1


def test_corner_hard_sector_sum():
    expected = (-sp.Rational(11,3) - sp.Rational(9,8)*sp.zeta(3)
                + sp.pi**2/18 + sp.Rational(7,12)*sp.pi**2*sp.log(2))
    assert sp.simplify(corner_hard_primary_result()+corner_shift_correction_result()-expected) == 0
    assert sp.simplify(corner_hard_total_result()-expected) == 0


def test_corner_z_sector():
    expected = sp.Rational(7,8)+sp.Rational(5,8)*sp.zeta(3)-sp.pi**2*sp.log(2)/4
    assert sp.simplify(corner_z_sector_result()-expected) == 0


def test_corner_final_finite_part():
    assert corner_result_difference() == 0
    assert sp.simplify(corner_finite_result()-corner_expected_finite_result()) == 0


def test_corner_self_energy_ir_cancellation():
    c = corner_self_energy_ir_cancellation()
    assert c.corner_log_coefficient == 1
    assert c.self_energy_log_coefficient == -1
    assert c.total_log_coefficient == 0
    expected = -sp.Rational(7,3)-sp.zeta(3)/2+sp.pi**2*sp.log(2)/3
    assert sp.simplify(c.combined_finite-expected) == 0


def test_corner_soft_hard_diagnostic_split():
    from qedcalc.operations.corner import (
        corner_soft_finite_constant,
        corner_hard_remainder_from_soft_split,
        corner_soft_hard_split_difference,
    )
    expected_soft = sp.pi**2/6 + sp.log(2)**2 - 3*sp.log(2) - sp.Rational(7,4)
    assert sp.simplify(corner_soft_finite_constant()-expected_soft) == 0
    expected_hard = (-sp.Rational(25,24)-sp.pi**2/9-sp.log(2)**2+3*sp.log(2)
                     -sp.zeta(3)/2+sp.pi**2*sp.log(2)/3)
    assert sp.simplify(corner_hard_remainder_from_soft_split()-expected_hard) == 0
    assert corner_soft_hard_split_difference() == 0
