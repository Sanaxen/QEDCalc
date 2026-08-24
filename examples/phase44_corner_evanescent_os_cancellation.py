import sympy as sp
from qedcalc.operations.corner import corner_phase44_evanescent_os_cancellation
r=corner_phase44_evanescent_os_cancellation()
print('Phase-44 corner evanescent OS-cancellation bridge')
for k,v in r.items(): print(k,':',v)
assert r['local_shift']==-sp.Rational(3,2)
assert r['bare_local_coeff']==r['B_local_coeff']
assert r['renormalized_local_coeff']==0
assert r['outer_base_residual']==0
assert r['outer_transverse_residual']==0
print('Phase-44: PASS')
