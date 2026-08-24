from qedcalc.operations.corner import corner_phase42_physical_remainder_audit
r=corner_phase42_physical_remainder_audit()
print('Phase-42 physical inner/outer bridge')
for k,v in r.items(): print(k,':',v)
assert r['temporal_on_shell_residual']==0
assert all(r['odd_flags'])
for key in ('lp_poles','B_poles','log_poles'):
    assert all(c==0 for _,c in r[key]), (key,r[key])
print('Phase-42: PASS')
