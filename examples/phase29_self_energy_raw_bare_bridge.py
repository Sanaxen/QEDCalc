import sympy as sp
from qedcalc.operations.self_energy import self_energy_raw_bare_parametric_integrand
r=self_energy_raw_bare_parametric_integrand()
print('Phase-29 self-energy raw bare magnetic bridge')
print('Base magnetic polynomial terms:',r.base_term_count)
print('Gaussian sectors:',r.gaussian_sector_keys)
print('Delta:',sp.factor(r.Delta))
print('F:',sp.factor(r.F))
print('Numerator terms:',len(sp.Poly(sp.together(r.numerator),*sp.symbols('x y u v rho')).terms()))
print('Checkpoint residuals:',r.sample_checks)
print('Phase-29 self-energy raw bare magnetic bridge: PASS' if all(v==0 for v in r.sample_checks) else 'FAIL')
from qedcalc.operations.self_energy import self_energy_raw_uv_subdivergence
uv=self_energy_raw_uv_subdivergence()
print('UV Y-integrated coefficient:',uv.coefficient_x)
print('UV rho=0:',uv.coefficient_rho0)
print('UV checkpoint difference:',uv.archived_difference)
print('Phase-29 UV sector: PASS' if uv.archived_difference==0 else 'FAIL')
