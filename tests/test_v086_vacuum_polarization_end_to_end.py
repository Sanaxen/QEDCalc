import sympy as sp
from qedcalc.operations.vacuum_polarization import vp_phase79_end_to_end_checkpoint


def test_phase79_vacuum_polarization_end_to_end_exact_closure():
    c = vp_phase79_end_to_end_checkpoint()
    assert c["transverse_residual"] == 0
    assert c["on_shell_subtraction_residual"] == 0
    assert c["four_dimensional_kernel_residual"] == 0
    assert c["outer_insertion_kernel_residual"] == 0
    assert c["z_kernel_residual"] == 0
    assert c["primitive_derivative_residual"] == 0
    assert c["endpoint_one"] == sp.Rational(11,36) - sp.pi**2/3
    assert c["endpoint_zero"] == -3
    assert c["final_closed_form_residual"] == 0
