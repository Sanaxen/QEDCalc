import sympy as sp

from qedcalc.operations.crossed_ladder import (
    crossed_h_u_integrated_kernel_checks,
    crossed_tq_preintegration_checks,
)


def test_crossed_u_domain_bridge():
    checks = crossed_h_u_integrated_kernel_checks()
    assert checks["u_lower"] == 0
    assert checks["upper_endpoint_S"] == 1


def test_crossed_tq_triangle_bridge():
    checks = crossed_tq_preintegration_checks()
    assert checks["jacobian_difference"] == 0
    assert checks["log_argument_difference"] == 0
    assert checks["triangle_conditions"] == ("t>0", "q>=t", "q<=1")
