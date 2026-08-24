import sympy as sp
from qedcalc.operations.corner import (
    corner_raw_inner_vertex_finite_bridge,
    corner_raw_inner_vertex_radial_residuals,
    corner_raw_inner_vertex_on_shell_residuals,
    corner_raw_inner_vertex_log_coeff_residuals,
    corner_raw_inner_shift_coefficients,
)

print('Phase-38 corner raw inner-vertex finite bridge')
b=corner_raw_inner_vertex_finite_bridge()
print("Lambda0^2:", b.lambda0_sq)
print("Lambda'^2:", b.lambda_prime_sq)
print('Shift coefficients:', corner_raw_inner_shift_coefficients())
print('Radial gamma residuals:', [M == sp.zeros(4) for M in corner_raw_inner_vertex_radial_residuals()])
print('On-shell k=0 residuals:', [M == sp.zeros(4) for M in corner_raw_inner_vertex_on_shell_residuals()])
print('Log gamma residuals:', [M == sp.zeros(4) for M in corner_raw_inner_vertex_log_coeff_residuals()])
assert all(M == sp.zeros(4) for M in corner_raw_inner_vertex_radial_residuals())
assert all(M == sp.zeros(4) for M in corner_raw_inner_vertex_on_shell_residuals())
assert all(M == sp.zeros(4) for M in corner_raw_inner_vertex_log_coeff_residuals())
print('Phase-38 corner raw inner-vertex finite bridge: PASS')
