import sympy as sp

from qedcalc.operations.vacuum_polarization import (
    vp_shifted_even_tensor_coefficients,
    vp_dimensional_transverse_reduction,
    vp_hat_dimreg_subtracted_integrand,
    vp_hat_renormalized_integrand_from_dimreg,
    vp_gminus2_double_integrand,
    vp_gminus2_double_integrand_from_dimreg,
    vp_z_integrated_kernel,
    vp_z_integrated_kernel_derived,
    vp_x_integrand_derived,
    vp_x_primitive_derived,
    vp_x_primitive_derivative_residual,
    vp_x_endpoint_one_from_primitive,
    vp_x_endpoint_zero_from_primitive,
    vp_final_coefficient_derived,
    vp_expected_analytic,
)


def test_v052_shifted_trace_coefficients_reproduce_4d_audit():
    z, k2, m2, r2 = sp.symbols('z k2 m2 r2')
    g, kk = vp_shifted_even_tensor_coefficients(4, z, k2, m2, r2)
    a = z*(1-z)
    assert sp.simplify(g - (4*m2 - 2*r2 + 4*a*k2)) == 0
    assert sp.simplify(kk + 8*a) == 0


def test_v052_dimensional_ibp_makes_tensor_exactly_transverse():
    D, z, k2, m2, J2 = sp.symbols('D z k2 m2 J2')
    r = vp_dimensional_transverse_reduction(D,z,k2,m2,J2)
    a=z*(1-z)
    assert sp.simplify(r['metric'] - 8*a*k2*J2) == 0
    assert sp.simplify(r['kk'] + 8*a*J2) == 0
    assert r['transverse_residual'] == 0


def test_v052_dimreg_subtraction_generates_finite_log_integrand():
    D, z, k2, m2 = sp.symbols('D z k2 m2', positive=True)
    raw = vp_hat_dimreg_subtracted_integrand(D,k2,m2,z)
    assert raw.has(sp.gamma(2-D/2))
    finite = vp_hat_renormalized_integrand_from_dimreg(k2,m2,z)
    expected = 2*z*(1-z)*sp.log(m2/(m2-k2*z*(1-z)))
    assert sp.simplify(sp.expand_log(finite, force=True)-sp.expand_log(expected, force=True)) == 0


def test_v052_outer_magnetic_insertion_regenerates_double_kernel():
    x,z=sp.symbols('x z', positive=True)
    assert sp.simplify(vp_gminus2_double_integrand_from_dimreg(x,z)-vp_gminus2_double_integrand(x,z)) == 0


def test_v052_elementary_z_integration_regenerates_existing_H():
    x=sp.symbols('x', positive=True)
    assert sp.simplify(vp_z_integrated_kernel_derived(x)-vp_z_integrated_kernel(x)) == 0


def test_v052_generated_primitive_differentiates_to_x_kernel():
    x=sp.symbols('x', positive=True)
    assert vp_x_primitive_derivative_residual(x) == 0
    assert vp_x_primitive_derived(x).has(sp.polylog(2,x))


def test_v052_endpoint_generation_and_final_coefficient():
    x=sp.symbols('x', positive=True)
    e1=vp_x_endpoint_one_from_primitive(x)
    e0=vp_x_endpoint_zero_from_primitive(x)
    assert sp.simplify(e1-(sp.Rational(11,36)-sp.pi**2/3)) == 0
    assert e0 == -3
    assert sp.simplify(vp_final_coefficient_derived()-vp_expected_analytic()) == 0
