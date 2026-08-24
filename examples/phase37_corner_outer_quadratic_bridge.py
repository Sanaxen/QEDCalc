import sympy as sp
from qedcalc.operations.corner import (
    corner_lambda_prime_bulk_coefficients,
    corner_outer_quadratic_bridge,
    corner_outer_quadratic_checkpoint_residuals,
)

u,v,ad,al,z=sp.symbols('u v a_d a_l z', positive=True)
print('Phase-37 corner Lambda-prime -> outer quadratic bridge')
lp=corner_lambda_prime_bulk_coefficients(u,v)
print("Lambda' k^2 coefficient:", lp['k2'])
print("Lambda' p.k coefficient:", lp['pk'])
b=corner_outer_quadratic_bridge(u,v,ad,al,z)
print('H:', sp.factor(b.H))
print('B shift:', sp.factor(b.shift_B))
print('Q:', sp.factor(b.Q))
print('H_z:', sp.factor(b.H_z))
print('B_z shift:', sp.factor(b.shift_B_z))
print('Q_z:', sp.factor(b.Q_z))
r=corner_outer_quadratic_checkpoint_residuals(u,v,ad,al,z)
print('Residuals:', r)
assert all(x == 0 for x in r.values())
print('Phase-37 corner Lambda-prime -> outer quadratic bridge: PASS')
