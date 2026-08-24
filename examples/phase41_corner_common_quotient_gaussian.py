from qedcalc.operations.corner import corner_phase41_audit
r=corner_phase41_audit()
print('Phase-41 corner common-quotient/Gaussian bridge')
for k,v in r.items(): print(k,':',v)
assert all(r['odd_flags'])
assert r['log_delta_residual']==0
for key in ('lp_poles','l0_poles','log_photon_poles','log_electron_poles'):
    assert all(coeff==0 for _,coeff in r[key]), (key,r[key])
print('Phase-41: PASS')
