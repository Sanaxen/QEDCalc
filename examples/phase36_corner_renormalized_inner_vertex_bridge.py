import sympy as sp
from qedcalc.operations.corner import (
    corner_renormalized_inner_vertex_sectors,
    corner_inner_vertex_z_integral_residual,
    corner_inner_vertex_kappa_difference_residual,
    corner_inner_vertex_sector_scalar_coefficients,
)

print('Phase-36 corner renormalized-inner-vertex sector bridge')
r=corner_renormalized_inner_vertex_sectors()
print('K sector:', r.K_sector)
print('z sector closed:', r.z_sector_closed)
print('kappa sector:', r.kappa_sector)
print('gamma total:', r.gamma_sector_closed)
print('z integral residual:', corner_inner_vertex_z_integral_residual())
print('kappa denominator identity residual:', corner_inner_vertex_kappa_difference_residual())
L0=sp.Symbol('L0', positive=True)
print('on-shell scalar coefficients:', corner_inner_vertex_sector_scalar_coefficients(lambda0_sq=L0,lambda_prime_sq=L0))
assert corner_inner_vertex_z_integral_residual() == 0
assert corner_inner_vertex_kappa_difference_residual() == 0
c=corner_inner_vertex_sector_scalar_coefficients(lambda0_sq=L0,lambda_prime_sq=L0)
assert all(sp.simplify(c[k]) == 0 for k in ('z_log','kappa_difference','gamma_total'))
print('Phase-36 corner renormalized-inner-vertex sector bridge: PASS')
