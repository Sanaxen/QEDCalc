from qedcalc.operations.corner import corner_phase43_dimensional_audit
r=corner_phase43_dimensional_audit()
print('Phase-43 corner D-dimensional inner-radial audit')
for k,v in r.items(): print(k,':',v)
assert r['four_dimensional_limit']==1
import sympy as sp
assert r['gamma_coefficient_linear']==-sp.Rational(3,2)
assert r['evanescent_finite_shift']==-sp.Rational(3,2)
print('Phase-43: PASS')
