from qedcalc.operations.corner import corner_phase63_pure_matching_audit

a=corner_phase63_pure_matching_audit()
print('Phase-63 pure finite-rho matching audit')
for k,v in a.items():
    print(f'{k}: {v}')
assert a['analytic_matching_constant'] == 0
assert a['last_within_uncertainty']
print('Phase-63: PASS')
