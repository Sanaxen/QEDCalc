import sympy as sp
from qedcalc.operations.self_energy import (
    finite_b_integrated_kernel_derived, finite_b_integrated_kernel,
    finite_one_variable_kernel_derived, finite_one_variable_kernel,
    finite_one_variable_kernel_residual,
    self_energy_standard_integrals, finite_part_analytic_derived,
    finite_part_expected, self_energy_ir_asymptotic_derived,
    total_self_energy_coefficient_derived, total_self_energy_coefficient,
)


def test_v052_b_integral_is_regenerated_from_GA():
    a,z,q=sp.symbols('a z q', positive=True)
    got=finite_b_integrated_kernel_derived(a,z,q)
    L=sp.log(1+a/(q*z*(1-a)))
    C1=q*(a-1)*(5*a*q+a-5*q+7)*z-2*a*(2*a*q+a-2*q+2)
    C0=a*(5*a*q+a-5*q+7)
    ref=q*(a-1)*(q-1)/a**2*(C1*L+C0)
    assert sp.simplify(got-ref) == 0


def test_v052_q_reduction_regenerates_one_variable_kernel():
    a=sp.symbols('a', positive=True)
    assert finite_one_variable_kernel_residual(a) == 0
    assert sp.simplify(sp.expand_log(finite_one_variable_kernel_derived(a),force=True)-sp.expand_log(finite_one_variable_kernel(a),force=True)) == 0


def test_v052_standard_integrals_are_generated_from_general_identities():
    I=self_energy_standard_integrals()
    assert I['x_log_x'] == -sp.Rational(1,4)
    assert I['log_x'] == -1
    assert sp.simplify(I['log_x_over_1mx'] + sp.pi**2/6) == 0
    assert I['x_log_1mx'] == -sp.Rational(3,4)
    assert I['endpoint_pair'] == -1


def test_v052_finite_part_is_assembled_without_stored_final_value():
    f=finite_part_analytic_derived()
    assert sp.simplify(f['ln_a']-(sp.Rational(1,24)-sp.pi**2/36)) == 0
    assert sp.simplify(f['ln_one_minus_a']-(sp.Rational(5,24)-sp.pi**2/36)) == 0
    assert f['endpoint_pair'] == -sp.Rational(1,6)
    assert f['rational'] == -sp.Rational(1,8)
    assert sp.simplify(f['total']-finite_part_expected()) == 0


def test_v052_ir_factorized_piece_generates_log_and_half():
    rho=sp.symbols('rho', positive=True)
    ir=self_energy_ir_asymptotic_derived(rho)
    assert ir['A1_limit'] == sp.Rational(1,2)
    assert ir['J_log_coefficient'] == -1
    assert ir['J_finite'] == -sp.Rational(1,2)
    assert sp.simplify(ir['B_asymptotic']-(sp.log(rho)+sp.Rational(1,2))) == 0


def test_v052_total_self_energy_matches_audited_checkpoint():
    rho=sp.symbols('rho', positive=True)
    assert sp.simplify(total_self_energy_coefficient_derived(rho)-total_self_energy_coefficient(rho)) == 0
